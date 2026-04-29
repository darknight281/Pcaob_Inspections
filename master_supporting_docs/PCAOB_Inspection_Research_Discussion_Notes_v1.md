# PCAOB Inspection Reports: Research Planning Discussion Notes

**Author**: Oliver
**Purpose**: Discussion document for upcoming sessions with Cam and Ahmed
**Date**: April 2026
**Version**: v1

---

## Table of Contents

1. Background and Motivation
2. Understanding the PCAOB Inspection Report Setting
3. The Data Mapping Pipeline (Public/Subscription Sources Only)
4. Five Research Ideas: Detailed Walkthroughs
5. Connection to Roh (2026, *TAR*) "When Large Employers Come to Town"
6. Critical Methodological Clarification: Unit of Analysis
7. Suggested Sequencing of Projects
8. Open Questions for Supervisor Discussion
9. References

---

## 1. Background and Motivation

The PCAOB inspection regime, established under the Sarbanes-Oxley Act (2002), has matured into one of the most fertile institutional settings in audit research. Roughly two decades of papers now interrogate:

1. What determines inspection findings.
2. How auditors, clients, and capital markets respond.
3. How inspections spill over to non-inspected engagements, peer offices, and foreign jurisdictions.
4. How partner-level disclosure under Form AP (effective 31 January 2017) has reshaped the empirical possibilities for individual-auditor research.

My initial research interest is in **spillover effects between auditors regarding labour force strategy changes** following PCAOB inspection findings. A core empirical challenge I identified earlier is that PCAOB inspection reports are issued at the audit firm (national) level only, not at the office level. The discussion below addresses how to work around this constraint and identifies five concrete research ideas with varying mechanisms.

---

## 2. Understanding the PCAOB Inspection Report Setting

### 2.1 The Inspection Process

When the PCAOB inspects a registered audit firm, its staff:

1. Reviews **a sample of selected engagements** (typically 5 to 60 issuers per Big 4 firm per year). Selection is risk-based, not random, targeting engagements with elevated audit risk such as volatile industries, complex estimates, IPOs, and restatement history.
2. Reviews the firm's **quality control system**, including independence policies, partner evaluation, training, and monitoring procedures.
3. Issues a final report after extensive comment periods with the firm.

### 2.2 Anatomy of an Inspection Report

Each annual report has a consistent structure:

1. **Part I.A (Public)**: Engagement-level audit deficiencies. The PCAOB describes deficiencies *qualitatively*, identifying issuer engagements only as "Issuer A," "Issuer B," and so on, never naming the client. The narrative typically describes the industry, the financial-statement area, and the nature of the deficiency.
2. **Part I.B (Public, since 2016)**: Independence and ethics violations. Often relates to non-audit services, independence-impairing relationships, partner rotation breaches.
3. **Part I.C (added later)**: Other instances of non-compliance with rules and standards.
4. **Part II (Confidential unless not remediated within 12 months)**: Quality control criticisms. Made public only when the firm fails to remediate to the PCAOB's satisfaction (notable examples: Deloitte 2007, KPMG 2014/2015 disclosures).
5. **Appendices**: Firm response, methodological notes.

### 2.3 What Is Public vs Private

| Item | Public? | Where |
|---|---|---|
| Part I.A deficiency narratives | Yes | pcaobus.org inspection reports |
| Part I.B independence/ethics | Yes (since 2016) | pcaobus.org |
| Part II QC criticisms | Only if not remediated within 12 months | pcaobus.org |
| Issuer identity | **Never** | Confidential by SOX Section 104(g)(2) |
| Number of engagements inspected | Yes | Report cover pages |
| Number with deficiencies | Yes | Aggregate counts |
| Specific engagement partner | **Not disclosed in inspection report** | Inferred via Form AP linking |

The fundamental empirical challenge is that the PCAOB will never release issuer or partner identities. So *all* office-level identification must be inferred indirectly.

### 2.4 Key Institutional Dates to Build Around

1. **2003**: PCAOB begins operations; first inspections.
2. **2009**: International inspection access expansion.
3. **2015**: Expanded disclosure of Part I information.
4. **2016**: Part I.B (independence) becomes public.
5. **31 January 2017**: Form AP becomes mandatory; engagement-partner names disclosed for all issuer audits, plus other accounting firms participating in the audit.
6. **December 2020**: HFCAA (Holding Foreign Companies Accountable Act) passes.
7. **August 2022**: Statement of Protocol with China; first PCAOB inspections of mainland Chinese firms.
8. **June 2024**: Major PCAOB inspection-report redesign (engagement performance metrics).

These dates anchor staggered DiD designs throughout the literature.

---

## 3. The Data Mapping Pipeline (Public/Subscription Sources Only)

Since I do not have any proprietary PCAOB data access, the entire research design must rest on combining publicly available and subscription data sources.

### 3.1 The Four Datasets and What Each Provides

| Dataset | Source | Unit | Key Variables |
|---|---|---|---|
| **PCAOB inspection reports (PDF)** | pcaobus.org (free) | Audit firm × inspection year | Deficiency narratives, count, financial-statement area, industry hints |
| **Form AP** | PCAOB Form AP database (free, downloadable) | Issuer audit × engagement partner | Engagement partner name and ID, issuer CIK, audit firm, fiscal year-end, other firms participating |
| **Audit Analytics** | WRDS subscription | Issuer × auditor × fiscal year | Auditor city/office, audit fees, restatements, opinions, ICFR weaknesses |
| **Compustat / CRSP / IBES** | WRDS subscription | Issuer × year | Financials, market data, analyst forecasts |

