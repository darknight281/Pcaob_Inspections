# Codebook — PCAOB Quality-Control (Part II) Criticisms and Firm Responses

**Version:** 0.1 (2026-09-23), pre-pilot. Revise after the first 30 double-coded units, then freeze.
**Used by:** human coders (Oliver, Cam, Ahmed) and the LLM classifier (`scripts/04_classify_llm.py`
sends this file verbatim as its system prompt, so keep it self-contained).
**Theory behind the families:** `feasibility_memo.md` §3.

---

## Part A — Criticism units

### A.1 What is a unit

A **criticism unit** is one QC criticism the PCAOB made public. Typically it is one of:

- one headed subsection of the released Part II portion; or
- one paragraph built around "the firm's system of quality control does not provide reasonable
  assurance that …" (or equivalent), together with the paragraphs that elaborate it.

**Not a unit:** procedural boilerplate. This covers explanations of SOX §104(g)(2), the 12-month
remediation window, "the Board has determined to make public …", tables of contents, page headers,
and the firm's response letter (which is coded under Part B). If a segment is only boilerplate, give it
the single code `OTHER`, primary `OTHER`, and put "boilerplate" in `notes`.

### A.2 What to code for each unit

| Field | Values | Rule |
|---|---|---|
| `codes` | one or more sub-codes (A.3) | Every sub-code whose locus the text *asserts is deficient* |
| `primary_code` | one sub-code, must be in `codes` | Rule P1 below |
| `form` | `DESIGN` / `OPERATION` / `PATTERN` / `UNCLEAR` | A.5 |
| `root_cause_stated` | true / false | True only if the text explicitly gives a cause |
| `root_cause_family` | `OBJ` / `CAP` / `EXE` / `MON` / `INC` / `PRO` / `NONE` | Family of the stated cause; `NONE` if not stated |
| `evidence_quote` | ≤ 40 words copied verbatim | The span that determines `primary_code` |
| `confidence` | `low` / `medium` / `high` | Coder's own confidence |

### A.3 Families and sub-codes

Six families, each defined by *what the firm's QC system fails to secure*. Code the **locus asserted by
the PCAOB**, not the audit area (revenue, estimates, …) in which the problem surfaced.

#### OBJ — Objectivity (independence, client acceptance, integrity)

| Code | Definition | Include | Exclude |
|---|---|---|---|
| `OBJ_INDEP` | Independence compliance systems and personal/firm independence | financial holdings/interests, independence confirmations, prohibited employment or business relationships, independence tracking and monitoring systems, SEC Rule 2-01 / PCAOB Rule 3520 | NAS and pre-approval (→ `OBJ_NAS`) |
| `OBJ_NAS` | Non-audit services, fee arrangements, and independence communications with the audit committee | NAS permissibility, audit-committee pre-approval, PCAOB Rules 3521–3526, contingent fees | General audit-committee communications (→ `PRO_COMMS`) |
| `OBJ_ACCEPT` | Client acceptance and continuance | risk assessment before accepting or continuing clients, accepting clients beyond competence, management integrity considerations | Competence of assigned staff once accepted (→ `CAP_STAFF`) |
| `OBJ_INTEGRITY` | Integrity and ethical conduct of personnel | altering or backdating audit documentation, exam/training misconduct, dishonesty toward inspectors | Ordinary documentation gaps (→ `EXE_DOC`) |

#### CAP — Capability (human and technical resources)

| Code | Definition | Include | Exclude |
|---|---|---|---|
| `CAP_STAFF` | Assignment, competence, experience, and capacity of personnel | assigning staff lacking expertise, workload and capacity problems, reliance on one individual, industry expertise | Supervising the staff that were assigned (→ `EXE_SUPERV`) |
| `CAP_TRAIN` | Training and professional development named as inadequate | insufficient or missing training on a standard or topic, CPE | Training merely mentioned as existing |
| `CAP_METHOD` | Firm methodology, guidance, practice aids, templates, tools | methodology does not require X, guidance is inadequate or absent, audit programs or software deficient | Teams not following adequate methodology (→ `EXE_*`, form `OPERATION`) |
| `CAP_CONSULT` | Consultation processes and use of specialists | consultation on difficult matters, national office resources, using the work of specialists | Other auditors (→ `EXE_OTHERAUD`) |

