# WRDS Revelio Labs Schema Reference

**Purpose:** Raw WRDS schema reference for querying Revelio Labs via Python (`wrds`/`duckdb`).
**Companion doc:** `revelio_labs_integration.md` (outcome variables and audit-firm logic).
**Status:** Draft — multiple fields unverified; Oliver to confirm via WRDS UI/`SELECT * LIMIT 1`.

---

## 1. Connection

- **Host:** `wrds-pgdata.wharton.upenn.edu`, port `9737`, db `wrds`
- **Library prefix:** `revelio` (schema name on Postgres) — *unverified — confirm in WRDS UI*
- **Access:** Requires WRDS subscription with Revelio Labs add-on entitlement

---

## 2. Inventory

| Table | Purpose | Primary Key | Key Columns | Time Coverage | Notes |
|---|---|---|---|---|---|
| `revelio.company_ref` | Company dimension (RCID master) | `rcid` | `rcid`, `company`, `ticker`, `naics`, `country`, `domain` | static (refreshed) | RCID is Revelio's canonical company ID — *unverified table name* |
| `revelio.workforce_dynamics` | Headcount/inflow/outflow panel | `rcid` × `month` | `rcid`, `month`, `headcount`, `inflow`, `outflow`, `attrition_rate` | ~2008–present | monthly panel — *unverified* |
| `revelio.individual_position` | Person-spell history (LinkedIn-derived) | `user_id` × `position_id` | `user_id`, `rcid`, `start_date`, `end_date`, `title_raw`, `seniority`, `role_k1500`, `location` | ~2008–present | Core micro table; very large — *unverified column names* |
| `revelio.individual_user` | Person dimension | `user_id` | `user_id`, `country`, `metro_area`, `education_level`, `gender_predicted`, `ethnicity_predicted` | static | Demographic predictors are model-imputed — *unverified* |
| `revelio.job_postings` | Job-posting flow (vacancies) | `posting_id` | `posting_id`, `rcid`, `posted_date`, `removed_date`, `title_raw`, `salary_low`, `salary_high`, `location` | ~2018–present | Flow data; coverage varies — *unverified* |
| `revelio.salary` | Modeled compensation | `rcid` × `role` × `month` (?) | `rcid`, `role_k1500`, `seniority`, `month`, `total_comp`, `base_pay` | ~2014–present | Modeled, not actual paid — *unverified granularity* |
| `revelio.sentiment` | Glassdoor-style review aggregates | `rcid` × `month` (?) | `rcid`, `month`, `overall_rating`, `culture`, `comp_benefits`, `n_reviews` | varies | *unverified — table may be split by source* |

> All table names with the `revelio.` prefix are **unverified** — confirm via `SELECT table_name FROM information_schema.tables WHERE table_schema LIKE 'revelio%';`

---

## 3. Per-Table Mini-Detail

### 3.1 `revelio.company_ref` (or `company_mapping`)
- **PK:** `rcid` (integer, Revelio Company ID)
- **Top columns:** `rcid`, `company` (legal name), `ticker`, `naics`, `sic`, `country`, `domain` (URL), `linkedin_url`
- **Use:** Lookup table to map RCID → firm name/ticker. Filter audit firms by name regex on `company`.
- **Notes:** *unverified — confirm column names; Revelio sometimes calls this `company_mapping` or `company`.*

### 3.2 `revelio.workforce_dynamics`
- **PK:** `(rcid, month)` — *unverified*
- **Top columns:** `rcid`, `month` (date), `headcount`, `inflow`, `outflow`, `attrition_rate`, `growth_rate`, `tenure_avg`
- **Use:** Aggregate firm-level employee counts; primary panel for office/firm headcount tracking.
- **Granularity:** Firm-level only in this table; for office-level, aggregate from `individual_position` by `location`.

### 3.3 `revelio.individual_position`
- **PK:** `(user_id, position_id)` — *unverified, possibly just `position_id`*
- **Top columns:** `user_id`, `rcid`, `position_id`, `start_date`, `end_date`, `title_raw`, `title_clean`, `role_k1500`, `seniority`, `location_raw`, `metro_area`
- **Use:** Spell-level table; build office-level panels by aggregating to (rcid × metro × month).
- **Notes:** Multi-billion rows. Use DuckDB partitioning or WRDS server-side filters. *unverified.*

