# WRDS Audit Analytics — PostgreSQL Schema Reference

**Purpose.** Quick-reference for Python (`wrds`/`psycopg2`/`duckdb`) querying of
Audit Analytics on Monash WRDS. Scoped to modules used by the PCAOB Inspections
research program (Ideas A–E). Verified facts only — fields flagged
*unverified* must be confirmed inside the WRDS UI before use.

**Verification status.** WRDS web pages (`wrds-www.wharton.upenn.edu/pages/get-data/...`)
returned HTTP 403 from this environment, so direct module pages were not loadable.
Module-page URLs in §1 of the user request are still authoritative; treat this
file as a starting point and confirm column names against the WRDS Variables tab
the first time each table is queried.

---

## 1. Connection

| Setting | Value |
|---|---|
| Host | `wrds-pgdata.wharton.upenn.edu` |
| Port | `9737` |
| Database | `wrds` |
| Schema (library) | `audit` |
| SSL | required |
| Auth | WRDS username + `.pgpass` (or `wrds.Connection()` interactive) |

The `wrds` Python package handles SSL and `.pgpass` automatically. All
Audit Analytics tables live under the `audit.` schema.
[wrds_pg/audit](https://github.com/iangow/wrds_pg/blob/master/audit/readme.md)

---

## 2. Module Inventory

WRDS exposes Audit Analytics modules under both legacy short names
(e.g. `audit.auditopin`) and — in some mirrors — long names
(e.g. `feed05_audit_opinions`). The legacy short names are the ones surfaced
by the WRDS web UI URL path (`/wrds/ds/audit/auditopin/`) and are the names
used in most published replication code. Treat the long names as informative
only until confirmed via `db.list_tables(library='audit')`.

| Module | WRDS table (short name) | Purpose | Key columns | Time coverage |
|---|---|---|---|---|
| Auditors (firm directory) | `audit.auditors` | Audit-firm directory; resolves `auditor_key` to firm name and PCAOB ID | `auditor_key`, auditor name | unverified |
| Audit Opinions | `audit.auditopin` | Annual audit-report opinion per issuer-fiscal-year, incl. going-concern flag | `auditor_key`, `company_fkey`, `fiscal_year_end`, `going_concern` | unverified — confirm in WRDS UI |
| Auditor Changes (8-K) | `audit.auditchanges` (unverified) | Predecessor/successor auditor on Item 4.01 8-Ks | `auditor_key`, predecessor/successor flags, dismissal vs. resignation | unverified |
| Audit Fees | `audit.auditfees` | Audit, audit-related, tax, other fees by fiscal year | `auditor_key`, `company_fkey`, `fiscal_year_end`, audit fees, non-audit fees | unverified |
| Non-Reliance Restatements | `audit.auditnonreli` | Item 4.02 non-reliance restatement events | `company_fkey`, restatement disclosure date, period restated | unverified |
| SOX 404 ICFR | `audit.auditsox404` (unverified) | Auditor's ICFR opinion under SOX 404(b); material weaknesses | `auditor_key`, `company_fkey`, `fiscal_year_end`, ICFR effective flag | unverified |
| Engagement Partners (Form AP) | unverified short name | Form AP partner-level disclosures (since 31 Jan 2017) | partner ID, partner name, `auditor_key`, `company_fkey`, fiscal year | unverified — see §4 |
| Going Concern | reported as a column (`going_concern`) inside `audit.auditopin` and `audit.auditrevop` (revised opinions); also exists as an `auditgc` standalone in legacy releases | Going-concern qualifications | `company_fkey`, `fiscal_year_end`, `going_concern` | unverified |
| Auditor City/Office | reported via city/state fields on `audit.auditors`, `audit.auditfees`, and `audit.auditopin` (auditor location of signing office) | Office-level identification for Ideas A and B | auditor city, auditor state, auditor country | unverified |
| Director & Officer Changes | `audit.audrdor` (unverified) — narrow, not detailed here | D&O turnover from 8-Ks | — | unverified |
| Benefit Plan Audits | `audit.audbenft` (unverified) — narrow, not detailed here | ERISA Form 5500 audit opinions; not used for Ideas A–E | — | unverified |
| Comment Letters | narrow — not detailed here | SEC staff comment letters | — | — |
| Late Filers (NT) | narrow — not detailed here | NT 10-K / NT 10-Q filings | — | — |

Sources: [iangow/wrds_pg audit readme](https://github.com/iangow/wrds_pg/blob/master/audit/readme.md);
WRDS short-name URL pattern observed at `wrds-web.wharton.upenn.edu/wrds/ds/audit/auditopin/`.

---

## 3. Per-Module Detail

For each module: schema-qualified table, primary key, top columns useful for
event studies and office-level analysis. Column names below follow conventions
seen in WRDS replication code; **always confirm in the WRDS UI the first time
you query each table**.

### 3.1 `audit.auditors` — Auditor Directory

- **Use:** resolve `auditor_key` to firm identity (PCAOB-registered audit firm).
- **Primary key:** `auditor_key`.
- **Useful columns:**
  - `auditor_key` (int) — Audit Analytics auditor ID
  - `auditor_name` — firm name as filed
  - PCAOB firm ID (column name unverified — typically a `pcaob_id` or similar field)
  - auditor city/state/country fields
- **Time coverage:** snapshot table; covers all Audit Analytics auditors.
- **Notes:** this table is the master join key for every other Audit Analytics
  table that exposes `auditor_key`. Many other tables drop the auditor name to
  save space, so join here to recover it.
  [iangow/wrds_pg](https://github.com/iangow/wrds_pg/blob/master/audit/readme.md)

### 3.2 `audit.auditopin` — Audit Opinions

- **Use:** issuer × fiscal-year audit opinion; the canonical going-concern
  source; office-level location of signing auditor.
- **Primary key:** unverified — likely (`company_fkey`, `fiscal_year_end`, `auditor_key`).
- **Useful columns:**
  - `auditor_key` — engagement audit firm
  - `company_fkey` — issuer CIK (zero-padded string in some releases)
  - `fiscal_year_end` (date)
  - opinion-type code (clean / qualified / adverse / disclaimer)
  - `going_concern` (boolean) — see §3.8
  - signing-auditor city / state — used to construct office identifiers
  - filing-form type (10-K, 10-K/A, etc.) and filing date
- **Time coverage:** approximately 2000–present; **unverified** exact start year.
  [WRDS UI](https://wrds-www.wharton.upenn.edu/pages/get-data/audit-analytics/audit-opinions/)

### 3.3 `audit.auditchanges` — Auditor Changes (8-K Item 4.01)

- **Use:** identify dismissal/resignation events; predecessor/successor pairs.
- **Primary key:** unverified — likely an event-level key on (`company_fkey`, change date).
- **Useful columns:**
  - `company_fkey` — issuer CIK
  - predecessor `auditor_key` and successor `auditor_key`
  - dismissal vs. resignation flag
  - 8-K filing date and effective date of change
  - reason-for-change indicators
- **Time coverage:** 2001–present; **unverified** exact start year.
  [WRDS UI](https://wrds-www.wharton.upenn.edu/pages/get-data/audit-analytics/auditor-changes/)

### 3.4 `audit.auditfees` — Audit and Non-Audit Fees

- **Use:** annual audit-fee panel; office × issuer × year for fee-pressure analyses.
- **Primary key:** unverified — likely (`company_fkey`, `fiscal_year_end`, `auditor_key`).
- **Useful columns:**
  - `auditor_key`, `company_fkey`, `fiscal_year_end`
  - `audit_fees`, `audit_related_fees`, `tax_fees`, `other_fees`, `non_audit_fees`, `total_fees` (USD; column names unverified)
  - signing-auditor city / state
  - filing form (10-K, DEF 14A, etc.)
- **Time coverage:** 2000–present (proxy fee disclosures begin in 2000);
  **unverified** exact start year.
  [WRDS UI](https://wrds-www.wharton.upenn.edu/pages/get-data/audit-analytics/audit-fees/)

### 3.5 `audit.auditnonreli` — Non-Reliance Restatements (Item 4.02)

- **Use:** identify restatement events; period covered; severity tags.
- **Primary key:** unverified — likely event-level on (`company_fkey`, restatement disclosure date).
- **Useful columns:**
  - `company_fkey` — issuer CIK
  - restatement-disclosure date (Item 4.02 8-K date)
  - restatement-period begin / end dates
  - issue codes (revenue, accounting policies, etc.)
  - restatement-by-auditor-resignation indicator
- **Time coverage:** 2000–present; **unverified** exact start year.
  [WRDS UI](https://wrds-www.wharton.upenn.edu/pages/get-data/audit-analytics/non-reliance-restatements/)

### 3.6 `audit.auditsox404` — SOX 404 ICFR Audit Opinions

- **Use:** auditor's ICFR opinion under SOX 404(b); identify material weaknesses.
- **Primary key:** unverified — likely (`company_fkey`, `fiscal_year_end`, `auditor_key`).
- **Useful columns:**
  - `auditor_key`, `company_fkey`, `fiscal_year_end`
  - ICFR opinion type (effective / ineffective / adverse)
  - material weakness flag and count
  - issue-area codes for weaknesses (revenue recognition, tax, etc.)
- **Time coverage:** 2004–present (SOX 404(b) phase-in begins fiscal 2004 for accelerated filers);
  **unverified** exact start year.
  [WRDS UI](https://wrds-www.wharton.upenn.edu/pages/get-data/audit-analytics/sox-internal-controls/)

### 3.7 Engagement Partners (Form AP)

- **Use:** partner-level identification for Ideas A, B, D, E. Form AP filings became
  mandatory for partner names on 31 Jan 2017; for "other accounting firms"
  on 30 June 2017.
- **Schema-qualified table name:** **unverified** — confirm in WRDS UI. Audit
  Analytics markets a Form-AP-linked engagement-partner dataset; the WRDS short
  name is not confirmed by sources accessible from this environment.
- **Useful columns (expected):**
  - partner-level identifier (Form AP partner ID or Audit Analytics partner key)
  - partner name
  - `auditor_key` (audit firm)
  - `company_fkey` (issuer CIK)
  - fiscal-year-end / report date
  - "other accounting firms" flag and percentage of audit hours
- **Time coverage:** partner names 31 Jan 2017–present; other firms 30 Jun 2017–present.
  [WRDS UI](https://wrds-www.wharton.upenn.edu/pages/get-data/audit-analytics/audit-engagement-partner/);
  [PCAOB Form AP](https://pcaobus.org/oversight/standards/implementation-resources-PCAOB-standards-rules/form-ap-auditor-reporting-certain-audit-participants)

### 3.8 Going Concern

- **Use:** going-concern qualifications.
- **Where it lives:** as a boolean column (typical name `going_concern`) inside
  `audit.auditopin` and the revised-opinions table. A standalone going-concern
  table may also exist in some Audit Analytics releases (`audit.auditgc` —
  unverified short name); for analytical work the column on `auditopin` is
  generally sufficient.
- **Time coverage:** matches `auditopin`.

### 3.9 Auditor City / Office

- **Use:** office-level identification for Ideas A (workforce-strategy) and
  B (cross-office spillovers). The auditor's signing office is reported on the
  audit opinion and on fee filings as city/state/country fields.
- **Where it lives:** auditor city and state fields are exposed on
  `audit.auditors`, `audit.auditfees`, and `audit.auditopin`. There is no
  separate "office directory" table; offices are constructed by deduplicating
  (`auditor_key`, city, state) tuples and applying a modal-city rule per
  partner per year (see `firm_to_office_mapping_methodology.md`).

---

## 4. Linking Conventions

### 4.1 `auditor_key` → PCAOB firm ID

`audit.auditors` carries `auditor_key` and (per the iangow mirror documentation)
a PCAOB firm-identifier column; column name is **unverified** in the live WRDS
schema. Join to recover firm name and PCAOB ID:

```sql
SELECT a.*, f.auditor_name
FROM audit.auditfees AS a
LEFT JOIN audit.auditors AS f USING (auditor_key);
```

### 4.2 `company_fkey` (CIK) → GVKEY → PERMNO

`company_fkey` in Audit Analytics is the SEC CIK. Two routes to Compustat:

```sql
-- Route A: direct via Compustat company table (1:1 on CIK->GVKEY)
SELECT aa.*, c.gvkey
FROM audit.auditopin AS aa
LEFT JOIN comp.company AS c
  ON LPAD(aa.company_fkey::text, 10, '0') = LPAD(c.cik::text, 10, '0');

-- Route B: GVKEY -> PERMNO via CRSP-Compustat link history
SELECT *
FROM comp.company AS c
JOIN crsp.ccmxpf_lnkhist AS l
  ON c.gvkey = l.gvkey
 AND l.linktype IN ('LU','LC')
 AND l.linkprim IN ('P','C');
```

CIK width: Audit Analytics historically pads CIK to 10 digits as a string;
Compustat stores it as numeric. Always normalise widths before joining.

### 4.3 Form AP partner ID → Audit Analytics engagement-partner table

The PCAOB publishes raw Form AP CSVs (free download). Audit Analytics ingests
and assigns its own partner-level IDs. Linkage between PCAOB-assigned partner
identifiers and Audit Analytics partner keys is **unverified** from accessible
sources — confirm in the WRDS UI Variables tab on the engagement-partner
table. Join key is typically (`auditor_key`, partner-name, fiscal year end)
plus issuer CIK.

---

## 5. Python Query Snippet

```python
import wrds
import pandas as pd

# Connect (prompts for password on first call; cached in ~/.pgpass thereafter)
db = wrds.Connection(wrds_username="oliver_monash")

# Inspect schema
db.list_tables(library="audit")[:20]
db.describe_table(library="audit", table="auditopin").head(30)

# Pull all audit opinions for a CIK list
ciks = ["0000320193", "0000789019", "0001318605"]  # zero-padded strings

opin = db.raw_sql(
    """
    SELECT o.company_fkey, o.fiscal_year_end, o.auditor_key,
           o.going_concern, o.opinion_text_id, a.auditor_name
    FROM audit.auditopin AS o
    LEFT JOIN audit.auditors AS a USING (auditor_key)
    WHERE o.company_fkey = ANY(%(ciks)s)
    ORDER BY o.company_fkey, o.fiscal_year_end
    """,
    params={"ciks": ciks},
)

opin.to_parquet("data/cleaned/auditopin_sample.parquet")
db.close()
```

For the EDGAR-spillover panel (Idea C), pull `auditopin`, `auditsox404`, and
`auditnonreli` together, then merge to the Form AP partner table on
(`auditor_key`, `company_fkey`, `fiscal_year_end`).

---

## 6. Caveats and Open Items

1. **Verify short table names** before first query: run
   `db.list_tables(library="audit")` and `db.describe_table(...)`. Several
   short names above are flagged *unverified*.
2. **Form AP engagement-partner table name** is the largest open item — check
   the WRDS UI page at `/get-data/audit-analytics/audit-engagement-partner/`.
3. **Time coverage start years** are stated as approximate; confirm against
   each table's Variables tab (WRDS shows the min/max date).
4. **Column-level granularity** (e.g., individual fee categories on `auditfees`,
   issue-area codes on `auditsox404`) was not fully verifiable from this
   environment and must be confirmed in the WRDS UI.
5. **Audit Analytics Europe** (a separate WRDS subscription) lives under a
   different schema and is out of scope for this file.
