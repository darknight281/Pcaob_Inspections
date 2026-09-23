"""Step 0 — Inventory WRDS for any PCAOB-inspection / QC tables before building from PDFs.

Run locally (WRDS credentials live in ~/.pgpass and shell env vars; never in the repo):

    python explorations/qc_criticism_taxonomy/scripts/00_wrds_discover.py

Writes output/wrds_inventory.csv: schema, table, column, data_type for every column whose schema is
an Audit Analytics library or whose table/column name mentions pcaob / inspect / deficien / qc /
part ii. If a usable table exists, record it in master_supporting_docs/wrds_audit_analytics_schema.md.
Requires the `wrds` package (pip install wrds).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import wrds

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from qclib.config import OUT_DIR  # noqa: E402

SQL = r"""
SELECT table_schema, table_name, column_name, data_type
FROM information_schema.columns
WHERE table_schema ILIKE 'audit%%'
   OR table_name ~* '(pcaob|inspect|deficien|qc_|part_?ii)'
   OR column_name ~* '(pcaob|inspect|deficien|qc_crit|part_?ii)'
ORDER BY table_schema, table_name, ordinal_position
"""
MATCH = r"(?i)pcaob|inspect|deficien|qc_|part_?ii"


def main() -> None:
    username = os.environ.get("WRDS_USERNAME") or os.environ.get("WRDS_USER") or os.environ.get("PGUSER")
    db = wrds.Connection(wrds_username=username)
    try:
        inv = db.raw_sql(SQL)
    finally:
        db.close()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    inv.to_csv(OUT_DIR / "wrds_inventory.csv", index=False)
    hits = inv[
        inv["table_name"].str.contains(MATCH, regex=True) | inv["column_name"].str.contains(MATCH, regex=True)
    ]
    print(
        f"{len(inv):,} columns inventoried; {hits[['table_schema', 'table_name']].drop_duplicates().shape[0]} "
        "candidate tables mention PCAOB/inspection terms:"
    )
    print(hits.groupby(["table_schema", "table_name"]).size().to_string())


if __name__ == "__main__":
    main()
