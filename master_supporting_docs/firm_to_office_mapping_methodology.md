# Methodology — Mapping Audit-Firm Inspection Findings to Audit Offices

**Status:** design (pre-implementation)
**Applies to:** Ideas A, B, and any future office-level paper
**Last updated:** 2026-04-29
**Owner:** Oliver

---

## 1. The problem

PCAOB inspection reports are issued at the **audit firm** level
(Big 4 nationally, mid-tier nationally). The reports describe
deficiencies *qualitatively* in Part I.A as "Issuer A," "Issuer B,"
etc., never naming the issuer or the engagement office. By statute
(SOX §104(g)(2)), the PCAOB will never release issuer or partner
identities for inspected engagements.

Yet the **mechanisms** in Ideas A and B operate at the **audit
office** level: hiring, retention, partner promotion, internal-QC
discipline, and reputation effects are all locally instantiated. A
KPMG inspection finding narrated about energy-industry revenue
recognition affects KPMG Houston (an energy hub) far more than
KPMG Boston.

We therefore need an **office-level exposure measure** built from
public + subscription data alone. This document specifies the
construction, validation, and known limitations of that measure.

---

## 2. Inputs

| # | Source | Unit of observation | Used to derive |
|---|---|---|---|
| 1 | PCAOB inspection reports (PDFs) | Audit firm × inspection year | Deficiency narratives + structured exposure profile (industry × area × severity) |
| 2 | Form AP (PCAOB) | Issuer audit × engagement partner | Audit firm × partner × issuer × fiscal year-end |
| 3 | Audit Analytics (WRDS) | Issuer × audit firm × fiscal year | Auditor city/office + fees + restatements + ICFR opinions |
| 4 | Compustat (WRDS) | Issuer × year | Industry (SIC), size, complexity controls |
| 5 | Revelio Labs | Person × employer × month | Independent office membership signal (city tag) and outcomes for Ideas A, B |

All data are public or subscription-accessible; no proprietary
PCAOB feed is required.

---

## 3. Pipeline overview

```
PCAOB PDFs ─────► Step 4: deficiency profile (firm × year × industry × area × severity)
                       │
Form AP ────┐          │
            ├─► Step 2: partner-office crosswalk
Audit       │          │
Analytics ──┘          ▼
                  Step 3: office × client portfolio panel
                       │
                       ▼
                  Step 5: office-level exposure
                       │       Exposure(o, t) = Σ Deficiency(f,t,i,a) × PortfolioShare(o,t-1,i,a)
                       ▼
                  Step 6: validation
                       │
                       ▼
            Used as continuous treatment in Ideas A and B
```

---

## 4. Step-by-step procedure

### Step 1 — Ingest PCAOB inspection reports

**Inputs:** all annual inspection-report PDFs for each registered
audit firm, 2004 onward (pcaobus.org).

**Procedure:**
1. Scrape the PCAOB inspection-reports index page; collect PDF URLs
   for every (audit firm × inspection year). Store metadata
   (firm, PCAOB-ID, year, release date) in
   `data/raw/pcaob/inspection_index.parquet`.
2. Download PDFs to `data/raw/pcaob/reports/{firm_id}/{year}.pdf`.
3. Extract text from each PDF using `pdfplumber` (preferred for
   Part I tabular structure) and `pymupdf` as a fallback.
4. Use a section-detection regex to split into Part I.A, Part I.B,
   Part I.C, Part II, Appendices.
5. Store extracted sections as
   `data/cleaned/pcaob/inspection_sections.parquet` with columns
   `[firm_id, year, release_date, part, deficiency_id,
   raw_text, page_start, page_end]`.

**Quality checks:**
- Reconcile counts in Part I.A narrative against the cover-page
  aggregate ("X engagements reviewed, Y with deficiencies"). Flag
  cases where extracted-narrative count diverges by more than 10%.
- Random sample of 50 narratives per firm per year manually
  verified against the PDF.

**Tools:** `requests`, `pdfplumber`, `pymupdf`, `polars`.

---

### Step 2 — Build the partner-to-office crosswalk

**Inputs:** Form AP raw file, Audit Analytics audit-firm panel.

**Procedure:**
1. Load the Form AP CSV (refreshed annually). Columns of interest:
   `audit_firm_pcaob_id`, `engagement_partner_id`,
   `engagement_partner_name`, `issuer_cik`, `fiscal_period_end`,
   `other_audit_firms_participating`.
2. Load Audit Analytics auditor-engagement panel. Columns of
   interest: `auditor_pcaob_id`, `client_cik`, `fiscal_year_end`,
   `auditor_office_city`, `auditor_office_state`,
   `auditor_office_country`, `audit_fees`.