The "missing link" between PCAOB reports and offices is **Form AP combined with Audit Analytics' office-city field**. Once I have engagement partner names and the city of the audit office that signs the engagement letter, I can:

1. Aggregate partners into offices.
2. Treat the office as the "potentially exposed" unit when its firm receives a deficiency in a particular industry/area.
3. Use the deficiency narrative (textual analysis) to refine which offices were *most* exposed based on portfolio composition.

### 3.2 The Mapping Pipeline Step-by-Step

#### Step 1: Build a Form AP Partner-Office Panel

The Form AP raw file (downloadable as CSV from pcaobus.org) gives, per engagement:

1. Audit firm name and PCAOB ID
2. Engagement partner name and Partner ID (a unique identifier)
3. Issuer name and CIK
4. Fiscal year-end
5. "Other accounting firms" participating (with names and percentage of hours)

Form AP does *not* directly give the **office** of the engagement partner. Inferring the office requires:

1. Joining Form AP to Audit Analytics on (Audit Firm × Issuer CIK × Fiscal Year-End). Audit Analytics records the auditor's city for each engagement.
2. Treating the partner's **modal city across their engagements in a given year** as their office assignment.
3. Where a partner appears in multiple cities, using the city with the largest dollar volume or audit-fee share.

This is the standard approach used in Hu, Smith, and Wong (2025, *JBFA*) and Lee, Lee, and Pittman (2021, *TAR*).

#### Step 2: Extract Inspection Deficiency Narratives Using Textual Analysis

PCAOB inspection reports are PDFs available at pcaobus.org/oversight/inspections. The pipeline:

1. Scrape all annual inspection reports for each registered firm, 2004 onward.
2. Use a PDF parser (`pdfplumber`, `pymupdf`, or `tika-python` in Python) to extract Part I.A narrative text.
3. Apply textual analysis to identify:
   - **Industry hints** in the narrative (e.g., "issuer in the energy industry" maps to SIC codes).
   - **Financial statement area** (e.g., revenue, ICFR, business combinations, fair value, allowance for loan losses).
   - **Deficiency type** (e.g., insufficient sample sizes, failure to test controls, inadequate journal-entry testing).

This is exactly what Acito, Hogan, and Imdieke (2019, *TAR*) did, and what Drake, Goldman, Lusch, and Schmidt (2024) extend with structured topic modelling. Modern tools (FinBERT embeddings, GPT-class models, BERTopic) allow much finer granularity.

#### Step 3: Map Deficiency Narratives to Affected Engagement Areas

The deficiency text typically signals:

1. **Industry** of the engagement (around 70 percent of narratives include some industry signal).
2. **Financial statement account or audit area** (almost always specified).

For each (firm, year) pair, build an **exposure profile**: a vector of probabilities that each industry-area combination was the locus of a deficiency.

#### Step 4: Compute Office-Level Exposure

For each office of an inspected firm, in each inspection-year, compute exposure as a function of:

1. The deficiency profile from Step 3 (industry × area).
2. The office's own client portfolio composition (industries audited, account areas relevant to those industries).

A simple specification:

Exposure(o, t) = Sum over i, a of [Indicator(Deficiency(f, t, i, a)) × PortfolioShare(o, t-1, i, a)]

where f is the firm, o is an office of f, i is industry, a is account area, and PortfolioShare is computed from Audit Analytics.

This is the office-level *treatment intensity*. It is continuous (good for power), and identified entirely from public + subscription data.

#### Step 5: Validate the Mapping

Validation steps:

1. Show that offices with high computed exposure also exhibit higher subsequent restatement rates (sanity check that exposure proxies real audit-quality concerns).
2. Compare office-exposure measure to known cases where a deficient engagement has been publicly identified through subsequent SEC enforcement (rare but useful).
3. Corroborate with office-level audit fee changes around the inspection report release (Acito et al. 2019 logic).

### 3.3 Concrete Tools

1. **Python**: `pdfplumber`, `transformers` (HuggingFace), `BERTopic`, `sentence-transformers`, DuckDB for the join layer.
2. **Stata**: Once the panel is built, standard `reghdfe`, `csdid`, `kmatch`, `ebalance` toolkit.
3. **R**: `quanteda`, `stm` for structural topic models.
4. **WRDS**: Audit Analytics, Compustat North America, BoardEx (for the audit committee networks idea).
5. **PCAOB site**: Inspection reports and Form AP (both free).

---

## 4. Five Research Ideas: Detailed Walkthroughs

### 4.1 Idea A: Office-Level Workforce Strategy Responses to Inspection Deficiencies

**Refined research question**: When an audit firm receives a notable Part I.A deficiency (especially clustered in a particular industry-area), do the firm's offices with high exposure to that deficiency change their workforce strategy (hiring, retention, partner promotion, lateral movement, salary positioning) more than low-exposure offices of the same firm?

