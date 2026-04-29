# Plan — Idea B Scoping: Cross-Office Spillovers Within Big 4 Networks

**Date:** 2026-04-29
**Author:** Oliver
**Status:** scoping (pre-discovery; depends on the firm-to-office mapping pipeline)
**Sequencing:** fourth paper (after Idea C, Idea E, Idea A)
**Source documents:**
- `master_supporting_docs/PCAOB_Inspection_Research_Discussion_Notes_v1.md` §4.2, §6.2
- `master_supporting_docs/firm_to_office_mapping_methodology.md`
- `master_supporting_docs/revelio_labs_integration.md`

---

## Context

Idea A asks: "if my office is exposed to a deficiency, how do I
respond?" Idea B asks the inverse: "if my **sibling** office
within the same audit firm is exposed, how do *I* respond — even
though my own engagements weren't criticised?"

The mechanism is internal-QC discipline + reputation transmission
+ partner-network learning. When KPMG Houston receives a high-
profile deficiency, the firm's central QC group typically rolls
out new procedures to *all* KPMG audit offices, the partnership
recalibrates training and review intensity firm-wide, and
inter-office partner-rotation patterns shift. Sibling offices —
without their own deficiency — should still respond.

This is the **within-firm analogue** of the cross-firm spillover
documented by Lamoreaux, Mowchan, & Zhang (2023, *TAR*) for
PCAOB enforcement. Together with their paper, Idea B maps the
two complementary spillover channels (within-firm office network
and cross-firm market network).

---

## Research question

When one office of a Big 4 firm `f` receives a high-profile
Part I.A or Part II deficiency, do **non-deficient** offices of
the same firm `f` — net of own-office exposure — increase audit
effort, fees, hiring, training, and partner-network engagement,
relative to matched offices of *other* Big 4 firms in the same
MSA?

---

## Identification design

| Element | Choice |
|---|---|
| Treated unit | Non-deficient office (low exposure) of an audit firm `f` that experienced a deficiency in *another* office. "Non-deficient" = bottom tercile of Exposure within firm-cohort. |
| Control unit | Matched office of a *different* Big 4 firm in the same MSA, with similar size, industry mix, and exposure history. |
| Treatment variation | Exists only across firms because all offices of the same Big 4 firm are exposed to the firm-wide spillover; the matched cross-firm design isolates the spillover from local-market effects. |
| Estimator | Stacked DiD by firm × deficiency-event cohort, with each firm's set of non-deficient offices treated together. Callaway-Sant'Anna weighting. |
| Pre-trend test | Standard event-study leads; bonus: a placebo cohort of "no-deficiency" firm-years should show null effects. |

### Identification logic

The threat: when KPMG Houston is criticised, KPMG's clients in
*all* offices may renegotiate fees, KPMG-trained staff may exit
to competitors, *and* market participants may reassess the
quality of all Big 4 audits — meaning Deloitte / PwC / EY
offices in the same MSA also adjust. The cross-firm matched-
control design addresses this:

- The **treated** comparison is non-deficient KPMG offices.
- The **control** comparison is matched Deloitte / PwC / EY
  offices in the same MSA, with similar lagged size, fees,
  industry mix, and (importantly) lagged exposure history.

The spillover-of-interest is what's *specific* to KPMG — the
within-firm internal-QC and reputation transmission channels —
above and beyond any local-market or aggregate effects that hit
all Big 4 in the same MSA.

### Why office-level (not firm-level)