#### EXE — Execution (engagement performance)

| Code | Definition | Include | Exclude |
|---|---|---|---|
| `EXE_EVIDENCE` | Sufficiency of substantive audit evidence | substantive procedures, estimates, fair value, revenue, inventory, going concern, business combinations | Controls testing (→ `EXE_CONTROLS`) |
| `EXE_CONTROLS` | Testing internal controls (ICFR audits, or control reliance) | identifying and selecting controls, design and operating effectiveness, review-type controls, precision, management review controls | Data used in controls (→ also `EXE_IPE`) |
| `EXE_IPE` | Reliance on information/data/reports produced by the entity | testing accuracy and completeness of IPE, system-generated reports, data reliability | — |
| `EXE_SKEPTIC` | Professional skepticism and due care, *explicitly* named | skepticism, due professional care, contradictory evidence | Inferring skepticism from insufficient testing (code `EXE_EVIDENCE` only) |
| `EXE_SUPERV` | Supervision and review *within the engagement team* | engagement partner / manager supervision and review, AS 1201 | Engagement quality reviewer (→ `MON_EQR`) |
| `EXE_DOC` | Audit documentation | AS 1215, work papers incomplete, assembly | Deliberate alteration (→ `OBJ_INTEGRITY`) |
| `EXE_OTHERAUD` | Using or supervising other/component auditors | referred-to or component auditors, network firms, AS 1205 / AS 1206 | — |

#### MON — Monitoring (review and feedback systems)

| Code | Definition | Include | Exclude |
|---|---|---|---|
| `MON_EQR` | Engagement quality review | EQR not performed, not timely, or not effective; reviewer qualifications or objectivity; AS 1220 | Supervision by the engagement partner (→ `EXE_SUPERV`) |
| `MON_INSPECT` | Firm-level monitoring of the QC system | internal inspection program, QC monitoring, root-cause analysis | — |
| `MON_REMED` | Failure to remediate or prevent recurrence | previously identified deficiencies recur; prior remediation actions ineffective | First-time deficiencies |

#### INC — Incentives and culture

| Code | Definition | Include | Exclude |
|---|---|---|---|
| `INC_ACCOUNT` | Accountability, evaluation, compensation, promotion | partner or staff evaluations not reflecting audit quality, compensation, consequences for deficiencies | — |
| `INC_TONE` | Tone at the top, leadership, culture, governance | leadership emphasis on quality vs commercial goals, messaging, governance of quality | — |

#### PRO — Procedural compliance (placebo family)

| Code | Definition | Include | Exclude |
|---|---|---|---|
| `PRO_FORMAP` | Form AP / reporting of audit participants | Rule 3211, Form AP filed late, missing, or inaccurate | — |
| `PRO_REPORT` | Form and content of the auditor's report | dating, CAM communication, report elements, AS 3101 / 3105 | Evidence supporting the opinion (→ `EXE_*`) |
| `PRO_COMMS` | Required communications with the audit committee (non-independence) | AS 1301 communications | Independence communications (→ `OBJ_NAS`) |

#### OTHER

`OTHER` is for a unit that fits no sub-code, or pure boilerplate. Explain in `notes`.

### A.4 Decision rules

