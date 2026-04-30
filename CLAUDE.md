# CLAUDE.MD -- PCAOB Inspections Research Program

<!-- HOW TO USE: Keep this file under ~150 lines — Claude loads it every session.
     Scaffold adapted from hugosantanna/clo-author @ 65176f7 (MIT). See guide/
     for the upstream user manual; see master_supporting_docs/ for project context. -->

**Project:** PCAOB Inspections — Audit Quality, Labour, and Information Spillovers
**Author:** Oliver (Monash University)
**Prospective collaborators:** Cam, Ahmed (and SEC EDGAR project: Qinfang, Qiuhong)
**Field:** Accounting / Auditing (with audit labour-economics and information-economics framing)
**Analysis language:** Python (3.11+) — pandas for small data, polars + duckdb for large
**Branch:** main

---

## Research Program in Brief

Five candidate papers exploiting the PCAOB inspection regime
(established 2002; Form AP partner-disclosure since 31 Jan 2017):

1. **Idea A** — Office-level workforce-strategy responses to deficiencies (LinkedIn-derived)
2. **Idea B** — Cross-office spillovers within Big 4 networks
3. **Idea C** — EDGAR information spillovers from inspection-report releases *(first paper)*
4. **Idea D** — Audit-committee-network transmission of Part II disclosures
5. **Idea E** — LLM textual mining of inspection narratives → restatement prediction

See `master_supporting_docs/PCAOB_Inspection_Research_Discussion_Notes_v1.md`
for the full design document, data pipeline, and reference set.

**Current focus:** Idea C scoping (`quality_reports/plans/2026-04-29_idea_c_scoping.md`).

---

## Core Principles

- **Plan first** -- enter plan mode before non-trivial tasks; save plans to `quality_reports/plans/`
- **Verify after** -- compile and confirm output at the end of every task
- **Single source of truth** -- Paper `main.tex` is authoritative; talks and supplements derive from it
- **Quality gates** -- weighted aggregate score; nothing ships below 80/100; see `.claude/rules/quality.md`
- **Worker-critic pairs** -- every creator has a paired critic; critics never edit files
- **Auto-memory** -- corrections and preferences are saved automatically via Claude Code's built-in memory system
- **Branching policy** -- work directly on `main`. Do **not** create feature/topic branches without an explicit user request. Commit and push to `main` for all routine work. If a Claude Code harness rule designates a different branch, it is overridden by this principle.

---

## Data tooling convention

- **`pandas`** for small/medium tabular work (<2 GB in memory); panel construction; final regressions.
- **`polars` (lazy)** and **`duckdb`** for the EDGAR log files (~2 TB), Form AP × Audit Analytics joins, and any analytical pass that would not fit in pandas.
- Materialise final analysis-ready panels as `.parquet` under `data/cleaned/`.
- See `.claude/references/coding-standards-python.md` for the full stack.

### WRDS access (local machine)

WRDS runs from the local machine — credentials are already configured outside the repo:

- `~/.pgpass` holds the WRDS PostgreSQL password (host `wrds-pgdata.wharton.upenn.edu`, port 9737).
- Shell environment variables hold the WRDS username/password for the `wrds` Python package.
- **Never commit credentials.** `.pgpass`, `.env`, and `.claude/state/*` are gitignored; agents must not echo or write secrets into the repo.

**Use the `/db2pq-download` skill** as the canonical path for pulling WRDS tables to local parquet (Audit Analytics, Compustat, CRSP, IBES, BoardEx, ISS Risk Metrics, Revelio Labs). Outputs land under `data/cleaned/*.parquet`. Prefer this over writing ad-hoc `wrds.Connection()` scripts.

Primary data sources (status in `master_supporting_docs/data_sources.md`):

| Source | Access | Use |
|---|---|---|
| PCAOB inspection reports (PDFs) | free, pcaobus.org | Deficiency narratives (Part I.A/I.B/II) |
| Form AP | free, PCAOB | Engagement-partner × issuer × year |
| Audit Analytics | WRDS subscription | Auditor city/office, fees, restatements, ICFR |
| Compustat / CRSP / IBES | WRDS subscription | Financials, market data, forecasts |
| EDGAR log files | free, SEC | Co-search dyads (Idea C) |
| BoardEx / ISS Risk Metrics | WRDS subscription | Audit-committee networks (Idea D) |
| LinkedIn / Revelio Labs / Lightcast | TBD | Office workforce dynamics (Ideas A, B) |

---

## Folder Structure

```
Pcaob_Inspections/
├── CLAUDE.md                    # This file
├── MEMORY.md                    # Session memory and context
├── .claude/                     # Rules, skills, agents, hooks
├── Bibliography_base.bib        # Centralized bibliography (35 refs from research notes)
├── paper/                       # Main LaTeX manuscript (source of truth)
│   ├── main.tex                 # Primary paper file
│   ├── sections/                # Section-level .tex files
│   ├── figures/                 # Generated figures (.pdf, .png)
│   ├── tables/                  # Generated tables (.tex)
│   ├── talks/                   # Beamer presentations
│   ├── quarto/                  # Quarto RevealJS presentations
│   ├── preambles/               # LaTeX headers / shared preamble
│   ├── supplementary/           # Online appendix and supplements
│   └── replication/             # Replication package for deposit
├── data/                        # Project data (raw/ and cleaned/*.parquet gitignored)
├── scripts/python/              # Analysis code (Python; pyproject.toml)
├── quality_reports/             # Plans, session logs, reviews, scores
├── explorations/                # Research sandbox (see rules)
├── templates/                   # Session log, quality report templates
├── master_supporting_docs/      # Project context (research notes, data sources)
└── guide/                       # Upstream clo-author user manual (Quarto site)
```

