"""Step 4 — Code criticism units (or firm responses) with Claude, using codebook.md as a cached system prompt.

    # Inspect one request without calling the API
    python explorations/qc_criticism_taxonomy/scripts/04_classify_llm.py --dry-run

    # Synchronous, resumable (skips ids already in the output JSONL)
    python .../04_classify_llm.py --mode sync --limit 50

    # Message Batches API (50% cheaper, asynchronous): submit, then collect when ended
    python .../04_classify_llm.py --mode batch-submit
    python .../04_classify_llm.py --mode batch-collect

    # Firm responses instead of criticism units
    python .../04_classify_llm.py --target responses --mode sync

Credentials: the Anthropic SDK reads ANTHROPIC_API_KEY (or an `ant auth login` profile).
Sync mode opts into server-side refusal fallbacks (`fallbacks="default"`); the Batches API does not
accept that parameter, so batch results record any refusal as-is.
Output: data/cleaned/pcaob/llm/<target>_<model>.jsonl — one JSON object per item.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import anthropic
import pandas as pd
from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
from anthropic.types.messages.batch_create_params import Request

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from qclib.config import LLM_DIR, RESPONSES_PATH, UNITS_PATH, load_taxonomy  # noqa: E402
from qclib.llm import DEFAULT_EFFORT, DEFAULT_MODEL, FALLBACK_BETA, request_params, validate_unit  # noqa: E402


def load_items(target: str) -> pd.DataFrame:
    """(item_id, text, firm, year) for units (non-boilerplate) or responses."""
    if target == "units":
        df = pd.read_parquet(UNITS_PATH)
        df = df[~df["is_boilerplate"].astype(bool)]
        return pd.DataFrame(
            {
                "item_id": df["unit_id"],
                "text": df["text"],
                "firm": df["firm_name"].fillna(""),
                "year": df["year_hint"].fillna(""),
            }
        )
    df = pd.read_parquet(RESPONSES_PATH)
    return pd.DataFrame(
        {
            "item_id": df["doc_id"] + "_resp",
            "text": df["response_text"],
            "firm": df["firm_name"].fillna(""),
            "year": df["year_hint"].fillna(""),
        }
    )


def out_path(target: str, model: str) -> Path:
    return LLM_DIR / f"{target}_{model}.jsonl"


def done_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return {
        json.loads(line)["item_id"] for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    }


def record(item_id: str, text: str, msg, target: str, tax) -> dict:
    """Parse one Message into an output row, applying codebook validation for units."""
    row = {
        "item_id": item_id,
        "model": msg.model,
        "stop_reason": msg.stop_reason,
        "usage": {
            "input": msg.usage.input_tokens,
            "output": msg.usage.output_tokens,
            "cache_read": msg.usage.cache_read_input_tokens or 0,
            "cache_write": msg.usage.cache_creation_input_tokens or 0,
        },
    }
    if msg.stop_reason == "refusal":
        row["error"] = f"refusal: {getattr(msg.stop_details, 'category', None)}"
        return row
    if msg.stop_reason == "max_tokens":
        row["error"] = "max_tokens"
        return row
    body = next((b.text for b in msg.content if b.type == "text"), "")
    try:
        out = json.loads(body)
    except json.JSONDecodeError:
        row["error"] = "invalid_json"
        return row
    if target == "units":
        out, issues = validate_unit(out, tax, text)
        row["issues"] = issues
    row["output"] = out
    return row


def run_sync(items: pd.DataFrame, args, tax, path: Path) -> None:
    client = anthropic.Anthropic()
    with path.open("a", encoding="utf-8") as fh:
        for n, it in enumerate(items.itertuples(index=False), start=1):
            params = request_params(
                args.target,
                tax,
                it.item_id,
                it.text,
                firm=it.firm,
                year=it.year,
                model=args.model,
                effort=args.effort,
            )
            try:
                msg = client.beta.messages.create(**params, betas=[FALLBACK_BETA], fallbacks="default")
            except anthropic.BadRequestError as err:  # not retryable; log and continue
                row = {"item_id": it.item_id, "error": f"400: {err.message}"}
            except (
                anthropic.RateLimitError,
                anthropic.APIConnectionError,
                anthropic.InternalServerError,
            ) as err:
                print(f"Stopping after retries exhausted: {type(err).__name__}. Rerun to resume.")
                break
            else:
                row = record(it.item_id, it.text, msg, args.target, tax)
            fh.write(json.dumps(row) + "\n")
            fh.flush()
            if n % 25 == 0:
                print(f"  {n}/{len(items)} coded")


def batch_submit(items: pd.DataFrame, args, tax) -> None:
    client = anthropic.Anthropic()
    requests = [
        Request(
            custom_id=it.item_id[:64],
            params=MessageCreateParamsNonStreaming(
                **request_params(
                    args.target,
                    tax,
                    it.item_id,
                    it.text,
                    firm=it.firm,
                    year=it.year,
                    model=args.model,
                    effort=args.effort,
                )
            ),
        )
        for it in items.itertuples(index=False)
    ]
    batch = client.messages.batches.create(requests=requests)
    (LLM_DIR / f"batch_{args.target}_{args.model}.id").write_text(batch.id, encoding="utf-8")
    print(f"Submitted batch {batch.id} with {len(requests)} requests; status {batch.processing_status}.")


def batch_collect(items: pd.DataFrame, args, tax, path: Path) -> None:
    client = anthropic.Anthropic()
    batch_id = (LLM_DIR / f"batch_{args.target}_{args.model}.id").read_text(encoding="utf-8").strip()
    batch = client.messages.batches.retrieve(batch_id)
    if batch.processing_status != "ended":
        sys.exit(
            f"Batch {batch_id} is {batch.processing_status}; processing={batch.request_counts.processing}."
        )
    text_by_id = dict(zip(items["item_id"].str[:64], items["text"], strict=True))
    full_id = dict(zip(items["item_id"].str[:64], items["item_id"], strict=True))
    with path.open("a", encoding="utf-8") as fh:
        for res in client.messages.batches.results(batch_id):  # results arrive in any order
            item_id = full_id.get(res.custom_id, res.custom_id)
            if res.result.type == "succeeded":
                row = record(item_id, text_by_id.get(res.custom_id, ""), res.result.message, args.target, tax)
            else:
                row = {"item_id": item_id, "error": res.result.type}
            fh.write(json.dumps(row) + "\n")
    print(f"Collected batch {batch_id} → {path}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--target", choices=["units", "responses"], default="units")
    ap.add_argument("--mode", choices=["sync", "batch-submit", "batch-collect"], default="sync")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--effort", default=DEFAULT_EFFORT, choices=["low", "medium", "high", "xhigh", "max"])
    ap.add_argument("--limit", type=int, default=0, help="Code at most N not-yet-coded items (0 = all)")
    ap.add_argument("--dry-run", action="store_true", help="Print the first request and exit")
    args = ap.parse_args()

    tax = load_taxonomy()
    items = load_items(args.target)
    LLM_DIR.mkdir(parents=True, exist_ok=True)
    path = out_path(args.target, args.model)
    todo = items[~items["item_id"].isin(done_ids(path))]
    if args.limit:
        todo = todo.head(args.limit)
    if args.dry_run:
        it = todo.iloc[0]
        params = request_params(
            args.target,
            tax,
            it.item_id,
            it.text,
            firm=it.firm,
            year=it.year,
            model=args.model,
            effort=args.effort,
        )
        params["system"][0]["text"] = params["system"][0]["text"][:400] + " …[codebook truncated in dry run]"
        print(json.dumps(params, indent=2)[:6000])
        return
    print(f"{len(todo)} of {len(items)} {args.target} to code with {args.model} (effort={args.effort}).")
    if args.mode == "sync":
        run_sync(todo, args, tax, path)
    elif args.mode == "batch-submit":
        batch_submit(todo, args, tax)
    else:
        batch_collect(items, args, tax, path)


if __name__ == "__main__":
    main()