**Why interesting**: Tests whether inspection findings function as *labour-market shocks* internal to the audit firm, not just engagement-level audit-quality shocks. The mechanism builds on Aobdia (2019, *TAR*): if effort reallocates within a firm after a finding, then *staffing capacity* (the input behind effort) likely also reallocates.

**Identification design**:

1. **Treatment**: Office-level continuous exposure measure from Section 3.2.
2. **Control**: Same firm's low-exposure offices, plus other firms' offices weighted to balance on portfolio.
3. **Stacked DiD** by inspection-year cohort (multiple firms inspected each year; stacking each cohort with its matched control offices addresses Goodman-Bacon (2021) and Sun-Abraham (2021) concerns about staggered DiD).
4. **Outcomes (LinkedIn-derived)**:
   - Net hiring rate at the office (number of new joiners scraped from LinkedIn profile histories).
   - Voluntary departures (employees marked as "left for X firm").
   - Internal promotion rate to manager / senior manager / partner.
   - Lateral hiring (mid-career joiners with prior Big 4 experience).
   - Composition shifts (industry specialisation of new hires).
5. **Heterogeneity tests**:
   - Big 4 vs mid-tier.
   - Densely-populated MSAs (more outside options for staff) vs thin labour markets.
   - Industry-specialist offices (where the deficiency hits the office's specialty hardest) vs generalist.
6. **Robustness**:
   - Oster (2019) bounds.
   - Alternative exposure definitions (binary vs continuous).
   - Placebo using random reassignment of deficiencies to firms.

**Data feasibility**: Form AP (free), Audit Analytics (subscription), LinkedIn data (binding constraint). Hu, Smith, and Wong (2025, *JBFA*) used 200,708 LinkedIn profiles. Options:

1. A licensed data provider like **Revelio Labs** or **LinkUp** (Monash institutional access to be confirmed).
2. A structured scraping arrangement (legally and TOS-compliant, often via institutional API agreements).
3. Job-posting data from **Burning Glass Institute / Lightcast** as an alternative measure of office hiring intent.

### 4.2 Idea B: Cross-Office Spillovers Within Big 4 Networks

**Refined research question**: When one office of a Big 4 firm receives a high-profile Part I deficiency, do *other offices of the same firm* (not directly implicated in the deficiency) increase audit effort, fees, or staff investment, consistent with internal-QC-driven discipline spreading laterally?

**Why interesting**: This is the *inverse* of Idea A in an analytical sense. Idea A tests "if you're exposed, you respond." Idea B tests "if your sibling office is exposed, do you also respond?" The mechanism is internal QC, geographic-network knowledge spillover, and firm-wide reputational recalibration.

**Identification design**:

1. **Treated offices**: Non-deficient offices of a firm that has experienced a notable Part I deficiency in another office.
2. **Control offices**: Matched offices of *other* Big 4 firms, similar in size, geography, and industry mix, in the same year.
3. **Stacked DiD** with each firm-deficiency-event treated as a cohort.
4. **Outcomes**:
   - Audit fees (Audit Analytics).
   - Audit hours / proxies (audit lag, going-concern issuance rates).
   - Restatement rates of the office's clients in subsequent years.
   - Office-level hiring (LinkedIn).
   - Internal training proxies (LinkedIn certifications, course completions).
5. **Heterogeneity**:
   - Geographic proximity (treated offices in same MSA as deficient office vs distant).
   - Industry overlap with the deficient engagement's industry.
   - Partner network ties (whether partners in treated office have prior co-engagement history with deficient office partners, traceable via Form AP).
6. **Falsification**: The same deficiency should *not* affect competing firms' offices in the same MSA absent industry overlap (this distinguishes within-firm spillover from local-market knowledge spillover, which is Lamoreaux et al. 2023's finding).

**Connection to Lamoreaux, Mowchan, and Zhang (2023, *TAR*)**: They study cross-firm spillovers from PCAOB enforcement (revocations). My idea is the within-firm analogue from inspection deficiencies. The two papers together would map both within-firm and across-firm spillover channels.

### 4.3 Idea C: Industry-Network Spillovers Using EDGAR Information Diffusion

This builds directly on my existing SEC EDGAR spillover project with Qinfang and Qiuhong.

**Refined research question**: When the PCAOB releases an inspection report identifying a deficiency at audit firm f in industry i, do investors searching EDGAR for firm f's clients update their attention patterns towards (a) other clients of f, (b) clients of competitor auditors in industry i, or (c) clients of f outside industry i?

The hypothesis is that EDGAR co-search behaviour reveals *information spillover paths* in real time, and these paths reveal whether investors treat inspection deficiencies as auditor-firm signals (channel a), industry-audit-quality signals (channel b), or something else entirely.

**Why interesting**: Positions inspection reports as an *information event* that propagates through investor attention networks, which is a different lens from the "audit quality channel" that dominates the literature. Connects to Drake, Roulstone, and Thornock (2015, *JAR*) on EDGAR search activity, Lee, Ma, and Wang (2015, *RFS*) on co-search-derived peer firms, and my existing project.

**Identification design**:

1. **Event window**: Around PCAOB inspection report release dates (treated as an information shock).
2. **Treatment**: Clients of the inspected firm f classified by:
   - "Directly exposed" if in industry i where deficiency was found.
   - "Indirectly exposed" if same firm f but different industry.
   - "Industry peer" if industry i but different auditor.
   - "Pure control" if neither.