### 3.4 `revelio.individual_user`
- **PK:** `user_id`
- **Top columns:** `user_id`, `country`, `metro_area`, `education_highest`, `school`, `gender_predicted`, `ethnicity_predicted`, `years_experience`
- **Use:** Demographic controls / heterogeneity analyses.
- **Notes:** Many fields are ML-imputed (gender, ethnicity); flag carefully in any paper.

### 3.5 `revelio.job_postings`
- **PK:** `posting_id`
- **Top columns:** `posting_id`, `rcid`, `posted_date`, `removed_date`, `title_raw`, `role_k1500`, `seniority`, `salary_low`, `salary_high`, `location`, `remote_flag`
- **Use:** Hiring intent / vacancy flow. Useful as labour-demand proxy.
- **Notes:** Coverage starts ~2018; pre-2018 sparse. *unverified.*

### 3.6 `revelio.salary`
- **PK:** *unverified — likely `(rcid, role_k1500, seniority, month)` or similar*
- **Top columns:** `rcid`, `role_k1500`, `seniority`, `month`, `total_comp`, `base_pay`, `bonus_pct`, `n_obs`
- **Use:** Compensation panel. Modeled, not actual payroll.
- **Notes:** Salary is *imputed from postings + reported pay*; treat as estimate.

### 3.7 `revelio.sentiment`
- **PK:** *unverified*
- **Top columns:** `rcid`, `month`, `overall_rating`, `culture_rating`, `comp_benefits_rating`, `senior_mgmt_rating`, `n_reviews`
- **Use:** Employee-sentiment panel for audit-quality / morale analyses.
- **Notes:** Source may be Glassdoor scrape; coverage uneven across firms. *unverified.*

---

## 4. Audit-Firm Filtering

The relevant Revelio company-ID field is `rcid` (integer). To filter to Big 4 + mid-tier audit firms:

```sql
SELECT rcid, company, ticker, country
FROM revelio.company_ref
WHERE LOWER(company) ~ '(deloitte|pricewaterhouse|pwc|ernst.*young|kpmg|bdo|grant thornton|rsm|crowe|baker tilly|mazars)'
  AND country IN ('United States','USA','US');
```

- **Big 4 RCIDs:** Deloitte / PwC / EY / KPMG — *specific RCID integers unverified; Oliver to confirm via WRDS query.*
- **Mid-tier:** BDO, Grant Thornton, RSM, Crowe, Baker Tilly, Mazars (US) — also unverified RCIDs.
- **Subsidiaries/affiliates:** Each Big 4 firm has dozens of country/legal-entity RCIDs (e.g. "Deloitte Tax LLP", "Deloitte Consulting"). Decide whether to roll up or keep separate.
- **Cross-check:** Compare RCID-derived headcount to Big 4 published figures (~100k US employees each) for sanity.

---

## 5. Function / Role Taxonomy

- **Field name:** `role_k1500` (1,500-cluster Revelio role taxonomy) — *unverified field name*
- **Alternative:** `job_category_top` (~30 high-level buckets) — *unverified*
- **Typical values for audit firms:** `Auditor`, `Tax Associate`, `Audit Manager`, `Audit Partner`, `Consulting`, `Advisory`, `Risk Advisory`, `IT Audit`
- **Seniority field:** `seniority` (1–7 ordinal) — *unverified scale: may be 0–7 or string*
- **Use:** Filter to audit-line employees by `role_k1500 LIKE '%audit%'` + exclude `consulting`/`advisory`/`tax` if pure audit-quality is the focus.
- **Caveat:** Self-reported LinkedIn titles; classification is ML-derived. Validate cluster contents before finalizing filters.

---

## 6. Linking to Public-Firm IDs

