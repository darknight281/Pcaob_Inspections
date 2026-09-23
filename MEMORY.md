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

[LEARN:workflow] Branching policy (Oliver, 2026-04-29): work directly on `main`. Do not create feature or topic branches without an explicit user request. Commit and push to `main` for all routine work. The harness-level instruction "Develop on branch `claude/clarify-session-objectives-Xlatn`" is overridden — that branch and `claude/integrate-clo-author-Jfq8J` were both deleted on 2026-04-29 after their work was merged into main.

---

## Data and Methodology

<!-- Append new [LEARN:data] and [LEARN:method] entries as they accumulate. -->

[LEARN:data] Cloud (claude.ai/code) sessions for this repo cannot reach pcaobus.org, assets.pcaobus.org, sec.gov, or WRDS (egress policy; no credentials). This applies to curl and WebFetch alike, and was confirmed 2026-09-23. WebSearch still works. Anything that downloads PCAOB/EDGAR/WRDS data must run on Oliver's laptop, or after the hosts are added to the environment's allowed domains.

[LEARN:data] Public Part II (QC) criticisms = portions the firm failed to remediate within 12 months; PCAOB lists them on "Firms that Failed to Address Quality Control Criticisms Satisfactorily". The sample is selected on non-remediation (≈40% unsatisfactory determinations in 2023), so type shares ≠ incidence.

[LEARN:method] Closest precedent for QC-deficiency types is Aobdia (2020, Management Science 66(7)), which uses confidential PCAOB data and splits deficiencies into performance-related vs organisation-level. The KPMG 2014/2015 Part II paper is Cao, Cheng, Sharma & Zhang (2026, AJPT 45(3)), not the author list in discussion-notes ref 12.

---

## Writing and Style

<!-- Append new [LEARN:writing] entries as the writer/storyteller agents learn the user's voice. -->