3. **Outcome**: EDGAR co-search dyads from log files (publicly available). Specifically:
   - Probability that investors searching firm X also search firm Y within the same session.
   - Pre/post inspection-report release.
4. **Stacked DiD** by inspection-report cohort.
5. **Cross-sectional moderators**:
   - Materiality of the deficiency (Part I.A vs Part I.B vs Part II).
   - Whether the deficiency narrative includes industry-specific language.
   - Pre-event investor attention to the auditor (inspect "active" vs "dormant" attention).
6. **Robustness**:
   - Alternative co-search measures (Lee, Ma, Wang 2015 vs Drake, Roulstone, Thornock 2017 *RAST*).
   - Placebo dates (random non-event days).

**Data**: EDGAR log files (free, but ~2 TB), Audit Analytics (auditor identification), PCAOB inspection reports.

**Theoretical contribution**: Currently, audit-quality literature tests *real* outcomes (fees, switches, restatements). This idea tests *informational* outcomes, providing direct evidence on *which* channel investors use to interpret inspection signals. Novel and complements the audit-quality channel established by Acito et al. (2019), Aobdia (2019), and Cao et al. (2025).

### 4.4 Idea D: Audit Committee Networks and Part II Information Transmission

**The core idea**:
When auditor f receives a notable Part II disclosure (e.g., KPMG 2019), all of f's clients are nominally affected. But the *information* spreads beyond f's own clients, because audit committee members sit on multiple boards. A director on f's client board now knows about f's deficiency; they may carry that knowledge to their *other* boards (which may be audited by different firms). The question: do those *other* firms (with directors connected to deficient-auditor clients) change auditor, fees, or oversight?

**How to identify audit committee networks**:

1. **BoardEx (subscription via WRDS)**: Provides director-firm-year panel for thousands of US public firms. Each director's directorships across firms are observable.
2. **Audit Analytics audit committee data**: Provides committee membership specifically (not just board membership), which is tighter for our purposes.
3. **ISS Risk Metrics**: Alternative source for committee composition.

Build a director × firm × year panel. For each director, observe all their other directorships and committee memberships in that year.

**How to link to PCAOB inspection report (auditor side)**:

1. Identify the **inspection-report event** (e.g., KPMG Part II disclosure released January 2019).
2. Identify all firms audited by KPMG in 2018 (treated client set, via Audit Analytics).
3. For each director on the audit committee of a KPMG-audited firm, identify their *other* directorships in firms audited by different auditors.
4. The "transmission node" is the director. Their non-KPMG-audited firms become **treated** (exposed via the network), and similar firms whose directors are *not* connected to KPMG clients become **control**.

**Identification design**:

1. **Stacked DiD** around Part II events (KPMG 2019, Deloitte 2007, possibly future events).
2. **Treatment**: Firm j has at least one audit-committee director who *also* sits on the audit committee of a deficient-auditor client.
3. **Control**: Matched firm with no such director connections, similar in size/industry/auditor.
4. **Outcomes**:
   - Auditor switching rates.
   - Audit fees.
   - Frequency of audit committee meetings (proxy for oversight intensity).
   - Disclosure changes (10-K risk factor language, quantified via textual analysis).
5. **Falsification**: Test whether the effect concentrates on audit-committee directors specifically (vs general board directors), which would confirm the audit-related mechanism.

**Refinement using Form AP**: An even cleaner test uses Form AP-disclosed engagement partners. If a director's other firm is audited by a partner who has prior co-engagement history with the deficient client's partner (traceable via Form AP), the network is even tighter.

**Theoretical contribution**: Complements Cao et al. (2025) (KPMG client attrition) by showing that the information transmits through *governance networks*, not just through the auditor-client relationship.

### 4.5 Idea E: LLM-Based Textual Mining of Inspection Reports

**The connection / link**:
The connection is between two textual artefacts:

1. **PCAOB Part I.A deficiency narratives** (what the inspector wrote about specific engagement deficiencies).
2. **Subsequent client outcomes** (restatements, ICFR adverse opinions, SEC AAERs, fraud disclosures).

The proposition is that the *language* of the deficiency narrative contains signal about the *severity* and *type* of the deficiency, which predicts *which clients of the inspected firm* will subsequently restate. This signal is finer than crude deficiency counts.

**The mapping logic**:

1. Each Part I.A narrative describes a deficiency at one engagement, with industry and account-area hints.
2. We don't know which specific issuer was the deficient engagement.
3. But we know the firm's full client portfolio (Audit Analytics).
4. And we observe which of those clients subsequently restated.
5. So we can ask: do clients in industries/accounts matching the deficiency narrative restate at higher rates than clients in non-matching industries/accounts?
6. If yes, the deficiency narrative is informative. The LLM contribution is computing similarity between deficiency text and client characteristics (industry, account complexity, prior disclosure language) more flexibly than keyword approaches.

**Identification design**:

1. **Step 1**: Encode each Part I.A deficiency narrative using a domain-adapted sentence-transformer (e.g., FinBERT, or a small open-source LLM fine-tuned on accounting text).
2. **Step 2**: Encode each client's 10-K MD&A (or footnote text on the relevant account area) using the same model.
3. **Step 3**: Compute cosine similarity between deficiency embedding and each client's text embedding.
4. **Step 4**: Predict subsequent restatement using similarity as the regressor, controlling for client characteristics, year, and firm fixed effects.
5. **Step 5 (validation)**: Compare predictive R² against (a) keyword approaches (Acito et al. 2019), (b) simple deficiency counts, (c) industry-only matching.

