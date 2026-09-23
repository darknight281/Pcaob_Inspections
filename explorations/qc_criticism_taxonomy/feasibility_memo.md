# Feasibility Memo — Are PCAOB QC Criticisms Classifiable into Theoretically Distinct Types?

**Date:** 2026-09-23 · **Status:** ex-ante memo (written before any real Part II text was coded)
**Companion files:** `codebook.md` (coding rules), `taxonomy.yaml` (machine-readable codes),
`quality_reports/plans/2026-09-23_qc_criticism_classification_feasibility.md` (plan + go/no-go gates)

---

## 1. Bottom line (ex ante)

- **Classification is probably feasible at the level of 5–6 families.** PCAOB Part II prose is formulaic
  ("the firm's system of quality control does not provide reasonable assurance that …"). The object of that
  clause names *where* the QC system failed, which makes coding tractable. Three proofs of concept (§8):
  - Buslepp, DeLisle & Victoravich (2018, *MAJ*) split public Part II criticisms into audit-performance
    vs firm-management criticisms, and find different client responses by type.
  - Ragothaman (2012, symposium paper) compared 106 released QC reports with peer-review reports by QC
    element.
  - Aobdia (2020) split confidential QC deficiencies into performance-related and organisation-level ones.

  No study found uses a theory-based typology finer than two types, or links types to firm-side responses.
- **The main theoretical risk is text framing, not coder reliability.** The PCAOB describes *loci*
  (supervision, EQR, controls testing, independence) far more often than *mechanisms* (incentives, culture,
  capacity). Families defined by mechanism (Monitoring, Incentives & Culture) may therefore be thin in the
  public text even where they matter economically. The codebook records the stated locus and the stated
  root cause separately, so the pilot measures this risk directly.
- **The main inferential risk is selection.** Only criticisms a firm *failed* to remediate become public.
  In 2023 the Board made remediation determinations on 92 reports, about 60% of them satisfactory, per the
  PCAOB inspection Spotlight as reported in secondary sources. Type frequencies in the public sample are
  therefore incidence × P(not remediated | type). This is a feature for a response paper (it is the
  remediation-failure margin) but a bug for any claim about how common each type is.

## 2. The data-generating process

- Part II of an inspection report (QC criticisms) is non-public at issuance. Under SOX §104(g)(2), if the
  firm does not address the criticisms to the Board's satisfaction within 12 months, the unremediated
  portions are made public. The PCAOB keeps a list:
  *Firms that Failed to Address Quality Control Criticisms Satisfactorily* (pcaobus.org → Oversight →
  Inspections → Remediation).
- Unit of analysis: a **criticism unit**, meaning one QC criticism, usually one heading or one "does not
  provide reasonable assurance" paragraph. A released portion usually contains 1–6 units. The number of
  released reports is on the order of a few hundred since 2008, most of them small, triennially inspected
  firms, plus repeated large-firm releases (Deloitte, GT, KPMG, EY, PwC). **This is an order-of-magnitude
  guess to be replaced by step 1's count.** It implies roughly 600–1,500 units.
- Recent unsatisfactory determinations concentrate in EQR, independence (financial-holdings policies),
  testing controls, supervision, and Form AP reporting (PCAOB 2023 Spotlight, via secondary sources). So
  the realised distribution is lopsided, and the pilot must check that no family is empty.

## 3. Theory: why QC criticism types should differ

Treat the audit firm as a principal (leadership) contracting with agents (engagement teams) to produce an
audit of quality *q* for clients who may pressure the auditor. Following DeAngelo (1981),

> q = P(detect | θ, e) × P(report | b)

where θ is team **capability**, e is **effort**, and b is the **bias** induced by the client relationship.
Leadership cannot observe e directly. It chooses a **monitoring** technology m (review, EQR, internal
inspection) and an **incentive/cultural** regime w (evaluation, compensation, promotion, tone). Those in
turn determine e. A QC system is the bundle (θ-policies, m, w, b-safeguards) plus procedural compliance
obligations.

