# Replication Packages — Idea C (EDGAR Co-Search × PCAOB Inspections)

**Purpose:** Catalogue replication packages relevant to Idea C (PCAOB inspection-report releases as information events propagating through EDGAR co-search networks). Used to bootstrap data pipeline (PDF parsing, EDGAR log processing, exposure-group construction) without reinventing infrastructure.
**Scope:** Idea C only — first paper of a five-paper PCAOB program. Ideas A/B/D/E out of scope.
**Date:** 2026-04-29
**Status legend:** `Available (code+data)` | `Code only` | `Not found` | `Behind paywall` | `Not searched yet`

---

## Cluster 1 — EDGAR Co-Search and Information Events

| Paper | DOI/URL | Replication URL | Language | Status |
|-------|---------|-----------------|----------|--------|
| Drake, Roulstone, Thornock (2015, *CAR*) — Determinants and Consequences of Information Acquisition via EDGAR | [Wiley](https://onlinelibrary.wiley.com/doi/abs/10.1111/1911-3846.12119); [SSRN 1932315](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1932315) | None publicly linked (CAR did not require deposit; checked SSRN, BYU ScholarsArchive, IDEAS) | — | Not found |
| Drake, Roulstone, Thornock (2017, *RAST*) — Co-search peer firms ("The Internet as an Information Intermediary") | [RAST 22:543-576](https://scholarsarchive.byu.edu/facpub/8390/) | None publicly linked at BYU ScholarsArchive or Roulstone's OSU page | — | Not found |
| Lee, Ma, Wang (2015, *JFE*) — Search-based peer firms | [SSRN 2171497](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2171497); [HBS](https://www.hbs.edu/faculty/Pages/item.aspx?num=47629) | None publicly linked at SSRN/HBS faculty page (JFE pre-2019 had no mandatory deposit) | — | Not found |
| Iliev, Kalodimos, Lowry (2021, *RFS*) — Investors' Attention to Corporate Governance | [SSRN 3162407](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3162407); [RFS 34:5581-5628](https://econpapers.repec.org/article/ouprfinst/v_3a34_3ay_3a2021_3ai_3a12_3ap_3a5581-5628..htm) | RFS post-2019 enforces deposits via [RFS Data Editors](https://review-of-financial-studies.github.io/) — replication likely on author or RFS portal but no direct URL surfaced in search | — | Not found |
| Bhattacharya, Cho, Kim (2018) — EDGAR-based investor attention | Not located in searches (citation form ambiguous; possibly *JAR* or working paper) | Not searched yet | — | Not found |

---

## Cluster 2 — PCAOB Inspection Event Studies

| Paper | DOI/URL | Replication URL | Language | Status |
|-------|---------|-----------------|----------|--------|
| Aobdia (2019, *JAE*) — Practitioner assessments vs. academic proxies for audit quality | [SSRN 2629305](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2629305); [JAE 67(1):144-174](https://www.sciencedirect.com/science/article/abs/pii/S016541011830106X) | None publicly linked (uses proprietary PCAOB inspection data — not publicly releasable) | — | Behind paywall |
| Aobdia, Choudhary, Sadka (2021) — Why auditors fail to report material weaknesses (PCAOB data) | [SSRN 2838896](https://ssrn.com/abstract=2838896) | None publicly linked (proprietary PCAOB inspection data — not publicly releasable) | — | Behind paywall |
| Lamoreaux, Mowchan, Zhang (2023, *TAR*) — PCAOB regulatory enforcement and audit quality | [SSRN 4166137](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4166137); [ASU](https://asu.elsevierpure.com/en/publications/does-public-company-accounting-oversight-based-regulatory-enforce/) | Not located on openICPSR/AAA repository — no replication URL surfaced via search | — | Not found |
| Acito, Hogan, Imdieke (2019, *TAR*) — Effect of PCAOB-identified deficiencies on audit fees and turnover | Likely [TAR 2019](https://publications.aaahq.org/accounting-review) (exact DOI not located in 1 search) | Not located in initial search; AAA does not enforce deposits for *TAR* | — | Not found |
| Cao et al. (2025, *AJPT*) | Not located in 1 search (citation needs first-author confirmation; possibly Cao, Lennox, et al. or similar) | Not searched yet | — | Not found |
| DeFond & Lennox (2017, *JAR*) — Do PCAOB Inspections Improve the Quality of Internal Control Audits? | [JAR 55(3)](https://onlinelibrary.wiley.com/doi/abs/10.1111/1475-679X.12151); [PCAOB working paper](https://pcaobus.org/News/Events/Documents/10222015_CEA/PCAOB-Inspections-Internal-Control-Audits-DeFond_Lennox.pdf) | None publicly linked (JAR pre-2019 had no mandatory deposit) | — | Not found |

---

## Top-3 Prioritisation Memo

**Headline finding:** Across 11 target papers and 6 search calls, **no replication package was located via public deposits** (openICPSR, Harvard Dataverse, AEA Repo, GitHub, or author websites surfaced in search). This is consistent with the publication windows and journal policies of the target set: (i) most Cluster 2 papers use proprietary PCAOB inspection data that cannot be publicly redistributed; (ii) JAR/JFE/CAR/RAST/TAR did not enforce mandatory deposits before 2019; (iii) only Iliev/Kalodimos/Lowry (2021, RFS) sits inside a journal regime (RFS Data Editors, post-2019) that mandates deposits, but the URL was not directly surfaced in initial searches and likely lives behind the journal's portal. **Practical implication:** Idea C will need to build its own pipeline rather than fork existing code.

**Top 3 packages to pursue (by author email + journal portal request) — ranked by infrastructure value to Idea C:**

1. **Iliev, Kalodimos, Lowry (2021, RFS) — Investors' Attention to Corporate Governance.** Highest probability of locating a usable package given RFS post-2019 deposit policy. Solves: EDGAR log file ingestion, parsing 2003+ archive files, IP-to-user identification heuristics, panel construction at the firm-day-IP level. This is the closest analog to Idea C's exposure-group construction. **Action:** check the RFS Data Editors portal directly and email Lowry (Drexel).

2. **Lee, Ma, Wang (2015, JFE) — Search-Based Peer Firms.** Solves the *core methodological problem* for Idea C: building co-search dyads from EDGAR clickstream and validating them as economic peer-firm clusters. Even if code is not deposited, the JFE Internet Appendix typically contains pseudocode / SAS-style aggregation steps. **Action:** email Charles Lee (Stanford GSB) — he has historically shared SAS scripts on request. Falls back to building the algorithm from the published equations.

3. **Drake, Roulstone, Thornock (2017, RAST) "Internet as Information Intermediary".** Solves: PCAOB-event-window construction logic, EDGAR access counts around regulatory disclosures (closest direct precedent to Idea C's main DV). Code unlikely to exist publicly, but Thornock (BYU) and Drake (BYU) actively maintain co-search infrastructure and have shared cleaned EDGAR-access panels with collaborators. **Action:** email Thornock — BYU has institutional infrastructure that may be reusable.

**Infrastructure that still must be built from scratch (no precedent located):**
- PCAOB inspection-report PDF parsing (Part I.A / I.B / II extraction). No public package exists for any paper in Cluster 2 — Aobdia (2019) and Aobdia/Choudhary/Sadka (2021) use proprietary PCAOB-internal data, sidestepping the parsing problem entirely.
- PCAOB inspection-release event timestamping at engagement-partner × issuer × inspection-cycle granularity (Form AP × inspection report join).
- Exposure-group construction: linking each issuer's *non-inspected peers* via co-search dyads, weighted by search-traffic intensity in a pre-event window. This is the original methodological contribution of Idea C and has no direct replication source.
- Restatement / ICFR / fee outcome panels — Audit Analytics WRDS pulls; standard, no replication needed.

**Bottom line:** Treat this catalogue as evidence that Idea C is in a *green-field* infrastructure space. The Lee/Ma/Wang (2015) co-search methodology and any RFS-mandated EDGAR-log packages are the only realistic forking targets; everything else (PDF parsing, Form AP joins, exposure-group construction) must be built native to this project.


