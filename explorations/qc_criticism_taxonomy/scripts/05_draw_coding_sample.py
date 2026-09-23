"""Step 5 — Draw a stratified sample for human double-coding (codebook Part C).

    python explorations/qc_criticism_taxonomy/scripts/05_draw_coding_sample.py [--n-calibration 30] [--n-test 100]

Strata: annually vs triennially inspected firm × rule-based primary family, with a floor per stratum
so rare families appear. Rule labels are NOT written to the sheet (to avoid anchoring coders).
Coders fill the coder_A_* / coder_B_* columns independently, then the adjudicated_* columns, and
save the sheet as output/coding_sample_coded.csv.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from qclib.config import OUT_DIR, UNITS_PATH, UNITS_RULES_PATH  # noqa: E402

SEED = 20260923
MIN_PER_STRATUM = 3
CODER_FIELDS = (
    "codes",
    "primary_code",
    "form",
    "root_cause_stated",
    "root_cause_family",
    "confidence",
    "notes",
)


def allocate(sizes: pd.Series, n: int) -> pd.Series:
    """Proportional allocation with a floor, never exceeding stratum size."""
    alloc = np.minimum(sizes, MIN_PER_STRATUM)
    remaining = max(n - int(alloc.sum()), 0)
    spare = sizes - alloc
    if remaining and spare.sum():
        extra = np.floor(spare / spare.sum() * remaining).astype(int)
        alloc = alloc + np.minimum(extra, spare)
    return alloc.astype(int)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--n-calibration", type=int, default=30)
    ap.add_argument("--n-test", type=int, default=100)
    args = ap.parse_args()
    rng = np.random.default_rng(SEED)

    units = pd.read_parquet(UNITS_PATH).merge(pd.read_parquet(UNITS_RULES_PATH), on=["unit_id", "doc_id"])
    units = units[units["rule_primary_family"] != "OTHER"].copy()
    units["stratum"] = (
        np.where(units["is_annual_firm"], "annual", "triennial") + "|" + units["rule_primary_family"]
    )

    n_total = min(args.n_calibration + args.n_test, len(units))
    alloc = allocate(units["stratum"].value_counts(), n_total)
    picks = [
        grp.sample(n=int(alloc[s]), random_state=int(rng.integers(0, 2**31 - 1)))
        for s, grp in units.groupby("stratum")
        if alloc.get(s, 0) > 0
    ]
    sample = pd.concat(picks).sample(frac=1.0, random_state=int(rng.integers(0, 2**31 - 1)))
    sample["sample_role"] = ["calibration"] * min(args.n_calibration, len(sample)) + ["test"] * max(
        len(sample) - args.n_calibration, 0
    )

    sheet = sample[["sample_role", "unit_id", "doc_id", "firm_name", "year_hint", "text"]].reset_index(
        drop=True
    )
    for who in ("coder_A", "coder_B", "adjudicated"):
        for f in CODER_FIELDS:
            sheet[f"{who}_{f}"] = ""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    sheet.to_csv(OUT_DIR / "coding_sample.csv", index=False)
    print(f"Sample of {len(sheet)} units written to {OUT_DIR / 'coding_sample.csv'}")
    print(sample["stratum"].value_counts().to_string())


if __name__ == "__main__":
    main()