- **WRDS-published crosswalk:** Revelio includes `ticker` directly on `company_ref` — *unverified column*; CIK/GVKEY are **not** native to Revelio.
- **Build crosswalk:** Join Revelio `ticker` → CRSP `ticker`/`permno` → CCM Linktable → Compustat `gvkey` → SEC `cik` (via Compustat's CIK field or WRDS SEC linktable).
- **Caveats:**
  - Multiple RCIDs may map to one ticker (parent/sub structure).
  - Big 4 firms are private partnerships → no ticker; match by name only.
  - Historical ticker changes need point-in-time matching (use CRSP `dsenames`).
- *unverified — confirm whether WRDS provides a `revelio.ticker_crosswalk` or similar.*

---

## 7. Python Query Snippet

```python
import wrds
import pandas as pd

db = wrds.Connection(wrds_username="oliver_user")  # uses ~/.pgpass

# 1) Identify audit-firm RCIDs
audit_firms = db.raw_sql("""
    SELECT rcid, company, ticker
    FROM revelio.company_ref
    WHERE LOWER(company) ~ '(deloitte|pwc|pricewaterhouse|ernst.*young|kpmg|bdo|grant thornton|rsm)'
      AND country IN ('United States','USA','US')
""")

rcid_list = tuple(audit_firms['rcid'].tolist())

# 2) Pull monthly headcount panel for those firms
panel = db.raw_sql(f"""
    SELECT rcid, month, headcount, inflow, outflow, attrition_rate
    FROM revelio.workforce_dynamics
    WHERE rcid IN {rcid_list}
      AND month >= '2010-01-01'
""", date_cols=['month'])

panel = panel.merge(audit_firms[['rcid','company']], on='rcid', how='left')
panel.to_parquet('data/cleaned/revelio_audit_headcount.parquet')
db.close()
```

---

## 8. Open Questions for Oliver

1. **Schema name:** is the Postgres library `revelio`, `revelio_revelio`, or split into multiple (e.g. `revelio_main`, `revelio_postings`)?
2. **Refresh cadence:** monthly delivery vs on-request extract? WRDS sometimes flags Revelio as "extract-on-request" requiring per-query approval.
3. **Big 4 RCIDs:** confirm exact integer RCIDs for Deloitte/PwC/EY/KPMG US entities (and decide rollup of subsidiaries).
4. **Office-level granularity:** is metro/MSA available directly on `workforce_dynamics`, or only via aggregation from `individual_position`?
5. **`role_k1500` vs alternative taxonomies:** which field/granularity does WRDS expose? Is there a documented mapping table?
6. **Salary table PK:** confirm whether `salary` is at firm × role × month or includes seniority breakdown.
7. **Sentiment source:** Glassdoor vs Indeed vs aggregated? Confirm whether reviews tie to RCID directly.
8. **Crosswalk:** does WRDS publish a Revelio↔CRSP/Compustat link, or must we build via ticker/name?
9. **Demographic imputations:** which fields (`gender_predicted`, `ethnicity_predicted`) carry confidence scores, and what's the recommended threshold?
10. **Coverage caveats:** which years/regions are sparse? (Pre-2010 LinkedIn coverage likely thin; non-US sparse.)

---

## Verification Pointers

WebFetch attempts to WRDS docs and Revelio data-dictionary pages all returned 403 (auth-walled or scraper-blocked). Recommended manual verification path for Oliver:

- **WRDS Revelio landing page:** `https://wrds-www.wharton.upenn.edu/pages/get-data/revelio/` (login required)
- **Revelio canonical data dictionary:** `https://www.data-dictionary.reveliolabs.com/`
- **HBS reference code (canonical starting point):** `https://github.com/hbs-brds/wrds_revelio` — `MetaData.R` script enumerates all tables in the WRDS Revelio schema and produces an Excel codebook with 20 sample rows per table. Run this first to ground-truth all `unverified` items above.
- **Quick verification SQL** (run in WRDS web SQL or via `wrds.Connection.raw_sql()`):
  ```sql
  SELECT table_schema, table_name FROM information_schema.tables
  WHERE table_schema ILIKE '%revelio%' ORDER BY 1, 2;
  ```
