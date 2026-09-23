# Plan — Feasibility of Classifying PCAOB QC (Part II) Criticisms into Theoretically Distinct Types

**Date:** 2026-09-23
**Author:** Oliver (with Claude)
**Status:** DRAFT — infrastructure built and tested on synthetic fixtures; real-data pilot blocked in the cloud session (network), to be run locally
**Workspace:** `explorations/qc_criticism_taxonomy/` (exploration sandbox, 60/100 threshold)

---

## Question

1. Can the quality-control (QC) criticisms that the PCAOB makes public (Part II portions a firm failed to
   remediate within 12 months) be classified reliably into a small set of criticism *types*?
2. Are those types *theoretically* distinct, i.e. do they correspond to different economic mechanisms with
   different remediation technologies, and not just to different regulatory labels?
3. If yes: do *responses* (firm response letters, recurrence, and real-margin responses) vary systematically
   across types? This is the substantive pathway the classification is meant to open.

## Approach

| Step | What | Output |
|---|---|---|
| 0 | WRDS discovery: list any `audit*` tables/columns matching `pcaob|inspect|qc|deficien` | `output/wrds_inventory.csv` |
| 1 | Fetch the PCAOB list "Firms that Failed to Address Quality Control Criticisms Satisfactorily" and the linked report PDFs | `data/raw/pcaob/qc_released/*.pdf`, `qc_reports_index.csv` |
| 2 | Extract text, locate the released QC-criticism section and the firm response, segment into criticism units | `data/cleaned/pcaob/qc_units.parquet`, `qc_responses.parquet` |
| 3 | Rule-based (dictionary) classifier: transparent baseline | `qc_units_rules.parquet` |
| 4 | LLM classifier (Claude, codebook as cached system prompt, JSON schema output) | `qc_units_llm.jsonl` |
| 5 | Draw a stratified double-coding sample for two human coders (Oliver + Cam/Ahmed) | `output/coding_sample.csv` |
| 6 | Feasibility diagnostics: volume, reliability (κ, Krippendorff α), co-occurrence, lexical distinctiveness, unsupervised-structure check against permutation null | `output/feasibility_report.md` |

Theory and codebook: `explorations/qc_criticism_taxonomy/feasibility_memo.md` and `codebook.md`.

## Go / no-go criteria (pre-registered before seeing data)

- **G1 Coverage:** ≥ 80% of downloaded released-Part II documents yield ≥ 1 automatically segmented unit.
- **G2 Volume:** ≥ 300 criticism units; ≥ 30 units (any-label) in at least 4 of the 6 families.
- **G3 Reliability:** human–human Krippendorff α ≥ 0.70 on primary family (n ≥ 100 double-coded units);
  LLM vs adjudicated human κ ≥ 0.70. Sub-code α ≥ 0.60 is acceptable at this stage.
- **G4 Distinctiveness:** no family pair with φ ≥ 0.5; NMI between unsupervised clusters and primary
  family above the 95th percentile of the permutation null.
- **G5 Response data:** ≥ 60% of released documents carry a firm response with ≥ 1 QC/remediation sentence.

Fallback if G3 fails at six families: collapse to the two-way split used in prior work and re-test.
That split is audit-performance vs firm-management criticisms (Buslepp, DeLisle & Victoravich 2018,
public Part II), which corresponds to Aobdia's (2020) performance-related vs organisation-level
(confidential data).

## Blockers (as of 2026-09-23)

- The cloud session's network policy blocks `pcaobus.org`, `assets.pcaobus.org`, `sec.gov`, and WRDS
  (port 9737); WRDS credentials live only on Oliver's laptop. Steps 0–2 must be run locally (or after
  adding the hosts to the environment's allowed domains).
- The shared claude.ai discussion referenced in the request could not be retrieved (client-rendered page
  behind Cloudflare). Any design choices made there are not yet reflected here.

## Verification

- `pytest explorations/qc_criticism_taxonomy/tests` passes (synthetic fixtures; no network).
- After the local run: `feasibility_report.md` reports G1–G5 with pass/fail.