3. Join Form AP to Audit Analytics on
   (`audit_firm_pcaob_id` × `issuer_cik` × `fiscal_period_end`).
   Match rate target ≥ 95% post-2017 (when Form AP became
   mandatory).
4. For each `(engagement_partner_id, year)`, compute the **modal
   office city** weighted by audit-fee dollars across that
   partner's engagements. Store as
   `partner_office_assignment.parquet` with columns
   `[partner_id, year, audit_firm_id, office_city, office_state,
   modal_share, n_engagements_in_modal, total_n_engagements]`.
5. Apply the **purity threshold**: a partner-year is counted as
   "office-assigned" if `modal_share ≥ 0.7`. Below threshold,
   tag as `multi-office` and record both top-2 cities. Carry
   `multi-office` partners through the rest of the pipeline with
   weighted contributions to each office (not as a single
   assignment).
6. Within each office, define the **partner roster** as the set
   of partner-years assigned to that office. The roster is the
   primary unit at which we observe internal labour-market
   dynamics.

**Outputs:**
- `data/cleaned/crosswalk/partner_office_assignment.parquet`
- `data/cleaned/crosswalk/office_partner_roster.parquet`
  (firm × office × year → list of partner_ids and weights)

**Quality checks:**
- Partner-year purity distribution: histogram of `modal_share`.
  Expect a heavy right tail (most partners purely in one office).
  If <60% have purity ≥ 0.9, investigate.
- Stability check: partner office assignments should be stable
  year-over-year. A partner moving cities is rare and meaningful;
  flag for the `lateral_move` outcome variable used in Idea A.
- Cross-validate against Revelio Labs: the partner's
  `most_recent_location` in Revelio should match the
  modal-city assignment in ≥ 90% of cases. If not, audit the
  mismatches — could indicate either (a) a Form AP / Audit
  Analytics data-quality issue or (b) a partner who works remotely
  from a different city than their engagement office.

**Tools:** `polars` (lazy joins), `duckdb` (windowed aggregations),
`pandas` (final tabular outputs).

---

### Step 3 — Build the office × client portfolio panel

**Inputs:** Audit Analytics, Compustat, partner-office crosswalk.

**Procedure:**
1. For each `(audit_firm, office, fiscal_year)` cell, enumerate
   the set of issuer-clients audited by that office. An engagement
   is assigned to an office if its lead engagement partner is
   assigned to that office (Step 2).
2. Pull each issuer's industry classification from Compustat
   (`sich` first; fallback to `gsubind` for finer granularity).
   Map to research-relevant industry buckets (energy, financials,
   tech, healthcare, manufacturing, utilities, etc.) using a
   hand-curated SIC-to-bucket map at
   `master_supporting_docs/sic_industry_buckets.csv` (to be built).
3. Pull each issuer's account-area exposure from Audit Analytics:
   indicators for material-weakness areas, restatement-prone
   accounts (revenue, allowance for loan losses, fair value,
   business combinations, ICFR), going-concern flags. This forms
   the **account-area vector** for each engagement.
4. Aggregate to office level: for each
   `(audit_firm, office, year)`, compute
   `PortfolioShare(o, t, i, a)` = share of office's total audit
   fees coming from clients in industry `i` × account area `a`.
   Use audit fees (not engagement count) so larger engagements
   weigh proportionally.

**Output:**
- `data/cleaned/office/office_portfolio_panel.parquet`
  with columns
  `[audit_firm_id, office_city, year, industry_bucket,
  account_area, portfolio_share, total_audit_fees,
  n_engagements]`.

**Quality checks:**
- For each Big 4 office × year, total `portfolio_share` across
  industries × areas should sum to 1 (within rounding).
- Office size (total fees) distribution: identify and document
  the long tail. Drop offices below a size floor (e.g., < $5M
  in audit fees / year, < 5 issuer-clients) for the main analysis.
- Coverage: for the Big 4, expect ~50–80 distinct offices
  per year per firm. For mid-tier, expect 10–30.

---

### Step 4 — Encode deficiency narratives

**Inputs:** `inspection_sections.parquet` (Part I.A only for the
main exposure measure; Part I.B and Part II as severity-tier
indicators).

**Procedure:**
1. For each Part I.A deficiency narrative, run two parallel
   classifiers:
   - **Industry classifier**: a small fine-tuned encoder (or LLM
     few-shot with exemplars) outputting a probability vector
     over the same industry buckets used in Step 3. Train/few-shot
     on ~200 manually-coded narratives drawn from a stratified
     sample across firms and years.
   - **Account-area classifier**: same architecture, output is a
     probability vector over the account-area taxonomy used in
     Step 3 (revenue, ICFR, fair value, allowance for credit
     losses, business combinations, journal entries, etc.). The
     categories follow Acito, Hogan, & Imdieke (2019) plus the
     extensions Drake, Goldman, Lusch, & Schmidt (2024) propose.