The phrase "cross-office" is itself the question. There's no
firm-level analogue. Internal QC operates through office-
specific implementation; reputation transmission is partly
office-bounded (a partner in KPMG Boston has limited interaction
with engagements in KPMG Houston's energy practice).

---

## Step-by-step plan

### Phase 1 — Data foundation (shared with Idea A)

1. **Use the firm-to-office mapping pipeline output**
   (`master_supporting_docs/firm_to_office_mapping_methodology.md`,
   Steps 1–6) — already built for Idea A.
2. **Use the Revelio panel** — already built for Idea A.
3. Extend the Audit Analytics extract to include **fee variables**,
   **audit-lag**, **going-concern issuance rates**, **restatement
   rates** at the office × year level. These are the audit-quality
   outcomes that complement the workforce outcomes.

### Phase 2 — Define the treated and control sets (months 1–2)

4. **Identify deficiency cohorts**: for each (audit firm × year)
   inspection report that has at least one office with high
   exposure (e.g., top quartile within firm-year), the cohort
   year is `t = release date`.
5. **Treated set**: within each cohort, identify non-deficient
   offices of the same firm — bottom tercile of Exposure.
   These offices are *not* directly criticised but operate
   under firm-wide spillover.
6. **Control set**: match each treated office to up to 3 offices
   of *different* Big 4 firms in the same MSA, using:
   - Lagged total audit fees (within ±25%)
   - Lagged industry-mix cosine similarity (≥ 0.7)
   - Lagged headcount (within ±25%)
   - Lagged exposure history (no high-exposure events in the
     prior 3 years)

   Match via Mahalanobis distance or coarsened exact matching;
   document the matching procedure in the pre-analysis plan.

### Phase 3 — Pre-analysis design (month 2–3)

7. **Pre-register** the analysis plan covering:
   - Sample (Big 4 deficiency cohorts; matched controls)
   - Treatment definition (non-deficient office of deficient firm)
   - Primary outcomes
   - Secondary outcomes
   - Estimator
   - Heterogeneity (4 declared in advance)
   - Robustness (5 declared in advance)
   - Falsification tests

### Phase 4 — Estimation (months 3–6)

8. **Main specification**: stacked DiD by deficiency cohort.
   ```
   Y(o, t) = α + Σ_τ β_τ · Treated(o, c) · 1{t = c + τ}
                + γ_o + γ_(MSA, c, t) + δ · X(o, t-1) + ε
   ```
   Note `γ_(MSA, c, t)` — MSA × cohort × time fixed effects
   absorb local labour-market and macroeconomic shocks. The
   identifying variation is *within-MSA, within-cohort, between
   firms*.
9. **Bootstrap SEs** clustered at audit-firm × MSA level.
10. **Event-study plots** for each primary outcome.
11. **Heterogeneity** via interactions.
12. **Falsification battery** — see §Falsification.

### Phase 5 — Mechanism interpretation and writing (months 6–10)

13. **Distinguishing channels**:
    - **Internal QC channel**: if `training_certification_rate`
      and `restatement_rate(t+k)` move, internal QC is active.
    - **Reputation channel**: if `voluntary_exit_rate` (esp. to
      competing firms) and `glassdoor_rating_delta` move, the
      labour-market reputation effect dominates.
    - **Partner-network channel**: if changes are concentrated
      in offices whose partners had prior co-engagement history
      (traceable via Form AP) with the deficient office, the
      micro-network channel dominates.

14. **Connection to Lamoreaux et al. (2023)**: explicitly map
    the within-firm spillover (Idea B) to their cross-firm
    enforcement spillover. Frame as: "Lamoreaux et al. show that
    enforcement spills *across* firms; we show inspections spill
    *within* firms — together, the channels span the audit
    industry's spillover topology."

15. **Write-up** following clo-author working-paper format.

### Phase 6 — Submission targeting

Pre-registered target journals (in priority order):
1. *The Accounting Review* — Lamoreaux et al. (2023) is in
   *TAR*; sibling-paper editorial fit.
2. *Journal of Accounting Research*
3. *Contemporary Accounting Research*

---

## Outcomes

### Audit-quality outcomes (from Audit Analytics)

- `audit_fees(o, t)` — log changes
- `audit_lag(o, t)` — days from fiscal year-end to filing
- `going_concern_issuance_rate(o, t)`
- `restatement_rate(o, t+k)` for k = 1, 2, 3 (quality-improvement test)
- `icfr_adverse_opinion_rate(o, t)`

### Workforce outcomes (from Revelio)

Same as Idea A primary outcomes, with one addition unique to
Idea B:

- `cross_office_lateral_rate(o, t)` — internal moves from
  the deficient office to the non-deficient office
  (proxy for internal QC personnel reallocation)

### Network outcomes (from Form AP)

- `partner_co_engagement_with_deficient_office(o, t)` —
  share of office partners who in any prior year shared an
  engagement with a partner in the deficient office (proxy
  for direct partner-network exposure)

---

## Cross-sectional moderators (heterogeneity)

1. **Geographic proximity**: treated offices in the same MSA as
   the deficient office vs distant. Same-MSA effects should be
   stronger if local-network learning matters.
2. **Industry overlap**: treated office's industry-mix cosine
   similarity with the deficient engagement's industry. Higher
   overlap → stronger spillover.
3. **Partner-network ties**: treated office partners' prior co-
   engagement history with deficient-office partners (via Form
   AP). Stronger ties → stronger spillover.
4. **Big 4 internal structure**: variation in how each Big 4
   centralises QC (publicly observable via firm transparency
   reports) — moderate the within-firm spillover by firm-level
   QC centralisation.

---

## Falsification tests

These are essential for distinguishing within-firm spillover
from confounded local effects.

1. **Cross-firm placebo**: in the same MSA, in the same year,
   competing Big 4 firms' offices should *not* react to KPMG's
   deficiency. Construct a "placebo treatment" in which Deloitte
   offices are mis-coded as treated; effect should be null.
   This distinguishes within-firm spillover from
   Lamoreaux-Mowchan-Zhang-style cross-firm spillover.
2. **Industry mismatch placebo**: when KPMG receives an energy
   deficiency, KPMG offices that audit zero energy clients should
   show smaller responses than energy-specialist offices (and
   the contrast itself is a structural test).
3. **Pre-trend leads**: `β_{-2}, β_{-3}` should be null.
4. **No-event placebo cohorts**: years in which a firm received
   a routine inspection with no notable Part I.A deficiencies
   should produce null treatment effects.

---

## Data needs (consolidated)

Identical to Idea A; reuses the firm-to-office mapping pipeline
output and the Revelio panel. No additional access required.

---

## Open questions before discovery sprint

1. **Define "high-profile" deficiency**. Pre-register: top quartile
   of within-firm-year exposure intensity, OR Part II disclosure,
   OR press coverage above a threshold (Factiva mentions). Pick
   in pre-analysis plan.
2. **Match strength**. Run a balance table after matching;
   pre-register acceptance thresholds for covariate balance.
3. **Cross-firm spillover overlap with Lamoreaux et al. (2023)**.
   They study enforcement; we study inspections. Confirm with
   editor (or simulated peer-review) that the inspection variant
   is sufficiently distinct.
4. **Number of cohort-years**. With ~10 high-profile deficiency
   events × ~50 sibling offices × ~5 control offices each, the
   sample is ~2,500 office-years. Power simulation needed for
   detection thresholds.
5. **Co-authorship**: Idea B is a natural fit for Cam (governance/
   internal-control angle) or for the Lamoreaux et al. team
   (extension of their framework).

---

## Immediate next action

Idea B does **not** have its own immediate action — it shares the
upstream infrastructure with Idea A (Phase 1 of both plans is
identical). The first Idea-B-specific action is Phase 2 (define
treated and control sets), which should begin once the
firm-to-office mapping pipeline output is available and Idea A
has reached estimation stage (i.e., the design infrastructure is
debugged on Idea A first).

When ready, invoke:

```text
/discover literature "Cross-office spillovers within Big 4 networks from PCAOB inspection deficiencies. Position relative to: Lamoreaux, Mowchan, & Zhang (2023, TAR) on cross-firm enforcement spillovers; Acito, Hogan, & Imdieke (2019, TAR); Aobdia (2019, TAR); Lennox & Pittman (2010, JAE); Beck, Gunn, & Hallman (2019, CAR)."
```

---

## Sequencing constraint

Idea B is **paper four** in the sequence. The pipeline reuse with
Idea A is intentional — Idea A debugs the office-level
infrastructure on a within-firm comparison; Idea B then
generalises to the cross-firm matched-control design. Attempting
both in parallel is feasible but risks double-counting the data-
build effort and confusing the pre-registration commitments.

---

*End of scoping plan. Updates appended below as decisions resolve.*