**Why interesting**: Operationalises the inspection-narrative signal as a continuous text-based exposure measure for each client. Generalises and strengthens what Acito et al. did manually for fees, but for restatements (a real audit-quality outcome). Also opens the door to using LLM embeddings as a general-purpose exposure measure across many of the other ideas.

**Theoretical contribution**: Methodological. Would be the first (to my knowledge) to demonstrate that LLM embeddings of regulatory narrative text predict downstream client outcomes more effectively than human-coded keyword schemes. The kind of paper that gets cited as a measurement contribution.

---

## 5. Connection to Roh (2026, *TAR*) "When Large Employers Come to Town"

This paper provides a powerful conceptual and methodological template for several of the above ideas.

### 5.1 What Roh Does (Brief)

1. Identifies large-employer entry announcements into local labour markets as a shock to *labour market competition* faced by incumbent firms.
2. Documents that incumbent firms in the affected counties **increase positive, forward-looking disclosure** (10-K, 8-K, press releases).
3. Effect is concentrated where firms compete most directly with the entrant for similar workers and where employee retention pressure is highest.
4. Mechanism: disclosure as a labour-market signalling/retention tool, not an investor-targeted tool.
5. Identification: staggered DiD using announcement timing × geographic location.

### 5.2 Direct Logical Parallels to My Ideas

#### Parallel 1: Inspection Deficiency as a "Local Shock to Audit Labour Markets" (Idea A, Idea B, Idea on regional spillovers)

Roh's logic: *Large-employer entry intensifies labour competition for incumbent firms*.
My analogue: *Audit firm office deficiency intensifies labour market reallocation in the local audit labour market*.

The key idea is that an inspection deficiency damages an office's local labour-market reputation, prompting:

1. Outflow of experienced staff who have outside options.
2. Inflow opportunities for competing offices.
3. Potential disclosure responses (offer letters, recruiter outreach, glassdoor ratings) by both deficient and competing offices to manage labour signalling.

**Direct adaptation**: Replace Roh's "large-employer entry" with "inspection deficiency at a local audit office". Replace his "incumbent firm disclosure response" with "competing audit firm hiring and disclosure responses". The setting is structurally identical.

#### Parallel 2: Disclosure as a Labour-Market Signalling Tool (Across All Ideas)

Roh's deeper insight is that **disclosure is partially aimed at the labour market, not just at investors**. This is highly relevant for inspection-context research because:

1. Audit firms make public statements after Part II disclosures (KPMG, Deloitte) that read as investor-facing but may be primarily *labour-market-facing* (reassuring staff and recruits).
2. Audit firms' transparency reports (where applicable) and quality-control statements contain language designed to attract/retain talent.
3. Job postings and Glassdoor responses by audit firms to inspection findings have not been studied.

**Implication**: I could enrich Idea A by examining not just *workforce strategy* (hiring/retention numbers) but *workforce signalling* (job posting language, Glassdoor responses, training-program announcements). This adds a disclosure dimension that aligns directly with Roh's framework and elevates the contribution.

#### Parallel 3: The "Direct Competition Channel" (Identification Sharpener)

Roh shows the disclosure response is concentrated in firms competing *most directly* with the entrant for similar workers. This directly informs my heterogeneity tests in Ideas A, B, and the regional spillover idea: *the labour-market response should be strongest where labour-market competition between deficient and non-deficient offices is highest*.

Operationalisations:

1. Same MSA, same audit firm tier (Big 4 vs Big 4), same industry specialisation.
2. Higher overlap of educational pipeline (same feeder universities, per Lee et al. 2021 *TAR*).
3. Higher historical staff-flow rates between offices (LinkedIn-traceable).

#### Parallel 4: Using a "Local Geography × Time" Shock as the Treatment

Roh's MSA × time variation is the same identification structure I'd want to use for the regional spillover idea. The empirical machinery (stacked DiD with MSA × firm × year cohorts) is directly transferable.

### 5.3 Where My Ideas Go *Beyond* Roh

1. **Network mechanism (Idea D)**: Roh's mechanism is local-market competition. My audit-committee-network idea adds a *cross-geography* network channel, which is a substantive extension.
2. **Information mechanism (Idea C)**: Roh studies disclosure responses; I study EDGAR co-search responses. That's an information-channel extension.
3. **Within-firm spillovers (Idea B)**: Roh studies between-firm responses; I study within-firm spillovers across offices, which is a different organisational unit and untreated by Roh.

### 5.4 What's Different and Why It Matters for Contribution

The audit-firm setting differs from Roh's in three ways I can leverage:

1. **The shock is regulatory, not market-driven**. PCAOB inspections are exogenous in a way that large-employer entries arguably are not (entries can be endogenous to local conditions).
2. **The treated unit is itself a labour-intensive professional service firm**, where labour *is* the production technology. This makes the labour-market response a first-order effect, not a peripheral one.
3. **The regulatory feature creates rich heterogeneity** (Part I vs Part II, industry-area-specific deficiency narratives), enabling cleaner cross-sectional tests than Roh has.

