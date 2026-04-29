# Project Memory

Corrections and learned facts that persist across sessions.
When a mistake is corrected, append a `[LEARN:category]` entry below.

---

## Project Context

[CONTEXT] Project: PCAOB Inspections — Audit Quality, Labour, and Information Spillovers. Author: Oliver (Monash University). Prospective collaborators: Cam and Ahmed (audit/governance angle); Qinfang and Qiuhong (existing SEC EDGAR collaboration that feeds into Idea C).

[CONTEXT] Five candidate papers (A workforce-strategy spillovers; B cross-office spillovers; C EDGAR information spillovers; D audit-committee networks; E LLM textual mining → restatements). Suggested sequencing: C (first, leverages existing EDGAR infra) → E (measurement contribution) → A or B (the labour-market paper) → D (collaborative). See `master_supporting_docs/PCAOB_Inspection_Research_Discussion_Notes_v1.md`.

[CONTEXT] Conceptual template: Roh (2026, *TAR*) "When Large Employers Come to Town" — labour-market entry as disclosure shock. Apply to a labour-intensive professional-services industry where labour *is* the production technology.

[CONTEXT] Analysis stack: Python 3.11+, pandas (small data), polars + duckdb (large data — EDGAR logs ~2 TB, Form AP × Audit Analytics joins). Final panels saved as parquet under `data/cleaned/`.

[CONTEXT] No proprietary PCAOB data access. Pipeline rests on public + WRDS subscription sources. See `master_supporting_docs/data_sources.md` for status; LinkedIn / Revelio Labs access is the binding constraint for Ideas A and B.

[CONTEXT] Form AP became mandatory 31 January 2017 — gives ~8–9 years of partner-level data. Power for staggered DiD in labour-market designs is an open question (research-notes §8 Q7).

[CONTEXT] Current focus: Idea C scoping. Plan: `quality_reports/plans/2026-04-29_idea_c_scoping.md`.

---

## Workflow Patterns

<!-- Append new [LEARN:workflow] entries below. Most recent at bottom. -->

[LEARN:workflow] Plans, specs, and session logs live on disk under `quality_reports/`, not just in conversation — they must survive context compression and session boundaries.

[LEARN:workflow] For non-trivial tasks (>1 hour or >3 files), use spec-then-plan: clarify requirements → write `quality_reports/specs/YYYY-MM-DD_description.md` with MUST/SHOULD/MAY → get approval → draft plan in `quality_reports/plans/`.

---

## Data and Methodology

<!-- Append new [LEARN:data] and [LEARN:method] entries as they accumulate. -->

---

## Writing and Style

<!-- Append new [LEARN:writing] entries as the writer/storyteller agents learn the user's voice. -->