Each QC criticism asserts that one of these components is deficient. The components differ in economic
content: what is broken, how costly it is to fix, and how verifiable the fix is to the PCAOB. That is the
sense in which the types are *theoretically*, not just nominally, distinct.

| Family | What is deficient (model object) | QC 20 element | QC 1000 component | Remediation technology | Verifiability to PCAOB | Predicted real-response margin |
|---|---|---|---|---|---|---|
| **OBJ** Objectivity | b: independence safeguards, client acceptance / continuance, integrity | Independence, integrity & objectivity; Acceptance & continuance | Ethics & independence; Acceptance & continuance | Compliance systems, portfolio pruning | Medium (systems observable; individual compliance not) | Client portfolio: resignations, NAS-fee ratio ↓ |
| **CAP** Capability | θ: staffing, expertise, training, methodology, consultation, specialists | Personnel management; Engagement performance (methodology, consultation) | Resources (human, technological, intellectual) | Investment in human and technical capital | Medium-high (inputs are countable) | Experienced hires, training, specialist use (Revelio; Ideas A/B) |
| **EXE** Execution | e (symptom): sufficiency of procedures, controls testing, IPE, skepticism, supervision, documentation | Engagement performance | Engagement performance | Behaviour change on engagements | Low (visible only in later inspections) | Audit hours / fees ↑, report lag ↑, leverage ↓ |
| **MON** Monitoring | m: EQR, internal inspection, root-cause analysis, remediation of prior findings | Monitoring (+ EQR under engagement performance) | Monitoring & remediation (+ EQR) | Redesign of review and feedback loops | Medium for design, low for effectiveness | EQR / partner reassignment (Form AP), recurrence ↓ |
| **INC** Incentives & culture | w: evaluation, compensation, promotion, accountability, tone at the top | Personnel management (advancement); not an explicit element | Governance & leadership (+ accountability in resources) | Structural change to reward systems and leadership | Lowest; slowest | Partner exits, leadership turnover, quality-linked compensation disclosures |
| **PRO** Procedural compliance | Obligations that do not enter q directly: Form AP, auditor-report form, audit-committee communications, PCAOB filings | (none; rules-based) | Information & communication (partly) | Checklists, filing processes | Highest; cheapest | None expected; this is the **placebo** family |

A management-control-systems lens (action / personnel / results / cultural controls; Merchant & Van der
Stede) gives a near-identical partition: CAP ≈ personnel controls, EXE + MON ≈ action controls,
INC ≈ results + cultural controls. That the two lenses agree is itself a sign the partition is not
arbitrary.

### Second dimension: form of the deficiency

Independently of family, each unit is coded for **form**:

- **DESIGN**: a policy or procedure is absent or inadequate. Cheap to remediate on paper.
- **OPERATION**: a policy exists but is not complied with or is not effective.
- **PATTERN**: a QC inference drawn from a pattern of engagement-level deficiencies (typically Part I.A).

This mirrors the ICFR design-vs-operating distinction and gives a second, orthogonal handle on
remediation cost.

Each unit also records whether the text **states a root cause** and, if so, which family it points to.
This lets the pilot measure how often the PCAOB speaks in mechanism terms (the text-framing risk in §1).

## 4. Hypotheses the classification unlocks

- **H1 (differentiation).** Families are reliably distinguishable in text (gate G3).
- **H2 (structure).** EXE co-occurs with MON and INC (symptom → oversight → incentives chain) more than
  with OBJ; OBJ and PRO are close to orthogonal to the rest.
- **H3 (persistence gradient).** The probability that the same family recurs in the firm's next released
  Part II is decreasing in verifiability: INC ≥ EXE > MON > OBJ ≈ CAP > PRO. Known counter-example to
  watch: Deloitte's repeated independence (financial holdings) criticisms.
- **H4 (response matching; discriminant validity).** Real responses load on the family's own margin and
  *not* on other families' margins (CAP → hiring/training; EXE → hours/fees/lag; OBJ → client portfolio /
  NAS; INC → partner and leadership turnover; PRO → nothing). This is the sharpest test that the types are
  economically meaningful. It connects directly to Ideas A/B (labour-market responses).