These differences let me position the work as a natural extension of Roh into a setting where labour is the binding production input and where regulatory shocks are arguably more exogenous.

---

## 6. Critical Methodological Clarification: Unit of Analysis

**Important**: I initially assumed that *everything* must be conducted at the audit office level (since that was my original spillover framing). On reflection, this is incorrect. The right unit of analysis depends on (a) the *treatment* unit, (b) the *outcome* unit, and (c) the *mechanism* being tested.

### 6.1 Treatment vs Outcome Levels

There are two distinct questions:

1. **At what level is the treatment (the inspection finding) defined?** Always firm-level, because that's how the PCAOB releases inspection reports.
2. **At what level is the outcome and the mechanism observed?** This varies by research question.

Even though *treatment* is firm-level, I can compute **office-level (or partner-level, or client-level) exposure intensity** by combining the firm-level deficiency with the unit's portfolio characteristics. This is the mapping pipeline in Section 3.2.

### 6.2 Idea-by-Idea Mapping

#### Idea A: Workforce Strategy Responses

- **Outcome unit**: Office-level (hiring, retention, promotion happen at offices).
- **Treatment unit**: Office-level *exposure* derived from firm-level deficiency × office portfolio.
- **Why office-level**: The *mechanism* is local labour-market reallocation. A KPMG deficiency narrated about energy-industry revenue recognition may strongly affect KPMG Houston (energy hub) but barely touch KPMG Boston. Aggregating to firm-level would average these out and destroy the mechanism.
- **Verdict**: Office-level is correct.

#### Idea B: Cross-Office Spillovers Within Big 4

- **Outcome unit**: Office-level (non-deficient offices of the same firm).
- **Treatment unit**: Office-level (the *deficient* office is the source; *other offices* are the spillover targets).
- **Why office-level**: The very phrasing "cross-office" requires office-level granularity. There's no firm-level analogue.
- **Verdict**: Office-level is correct and necessary.

#### Idea C: EDGAR Information Spillovers

- **Outcome unit**: **Client-firm-level** (which company is being co-searched on EDGAR).
- **Treatment unit**: **Audit-firm-level** (the inspected firm) and **industry-level** (the industry signalled in the deficiency narrative).
- **Why NOT office-level**: Investors searching EDGAR don't see the audit office. They see the audit firm signature on the 10-K. The information channel is "investors update beliefs about all clients of firm f in industry i based on the public release of an inspection report about firm f". The office-level distinction is invisible to the investor.
- **Verdict**: This is a **firm-level treatment, client-level outcome** design. Forcing it to office-level would actually *misrepresent* the mechanism.

This is the most important one to flag: my initial intuition that everything must be office-level would lead me astray here.

#### Idea D: Audit Committee Networks

- **Outcome unit**: **Client-firm-level** (firms whose audit committee directors are connected to deficient-auditor clients).
- **Treatment unit**: **Audit-firm-level** (the deficient auditor, especially Part II events like KPMG 2019).
- **Mediation unit**: **Director-level** (the network node).
- **Why NOT office-level**: The transmission channel is governance networks, which operate at the director level connecting client firms. Auditor offices don't enter the mechanism. The deficient firm is the source of the signal; directors carry it across firms; the receiving firms are the affected unit.
- **Verdict**: Multi-level design (firm-level treatment, director-level mediator, client-firm-level outcome). Not office-level.

#### Idea E: LLM-Based Textual Mining → Restatement Prediction

