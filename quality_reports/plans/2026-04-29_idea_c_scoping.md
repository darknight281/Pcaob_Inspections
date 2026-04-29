# Plan — Idea C Scoping: EDGAR Information Spillovers from PCAOB Inspection Reports

**Date:** 2026-04-29
**Author:** Oliver
**Status:** scoping (pre-discovery)
**Source documents:**
- `master_supporting_docs/PCAOB_Inspection_Research_Discussion_Notes_v1.md` §4.3 (Idea C),
  §6.2 (unit of analysis), §7 (sequencing), §8 (open questions)

---

## Context

Idea C is the first paper in the five-paper PCAOB Inspections research
program. It is sequenced first because it (a) directly leverages the
existing SEC EDGAR collaboration with Qinfang and Qiuhong, (b) has the
cleanest event-study identification (PCAOB inspection-report release
dates as information shocks), and (c) does not depend on the LinkedIn
data access that gates Ideas A and B.

The framing positions inspection reports as an *information event* that
propagates through investor attention networks (EDGAR co-search dyads),
distinct from the audit-quality channel that dominates the existing
literature.

## Research question

When the PCAOB releases an inspection report identifying a deficiency
at audit firm `f` in industry `i`, do investors searching EDGAR for
`f`'s clients update their attention patterns toward (a) other clients
of `f`, (b) clients of competitor auditors in industry `i`, or (c)
clients of `f` outside industry `i`?

## Identification design (initial)

| Element | Choice |
|---|---|
| Treatment | Public release of a PCAOB inspection report with a Part I.A deficiency |
| Treatment unit | **Audit firm × industry** (firm-level inspection × industry-narrative) |
| Outcome unit | **Client firm** — specifically EDGAR co-search dyads |
| Cohort window | Stacked DiD with each inspection-report release as a cohort |
| Estimator | Callaway–Sant'Anna (2021) or Sun–Abraham (2021); robust to staggered timing |
| Falsification | Random non-event placebo dates; alternative co-search measures |

Per research-notes §6.2, this is **firm-level treatment, client-level
outcome** — *not* office-level. EDGAR investors see the audit firm
signature on the 10-K, not the office.

## Data needs

1. **PCAOB inspection reports** (free, pcaobus.org) — release dates +
   Part I.A deficiency narratives (industry + financial-statement-area
   hints). Pipeline: scrape PDFs → extract Part I.A → label industry/area.
2. **Audit Analytics** (WRDS) — auditor identification per issuer-year
   to define the four exposure groups (directly exposed, indirectly
   exposed via same `f`, industry peer via different auditor, control).
3. **EDGAR log files** (free, SEC) — co-search dyads per session.
   Volume: ~2 TB. Pipeline: polars + duckdb to extract dyad pairs and
   aggregate to issuer-pair × day.
4. **Compustat / CRSP** — controls (size, book-to-market, industry).

## Variables

- `Treated_{ij,t}`: indicator that issuer `j` is a client of inspected
  firm `f` whose inspection-report release at time `t` was narrated
  with industry `i`.
- `CoSearch_{jk,t}`: count or rate of EDGAR sessions co-searching
  issuer `j` with peer issuer `k`, around event window `[t-W, t+W]`.
- Pre/post indicators; cohort fixed effects; issuer fixed effects.

## Cross-sectional moderators

1. **Materiality** of the deficiency (Part I.A vs Part I.B vs Part II).
2. Whether the deficiency narrative includes **industry-specific language**.
3. Pre-event investor attention to the auditor (active vs dormant).

## Open questions before discovery sprint

*Resolved 2026-04-29 — Oliver:*

1. **Audit Analytics coverage — RESOLVED.** All Audit Analytics
   modules for U.S. firms are subscribed via Monash WRDS. PostgreSQL
   schema and table inventory to be fetched by sub-agent and
   documented in `master_supporting_docs/data_sources.md`.
2. **EDGAR storage — RESOLVED.** Cleaned data persisted as parquet
   under `data/cleaned/`; raw ~2 TB log archive processed via polars
   + duckdb (lazy / streaming) without full materialisation.
3. **Co-search peer construction — RESOLVED.** Construct **both**
   Lee, Ma, & Wang (2015, *JFE*) and Drake, Roulstone, & Thornock
   (2017, *RAST*) peer sets. Each serves as the other's robustness
   test; primary specification chosen empirically based on event-
   window precision.
4. **Public-data ethics — RESOLVED.** All four exposure groups are
   constructible from public sources (PCAOB inspection PDFs, Audit
   Analytics, EDGAR logs, Compustat). No non-public PCAOB metadata
   required.
5. **Co-authorship boundary with Qinfang / Qiuhong — RESOLVED.**
   Idea C is Oliver's solo paper (sibling, not member of the
   existing SEC EDGAR project). Standalone co-author decisions
   deferred until first complete draft.

## Sub-agent tasks (dispatched 2026-04-29)

In parallel:

- **Agent 1 (explorer):** WRDS Audit Analytics PostgreSQL schema,
  table inventory, key columns, latest-data cut-offs. Output:
  `master_supporting_docs/wrds_audit_analytics_schema.md`.
- **Agent 2 (explorer):** WRDS Revelio Labs schema (replaces the
  open question in `revelio_labs_integration.md` §9 Q1). Tables,
  columns, refresh cadence. Output:
  `master_supporting_docs/wrds_revelio_labs_schema.md`.
- **Agent 3 (explorer):** PCAOB inspection report download paths +
  Part I.A / I.B / II structure; Form AP CSV schema and field
  definitions. Output:
  `master_supporting_docs/pcaob_data_structure.md`.
- **Agent 4 (general-purpose):** Replication-package hunt for
  Drake-Roulstone-Thornock co-search papers, PCAOB inspection
  event studies, and audit-deficiency labour outcome papers
  (covers Ideas A/B/C). Output:
  `master_supporting_docs/replication_packages.md`.

## Immediate next action

Run:

```text
/discover literature "PCAOB inspection report release as information event for EDGAR co-search behaviour. Position relative to: Drake, Roulstone, & Thornock (2015, *CAR*); Lee, Ma, & Wang (2015, *JFE*); Acito, Hogan, & Imdieke (2019, *TAR*); Lamoreaux, Mowchan, & Zhang (2023, *TAR*); Cao et al. (2025, *AJPT*); Roh (2026, *TAR*)."
```

The librarian + librarian-critic pair will return a structured
literature map identifying gaps and the precise contribution slot.

## Sequencing constraint

Per research-notes §7, this paper targets a **12-month horizon to
working-paper draft**. Subsequent papers (Idea E measurement
contribution; Idea A or B labour-market spillovers) build on
infrastructure created here (PDF extraction pipeline, deficiency
narrative encoding, exposure measure construction).

---

*End of scoping plan. Updates appended below as decisions resolve.*