- **H5 (response rhetoric).** In firm response letters, CAP / PRO / OBJ criticisms draw *specific*
  action lists, EXE / INC criticisms draw *generic* commitments, and contesting language concentrates in
  EXE (judgement disputes).

## 5. What would count as "meaningful differentiation"

Three layers, in increasing order of demandingness:

1. **Reliability.** Two trained coders agree on the family (Krippendorff α ≥ 0.70). If humans cannot
   agree, the types are not distinct *in the text*.
2. **Discriminant structure.** Families are not near-duplicates (pairwise φ < 0.5). An unsupervised
   decomposition of the text (TF-IDF → NMF) recovers the families better than chance (NMI above the
   permutation null). Each family also has a face-valid distinctive lexicon (weighted log-odds with
   informative Dirichlet prior; Monroe, Colaresi & Quinn 2008).
3. **Nomological validity.** Families predict *different* downstream responses (H3–H5). Only this layer
   establishes *theoretical* distinctiveness. Layers 1–2 are necessary conditions tested in the pilot.

## 6. Threats and mitigations

| Threat | Why it matters | Mitigation in the pipeline |
|---|---|---|
| Selection on non-remediation | Public frequencies ≠ incidence | Treat the sample as the remediation-failure margin; benchmark against PCAOB Spotlight aggregates; never interpret raw shares as incidence |
| Text states loci, not mechanisms | MON / INC may be thin | Separate `root_cause_stated` field; report share of units with a stated mechanism |
| Multi-label units (small-firm paragraphs list several failures) | Primary-type coding loses information | Code all applicable sub-codes plus one primary; analyse any-label and primary both |
| Format eras / scanned PDFs | Section detection fails | Coverage gate G1; extraction-failure log; manual-unit CSV fallback |
| Big-firm N is small, small-firm N is large | Heterogeneous populations | Stratify coding sample and diagnostics by annually vs triennially inspected |
| Firm response to Part II may be omitted from the public document | Response-letter pathway may be unavailable | Gate G5; fall back to recurrence and real-margin responses (WRDS / Revelio) |
| LLM coder drift / leakage | Inflated agreement | Human double-coding first; LLM never sees human labels; report LLM–human κ separately |

## 7. Relation to the programme

- Feeds **Idea E** (LLM textual mining) directly. It is a measurement instrument for QC narratives.
- The response-matching test (H4) is the bridge to **Ideas A/B**: the labour-market response to a QC
  criticism should depend on its type (capability criticisms → hiring; incentive criticisms → partner
  turnover).
- For **Idea C**, the type of a released Part II may condition the information content of the release.

## 8. Related literature (checked by web search on 2026-09-23 unless flagged)

- Aobdia, D. (2020). The economic consequences of audit firms' quality control system deficiencies.
  *Management Science*, 66(7), 2883–2905. Uses confidential PCAOB QC data. Deficiencies, mainly
  performance-related, are associated with lower audit quality; tone-at-the-top and methodology
  deficiencies partly drive this; non-remediation matters. **Closest precedent.** The public-text version
  plus response mapping is the increment.
- Cao, J., Cheng, Y., Sharma, D. S., & Zhang, J. H. (2026). The audit and economic ramifications of
  persistent organization-level quality control deficiencies in Big 4 PCAOB inspection reports: Evidence
  from a quasi-experiment. *AJPT*, 45(3), 25–52. Uses KPMG's 2014/2015 Part II, made public 25 Jan 2019.
- Carlisle, M., Yu, W., & Church, B. (2022). The effect of small audit firms' failure to remediate the
  PCAOB's quality control criticisms on audit market segmentation. *Journal of Accounting and Public
  Policy*.
- Ragothaman, S. (2012). Watching the watchdogs: An examination of the PCAOB quality control inspection
  reports on triennially inspected audit firms and the AICPA peer review reports. Presented at the
  Deloitte Foundation / University of Kansas Auditing Symposium, April 2012. University of South Dakota
  faculty repository. It compares 106 public PCAOB QC reports on triennially inspected firms with 2,355
  AICPA peer-review reports (firms with < 100 SEC clients). PCAOB reports disclose significantly more
  engagement-performance deficiencies. *Conference paper; no journal version found. Co-authors, if any,
  and the exact coding scheme are unverified; the full text was not reachable from the cloud session.*
