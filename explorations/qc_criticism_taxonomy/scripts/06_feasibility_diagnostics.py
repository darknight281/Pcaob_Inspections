"""Step 6 — Feasibility report: gates G1–G5 from the plan, with supporting tables and one figure.

    python explorations/qc_criticism_taxonomy/scripts/06_feasibility_diagnostics.py [--llm PATH]

Uses whatever coders are available, in order of authority: adjudicated human > LLM > rules.
Outputs output/feasibility_report.md, output/*.csv, output/figures/family_phi.pdf.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from qclib.config import (  # noqa: E402
    FIG_DIR,
    HUMAN_CODES_PATH,
    LLM_DIR,
    OUT_DIR,
    RESPONSES_PATH,
    RESPONSES_RULES_PATH,
    UNITS_PATH,
    UNITS_RULES_PATH,
    load_taxonomy,
)
from qclib.diagnostics import (  # noqa: E402
    cohen_kappa,
    family_indicators,
    krippendorff_alpha_nominal,
    lift_matrix,
    multilabel_kappas,
    phi_matrix,
    unsupervised_alignment,
    weighted_log_odds,
)

SEED = 20260923
N_PERM = 1000
QC_SENTENCE = re.compile(r"quality control|quality management|system of quality|remediat", re.IGNORECASE)
GATES = {
    "G1": 0.80,
    "G2_units": 300,
    "G2_per_family": 30,
    "G2_n_families": 4,
    "G3": 0.70,
    "G4_phi": 0.5,
    "G5": 0.60,
}


def split_codes(s: object) -> list[str]:
    if isinstance(s, list):
        return s
    return [c for c in str(s or "").split(";") if c]


def load_llm(path: Path | None) -> pd.DataFrame:
    if path is None:
        cands = (
            sorted(LLM_DIR.glob("units_*.jsonl"), key=lambda p: p.stat().st_mtime) if LLM_DIR.exists() else []
        )
        path = cands[-1] if cands else None
    if path is None or not path.exists():
        return pd.DataFrame()
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    rows = [r for r in rows if "output" in r]
    return pd.DataFrame(
        {
            "unit_id": [r["item_id"] for r in rows],
            "llm_codes": [r["output"]["codes"] for r in rows],
            "llm_primary_code": [r["output"]["primary_code"] for r in rows],
            "llm_primary_family": [r["output"]["primary_family"] for r in rows],
            "llm_form": [r["output"]["form"] for r in rows],
            "llm_root_cause_stated": [r["output"]["root_cause_stated"] for r in rows],
        }
    ).drop_duplicates("unit_id", keep="last")


def fmt_gate(ok: bool | None) -> str:
    return "n/a" if ok is None else ("PASS" if ok else "FAIL")


def md_table(df: pd.DataFrame, floatfmt: str = ".2f") -> str:
    return df.to_markdown(floatfmt=floatfmt) if not df.empty else "_(empty)_"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--llm", type=Path, default=None, help="LLM units JSONL (default: most recent)")
    args = ap.parse_args()
    rng = np.random.default_rng(SEED)
    tax = load_taxonomy()
    fams = list(tax.substantive_families)

    units = pd.read_parquet(UNITS_PATH).merge(pd.read_parquet(UNITS_RULES_PATH), on=["unit_id", "doc_id"])
    units = units[~units["is_boilerplate"].astype(bool)].copy()
    units["rule_codes"] = units["rule_codes"].map(split_codes)
    llm = load_llm(args.llm)
    if not llm.empty:
        units = units.merge(llm, on="unit_id", how="left")
    human = (
        pd.read_csv(HUMAN_CODES_PATH, dtype=str).fillna("") if HUMAN_CODES_PATH.exists() else pd.DataFrame()
    )

    # Best available labels for distributional diagnostics.
    labels_from = "rules"
    units["best_codes"], units["best_family"] = units["rule_codes"], units["rule_primary_family"]
    if "llm_primary_family" in units and units["llm_primary_family"].notna().any():
        has = units["llm_primary_family"].notna()
        units.loc[has, "best_codes"] = units.loc[has, "llm_codes"]
        units.loc[has, "best_family"] = units.loc[has, "llm_primary_family"]
        labels_from = "LLM (rules where LLM missing)"
    if not human.empty and (human["adjudicated_primary_code"] != "").any():
        adj = human[human["adjudicated_primary_code"] != ""].set_index("unit_id")
        m = units["unit_id"].isin(adj.index)
        units.loc[m, "best_codes"] = units.loc[m, "unit_id"].map(
            lambda u: split_codes(adj.at[u, "adjudicated_codes"])
        )
        units.loc[m, "best_family"] = units.loc[m, "unit_id"].map(
            lambda u: tax.code_family.get(adj.at[u, "adjudicated_primary_code"], "OTHER")
        )
        labels_from += " + adjudicated human where available"
    sub = units[units["best_family"] != "OTHER"].copy()

    report: list[str] = [
        "# Feasibility Report — PCAOB QC Criticism Classification",
        "",
        f"Labels for distributional diagnostics: **{labels_from}**.",
        "",
    ]
    gates: dict[str, bool | None] = {}

    # G1 coverage
    log_path = OUT_DIR / "extraction_log.csv"
    if log_path.exists():
        log = pd.read_csv(log_path)
        cov = float((log.get("n_substantive_units", pd.Series(0, index=log.index)).fillna(0) > 0).mean())
        gates["G1"] = cov >= GATES["G1"]
        report += ["## G1 Coverage", f"{len(log)} documents; {cov:.0%} yield ≥ 1 substantive unit.", ""]

    # G2 volume
    ind_any = family_indicators(sub["best_codes"], tax.code_family, fams)
    counts = pd.DataFrame(
        {
            "primary": sub["best_family"].value_counts().reindex(fams, fill_value=0),
            "any_label": ind_any.sum().reindex(fams, fill_value=0),
        }
    )
    counts["share_primary"] = counts["primary"] / max(len(sub), 1)
    counts.to_csv(OUT_DIR / "family_counts.csv")
    n_ok_fams = int((counts["any_label"] >= GATES["G2_per_family"]).sum())
    gates["G2"] = len(sub) >= GATES["G2_units"] and n_ok_fams >= GATES["G2_n_families"]
    by_size = pd.crosstab(sub["best_family"], np.where(sub["is_annual_firm"], "annual", "triennial"))
    report += [
        "## G2 Volume",
        f"{len(sub)} substantive units; {n_ok_fams} families with ≥ {GATES['G2_per_family']} units (any-label).",
        "",
        md_table(counts),
        "",
        "By inspection frequency (primary family):",
        "",
        md_table(by_size, ".0f"),
        "",
    ]

    # G3 reliability
    report += ["## G3 Reliability"]
    if not human.empty and (human["coder_B_primary_code"] != "").any():
        h = human[(human["coder_A_primary_code"] != "") & (human["coder_B_primary_code"] != "")]
        h = h[h["sample_role"] == "test"] if (h["sample_role"] == "test").any() else h
        fa = h["coder_A_primary_code"].map(tax.code_family)
        fb = h["coder_B_primary_code"].map(tax.code_family)
        alpha_fam = krippendorff_alpha_nominal(pd.DataFrame({"A": fa, "B": fb}))
        alpha_code = krippendorff_alpha_nominal(h[["coder_A_primary_code", "coder_B_primary_code"]])
        gates["G3"] = alpha_fam >= GATES["G3"]
        rel = [
            {
                "comparison": "human A vs B",
                "level": "primary family",
                "n": len(h),
                "stat": "Krippendorff α",
                "value": alpha_fam,
            },
            {
                "comparison": "human A vs B",
                "level": "primary code",
                "n": len(h),
                "stat": "Krippendorff α",
                "value": alpha_code,
            },
        ]
        ref = h.set_index("unit_id")["adjudicated_primary_code"].replace("", np.nan).dropna()
        for who, col in (("LLM", "llm_primary_code"), ("rules", "rule_primary_code")):
            if col in units:
                pred = units.set_index("unit_id")[col].reindex(ref.index)
                rel.append(
                    {
                        "comparison": f"{who} vs adjudicated",
                        "level": "primary family",
                        "n": int(pred.notna().sum()),
                        "stat": "Cohen κ",
                        "value": cohen_kappa(ref.map(tax.code_family), pred.map(tax.code_family)),
                    }
                )
        report += ["", md_table(pd.DataFrame(rel)), ""]
        mk = multilabel_kappas(
            h["coder_A_codes"].map(split_codes), h["coder_B_codes"].map(split_codes), list(tax.codes)
        )
        mk.to_csv(OUT_DIR / "per_code_kappa.csv", index=False)
        report += ["Per-code κ (human A vs B) written to `output/per_code_kappa.csv`.", ""]
    else:
        gates["G3"] = None
        if "llm_primary_family" in units:
            both = units.dropna(subset=["llm_primary_family"])
            k = cohen_kappa(both["rule_primary_family"], both["llm_primary_family"])
            report += [
                "",
                f"No human codes yet. Rules vs LLM (primary family, n = {len(both)}): Cohen κ = {k:.2f} "
                "(indicative only; neither is a benchmark).",
                "",
            ]
        else:
            report += ["", "No human or LLM codes yet — run steps 4–5.", ""]

    # G4 distinctiveness
    phi = phi_matrix(ind_any)
    phi.to_csv(OUT_DIR / "family_phi.csv")
    lift_matrix(ind_any).to_csv(OUT_DIR / "family_lift.csv")
    off = phi.where(~np.eye(len(phi), dtype=bool)).abs()
    max_phi = float(np.nanmax(off.to_numpy())) if off.notna().any().any() else float("nan")
    ua = unsupervised_alignment(sub["text"], sub["best_family"], rng, n_perm=N_PERM, seed=SEED)
    gates["G4"] = (
        (bool(max_phi < GATES["G4_phi"]) and bool(ua["nmi"] > ua.get("null_p95", np.inf)))
        if not np.isnan(ua["nmi"])
        else None
    )
    lo = weighted_log_odds(sub["text"], sub["best_family"])
    lo.to_csv(OUT_DIR / "log_odds_terms.csv", index=False)
    top_terms = (
        lo.groupby("group")["term"].apply(lambda s: ", ".join(s.head(8))).to_frame("distinctive terms")
    )
    report += [
        "## G4 Distinctiveness",
        f"Max |φ| between families: {max_phi:.2f}.",
        f"Unsupervised NMF (k = {ua['k']}): NMI = {ua['nmi']:.2f}, ARI = {ua['ari']:.2f}, "
        f"permutation 95th pct = {ua.get('null_p95', float('nan')):.2f}, p = {ua['p_value']:.3f}.",
        "",
        "φ matrix (any-label):",
        "",
        md_table(phi),
        "",
        md_table(top_terms),
        "",
    ]
    fig, ax = plt.subplots(figsize=(5.2, 4.4))
    im = ax.imshow(phi.to_numpy(), vmin=-1, vmax=1, cmap="RdBu_r")
    ax.set_xticks(range(len(fams)), fams)
    ax.set_yticks(range(len(fams)), fams)
    for (i, j), v in np.ndenumerate(phi.to_numpy()):
        ax.text(j, i, "" if np.isnan(v) else f"{v:.2f}", ha="center", va="center", fontsize=8, family="serif")
    fig.colorbar(im, ax=ax, label="φ")
    fig.tight_layout()
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG_DIR / "family_phi.pdf")
    plt.close(fig)

    # Form and root cause (text-framing risk)
    form_col = "llm_form" if "llm_form" in sub and sub["llm_form"].notna().any() else "rule_form"
    rc_col = (
        "llm_root_cause_stated"
        if "llm_root_cause_stated" in sub and sub["llm_root_cause_stated"].notna().any()
        else "rule_root_cause_stated"
    )
    report += [
        "## Form and stated root cause",
        f"Source: `{form_col}`, `{rc_col}`.",
        "",
        md_table(pd.crosstab(sub["best_family"], sub[form_col], normalize="index")),
        "",
        f"Share of units with an explicitly stated root cause: {sub[rc_col].astype(bool).mean():.0%} "
        "(low values mean MON/INC mechanisms are rarely named in the text).",
        "",
    ]

    # G5 response data
    if RESPONSES_PATH.exists() and log_path.exists():
        resp = pd.read_parquet(RESPONSES_PATH)
        n_docs = int(log["section_found"].fillna(False).astype(bool).sum())
        n_qc = (
            int(resp["response_text"].map(lambda t: bool(QC_SENTENCE.search(t))).sum())
            if not resp.empty
            else 0
        )
        share = n_qc / max(n_docs, 1)
        gates["G5"] = share >= GATES["G5"]
        report += [
            "## G5 Response data",
            f"{len(resp)} responses found; {n_qc} mention QC/remediation "
            f"({share:.0%} of {n_docs} documents with a QC section).",
            "",
        ]
        if RESPONSES_RULES_PATH.exists():
            rr = pd.read_parquet(RESPONSES_RULES_PATH)
            report += [
                "Rule-based stance distribution:",
                "",
                md_table(rr["rule_stance"].value_counts().to_frame("n"), ".0f"),
                "",
            ]

    summary = pd.DataFrame({"gate": list(gates), "result": [fmt_gate(v) for v in gates.values()]})
    report[4:4] = ["## Gate summary", "", md_table(summary), ""]
    (OUT_DIR / "feasibility_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print("\n".join(report[:12]))
    print(f"Full report: {OUT_DIR / 'feasibility_report.md'}")


if __name__ == "__main__":
    main()
