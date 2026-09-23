"""Prompt, JSON schema, and output validation for the Claude coder.

The codebook is sent verbatim as a cached system prompt, so every request shares the same prefix
and only the unit text varies. Output is constrained with `output_config.format` (JSON schema);
validation below enforces the codebook rules the schema cannot express.
"""

from __future__ import annotations

from qclib.config import CODEBOOK_PATH, FORMS, Taxonomy

DEFAULT_MODEL = "claude-opus-5"
DEFAULT_EFFORT = "high"
MAX_TOKENS = 16_000
FALLBACK_BETA = "server-side-fallback-2026-07-01"

UNIT_INSTRUCTIONS = """You are a trained content-analysis coder for an accounting research project.
Code the PCAOB quality-control criticism unit supplied by the user, following Part A of the
codebook below exactly. Code only what the text states; do not infer mechanisms it does not name
(rule P5). Copy `evidence_quote` verbatim from the unit (at most 40 words). Return JSON only.
"""

RESPONSE_INSTRUCTIONS = """You are a trained content-analysis coder for an accounting research project.
Code the audit firm's response text supplied by the user, following Part B of the codebook below
exactly. Code only what the text states. Copy `evidence_quote` verbatim (at most 40 words).
Return JSON only.
"""

RESPONSE_STANCES = ("ACCEPT", "ACCEPT_WITH_CONTEXT", "CONTEST", "NONE")
RESPONSE_ACTIONS = (
    "ACT_POLICY",
    "ACT_TRAINING",
    "ACT_STAFFING",
    "ACT_METHOD_TOOLS",
    "ACT_MONITORING",
    "ACT_LEADERSHIP_ACCOUNTABILITY",
    "ACT_INDEPENDENCE_SYSTEMS",
    "ACT_CLIENT_PORTFOLIO",
    "ACT_ENGAGEMENT_REWORK",
    "ACT_NONE_SPECIFIC",
)
CONFIDENCE = ("low", "medium", "high")


def system_prompt(target: str) -> str:
    """Instructions + full codebook. Must stay byte-stable across a run for caching."""
    head = UNIT_INSTRUCTIONS if target == "units" else RESPONSE_INSTRUCTIONS
    return head + "\n<codebook>\n" + CODEBOOK_PATH.read_text(encoding="utf-8") + "\n</codebook>\n"


def unit_schema(tax: Taxonomy) -> dict:
    """JSON schema for codebook Part A."""
    codes = list(tax.codes)
    fams = [f for f in tax.families if f != "OTHER"] + ["NONE"]
    return {
        "type": "object",
        "properties": {
            "codes": {"type": "array", "items": {"type": "string", "enum": codes}},
            "primary_code": {"type": "string", "enum": codes},
            "form": {"type": "string", "enum": list(FORMS)},
            "root_cause_stated": {"type": "boolean"},
            "root_cause_family": {"type": "string", "enum": fams},
            "evidence_quote": {"type": "string"},
            "confidence": {"type": "string", "enum": list(CONFIDENCE)},
            "notes": {"type": "string"},
        },
        "required": [
            "codes",
            "primary_code",
            "form",
            "root_cause_stated",
            "root_cause_family",
            "evidence_quote",
            "confidence",
            "notes",
        ],
        "additionalProperties": False,
    }


def response_schema() -> dict:
    """JSON schema for codebook Part B."""
    return {
        "type": "object",
        "properties": {
            "stance": {"type": "string", "enum": list(RESPONSE_STANCES)},
            "actions": {"type": "array", "items": {"type": "string", "enum": list(RESPONSE_ACTIONS)}},
            "specificity": {"type": "string", "enum": ["SPECIFIC", "GENERIC"]},
            "mentions_root_cause": {"type": "boolean"},
            "evidence_quote": {"type": "string"},
            "confidence": {"type": "string", "enum": list(CONFIDENCE)},
            "notes": {"type": "string"},
        },
        "required": [
            "stance",
            "actions",
            "specificity",
            "mentions_root_cause",
            "evidence_quote",
            "confidence",
            "notes",
        ],
        "additionalProperties": False,
    }


def user_message(item_id: str, text: str, firm: str = "", year: str = "") -> str:
    """Per-item user turn; the only request content that varies."""
    meta = f"id: {item_id}\nfirm: {firm or 'unknown'}\nreport year: {year or 'unknown'}"
    return f"{meta}\n<text>\n{text}\n</text>"


def request_params(
    target: str,
    tax: Taxonomy,
    item_id: str,
    text: str,
    *,
    firm: str = "",
    year: str = "",
    model: str = DEFAULT_MODEL,
    effort: str = DEFAULT_EFFORT,
) -> dict:
    """Keyword arguments for messages.create (also valid as batch `params`)."""
    schema = unit_schema(tax) if target == "units" else response_schema()
    return {
        "model": model,
        "max_tokens": MAX_TOKENS,
        "system": [{"type": "text", "text": system_prompt(target), "cache_control": {"type": "ephemeral"}}],
        "messages": [{"role": "user", "content": user_message(item_id, text, firm, year)}],
        "thinking": {"type": "adaptive"},
        "output_config": {"effort": effort, "format": {"type": "json_schema", "schema": schema}},
    }


def validate_unit(out: dict, tax: Taxonomy, unit_text: str) -> tuple[dict, list[str]]:
    """Enforce codebook rules the schema cannot: primary ∈ codes, OTHER exclusivity, quote fidelity."""
    issues: list[str] = []
    codes = [c for c in dict.fromkeys(out.get("codes", [])) if c in tax.code_family]
    primary = out.get("primary_code", "OTHER")
    if primary not in codes:
        issues.append("primary_not_in_codes")
        codes.insert(0, primary)
    if "OTHER" in codes and len(codes) > 1:
        issues.append("other_with_substantive_codes")
        codes = [c for c in codes if c != "OTHER"]
        primary = primary if primary != "OTHER" else codes[0]
    if not out.get("root_cause_stated") and out.get("root_cause_family", "NONE") != "NONE":
        issues.append("root_cause_family_without_statement")
        out["root_cause_family"] = "NONE"
    quote = " ".join(out.get("evidence_quote", "").split())
    if quote and quote.lower() not in " ".join(unit_text.split()).lower():
        issues.append("quote_not_verbatim")
    clean = dict(out, codes=codes, primary_code=primary, primary_family=tax.code_family[primary])
    return clean, issues