- Constance (2025). PCAOB inspection deficiencies and future financial reporting quality: Do the types of
  deficiencies matter? *CAR*. This is Part I deficiency types, not QC; useful as a design template.
- Aobdia, D., Li, E. X., Ramesh, K., & Shen, M. (2025). Deciphering the PCAOB inspection process:
  Evidence and predictive insights from public data. *Management Science*.
- Buslepp, W., DeLisle, R. J., & Victoravich, L. (2018). Does Part II of the PCAOB inspection report
  provide new information to the market? A re-examination of prior evidence. *Managerial Auditing
  Journal*, 33(8/9), 715–735. **The only published study found that splits public Part II criticisms
  by type:** "audit performance" vs "firm management" criticisms (used in a sensitivity analysis).
  Clients of firms with audit-performance criticisms leave after Part I is released. Clients of firms
  with firm-management criticisms leave during the remediation window, before Part II is public. This is
  prior evidence that the client response differs by criticism type. It is a coarse two-way split with
  a market-share outcome, so a finer theory-based typology with firm and real-margin responses is still
  open. *Exact coding rules not seen; full text not reachable from the cloud session.*
- Nagy, A. L. (2014). PCAOB quality control inspection reports and auditor reputation. *AJPT*, 33(3),
  87–104. Market-share loss after public QC disclosure. No type classification found in the abstract.
- Johnson, E. N., Reichelt, K. J., & Soileau, J. S. (2018). No news is bad news: Do PCAOB Part II reports
  have an effect on annually inspected firms' audit fees and audit quality? *Journal of Accounting
  Literature*, 41(1), 106–126. Annually inspected firms, 2007–2015. No type classification found in the
  abstract.
- Ahn, J., Akamah, H. T., & Shu, S. Q. (2021). The effect of disclosing audit quality control deficiencies
  on non-audit tax services: Evidence from Deloitte's 2007 PCAOB Part II inspection report. *JAPP*.
  Deloitte's 2007-inspection Part II (made public 17 Oct 2011, the first Big Four release) concerned
  audits of income-tax accounts. Deloitte clients became 17% less likely to buy auditor-provided tax
  services. This is a single-criticism, type-specific response, in the spirit of H4.
- Buslepp, W. L., & Victoravich, L. Does the PCAOB's quality control remediation process promote audit
  report and financial statement reliability? SSRN working paper 1883668. Firms that failed to remediate
  have more restatements than firms that remediated. No type split found in the abstract.
- DeAngelo, L. E. (1981). Auditor size and audit quality. *JAE*, 3(3), 183–199. This is the competence ×
  independence decomposition.
- Merchant, K. A., & Van der Stede, W. A. *Management Control Systems* (textbook). Control-type lens.
- Monroe, B. L., Colaresi, M. P., & Quinn, K. M. (2008). Fightin' words. *Political Analysis*, 16(4).
  Lexical distinctiveness statistic.

### Corrections flagged for `PCAOB_Inspection_Research_Discussion_Notes_v1.md` §9

- Ref 12 ("Cao, Chen, Lin & Petacchi 2025, KPMG Part II") appears to be the Cao, Cheng, Sharma & Zhang
  (2026, *AJPT* 45(3)) paper above. The author list and year in the notes look wrong.
- Ref 1 ("Acito, Hogan & Imdieke 2019, *TAR* 94(4)") could not be verified. What exists is an Acito, Hogan &
  Imdieke ISAR 2014 conference paper. The *TAR* paper on textual deficiency measures is Acito, Hogan &
  Mergenthaler (2018, *TAR* 93(2)).
- Ref 17 ("Drake, Goldman, Lusch & Schmidt 2024, topic-modelling WP") could not be found. The verified
  paper by these authors is K. Drake, Goldman & Lusch (2016, *TAR* 91(5), 1411–1439) on Deloitte's
  income-tax Part II criticism. The 2024 citation may be a conflation; confirm before citing.
