# Data Sources — Access Status

Synthesised from `PCAOB_Inspection_Research_Discussion_Notes_v1.md` §3.
Update the **Status** column as access is confirmed or blocked.

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

1. **EDGAR storage**: ~2 TB raw; on-prem or cloud bucket for the
   full log archive? Recommended: object store + duckdb federated
   queries.
2. **Revelio Labs delivery format**: WRDS-mounted cube vs. parquet
   snapshots? Confirms refresh cadence (research-notes §8 Q2).
3. **Compute**: BERTopic / sentence-transformer embeddings of
   ~20 years of PCAOB Part I.A narratives — local GPU vs. Monash
   HPC?
