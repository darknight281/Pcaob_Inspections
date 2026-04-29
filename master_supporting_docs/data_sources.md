# Data Sources — Access Status

Synthesised from `PCAOB_Inspection_Research_Discussion_Notes_v1.md` §3.
Update the **Status** column as access is confirmed or blocked.

**Schema references (added 2026-04-29):**
- `wrds_audit_analytics_schema.md` — WRDS Audit Analytics PostgreSQL inventory (14 modules, 9 detailed)
- `wrds_revelio_labs_schema.md` — WRDS Revelio Labs schema (skeleton, multiple `*unverified*` flags pending in-WRDS confirmation)
- `pcaob_data_structure.md` — PCAOB inspection-report PDF taxonomy (Part I.A/I.B/I.C/II), four format eras, Form AP CSV schema, storage layout
- `replication_packages.md` — Idea C replication-package inventory (**zero public packages located** — green-field infrastructure)

## Primary sources

| # | Dataset | Provider | Unit | Cost | Status |
|---|---|---|---|---|---|
| 1 | PCAOB inspection reports (PDFs) | pcaobus.org | Audit firm × inspection year | Free | **Available** — bulk-downloadable |
| 2 | Form AP | pcaobus.org | Issuer audit × engagement partner | Free | **Available** — CSV downloadable, mandatory since 31 Jan 2017 |
| 3 | Audit Analytics | WRDS | Issuer × audit firm × fiscal year | Subscription | **Available** |
| 4 | Compustat North America | WRDS | Issuer × year | Subscription | **Available** |
| 5 | CRSP | WRDS | Issuer × day | Subscription | **Available** |
| 6 | IBES | WRDS | Issuer × forecast date | Subscription | **Available** |

## Idea-specific sources

| Used by | Dataset | Provider | Status |
|---|---|---|---|
| Idea C | EDGAR log files | SEC (free) | **Available** — ~2 TB; processed via polars + duckdb |
| Idea D | BoardEx | WRDS | **Available** |
| Idea D | Audit Analytics audit-committee data | WRDS | **Available** (bundled with #3) |
| Idea D | ISS Risk Metrics | WRDS | **Available** (alternative to BoardEx) |
| Ideas A, B | Revelio Labs workforce panel | Revelio Labs | **Available** — see `revelio_labs_integration.md` |
| Ideas A, B | Job-posting data | Lightcast / Burning Glass | **Available** (alternative outcome measure) |

## Pipeline notes

The **firm-to-office mapping pipeline** is documented in
`firm_to_office_mapping_methodology.md`. It is the core methodology
shared by Ideas A and B (and any future office-level paper). Concrete
join-keys: Form AP × Audit Analytics on
(`audit_firm_pcaob_id` × `issuer_cik` × `fiscal_year_end`).

The "modal city across engagements" rule for partner-to-office
assignment follows Hu, Smith, & Wong (2025) and Lee, Lee, & Pittman
(2021). Revelio Labs provides an independent validation channel via
LinkedIn-derived job-tenure city tags.

## Open infrastructure questions

*Updated 2026-04-29 — Oliver:*

1. **EDGAR storage — RESOLVED.** Cleaned panels persisted as parquet
   under `data/cleaned/`; raw ~2 TB log archive processed via polars
   + duckdb (lazy / streaming) without full materialisation. Object
   store unnecessary at this stage.
2. **Revelio Labs delivery format — RESOLVED.** WRDS-mounted (Postgres
   schema). Schema documented in `wrds_revelio_labs_schema.md`.
   Refresh cadence per WRDS (vs Revelio direct API): pending
   in-WRDS confirmation — see open questions §8 of that file.
3. **Compute** for BERTopic / sentence-transformer embeddings of
   ~20 years of PCAOB Part I.A narratives — local GPU vs. Monash
   HPC? *Pending — Idea E (downstream paper).*

## Idea C — green-field infrastructure note

Per `replication_packages.md`, no public replication package was
located across 11 candidate papers in the EDGAR co-search and PCAOB
inspection event-study clusters. Idea C must build:

- PCAOB inspection-report PDF parser (4 era-specific templates per
  `pcaob_data_structure.md` §1.3)
- Form AP × inspection-report join (engagement-partner × issuer ×
  inspection cycle)
- Exposure-group construction (directly exposed / indirectly exposed
  via same firm / industry peer / control)

The Lee-Ma-Wang (2015, *JFE*) co-search methodology is the closest
precedent to fork — direct author outreach (Charles Lee, Stanford GSB)
recommended for the SAS scripts. The Iliev-Kalodimos-Lowry (2021,
*RFS*) package may be in the RFS Data Editors portal (post-2019
deposit mandate) and is the highest-priority retrieval target for
EDGAR log ingestion infrastructure.