- **P1 Primary code.** Take the sub-code attached to the main assertion ("the firm's system of QC does
  not provide reasonable assurance that **X**"). If several sub-codes are asserted with equal weight, take
  the one stated first.
- **P2 Locus, not area.** "…sufficient procedures to test controls over revenue" → `EXE_CONTROLS`, not a
  revenue code. Audit areas are not coded.
- **P3 Supervision ladder.** Engagement team's own review → `EXE_SUPERV`. EQR → `MON_EQR`. Firm-wide
  internal inspection → `MON_INSPECT`.
- **P4 Methodology vs execution.** Methodology deficient → `CAP_METHOD` (form `DESIGN`). Methodology
  adequate but not followed → the relevant `EXE_*` code (form `OPERATION`).
- **P5 Named, not inferred.** Code `EXE_SKEPTIC`, `CAP_TRAIN`, `INC_*` only when the text names the
  concept. Do not infer mechanisms the PCAOB did not state.
- **P6 Root cause.** `root_cause_stated = true` only with explicit causal language ("because", "due to",
  "resulting from", "the firm's approach to X led to"). A description of *what* went wrong is not a cause.
- **P7 Multi-label.** A small-firm paragraph listing several failures gets several codes. Do not force a
  single code into `codes`; only `primary_code` is single.

### A.5 Form of the deficiency

- `DESIGN`: policies or procedures absent or inadequate ("the firm's policies do not require …",
  "the firm has not established …").
- `OPERATION`: policies exist but are not complied with or not effective ("personnel did not comply
  with the firm's policies …", "the firm's procedures were not performed").
- `PATTERN`: QC inference drawn from engagement-level findings ("the deficiencies described in Part I …
  indicate …", "in N of the audits inspected, engagement teams did not …").
- `UNCLEAR`: none of the above can be determined.

### A.6 Illustrative (synthetic) examples

These are paraphrased to show the rules. They are **not** quotations from PCAOB reports.

1. "The inspection results indicate that the firm's system of quality control does not provide reasonable
   assurance that engagement teams test controls with a review element at a sufficient level of
   precision." → `codes = [EXE_CONTROLS]`, primary `EXE_CONTROLS`, form `PATTERN`.
2. "The firm's policies do not require that an engagement quality review be completed before the firm
   grants permission for the client to use its report." → `[MON_EQR]`, `DESIGN`.
3. "Firm personnel did not comply with the firm's policies requiring the reporting of financial
   holdings." → `[OBJ_INDEP]`, `OPERATION`.
4. "Partner evaluations give little weight to audit quality, and the deficiencies observed appear to
   result from this emphasis." → `[INC_ACCOUNT]`, root cause stated, `root_cause_family = INC`.
5. "The firm's sole audit partner performs all engagements without an engagement quality review and has
   not received training in auditing ICFR." → `[MON_EQR, CAP_TRAIN, CAP_STAFF]`, primary `MON_EQR`
   (stated first), `DESIGN`.

---

## Part B — Firm responses

Apply Part B to the firm's response letter or remediation statement, where one is published. A response
is coded once per document, and per QC unit where the letter addresses units separately.

| Field | Values | Rule |
|---|---|---|
| `stance` | `ACCEPT` / `ACCEPT_WITH_CONTEXT` / `CONTEST` / `NONE` | `ACCEPT`: agrees and commits. `ACCEPT_WITH_CONTEXT`: agrees but qualifies ("did not affect the opinion", "no restatement"). `CONTEST`: disputes the finding or the PCAOB's judgement. `NONE`: no substantive response |
| `actions` | any of the codes below | Actions the firm says it took or will take |
| `specificity` | `SPECIFIC` / `GENERIC` | `SPECIFIC`: names concrete actions, dates, quantities, or policies. `GENERIC`: commitment language only |
| `mentions_root_cause` | true / false | Mentions root-cause analysis or identified causes |

Action codes: `ACT_POLICY` (new or revised policies and procedures), `ACT_TRAINING`, `ACT_STAFFING`
(hiring, reassignment, specialists), `ACT_METHOD_TOOLS` (methodology, guidance, templates, technology),
`ACT_MONITORING` (EQR, internal inspection, root-cause programme), `ACT_LEADERSHIP_ACCOUNTABILITY`
(evaluation, compensation, leadership, tone), `ACT_INDEPENDENCE_SYSTEMS`, `ACT_CLIENT_PORTFOLIO`
(declining or resigning clients), `ACT_ENGAGEMENT_REWORK` (additional procedures on inspected audits),
`ACT_NONE_SPECIFIC`.

---

## Part C — Coding protocol

1. Both human coders code the same calibration batch of 30 units independently, compare, and revise this
   codebook. Record every change in the changelog below.
2. Freeze the codebook. Double-code a fresh stratified sample of ≥ 100 units (`scripts/05_draw_coding_sample.py`).
3. Compute α / κ (`scripts/06_feasibility_diagnostics.py`). Adjudicate disagreements. The adjudicated labels
   are the benchmark for the LLM and rule-based coders.
4. The LLM never sees human labels or the adjudication notes.

### Changelog

- 0.1 (2026-09-23): initial version, pre-pilot.
