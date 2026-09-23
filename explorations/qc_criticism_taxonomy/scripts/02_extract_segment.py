"""Step 2 — Extract the released QC section and the firm response; segment into criticism units.

    python explorations/qc_criticism_taxonomy/scripts/02_extract_segment.py

Inputs: data/raw/pcaob/qc_released/qc_reports_index.csv and the PDFs it lists. If
data/raw/pcaob/qc_released/qc_units_manual.csv exists (columns doc_id, text, and optionally
firm_name, year_hint), its rows are appended as hand-segmented units.

Outputs:
  data/cleaned/pcaob/qc_units.parquet       one row per criticism unit
  data/cleaned/pcaob/qc_responses.parquet   one row per document with a response found
  output/extraction_log.csv                 one row per document (coverage gate G1)
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from qclib.config import (  # noqa: E402
    CLEAN_DIR,
    MANUAL_UNITS_PATH,
    OUT_DIR,
    REPORTS_INDEX,
    RESPONSES_PATH,
    ROOT,
    UNITS_PATH,
    is_annual_firm,
    load_taxonomy,
)
from qclib.extract import extract_document  # noqa: E402


def main() -> None:
    tax = load_taxonomy()
    index = pd.read_csv(REPORTS_INDEX, dtype=str).fillna("")
    unit_rows, resp_rows, logs = [], [], []
    for _, rep in index.iterrows():
        pdf = ROOT / rep["local_path"]
        if not pdf.exists():
            logs.append({"doc_id": rep["report_id"], "error": "pdf_missing"})
            continue
        res = extract_document(pdf, tax, rep["report_id"])
        meta = {"firm_name": rep["firm_name"], "year_hint": rep["year_hint"], "url": rep["url"]}
        logs.append({**res.log, **meta})
        unit_rows.extend({**u, **meta} for u in res.units)
        if res.response_text:
            resp_rows.append({"doc_id": rep["report_id"], "response_text": res.response_text, **meta})

    units = pd.DataFrame(unit_rows)
    if MANUAL_UNITS_PATH.exists():
        manual = pd.read_csv(MANUAL_UNITS_PATH, dtype=str).fillna("")
        manual["unit_id"] = (
            manual["doc_id"] + "_m" + (manual.groupby("doc_id").cumcount() + 1).astype(str).str.zfill(2)
        )
        manual["is_boilerplate"] = False
        manual["heading"] = None
        units = pd.concat([units, manual], ignore_index=True)
        print(f"Appended {len(manual)} manual units.")
    if units.empty:
        sys.exit("No units extracted — check output/extraction_log.csv and taxonomy.yaml section patterns.")

    units["is_annual_firm"] = units["firm_name"].map(lambda f: is_annual_firm(f, tax))
    units["n_chars"] = units["text"].str.len()
    CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    units.to_parquet(UNITS_PATH, index=False)
    pd.DataFrame(resp_rows).to_parquet(RESPONSES_PATH, index=False)
    log = pd.DataFrame(logs)
    log.to_csv(OUT_DIR / "extraction_log.csv", index=False)

    n_docs = len(log)
    ok = int((log.get("n_substantive_units", pd.Series(dtype=float)).fillna(0) > 0).sum())
    print(
        f"Documents: {n_docs}; with ≥1 substantive unit: {ok} ({ok / max(n_docs, 1):.0%}) — gate G1 needs ≥ 80%."
    )
    print(
        f"Units: {len(units)} ({int((~units['is_boilerplate'].astype(bool)).sum())} substantive); "
        f"responses found: {len(resp_rows)}."
    )


if __name__ == "__main__":
    main()
