# QC Criticism Taxonomy — Feasibility Exploration

## Goal
Test whether the PCAOB quality-control criticisms that become public (unremediated Part II portions)
can be classified reliably into theoretically distinct types. If they can, test whether firm responses
differ by type.

## Status
IN PROGRESS (started 2026-09-23). The theory, codebook and pipeline are built, and tests pass on
synthetic fixtures. **No real PCAOB text has been coded yet.** The cloud session that built this could
not reach pcaobus.org or WRDS, so steps 0–2 must run locally.

## Files

| File | Purpose |
|---|---|
| `feasibility_memo.md` | Theory (why types should differ), hypotheses H1–H5, threats, literature, corrections to discussion notes |
| `codebook.md` | Coding manual for human coders; also the LLM coder's system prompt |
| `taxonomy.yaml` | Machine-readable codes, dictionary patterns, section-detection patterns |
| `qclib/` | Library code: extraction, rule coder, LLM request/validation, diagnostics |
| `scripts/00–06` | Pipeline steps (below) |
| `tests/` | Offline tests: unit tests, plus an end-to-end smoke test on a synthetic corpus |
| `output/` | Reports, coding sheets, figures (created by the scripts) |

Plan and go/no-go gates: `quality_reports/plans/2026-09-23_qc_criticism_classification_feasibility.md`.

## Hypotheses to test (pilot)
1. Six families (OBJ, CAP, EXE, MON, INC, PRO) are reliably distinguishable in the text (α ≥ 0.70).
2. Families are not near-duplicates (φ < 0.5), and unsupervised text structure recovers them above chance.
3. Released portions carry firm responses often enough to code response types (≥ 60% of documents).

## Success criteria
Gates G1–G5 in the plan. `scripts/06_feasibility_diagnostics.py` reports PASS/FAIL for each.

## How to run (local machine: network access to pcaobus.org, WRDS credentials)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r explorations/qc_criticism_taxonomy/requirements.txt
pytest explorations/qc_criticism_taxonomy/tests                  # offline; should pass

S=explorations/qc_criticism_taxonomy/scripts
python $S/00_wrds_discover.py        # does WRDS already hold PCAOB inspection / QC data?
python $S/01_fetch_pcaob.py          # list page + PDFs (use --html if Cloudflare blocks; --follow for firm pages)
python $S/02_extract_segment.py      # units + responses + extraction log (gate G1)
python $S/03_classify_rules.py       # dictionary baseline
python $S/04_classify_llm.py --dry-run            # inspect one request
python $S/04_classify_llm.py --mode sync --limit 30   # pilot: 30 units (needs ANTHROPIC_API_KEY)
python $S/05_draw_coding_sample.py   # 30 calibration + 100 test units for two human coders
#   coders fill output/coding_sample.csv → save as output/coding_sample_coded.csv
python $S/06_feasibility_diagnostics.py   # output/feasibility_report.md with gates G1–G5
```

Order of work that avoids wasted effort:
1. Steps 0–3.
2. Read 20 extracted units by eye and adjust the `section` patterns in `taxonomy.yaml` if needed.
3. Calibration round (30 units, both coders), then revise `codebook.md`.
4. Test round (100 units).
5. LLM on all units.
6. Diagnostics.

LLM cost: roughly 1–2k output tokens per unit at `effort=high`. Use `--mode batch-submit` for the
full run, which is 50% cheaper.

## Findings
(none yet — no real data coded)

## Timeline
- 2026-09-23: Theory memo, codebook v0.1, pipeline, and tests built in a cloud session
  (pcaobus.org / WRDS blocked there).