- §2.2's "Deloitte 2007" Part II example is correct. It is the Part II of Deloitte's 2007 inspection
  report, made public on 17 Oct 2011 (Ahn, Akamah & Shu 2021). Keep it distinct from the separate
  December 2007 PCAOB disciplinary order studied by Boone, Khurana & Raman (2015). *(An earlier version of
  this memo wrongly called it a disciplinary order only; corrected 2026-09-23.)*

## 9. Overlap with prior work and positioning (added 2026-09-23)

Web search, abstracts only. Idea as stated: "categorise PCAOB deficiencies, then test whether responses
vary by category."

**Step 1: categorising deficiencies is well established.** It is not a contribution on its own.

| Unit | How categorised | Studies |
|---|---|---|
| Part I | Account / audit area | Church & Shefchik (2012, *AH*); Acito, Hogan & Mergenthaler (2018, *TAR*) |
| Part I | GAAP / GAAS / ICFR | Abbott, Gunny & Zhang (2013, *AJPT*); Prasad & Webster (2022, *JAAF*); Alam, Cheng, Rickett & Skomra (2024, *JCAF*) |
| Part I | Entity-level vs application-level controls | *IJAIS* (2018) |
| Part I | Nature of failure, 5 types (e.g., failure to understand accounting vs insufficient substantive testing) | Constance (2025, *CAR*) |
| Part II | Audit performance vs firm management | Buslepp, DeLisle & Victoravich (2018, *MAJ*) |
| QC, confidential | Performance-related vs organisation-level (tone, methodology) | Aobdia (2020, *MS*) |

**Step 2: "responses vary by type" is partly done.**

| Response margin | Evidence by type |
|---|---|
| Audit fees | Alam et al. (2024): GAAS deficiencies → fees ↑, GAAP deficiencies → fees ↓ |
| Client market share | Buslepp et al. (2018): timing differs by QC type |
| Client relevance → fees, turnover | Acito et al. (2018) |
| Disputing a GAAP-deficient report → market | Buslepp, Notbohm & Abbott (2018, *Advances in Accounting*) |
| Future misstatements | Constance (2025) |
| Tax-type QC criticism → client tax reporting | K. Drake, Goldman & Lusch (2016, *TAR*) |
| Tax-type QC criticism → auditor-provided tax services | Ahn, Akamah & Shu (2021, *JAPP*) |
| Firm response letters (content, tone) | Blankley, Kerr & Wiggins (2012, *RAR*); Ege, Knechel, Lamoreaux & Maksymov (2020, *AOS*) |
| Auditors' reactions to inspection feedback (behavioural) | Johnson, Keune & Winchel (2019, *CAR*); Tegeler, Brown & Downey (2025, *TAR*) |

**Where space remains (candidate positioning):**
1. **Mechanism-based typology.** Prior schemes are regulatory or descriptive: area, standard, or a two-way
   QC split. A typology grounded in economic mechanism (capability, effort, monitoring, incentives,
   objectivity) yields *discriminant* predictions: type k moves response margin k and not the others.
   Prior papers test one outcome against one split.
2. **Firm-side real responses, especially labour** (hiring, experience mix, partner turnover, EQR/partner
   reassignment via Form AP). None of the studies above uses labour outcomes by deficiency type. This
   links the idea to Ideas A/B and to a data advantage (Revelio).
3. **Response letters × deficiency type.** Tone and disagreement are studied, but apparently not by
   deficiency type. Ege et al. (2020) report that firms stopped publicly disagreeing after the early
   years, so post-2010 variation may be thin.

**Main design risks:**
- Part I deficiencies are almost all "execution" failures that differ by area. Mechanism variation lives
  mainly in Part II (small, selected on non-remediation) and in Part I.B/I.C (independence).
- Deficiency mix reflects risk-based inspection selection (Aobdia, Li, Ramesh & Shen 2025), firm size,
  and client industry. Identification needs within-firm variation over time.
- Responses start before public release (Buslepp et al. 2018), so event timing is fuzzy.
