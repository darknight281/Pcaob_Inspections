# Plan — Idea A Scoping: Office-Level Workforce-Strategy Responses to PCAOB Inspection Deficiencies

**Date:** 2026-04-29
**Author:** Oliver
**Status:** scoping (pre-discovery; depends on the firm-to-office mapping pipeline)
**Sequencing:** third paper (after Idea C, Idea E)
**Source documents:**
- `master_supporting_docs/PCAOB_Inspection_Research_Discussion_Notes_v1.md` §4.1, §5, §6.2
- `master_supporting_docs/firm_to_office_mapping_methodology.md`
- `master_supporting_docs/revelio_labs_integration.md`

---

## Context

When an audit firm receives a notable Part I.A deficiency narrated
about a particular industry × account-area combination, the firm's
offices with the highest *exposure* to that deficiency
(industry-specialised, large portfolio share) face an internal
labour-market shock. Reputation among employees is locally
instantiated: the manager-level accountant in KPMG Houston with
energy-industry specialisation now works at an office whose
energy practice was just publicly criticised. They have outside
options.

The contribution: position PCAOB inspections as **labour-market
shocks internal to audit firms**, not just engagement-quality
shocks. This complements the audit-quality channel established by
Acito, Hogan, & Imdieke (2019), Aobdia (2019), and Cao et al.
(2025), and extends the disclosure-as-labour-signalling framework
of Roh (2026, *TAR*) into the labour-intensive professional-
services setting.

---

## Research question

When an audit firm receives a notable Part I.A deficiency
narrative concentrated in industry `i` and account-area `a`, do
that firm's offices with high exposure to `(i, a)` change their
workforce strategy more than low-exposure offices of the same
firm — specifically:

1. Net hiring rate
2. Voluntary exit rate (with industry / firm destination)
3. Internal promotion rate (entry-level → senior → partner)
4. Lateral inflows (mid-career hires from competitor Big 4 offices)
5. Industry-specialist composition shift among new hires
6. Glassdoor rating dynamics (independent disclosure-as-signal channel)

---

## Identification design

| Element | Choice |
|---|---|
| Treatment | Continuous office-level **exposure intensity** (firm-to-office mapping methodology, Step 5) |
| Treatment timing | PCAOB inspection-report release date (calendar quarter resolution) |
| Outcome unit | Audit firm × office (MSA) × year |
| Outcome panel | 2007–latest; Big 4 main, mid-tier robustness |
| Estimator | Stacked DiD with cohort = (audit firm × inspection year); within-cohort estimator: Callaway-Sant'Anna (2021) or Sun-Abraham (2021) |
| Control offices | Same audit firm, low-exposure offices for the same cohort (clean within-firm comparison); plus matched offices of *other* firms in the same MSA (cross-firm comparison) |
| Pre-trend test | Standard Goodman-Bacon (2021) decomposition + event-study leads |

The *same audit firm, low-exposure office* comparison is the
preferred design because it differences out firm-wide reputation
shocks, partnership-policy changes, and macroeconomic conditions.

The *matched cross-firm* design is the robustness check —
addresses the concern that within-firm comparisons may
under-estimate effects if low-exposure siblings also respond
(which is precisely the question of Idea B).

### Why office-level (not firm-level)

Per the unit-of-analysis discussion in research-notes §6.2:
hiring, retention, and promotion happen at offices. A KPMG energy-
industry deficiency may strongly affect KPMG Houston (energy hub)
but barely touch KPMG Boston. Aggregating to firm-level averages
across exposed and unexposed offices, destroying the mechanism.

### Why exposure (not binary inspection indicator)

Inspection occurs at the firm level on a fixed cycle (annually
for Big 4) — a binary "inspected vs not" indicator has no
within-Big-4 cross-sectional variation. The continuous exposure
measure exploits the fact that *which* areas were criticised
varies across years and across firms, and *which* offices are
most aligned with those areas varies cross-sectionally.

---

## Step-by-step plan

### Phase 1 — Data foundation (months 1–4)

1. **Build the firm-to-office mapping pipeline** as documented in
   `master_supporting_docs/firm_to_office_mapping_methodology.md`.
   Steps 1–6 inclusive. This is the foundation for both Idea A
   and Idea B.
2. **Build the Revelio panel** as documented in
   `master_supporting_docs/revelio_labs_integration.md`. Outcome
   variables for §4 of that document.
3. **Validation table 1**: office-assignment match rate between
   the Form AP × Audit Analytics modal-city assignment and the
   Revelio LinkedIn most-recent-location field. Pre-registered
   acceptance: ≥ 90%.
4. **Validation table 2**: exposure-measure validity checks
   (Step 6 of the mapping methodology).