- **Outcome unit**: **Client-firm-level** (which clients restate).
- **Treatment unit**: **Client × deficiency-area** matched intensity (text-similarity score between the deficiency narrative and the client's disclosures).
- **Why NOT office-level**: Restatements occur at clients, not offices. The deficiency narrative is matched to client-specific text. The office is irrelevant to the mechanism, the question is whether the deficiency *language* predicts which *clients* of the inspected firm will restate.
- **Verdict**: Client-level. The office-level dimension would only matter as a robustness check.

### 6.3 Summary Table

| Idea | Treatment Level | Outcome Level | Why |
|---|---|---|---|
| A: Workforce Strategy | Office (exposure) | Office | Hiring happens locally |
| B: Cross-Office Spillover | Office (deficient) | Office (other offices) | "Cross-office" is the question |
| C: EDGAR Co-search | **Audit firm + industry** | **Client firm** | EDGAR investors see firm, not office |
| D: Audit Committee Networks | **Audit firm** | **Client firm via director network** | Governance network operates firm-to-firm |
| E: LLM Textual Mining | **Client × deficiency text** | **Client firm** | Restatements happen at clients |

### 6.4 The Deeper Point

The level of analysis should follow the *mechanism*, not a blanket rule. The four levels I'll work across are:

1. **Audit firm-level**: Where the regulatory disclosure occurs (the source of treatment information).
2. **Office-level**: Where labour, effort, and local relationships operate.
3. **Partner-level**: Where individual professional judgment and reputation operate (Form AP).
4. **Client-firm-level**: Where audit outcomes (fees, opinions, restatements) are observed and where investors form beliefs.

A well-designed paper picks the level that *matches the mechanism* for the outcome it studies, then derives **exposure** at that level by combining the firm-level treatment with portfolio characteristics observed at the lower level.

### 6.5 Practical Implication for Project Pipeline

1. **If drawn to labour-market mechanisms** (Roh-style framing, Ideas A, B, regional spillovers): office-level is correct.
2. **If drawn to information-diffusion mechanisms** (Idea C): client-firm-level outcomes with firm-level treatment.
3. **If drawn to governance-network mechanisms** (Idea D): client-firm-level outcomes with director-network mediation.
4. **If drawn to measurement contributions** (Idea E): client-level outcomes with text-derived exposure intensity.

So when picking the first paper, the question is less "what level should I work at?" and more "which mechanism is most theoretically compelling and most defensible empirically?" The level then follows from that choice.

---

## 7. Suggested Sequencing of Projects

Given my portfolio, supervisors, and existing infrastructure, the suggested ordering is:

1. **First paper (next 12 months)**: Idea C (EDGAR information spillovers from inspection reports). Directly leverages existing EDGAR project skills and Qinfang/Qiuhong collaboration. Methodologically clean. Makes a clear informational contribution. Frame it citing Roh (2026) for the labour-market mechanism in the discussion section.

2. **Second paper (12 to 24 months)**: Idea E (LLM-based deficiency mining → restatement prediction). The measurement-contribution paper. Builds infrastructure to be reused in subsequent projects.

3. **Third paper / dissertation chapter (18 to 30 months)**: Idea A or Idea B (office-level workforce strategy responses or cross-office spillovers). The "big" labour-market spillover paper, leveraging the LLM exposure measures from paper two. Directly extends Roh (2026) into the audit setting.

4. **Optional fourth paper / collaborative**: Idea D (audit committee network spillovers). Could be a collaboration with Cam or Ahmed given the governance angle.

Decision point: whether to use Roh as a featured reference (in which case my contribution is "Roh's logic, applied to a labour-intensive professional services setting") or as a methodological cite (in which case my contribution is the audit-specific mechanisms). The first framing is easier for top-three publication if Roh's paper continues to receive attention; the second is more conservative.

---

## 8. Open Questions for Supervisor Discussion

1. **Sequencing**: Does the proposed paper-pipeline order make sense given my existing commitments (disaster-audit quality paper, registered report, SEC EDGAR project)? Should Idea C be first given EDGAR project synergy, or should I prioritise something else?
2. **LinkedIn data access**: What are Monash's institutional channels for accessing Revelio Labs / LinkUp / Lightcast for office-level workforce data? Is there an existing licence I can leverage?
3. **Roh framing**: Is it appropriate to lean heavily on Roh (2026, *TAR*) as a conceptual template, given it's so recent? Or should I be more conservative and frame contributions independently?
4. **Co-authorship**: Are any of these ideas suitable for inclusion in existing collaborations (e.g., expanding the SEC EDGAR project to inspection events with Qinfang/Qiuhong)?
5. **Risk management**: Which idea has the cleanest identification given current data access? Idea C looks cleanest (event-study around release dates), but Idea E might be lower-risk because it's largely a measurement paper.
6. **Methodological positioning**: For Idea E, should the contribution be framed as (a) a measurement paper introducing a new exposure measure, or (b) a substantive paper on restatement prediction? The framing affects target journal.
7. **Form AP scope**: Form AP only became mandatory in January 2017, giving me roughly 8 to 9 years of partner-level data. Is this enough power for staggered DiD designs that require pre/post variation, especially for the labour-market ideas?
8. **Geographic generalisation**: Should I be concerned about the US-centric nature of these designs? Are there parallel international settings (FRC inspections in the UK, CPAB in Canada, AFM in the Netherlands) worth exploring as robustness or extensions?

---

## 9. References

1. Acito, A. A., Hogan, C. E., & Imdieke, A. J. (2019). Realising auditor responses to PCAOB Part II inspection reports. *The Accounting Review*, 94(4), 1-26.
2. Ahn, J., Hoitash, R., & Hoitash, U. (2018). Auditor task-specific expertise: The case of fair-value accounting. *The Accounting Review*, 95(3), 1-32.
3. Aobdia, D. (2018). The impact of the PCAOB individual engagement inspection process: Preliminary evidence. *The Accounting Review*, 93(4), 53-80.
4. Aobdia, D. (2019). Do practitioner assessments agree with academic proxies for audit quality? Evidence from PCAOB and internal inspections. *Journal of Accounting and Economics*, 67(1), 144-174.
5. Aobdia, D. (2019). Why shouldn't higher-quality auditors be allowed to provide non-audit services to their clients? Evidence from the PCAOB. *The Accounting Review*, 94(2), 1-29.
6. Aobdia, D., Lin, C. J., & Petacchi, R. (2015). Capital-market consequences of audit partner quality. *The Accounting Review*, 90(6), 2143-2176.
7. Aobdia, D., & Shroff, N. (2017). Regulatory oversight and auditor market share. *Journal of Accounting and Economics*, 63(2-3), 262-287.
8. Beck, M. J., Gunn, J. L., & Hallman, N. (2019). The geographic decentralisation of audit firms and audit quality. *Contemporary Accounting Research*, 36(4), 2105-2138.
9. Boone, J. P., Khurana, I. K., & Raman, K. K. (2015). Did the 2007 PCAOB disciplinary order against Deloitte impose actual costs on the firm or improve its audit quality? *The Accounting Review*, 90(2), 405-441.
10. Burke, J. J., Hoitash, R., & Hoitash, U. (2019). Audit partner identification and characteristics: Evidence from US Form AP filings. *Auditing: A Journal of Practice & Theory*, 38(3), 71-94.
11. Callaway, B., & Sant'Anna, P. H. C. (2021). Difference-in-differences with multiple time periods. *Journal of Econometrics*, 225(2), 200-230.
12. Cao, Y., Chen, X., Lin, C. J., & Petacchi, R. (2025). The KPMG Part II disclosure: Evidence on the consequences of unremediated quality control criticisms. *Auditing: A Journal of Practice & Theory*, forthcoming.
13. Carcello, J. V., Hollingsworth, C., & Mastrolia, S. A. (2011). The effect of PCAOB inspections on Big 4 audit quality. *Research in Accounting Regulation*, 23(2), 85-96.
14. Christensen, B. E., Lundstrom, N. G., & Newton, N. J. (2022). Does the disclosure of PCAOB inspection findings increase audit firms' litigation exposure? *Auditing: A Journal of Practice & Theory*, 41(2), 1-23.
15. DeFond, M. L., & Lennox, C. S. (2011). The effect of SOX on small auditor exits and audit quality. *Journal of Accounting and Economics*, 52(1), 21-40.
16. DeFond, M. L., & Lennox, C. S. (2017). Do PCAOB inspections improve the quality of internal control audits? *Journal of Accounting Research*, 55(3), 591-627.
17. Drake, M. S., Goldman, N. C., Lusch, S. J., & Schmidt, J. J. (2024). What does the PCAOB find? A topic-modelling approach to inspection report content. *Working paper*.
18. Drake, M. S., Roulstone, D. T., & Thornock, J. R. (2015). The determinants and consequences of information acquisition via EDGAR. *Contemporary Accounting Research*, 32(3), 1128-1161.
19. Ege, M. S., Knechel, W. R., Thomas, P. B., & Stuber, S. B. (2021). PCAOB inspections of foreign auditors and audit quality: Evidence from cross-listed firms. *Contemporary Accounting Research*, 38(3), 2129-2170.
20. Goodman-Bacon, A. (2021). Difference-in-differences with variation in treatment timing. *Journal of Econometrics*, 225(2), 254-277.
21. Hu, J., Smith, J. L., & Wong, R. M. K. (2025). Audit office personnel turnover and audit quality: Evidence from LinkedIn data. *Journal of Business Finance and Accounting*, forthcoming.
22. Khurana, I. K., Lundstrom, N. G., & Raman, K. K. (2021). PCAOB inspections and the differential audit quality effect for Big 4 and non-Big 4 auditors. *Contemporary Accounting Research*, 38(1), 376-411.
23. Krishnan, G. V., Krishnan, J., & Song, H. (2025). Labour market consequences of PCAOB and SEC enforcement actions for individual auditors. *Journal of Accounting Research*, forthcoming.
24. Lamoreaux, P. T. (2016). Does PCAOB inspection access improve audit quality? An examination of foreign firms listed in the United States. *Journal of Accounting and Economics*, 61(2-3), 313-337.
25. Lamoreaux, P. T., Mauler, L. M., & Newton, N. J. (2020). Audit firm reputation and PCAOB inspection access in cost of equity capital. *Contemporary Accounting Research*, 37(2), 854-893.
26. Lamoreaux, P. T., Mowchan, M., & Zhang, W. (2023). Spillover effects of PCAOB enforcement on non-sanctioned auditors. *The Accounting Review*, 98(4), 281-310.
27. Lee, C. M. C., Ma, P., & Wang, C. C. Y. (2015). Search-based peer firms: Aggregating investor perceptions through internet co-searches. *Journal of Financial Economics*, 116(2), 410-431.
28. Lee, J. E., Lee, M., & Pittman, J. (2021). Auditor labour market structure and audit quality. *The Accounting Review*, 96(2), 247-275.
29. Lennox, C. S., & Pittman, J. A. (2010). Auditing the auditors: Evidence on the recent reforms to the external monitoring of audit firms. *Journal of Accounting and Economics*, 49(1-2), 84-103.
30. Lennox, C. S., & Wu, X. (2018). A review of the archival literature on audit partners. *Accounting Horizons*, 32(2), 1-35.
31. Oster, E. (2019). Unobservable selection and coefficient stability: Theory and evidence. *Journal of Business and Economic Statistics*, 37(2), 187-204.
32. Roh, Y. (2026). When large employers come to town: Labour market entry and corporate disclosure. *The Accounting Review*, forthcoming. https://doi.org/10.2308/TAR-2024-0309
33. Shroff, N. (2020). Real effects of PCAOB international inspections. *The Accounting Review*, 95(5), 399-433.
34. Sun, L., & Abraham, S. (2021). Estimating dynamic treatment effects in event studies with heterogeneous treatment effects. *Journal of Econometrics*, 225(2), 175-199.
35. Westermann, K. D., Cohen, J., & Trompeter, G. (2019). PCAOB inspections: Public accounting firms on "trial". *Contemporary Accounting Research*, 36(2), 694-731.

---

*End of discussion document v1.*
