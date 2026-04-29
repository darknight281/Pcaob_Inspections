# PCAOB Inspection-Report and Form AP Data Structure

**Project:** Idea C — EDGAR information spillovers from PCAOB inspection-report releases
**Author:** Oliver (Monash University)
**Date:** 2026-04-29
**Purpose:** Document the inputs the data pipeline must ingest. Event date for Idea C is `report_release_date` (PCAOB inspection report). Cross-sectional treatment is the partner/issuer cell from Form AP.

> **Verification status:** This document was written from priors and partially verified against the PCAOB website on 2026-04-29. Items marked `*unverified*` should be confirmed by sampling reports or downloading the source CSV.

---

## 1. PCAOB Inspection Reports

### 1.1 Inventory page

- Master listing: `https://pcaobus.org/oversight/inspections/firm-inspection-reports`
- Per-firm pages list all historical inspection reports as PDFs. Filenames typically encode firm + inspection-year (`*unverified — confirm naming convention by sampling*`).
- Site is fronted by Cloudflare. Automated GETs without a polite User-Agent and rate limit may be blocked or rate-limited.
- A sister directory `https://pcaobus.org/oversight/inspections/inspection-procedures` documents inspection scope but contains no data.

### 1.2 PDF section taxonomy

The internal structure of an inspection report has four parts. Each evolves across format eras (Section 1.3).

| Part  | Title                                                                                  | Public on release?                                                                                                  | Content                                                                              |
|-------|----------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------|
| I.A   | Deficiencies in audits of issuers — material/significant                               | Yes                                                                                                                 | Free-text audit-by-audit narrative; auditor failed to obtain sufficient evidence     |
| I.B   | Deficiencies in audits of issuers — non-material reportable (introduced ~2015)         | Yes                                                                                                                 | Lower-severity reportable items; sometimes labelled "Part I.B Instances of Non-Compliance with PCAOB Standards" `*unverified*` |
| I.C   | Independence non-compliance instances                                                  | Yes `*unverified — newer addition, confirm era*`                                                                    | Auditor-independence violations identified during inspection                          |
| II    | Quality-control criticisms                                                             | Confidential for ≥12 months; portions made public if firm fails to remediate within that window per Sarbanes-Oxley §104(g)(2) | Firm-wide QC concerns; tone of the top; tone re-test methodology; supervision        |

### 1.3 Format-era table

Major redesigns of the inspection-report PDF template. Era boundaries are approximate — confirm by sampling reports.

| Era   | Years (approx.)        | Notes                                                                                       |
|-------|------------------------|---------------------------------------------------------------------------------------------|
| Era 1 | 2004–~2010             | Early format; less standardised; smaller Part I; no Part I.B `*unverified*`                  |
| Era 2 | ~2010–~2017            | Standardised template; Part I.B introduced; deficiency-by-deficiency tables `*unverified*`   |
| Era 3 | ~2018–~2022            | Reformatted; cover-page summary; aggregate deficiency counts; "Part I.A / I.B / I.C / II" structure stabilised `*unverified*` |
| Era 4 | ~2022–present          | Post-2022 redesign; new graphical summaries; possible new section labels `*unverified*`     |

**Implication for pipeline:** Build four era-specific PDF extractors. A single regex/template will not work across all years.

### 1.4 Per-report metadata to capture

Target schema for `inspection_reports_index.csv` (one row per inspection report):

| Field                       | Type    | Description                                                                          |
|-----------------------------|---------|--------------------------------------------------------------------------------------|
| `audit_firm_name`           | string  | Registered firm name as on PCAOB report                                              |
| `audit_firm_pcaob_id`       | string  | PCAOB-assigned firm ID                                                               |
| `inspection_year`           | int     | Year of audits inspected (NOT release year)                                          |
| `inspection_cycle`          | string  | "annual" for firms with >100 issuer audits; "triennial" otherwise                    |
| `report_release_date`       | date    | **Event date for Idea C — critical**                                                 |
| `n_audits_inspected`        | int     | Number of issuer audits selected for inspection                                      |
| `part_ia_deficiency_count`  | int     | Count of Part I.A audits with deficiencies                                           |
| `part_ib_deficiency_count`  | int     | Count of Part I.B audits with deficiencies (NA before 2015) `*unverified era cutoff*` |
| `part_ic_present`           | bool    | Whether Part I.C section appears                                                     |
| `part_ii_present`           | bool    | Whether Part II section is included in initial release (rare — usually NO until ≥12-month remediation window expires) |
| `report_url`                | string  | Absolute URL on pcaobus.org                                                          |
| `report_pdf_path`           | string  | Local path under `data/raw/pcaob/inspection_reports/...`                              |
| `format_era`                | int     | 1–4, derived from release date                                                       |

### 1.5 Audit Analytics PCAOB Inspections module (WRDS)

`*unverified — confirm in WRDS UI whether a dedicated PCAOB Inspections module exists separately from "Audit Opinions" or "Auditor Changes"*`. Some Audit Analytics products do parse inspection-report metadata (firm, year, deficiency counts), but coverage and field naming vary. Oliver to confirm during data discovery; if available, this can replace the home-built `inspection_reports_index.csv` for header metadata while we still need PDF extraction for narratives.