2. For each narrative produce
   `(industry_prob_vector, area_prob_vector, severity_tier)`,
   where `severity_tier ∈ {I.A, I.B, II_unremediated, II_initial}`.
3. Aggregate across deficiencies per `(audit_firm, year)`:
   `DeficiencyProfile(f, t, i, a) =`
   sum over narratives `n` of
   `severity_weight(n) × P(industry = i | n) × P(area = a | n)`.

**Severity weights (initial calibration, pre-registered):**
- Part I.A: 1.0 (baseline)
- Part I.B (independence): 0.5
- Part II initial disclosure: 2.0 (Acito et al. 2019 evidence)
- Part II unremediated public: 3.0

**Output:**
- `data/cleaned/pcaob/deficiency_profile.parquet` with
  `[audit_firm_id, year, industry_bucket, account_area,
  weighted_intensity]`.

**Quality checks:**
- Inter-coder agreement on the 200-narrative training set
  (Cohen's κ ≥ 0.7 on industry; ≥ 0.6 on area).
- Validate classifier on a held-out sample of 100 narratives
  not seen during training/few-shot prompting.
- Compare to keyword-baseline (Acito et al. 2019 dictionary):
  embedding-based classifier should outperform keyword baseline
  on F1 by ≥ 5 points (this is also the contribution of Idea E,
  which formalises the comparison).

---

### Step 5 — Compute office-level exposure

**Inputs:** `office_portfolio_panel.parquet`,
`deficiency_profile.parquet`.

**Procedure:**
For each `(audit_firm, office, inspection_year)` triple,
compute:

```
Exposure(o, t) = Σ_i Σ_a  DeficiencyProfile(f, t, i, a)
                          × PortfolioShare(o, t-1, i, a)
```

where `f` is the office's audit firm, and `PortfolioShare` is
**lagged one year** to (a) avoid simultaneity with any anticipatory
behaviour and (b) reflect the portfolio composition the PCAOB
inspectors most plausibly observed.

**Variants for robustness:**
- **Binary exposure**: indicator that
  `Exposure(o, t) > median{Exposure(·, t)}` within firm-year.
- **Quantile-based**: top tercile / quartile within firm-year.
- **Industry-only exposure**: collapse over `a`.
- **Area-only exposure**: collapse over `i`.
- **Severity-stratified**: separate Part I.A vs Part II exposures.

**Output:**
- `data/cleaned/exposure/office_exposure_panel.parquet`
  with `[audit_firm_id, office_city, inspection_year, exposure,
  exposure_binary, exposure_tercile, exposure_industry_only,
  exposure_area_only, exposure_partII]`.

---

### Step 6 — Validate the exposure measure

The exposure measure must clear three validation hurdles before
being used as a treatment variable.

**Validation 1 — Audit-quality concordance.** Higher-exposure
offices should exhibit higher subsequent restatement rates among
their clients. Run a simple OLS at the office-year level:

```
RestatementRate(o, t+k) = α + β · Exposure(o, t)
                          + δ · X(o, t) + γ_f + γ_t + ε
```

for `k = 1, 2, 3`. β > 0 with reasonable significance is the
sanity check (Acito et al. 2019 logic). Document the magnitude.

**Validation 2 — Fee response.** Prior literature (Acito et al.
2019; DeFond & Lennox 2017) finds fee responses to inspection
findings. Replicate at the office level:
exposed offices should show audit-fee changes around inspection-
report release.

**Validation 3 — Independent corroboration via SEC enforcement.**
A small set of SEC AAERs explicitly identify the auditor and audit
office of the failed engagement. For these cases (manually coded),
the office should have high computed exposure for the relevant
year. Build a confusion matrix.

**Validation 4 — Revelio cross-check.** Aggregate Revelio's
Glassdoor rating change and audit-firm-rated review-volume change
by office × year. Higher-exposure offices should show:
- Lower Glassdoor rating in the year after inspection (modest effect),
- Higher review volume (proxy for elevated employee activity).

This is *not* a circular validation — Glassdoor signal is
independent of the audit-quality outcomes used in Validation 1.

---

## 5. Decisions and pre-registered choices

| Decision | Choice | Rationale |
|---|---|---|
| Treat Part I.A only as primary | Yes | Most consistent disclosure across years; Part I.B/I.C/II as robustness |
| Lag portfolio share by 1 year | Yes | Avoid simultaneity; reflect what inspectors observed |
| Exposure functional form | Continuous (primary), binary (robustness) | Power vs. interpretability trade-off |
| Office identifier | Audit Analytics city × firm | Standard in literature (Beck, Gunn, & Hallman 2019) |
| Partner-office assignment | Modal city, fee-weighted, ≥ 0.7 purity | Hu, Smith, & Wong (2025); Lee, Lee, & Pittman (2021) |
| Sample period | 2007–latest (so all firms have ≥ 1 inspection cycle pre-2017) | Power and pre-period balance |
| Form AP era subset | 2017+ for partner-level robustness | Limited but cleanest |
| Industry taxonomy | ~12 buckets aligned to PCAOB narrative vocabulary | Trade-off granularity vs. coding cost |
| Account-area taxonomy | ~10 categories per Acito et al. 2019 + Drake et al. 2024 | Consistency with prior literature |

---

## 6. Known limitations

1. **Pre-2017 partner identification is imperfect**. Form AP
   started 31 January 2017. For 2003–2016, partner-office
   assignment relies on alternative sources (state-board
   licensure, Audit Analytics partner-name fields where
   populated, hand-collected from prior literature). Document
   measurement-error assumptions; expect attenuation bias.

2. **Issuer non-identification in narratives is binding**. Even
   with perfect industry/area classification, the office that
   ran the deficient engagement is unobserved — so exposure is
   probabilistic, not certain. This is intrinsic to the setting.

3. **Big 4 dominance**. The Big 4 account for ~65% of public-
   issuer audits but receive the lion's share of inspections.
   Mid-tier identification is weaker; pre-register Big-4-only
   main analysis and treat mid-tier as heterogeneity.

4. **Office redefinition over time**. Big 4 firms occasionally
   merge or split offices. Document each restructuring and
   maintain a stable office identifier across the panel
   (e.g., MSA-based).

5. **PDF extraction error**. ~5% of older reports have extraction
   issues (scanned, multi-column, footnote spillover). Manual
   review of low-confidence narratives.

---

## 7. Files produced

```
data/cleaned/
├── pcaob/
│   ├── inspection_index.parquet
│   ├── inspection_sections.parquet
│   └── deficiency_profile.parquet
├── crosswalk/
│   ├── partner_office_assignment.parquet
│   └── office_partner_roster.parquet
├── office/
│   └── office_portfolio_panel.parquet
└── exposure/
    └── office_exposure_panel.parquet
```

Pipeline driver scripts (to be written) live under
`scripts/python/pipeline/`:
- `01_pcaob_scrape.py`
- `02_pcaob_extract.py`
- `03_form_ap_load.py`
- `04_audit_analytics_load.py`
- `05_partner_office_crosswalk.py`
- `06_office_portfolio.py`
- `07_deficiency_classifier.py`
- `08_office_exposure.py`
- `09_validation.py`

Each script is idempotent (re-runnable), reads upstream parquet,
and writes its own parquet output. The pipeline is orchestrated
either via a top-level `make pipeline` target or via the clo-author
`/analyze` skill once the data engineer agent is invoked.

---

## 8. Reuse across papers

| Paper | Which exposure variant | Modifications |
|---|---|---|
| Idea A (workforce strategy) | `exposure` continuous + `exposure_industry_only` for heterogeneity | None |
| Idea B (cross-office spillover) | Treated office: `exposure`; sibling office: 0 (or low). | Define "treated office" set per inspection cohort; sibling = same firm, different office, low exposure |
| Idea D (audit-committee networks) | Mostly firm-level; office variant as robustness | Limited use |
| Idea E (LLM textual mining) | The deficiency-classifier output is itself the contribution | Refines Step 4 |

Idea C (EDGAR information spillovers) does **not** use this
pipeline beyond Step 1 (the inspection-report ingestion) and
Step 4 (the industry classifier). Office mapping is irrelevant
to the EDGAR co-search mechanism.

---

## 9. Anchors in prior literature

- **Acito, Hogan, & Imdieke (2019, *TAR*)** — keyword-based
  deficiency classification, fee response.
- **Drake, Goldman, Lusch, & Schmidt (2024, WP)** — topic-model
  classification of inspection content.
- **Hu, Smith, & Wong (2025, *JBFA*)** — partner-office assignment
  via Form AP × LinkedIn (200,708 profiles).
- **Lee, Lee, & Pittman (2021, *TAR*)** — auditor labour-market
  structure; office-level identification.
- **Beck, Gunn, & Hallman (2019, *CAR*)** — geographic
  decentralisation of audit firms.
- **Burke, Hoitash, & Hoitash (2019, *AJPT*)** — audit partner
  identification from Form AP.
- **Lamoreaux, Mowchan, & Zhang (2023, *TAR*)** — spillover
  framework (cross-firm; we adapt to within-firm in Idea B).

All entries are in `Bibliography_base.bib`.

---

*End of methodology document. Updates appended below as choices
resolve in implementation.*