---

## Commands

```bash
# Paper compilation (latexmk handles multi-pass + biber automatically)
cd paper && latexmk main.tex

# Talk compilation
cd paper/talks && latexmk talk.tex

# Clean auxiliary files
cd paper && latexmk -c

# Python environment (one-time setup)
cd scripts/python && python -m venv ../../.venv && source ../../.venv/bin/activate && pip install -e .[dev]
```

> **Note:** `paper/latexmkrc` configures XeLaTeX, TEXINPUTS, and BIBINPUTS.
> On Overleaf, set compiler to XeLaTeX via Menu > Compiler — Overleaf reads `latexmkrc` automatically.

---

## Quality Thresholds

| Score | Gate | Applies To |
|-------|------|------------|
| 80 | Commit | Weighted aggregate (blocking) |
| 90 | PR | Weighted aggregate (blocking) |
| 95 | Submission | Aggregate + all components >= 80 |
| -- | Advisory | Talks (reported, non-blocking) |

See `.claude/rules/quality.md` for weighted aggregation formula.

---

## Skills Quick Reference

| Command | What It Does |
|---------|-------------|
| `/new-project [topic]` | Full pipeline: idea → paper (orchestrated) |
| `/discover [mode] [topic]` | Discovery: interview, literature, data, ideation |
| `/strategize [mode] [question]` | Identification strategy, pre-analysis plan, or formal theory section (`theory` mode) |
| `/analyze [dataset]` | End-to-end data analysis |
| `/write [section]` | Draft paper sections + humanizer pass (`style-guide` mode extracts voice from prior papers) |
| `/review [file/--flag]` | Quality reviews (routes by target: paper, code, peer) |
| `/revise [report]` | R&R cycle: classify + route referee comments |
| `/talk [mode] [format]` | Create, audit, or compile Beamer presentations |
| `/submit [mode]` | Journal targeting → package → audit → final gate |
| `/tools [subcommand]` | Utilities: commit, compile, validate-bib, journal, etc. |
| `/checkpoint [--flag]` | Session handoff: memory + SESSION_REPORT + research journal (+ Obsidian if configured) |

---

## Beamer Custom Environments (Talks)

| Environment    | Effect                                  | Use Case                                      |
|----------------|-----------------------------------------|-----------------------------------------------|
| `keymsg`       | Full-slide highlighted statement        | Headline takeaway / one-line contribution     |
| `result`       | Boxed numerical result with caption     | Coefficient, magnitude, or test statistic     |

(Placeholders — finalise envs when the first talk preamble is built in `paper/talks/`.)

---

## Output Organization

Output organization: by-script

<!-- by-script:  paper/figures/main_regression/figure1.pdf, paper/tables/main_regression/table1.tex -->
<!-- by-purpose: paper/figures/estimation/coefplot_main.pdf, paper/tables/robustness/alt_controls.tex -->

---

## Current Project State

*Last updated: 2026-04-30*

**Active focus:** Idea C — EDGAR information spillovers from PCAOB inspection-report releases. Scoping phase complete; literature-discovery sprint is the next gate.

| Component       | File                                              | Status                          | Description                                                                 |
|-----------------|---------------------------------------------------|---------------------------------|-----------------------------------------------------------------------------|
| Paper           | `paper/main.tex`                                  | not started — pre-discovery     | First paper: EDGAR information spillovers from PCAOB inspection releases    |
| Idea C plan     | `quality_reports/plans/2026-04-29_idea_c_scoping.md` | scoping complete; 5 open Qs resolved 2026-04-29 | Firm × industry treatment, client-firm outcome, stacked DiD (CS / SA)        |
| Data references | `master_supporting_docs/`                         | schemas captured                | PCAOB/Form AP, WRDS Audit Analytics, WRDS Revelio Labs, replication packages |
| Data pipeline   | `scripts/python/`                                 | not started                     | PDF extraction + WRDS pulls (`/db2pq-download`) + EDGAR joins (polars/duckdb)|
| Replication     | `paper/replication/`                              | not started                     | -                                                                           |
| Job Market Talk | `paper/talks/job_market_talk.tex`                 | not started                     | -                                                                           |

**Immediate next actions** (from `quality_reports/plans/2026-04-29_idea_c_scoping.md`):

1. Run `/discover literature` for Idea C — librarian + librarian-critic produce the literature map and contribution slot.
2. Run `/checkpoint` to instantiate `SESSION_REPORT.md` and `quality_reports/research_journal.md`.
3. Run `/discover data` for Idea C — explorer feasibility-grades the EDGAR + Audit Analytics + PCAOB stack.
4. Use `/db2pq-download` to pull the Audit Analytics tables identified by step 3 into `data/cleaned/`.