### Phase 2 — Pre-analysis design (month 4–5)

5. **Pre-register** the analysis plan via a working-paper-format
   document under `paper/sections/` and a parallel pre-analysis
   plan in `quality_reports/specs/`. Pre-registration covers:
   - Sample (Big 4, 2007+, MSA-resolvable offices, ≥ 5 issuers)
   - Treatment (continuous exposure; binary as robustness)
   - Primary outcomes (1–4 from research question)
   - Secondary outcomes (5–6)
   - Estimator (Callaway-Sant'Anna stacked DiD with bootstrap SEs)
   - Heterogeneity analyses (3 declared in advance)
   - Robustness (5 declared in advance)

6. **Heterogeneity declarations:**
   - Big 4 vs mid-tier (different inspection cycles)
   - Densely-populated MSAs (NYC, Chicago, LA — thick labour
     markets, more outside options) vs thin MSAs (Houston,
     Atlanta — thinner labour markets)
   - Industry-specialist offices (where the deficiency hits the
     office's specialty hardest, measured by lagged
     `portfolio_share` in the deficient `(i, a)`) vs generalist

7. **Robustness declarations:**
   - Oster (2019) bounds for unobserved selection
   - Alternative exposure functional forms (binary, terciles,
     industry-only)
   - Placebo using random reassignment of deficiencies to firms
     (preserve firm × year structure, randomise which `(i, a)`
     was the deficiency)
   - Pre-2017 vs 2017+ subsample (Form-AP era split)
   - Drop offices that closed / opened during the panel

### Phase 3 — Estimation (months 5–8)

8. **Main specification**: stacked DiD by inspection-year cohort.
   For each cohort `c`, define:
   ```
   Y(o, t) = α + Σ_τ β_τ · Exposure(o, c) · 1{t = c + τ}
                + γ_o + γ_(c,t) + ε_(o, c, t)
   ```
   where `τ ∈ {-3, -2, -1, 0, 1, 2, 3}` (no t = -1 baseline),
   `γ_o` is office fixed effects, `γ_(c,t)` is cohort-by-time
   fixed effects.
9. **Bootstrap SEs** clustered at the audit-firm × MSA level
   (the unit at which exposure varies); 1,000 reps.
10. **Event-study plots** for each primary outcome: visualise
    `β_τ` with 95% confidence bands. Pre-trends should be flat;
    treatment effects should emerge in `τ ∈ {1, 2, 3}`.
11. **Heterogeneity** via interactions in stacked DiD.
12. **Robustness battery** as pre-registered.

### Phase 4 — Mechanisms and writing (months 8–12)

13. **Mechanism evidence**: which response channels are most
    active?
    - If exits dominate: deficiency-induced reputation shock.
    - If lateral-in dominates: rivals poach exposed-office talent.
    - If internal promotion accelerates: firm reallocates talent
      to manage capacity / reputation.
    - If specialist composition shifts: skill-reallocation
      response.
    These are not mutually exclusive; the relative magnitudes
    inform the framing.
14. **Roh (2026) framing**: position the contribution as
    "labour-intensive professional services where labour *is*
    the production technology, with regulatory shocks as
    arguably more exogenous than market-driven entries."
    Two paths:
    - **Aggressive framing**: Roh as featured reference; my
      contribution = applying the labour-market disclosure
      framework to a setting where the framework's mechanism
      is first-order. Easier publication if Roh continues to
      receive attention.
    - **Conservative framing**: Roh as methodological cite; my
      contribution = audit-specific mechanisms (internal QC,
      regulatory exogeneity, partner labour-market structure).
      Lower citation risk if Roh is later contested.
    Decision: defer to first-draft stage; pick based on
    co-authors' read of Roh's reception (research-notes §8 Q3).
15. **Write-up** following clo-author working-paper format.
    `/write` skill drafts; `/review` runs the writer-critic;
    `/review --peer JAR` simulates initial referee report.

### Phase 5 — Submission targeting

Pre-registered target journals (in priority order):
1. *The Accounting Review* (TAR) — natural fit; Roh (2026) is a
   *TAR* paper, signalling editor receptivity.
2. *Journal of Accounting Research* (JAR) — credibility-revolution
   referee culture aligns with stacked-DiD methodology.
3. *Contemporary Accounting Research* (CAR) — broad audit-research
   audience.

`/submit packaging --target tar` runs the editor desk-review
simulation against TAR's journal profile. Address simulated
referee comments with `/revise` cycles before any actual
submission.

---

## Data needs (consolidated)

1. **PCAOB inspection reports** — free, scraped (firm-to-office
   mapping methodology Step 1).
2. **Form AP** — free, downloaded (Step 2).
3. **Audit Analytics** — WRDS subscription, available
   (Steps 2–3).
4. **Compustat** — WRDS subscription, available (Step 3 + controls).
5. **Revelio Labs** — subscription, available (primary outcomes —
   `revelio_labs_integration.md`).
6. **(Optional) Lightcast / Burning Glass** — alternative
   measure of office hiring intent via job-posting volume.

No further access negotiations required.

---

## Variables (consolidated)

### Treatment

- `Exposure(o, t)`: continuous; from `office_exposure_panel.parquet`.
- `Exposure_industry_only(o, t)`, `Exposure_area_only(o, t)`:
  alternative aggregations.
- `Exposure_partII(o, t)`: severity-stratified.

### Outcomes (primary)

From `revelio_office_headcount.parquet` and
`revelio_office_events.parquet`:

- `net_hire_rate(o, t)`
- `voluntary_exit_rate(o, t)` — distinguish quits from RIFs
- `internal_promotion_rate(o, t)`
- `partner_promotion_rate(o, t)`
- `lateral_in_rate(o, t)`
- `industry_specialist_share(o, t)`

### Outcomes (secondary)

- `glassdoor_rating_delta(o, t)` (independent disclosure channel)
- `tenure_distribution_shift(o, t)`
- `posting_volume(o, t)` (Lightcast — alternative hiring intent)

### Controls

Office-level: lagged headcount, lagged audit fees, MSA fixed
effects, audit-firm fixed effects.
Year-level: cohort fixed effects (in stacked DiD).

---

## Cross-sectional moderators

1. **Big 4 vs mid-tier** — pre-registered (different inspection
   cycles).
2. **Thick vs thin MSA labour market** (number of competing Big
   4 offices in MSA).
3. **Industry-specialist offices** (high pre-period
   `portfolio_share` in the deficient industry).
4. **Educational pipeline overlap** (Lee, Lee, & Pittman 2021
   logic — same feeder universities → tighter labour-market
   competition between offices).

---

## Open questions before discovery sprint

1. **Exposure measure validation**: does the Step 6 sanity check
   pass at sufficient power? Resolve before pre-registering the
   main specification.
2. **Sample size**: with ~50 Big-4 offices × 4 firms × 17 years
   = ~3,400 office-years, is power adequate for the
   heterogeneity tests? Run a power simulation in Phase 1.
3. **Glassdoor / Lightcast data licensing**: can these be merged
   in, and does the merged-key (company × MSA) match Revelio's
   resolution?
4. **Roh (2026) framing decision**: aggressive or conservative —
   defer to first-draft.
5. **Co-authorship**: does this paper invite Cam (governance/
   labour) or Ahmed (audit) as co-author? Decide before
   `/discover` to scope the literature review accordingly.
6. **Pre-2017 partner-office assignment**: how much of the
   pre-Form-AP period is salvageable for the main analysis?
   A key sensitivity that determines whether the panel starts
   in 2007 or 2017.

---

## Immediate next action

Two actions can run in parallel because Idea A is the third paper
in the sequence. Treat them as **upstream infrastructure that also
serves Idea B and any future office-level paper**:

1. Begin **Phase 1.1**: PCAOB inspection-report scrape and PDF
   extraction (`scripts/python/pipeline/01_pcaob_scrape.py`,
   `02_pcaob_extract.py`). Independent of Revelio access.

2. Begin **Phase 1.2**: Revelio Labs sample request — confirm
   delivery format, request the audit-firm subset. While waiting,
   write the panel-construction code skeleton against the
   documented schema in `revelio_labs_integration.md`.

When the foundation is ready (estimated: 4 months in elapsed
time with both Idea C and Idea E running in parallel), invoke:

```text
/discover literature "Office-level workforce-strategy responses to PCAOB inspection deficiencies. Position relative to: Roh (2026, TAR); Hu, Smith, & Wong (2025, JBFA); Lee, Lee, & Pittman (2021, TAR); Aobdia (2019, TAR); Beck, Gunn, & Hallman (2019, CAR); Krishnan, Krishnan, & Song (2025, JAR)."
```

---

## Sequencing constraint

Idea A is **paper three** in the sequence. Phase 1.1 and Phase
1.2 are upstream of Ideas A *and* B and can begin immediately —
they produce the firm-to-office mapping pipeline that both papers
rely on. Estimation and writing for Idea A should not begin until
Idea C is at least at submission stage and Idea E has produced
the validated deficiency classifier (which feeds Step 4 of the
mapping methodology).

---

*End of scoping plan. Updates appended below as decisions resolve.*
