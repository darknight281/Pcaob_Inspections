"""Step 3 — Rule-based (dictionary) coding of criticism units and firm responses.

    python explorations/qc_criticism_taxonomy/scripts/03_classify_rules.py

Outputs data/cleaned/pcaob/qc_units_rules.parquet and qc_responses_rules.parquet. Codes are stored as
';'-joined strings so the files round-trip through CSV.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from qclib.config import (  # noqa: E402
    RESPONSES_PATH,
    RESPONSES_RULES_PATH,
    UNITS_PATH,
    UNITS_RULES_PATH,
    load_taxonomy,
)
from qclib.rules import classify_response, classify_unit  # noqa: E402


def main() -> None:
    tax = load_taxonomy()
    units = pd.read_parquet(UNITS_PATH)
    coded = pd.DataFrame(
        [classify_unit(t, tax, bool(b)) for t, b in zip(units["text"], units["is_boilerplate"], strict=True)],
        index=units.index,
    )
    coded["codes"] = coded["codes"].str.join(";")
    out = pd.concat([units[["unit_id", "doc_id"]], coded.add_prefix("rule_")], axis=1)
    out.to_parquet(UNITS_RULES_PATH, index=False)
    print(out["rule_primary_family"].value_counts().to_string())

    if RESPONSES_PATH.exists():
        resp = pd.read_parquet(RESPONSES_PATH)
        if not resp.empty:
            rc = pd.DataFrame([classify_response(t, tax) for t in resp["response_text"]], index=resp.index)
            rc["actions"] = rc["actions"].str.join(";")
            pd.concat([resp[["doc_id"]], rc.add_prefix("rule_")], axis=1).to_parquet(
                RESPONSES_RULES_PATH, index=False
            )
            print(rc["stance"].value_counts().to_string())


if __name__ == "__main__":
    main()