---

## 2. Form AP

### 2.1 Canonical download path

- Search & export UI: `https://pcaobus.org/resources/auditorsearch` (a.k.a. AuditorSearch / Form AP search) `*unverified exact URL — confirm*`
- Bulk CSV export available from the search interface; refresh cadence approximately weekly `*unverified*`
- Coverage: 2017-01-31 onward (mandatory date when Form AP filing became compulsory under PCAOB Rule 3211)
- Earlier filings on a voluntary basis from late 2016 `*unverified — confirm voluntary window*`

### 2.2 Field-by-field schema

Schema based on PCAOB Release 2015-008 appendix and the AuditorSearch export form. **All rows below `*unverified — confirm via Release 2015-008 PDF appendix and a fresh CSV download*`.**

| Field                  | Type    | Description                                                                       |
|------------------------|---------|-----------------------------------------------------------------------------------|
| `firm_id`              | string  | PCAOB ID of the filing audit firm                                                 |
| `firm_name`            | string  | Filing audit firm name                                                            |
| `issuer_name`          | string  | Issuer being audited                                                              |
| `issuer_cik`           | string  | Issuer SEC CIK (zero-padded)                                                      |
| `issuer_file_number`   | string  | SEC file number                                                                   |
| `partner_id`           | string  | PCAOB-assigned engagement-partner ID (stable across firm switches)                |
| `partner_name`         | string  | Engagement partner full name                                                      |
| `fiscal_period_end`    | date    | Fiscal year-end audited                                                           |
| `audit_report_date`    | date    | Date the audit report was signed                                                  |
| `form_ap_filing_date`  | date    | Date Form AP was filed with PCAOB                                                 |
| `other_firms`          | nested  | Component-auditor firms used in audit; each row has PCAOB ID, country, hours-pct |
| `dual_dated`           | bool    | Whether audit report is dual-dated                                                |

### 2.3 Partner ID granularity

Per PCAOB rule, partner IDs are stable across firm switches — i.e., if a partner moves from KPMG to Deloitte, the same `partner_id` follows them. `*unverified — confirm in PCAOB technical specification*`. This is critical for tracking partner mobility (relevant for Idea A and the LinkedIn pipeline).

### 2.4 Linking to Audit Analytics

Typical join key to Audit Analytics' Engagement Partner module:

```
(firm_id, issuer_cik, fiscal_period_end)
```

Audit Analytics historically used CIK + fiscal-year-end + auditor; the addition of `partner_name` from Form AP allows partner-level linking from 2017-01-31 onward. Pre-2017 partner identities are not in Audit Analytics.

For Idea C event-study panel: Form AP gives the partner-issuer-fiscal-year cell, which is then attached to the inspection-report event via `(audit_firm_pcaob_id, inspection_year)`.

---

## 3. Storage layout

```
data/raw/pcaob/
├── inspection_reports/                         # PDFs organised by firm/year
│   ├── deloitte/2024/<filename>.pdf
│   ├── kpmg/2024/<filename>.pdf
│   ├── pwc/2024/<filename>.pdf
│   ├── ey/2024/<filename>.pdf
│   └── triennial/<firm-slug>/<year>/<filename>.pdf
├── inspection_reports_index.csv                # Per-report metadata (Section 1.4)
├── form_ap/
│   ├── form_ap_full.csv                        # Latest cumulative extract
│   └── snapshots/
│       ├── form_ap_2026-01.csv                 # Monthly snapshots for vintage tracking
│       └── form_ap_2026-04.csv
└── README.md                                   # Provenance, download dates, source URLs
```

Cleaned outputs land in `data/cleaned/pcaob/*.parquet` per the `polars`/`duckdb` convention in CLAUDE.md.

---

## 4. Open issues for Oliver

- **Cloudflare on pcaobus.org** may block automated scraping. Use a polite User-Agent string identifying the project, and throttle to ≤1 request/sec. If blocked, fall back to manual download for the inventory phase and only automate the per-firm directory listings.
- **Format-era discontinuities** will require four era-specific PDF extractors. Plan a sampling exercise: pull two reports per era and document the section headers and table styles before writing extractors.
- **Audit Analytics on WRDS** — confirm whether the PCAOB Inspections data is a stand-alone module or embedded inside Audit Opinions. If stand-alone, it may save us the home-built index.
- **Part II release-on-failure trigger** — for each historical Part II section that became public (because the firm failed to remediate within 12 months), confirm the actual public-release date. This is a second event date, distinct from the original `report_release_date`.
- **Form AP CSV column names** — confirm by downloading a sample after Discovery phase. The schema above is from priors; field names may differ slightly (e.g., `engagementPartnerId` vs `partner_id`).
- **Voluntary Form AP filings** — confirm whether any pre-2017-01-31 filings exist in the bulk CSV and how they should be flagged.
- **Partner ID stability across firm switches** — confirm in PCAOB technical spec that the same `partner_id` follows a partner across firms. If not, partner-mobility analyses (Ideas A/B) need a separate identity-resolution layer.
