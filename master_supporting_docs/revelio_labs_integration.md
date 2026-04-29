# Revelio Labs Integration — Audit-Office Workforce Outcomes

**Status:** design (pre-implementation)
**Applies to:** Ideas A, B (primary outcomes); validation cross-check for Step 2 of the firm-to-office mapping pipeline
**Last updated:** 2026-04-29
**Owner:** Oliver

---

## 1. What Revelio Labs provides

Revelio Labs delivers a person-month-level workforce panel
constructed from public LinkedIn profiles (and adjacent
sources) covering ~700M individuals globally. The relevant
deliverables for this project are:

| Product | Unit | Variables |
|---|---|---|
| **Workforce dynamics** | Company × month | Headcount, hires, exits, internal moves, attrition rate, growth rate |
| **Individual user history** | Person × position-spell | Employer, title, location, start date, end date, seniority, function, skills |
| **Job postings** | Posting × day | Posted requisitions by company × location × role |
| **Salary** | Person / role × company × location | Estimated compensation |
| **Sentiment / reviews** | Company × month | Glassdoor-derived rating, review volume, review-text aggregates |

For the PCAOB Inspections program, **Workforce dynamics** and
**Individual user history** are the primary feeds. Sentiment
provides a useful independent validation channel.

---

## 2. Audit-firm coverage

Revelio's coverage of the Big 4 is essentially comprehensive:
each firm has tens of thousands of US employees with
LinkedIn profiles, and partnership-track positions are
disproportionately well-covered (LinkedIn use is near-universal
for senior accountants).

Coverage drops for mid-tier firms (BDO, Grant Thornton, RSM,
Crowe, Mazars, etc.) but remains workable for firms with > 500
US employees. Below that threshold, coverage is uneven.

**Pre-registered scope: Big 4 main analysis; mid-tier as
heterogeneity / robustness.** This aligns with the inspection-
intensity heterogeneity (Big 4 inspected annually; mid-tier
triennially) and addresses the Revelio-coverage gradient.

---

## 3. Office identification within Revelio

A Revelio person-spell carries:

- `company_id` (Revelio's internal employer ID — maps to firm)
- `location` (city; usually MSA-resolvable)
- `seniority_score` (Revelio-defined ordinal)
- `function` (audit / tax / advisory / risk-consulting / other)

For our pipeline, an "audit office" of firm `f` in city `c` and
year `t` is the set of person-spells with:
1. `company_id ∈ {firm f's audit-line entities}` (most Big 4
   structure their audit practice as a separate legal entity —
   maintain a hand-curated list).
2. `function = audit` (drop tax, advisory, risk to avoid
   contaminating the audit-side labour-market analysis).
3. `location` resolvable to MSA; map to the same MSA taxonomy
   used in `office_portfolio_panel.parquet` (Step 3 of the
   firm-to-office mapping methodology).
4. `start_date ≤ t < end_date` (active in month `t`).

Build the **Revelio office panel**:

```
data/cleaned/revelio/
├── revelio_person_spells.parquet      # raw, filtered to audit-firm spells
├── revelio_office_headcount.parquet   # firm × office × year-month panel
└── revelio_office_events.parquet      # join, leave, internal-move events
```

---

## 4. Outcome variables for Idea A

| Outcome | Definition (per office × year) | Notes |
|---|---|---|
| `net_hire_rate` | (Hires − Exits) / lagged headcount | Primary outcome |
| `voluntary_exit_rate` | Exits not preceded by office layoffs / exits-to-other-firm / 3-12 mo. | Distinguish quits from RIFs |
| `lateral_in_rate` | New joiners with ≥ 5 years prior Big 4 experience / lagged headcount | Reputation-attractiveness signal |
| `lateral_out_rate` | Exits to a different Big 4 office of a different firm / lagged headcount | Negative reputation signal |
| `internal_promotion_rate` | Title changes upward (mgr → SM → director → partner) / eligible lagged headcount | Internal-labour-market signal |
| `partner_promotion_rate` | Promotions into partner / lagged senior-manager headcount | Apex of internal-labour signal |
| `industry_specialist_share` | Share of new hires whose prior employment matches the office's modal industry | Skill-reallocation signal |
| `tenure_distribution_shift` | Δ in median tenure of active workforce | Aging or rejuvenation |
| `glassdoor_rating_delta` | Δ rating year-over-year | Independent validation channel |

All outcomes are computed at the
`(audit_firm, office_msa, calendar_year)` cell.

---

## 5. Outcome variables for Idea B

For Idea B (cross-office spillovers), the outcomes are computed
at the **non-deficient** office — i.e., siblings of an exposed
office. The same Revelio variables in §4 apply, but the analytic
focus shifts to `internal_promotion_rate`, `industry_specialist_share`,
and `lateral_in_rate` (as the firm reallocates talent toward
quality-assurance / industry-specialist roles in response to
deficiencies elsewhere).

Add for Idea B:

| Outcome | Definition |
|---|---|
| `cross_office_lateral_rate` | Within-firm lateral moves *into* a sibling office from the deficient office (proxy for internal QC discipline) |
| `training_certification_rate` | Share of office headcount earning a CPE / specialty certification in the year (Revelio captures self-reported certifications) |

---

## 6. Validation against the Form AP × Audit Analytics crosswalk

The partner-office crosswalk (Step 2 of the firm-to-office mapping
methodology) assigns each engagement partner to a single office
based on their modal-city engagement portfolio. Revelio offers an
independent signal: the partner's most recent
`location` field on their public LinkedIn profile.

Validation procedure:
1. For each partner-year in `partner_office_assignment.parquet`,
   look up the matching Revelio person-spell (by name + employer
   + tenure window).
2. Compare the assignment-derived office (from Form AP × Audit
   Analytics) to the Revelio-derived office.
3. Pre-registered acceptance threshold: ≥ 90% match rate at
   MSA granularity.
4. Below that, audit the mismatches: hand-coded sample of 100
   discrepancies; classify as data-quality issue vs. genuine
   remote-work case.

The match rate itself becomes a Table 1 statistic in the paper
("our office assignments match independent LinkedIn-derived
location in X% of cases").

---

## 7. Operational notes

- **Refresh cadence**: Revelio updates monthly; settle on a
  cut-off date for the analysis sample (e.g., last full month
  before submission).
- **De-identification**: spells include hashed person-IDs;
  do not attempt to de-anonymise. Aggregate-only analysis
  satisfies Revelio TOS.
- **Storage**: full audit-firm spell panel is ~10–30 GB in
  parquet. Partition by `(audit_firm_id, year)` for efficient
  filtering with polars / duckdb.
- **Compute**: workforce-event aggregations are linear in
  spell count and trivially parallelisable; no GPU required.

---

## 8. Files produced

```
data/cleaned/revelio/
├── revelio_person_spells.parquet      # Filtered to audit-firm spells
├── revelio_office_headcount.parquet   # Monthly panel
├── revelio_office_events.parquet      # Hire / exit / move events
└── revelio_validation.parquet         # Office-assignment match rates
```

---

## 9. Open operational questions

1. Confirm Revelio delivery format: WRDS-mounted cube (clean,
   queryable via duckdb) vs. parquet snapshot drops vs. API.
2. Confirm coverage of the partner-track seniority tier — is
   there a known under-coverage of partners who joined pre-2010?
3. Lead-time on requesting historical snapshot extracts (some
   Revelio products are extract-on-request).
4. License terms for downstream replication: can the parquet
   snapshots ship with the replication package (probably no),
   or only the regression-ready aggregates (probably yes)?
