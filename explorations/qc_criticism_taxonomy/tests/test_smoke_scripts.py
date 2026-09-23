"""End-to-end smoke test: run the numbered scripts on a generated SYNTHETIC corpus in a temp QC_WORKDIR.

Checks that scripts 02, 03, 04 (--dry-run), 05, and 06 run and produce their outputs. The corpus is
built from template sentences; it says nothing about real PCAOB text.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pymupdf

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
SEED = 20260923

TEMPLATES = {
    "OBJ": [
        "Firm personnel did not comply with the firm's policies requiring the reporting of financial holdings.",
        "The firm's system of quality control does not provide reasonable assurance that non-audit services are "
        "pre-approved by the audit committee.",
    ],
    "CAP": [
        "The firm's methodology does not provide sufficient guidance on testing accounting estimates.",
        "The firm has not provided training, and assigned personnel lacked the necessary expertise.",
    ],
    "EXE": [
        "The inspection results indicate that the firm's system of quality control does not provide reasonable "
        "assurance that engagement teams test controls with a review element at a sufficient level of precision.",
        "The inspection results indicate that engagement teams did not perform sufficient substantive procedures.",
    ],
    "MON": [
        "The firm's system of quality control does not provide reasonable assurance that engagement quality "
        "reviews are performed with due care.",
        "The firm's internal inspection program did not identify deficiencies previously identified by the Board.",
    ],
    "INC": [
        "Partner evaluations and compensation give little weight to audit quality.",
        "Firm leadership messaging emphasizes revenue growth targets over audit quality; tone at the top is weak.",
    ],
    "PRO": [
        "The firm filed Form AP late for several issuer audits.",
        "The firm did not make required communications with the audit committee.",
    ],
}


def make_pdf(path: Path, units: list[str]) -> None:
    pars = [
        "PART II CRITICISMS OF, AND POTENTIAL DEFECTS IN, THE FIRM'S SYSTEM OF QUALITY CONTROL",
        "Section 104(g)(2) restricts the Board's public disclosure; portions are made public after 12 months.",
    ]
    for k, u in enumerate(units):
        pars += [f"{'ABCDEF'[k]}. Criticism {k + 1}", u]
    pars += [
        "PART III RESPONSE OF THE FIRM TO DRAFT INSPECTION REPORT",
        "We agree and are committed to quality. In 2020 we implemented new training for 40 partners.",
    ]
    doc = pymupdf.open()
    for par in pars:
        doc.new_page().insert_textbox(pymupdf.Rect(72, 72, 540, 770), par, fontsize=10)
    doc.save(path)


def run(script: str, env: dict, *args: str) -> str:
    out = subprocess.run(
        [sys.executable, str(SCRIPTS / script), *args], env=env, capture_output=True, text=True
    )
    assert out.returncode == 0, f"{script} failed:\n{out.stdout}\n{out.stderr}"
    return out.stdout


def test_scripts_end_to_end(tmp_path):
    rng = np.random.default_rng(SEED)
    raw = tmp_path / "raw"
    raw.mkdir()
    fams = list(TEMPLATES)
    rows = []
    for d in range(60):
        picks = rng.choice(fams, size=int(rng.integers(2, 4)), replace=False)
        units = [str(rng.choice(TEMPLATES[f])) for f in picks]
        rid = f"syn{d:03d}"
        make_pdf(raw / f"{rid}.pdf", units)
        rows.append(
            {
                "report_id": rid,
                "firm_name": "Big Firm LLP" if d % 5 == 0 else "Small CPA PC",
                "year_hint": str(2010 + d % 12),
                "url": f"synthetic://{rid}",
                "local_path": str(raw / f"{rid}.pdf"),
            }
        )
    pd.DataFrame(rows).to_csv(raw / "qc_reports_index.csv", index=False)

    env = {**os.environ, "QC_WORKDIR": str(tmp_path)}
    assert "gate G1" in run("02_extract_segment.py", env)
    run("03_classify_rules.py", env)
    dry = run("04_classify_llm.py", env, "--dry-run")
    assert '"json_schema"' in dry and '"cache_control"' in dry
    run("05_draw_coding_sample.py", env, "--n-calibration", "10", "--n-test", "40")

    # Fake a coded sheet (coder B disagrees on 10% of units) and an LLM JSONL to exercise those paths.
    sheet = pd.read_csv(tmp_path / "output" / "coding_sample.csv", dtype=str).fillna("")
    rules = pd.read_parquet(tmp_path / "cleaned" / "qc_units_rules.parquet").set_index("unit_id")
    prim = sheet["unit_id"].map(rules["rule_primary_code"])
    sheet["coder_A_primary_code"] = prim
    sheet["coder_B_primary_code"] = np.where(rng.random(len(sheet)) < 0.1, "OBJ_INDEP", prim)
    sheet["coder_A_codes"] = sheet["coder_B_codes"] = sheet["adjudicated_codes"] = prim
    sheet["adjudicated_primary_code"] = prim
    sheet.to_csv(tmp_path / "output" / "coding_sample_coded.csv", index=False)
    llm_dir = tmp_path / "cleaned" / "llm"
    llm_dir.mkdir(exist_ok=True)
    with (llm_dir / "units_synthetic.jsonl").open("w") as fh:
        for uid, r in rules.iterrows():
            out = {
                "codes": r["rule_codes"].split(";"),
                "primary_code": r["rule_primary_code"],
                "primary_family": r["rule_primary_family"],
                "form": r["rule_form"],
                "root_cause_stated": bool(r["rule_root_cause_stated"]),
            }
            fh.write(json.dumps({"item_id": uid, "output": out}) + "\n")

    run("06_feasibility_diagnostics.py", env)
    report = (tmp_path / "output" / "feasibility_report.md").read_text()
    for section in (
        "## Gate summary",
        "## G1 Coverage",
        "## G2 Volume",
        "## G3 Reliability",
        "## G4 Distinctiveness",
        "## G5 Response data",
    ):
        assert section in report
    assert (tmp_path / "output" / "figures" / "family_phi.pdf").exists()
    assert "Krippendorff" in report
