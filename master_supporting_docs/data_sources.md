# Data Sources — Access Status

Synthesised from `PCAOB_Inspection_Research_Discussion_Notes_v1.md` §3.
Update the **Status** column as access is confirmed or blocked.

## Primary sources

| # | Dataset | Provider | Unit | Cost | Status |
|---|---|---|---|---|---|
| 1 | PCAOB inspection reports (PDFs) | pcaobus.org | Audit firm × inspection year | Free | **Available** — bulk-downloadable |
| 2 | Form AP | pcaobus.org | Issuer audit × engagement partner | Free | **Available** — CSV downloadable, mandatory since 31 Jan 2017 |
| 3 | Audit Analytics | WRDS | Issuer × auditor × fiscal year | Subscription | TBD — confirm Monash WRDS coverage of Audit Analytics |
| 4 | Compustat North America | WRDS | Issuer × year | Subscription | TBD — confirm Monash WRDS coverage |
| 5 | CRSP | WRDS | Issuer × day | Subscription | TBD — confirm Monash WRDS coverage |
| 6 | IBES | WRDS | Issuer × forecast date | Subscription | TBD — confirm Monash WRDS coverage |

## Idea-specific sources

| Used by | Dataset | Provider | Status |
|---|---|---|---|
| Idea C | EDGAR log files | SEC (free) | **Available** — ~2 TB; will need polars + duckdb for processing |
| Idea D | BoardEx | WRDS | TBD — confirm institutional coverage |
| Idea D | Audit Analytics audit-committee data | WRDS | TBD — bundled with #3 |
| Idea D | ISS Risk Metrics | WRDS | TBD — alternative to BoardEx |
| Ideas A, B | LinkedIn workforce panel | Revelio Labs / LinkUp | **Open question** — Monash institutional access? See research-notes §8 Q2 |
| Ideas A, B | Job-posting data | Burning Glass / Lightcast | TBD — alternative to LinkedIn |

## Pipeline notes

The **office-level mapping** described in research-notes §3.2 requires
join-keys (Audit Firm × Issuer CIK × Fiscal Year-End) between Form AP
and Audit Analytics. The "modal city across engagements" rule is the
standard approach (Hu, Smith, & Wong 2025; Lee, Lee, & Pittman 2021).

## Open access questions

1. **WRDS portfolio**: which of Audit Analytics, BoardEx, ISS Risk
   Metrics, IBES does Monash subscribe to?
2. **LinkedIn data**: most binding access constraint for Ideas A and B.
   See research-notes §8 Q2 — first action is to confirm with the
   Monash library / commercial-data office.
3. **EDGAR storage**: ~2 TB raw; what cloud or on-prem storage is
   available for the full log archive?
