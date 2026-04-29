# PCAOB Inspections — Audit Quality, Labour, and Information Spillovers

A research program by Oliver (Monash University) on the consequences
of PCAOB inspection reports for audit firms, audit offices, audit
labour markets, and capital markets.

This repository hosts the full Claude Code research workflow — agents,
slash commands, paper templates, and quality gates — adapted from
[hugosantanna/clo-author](https://github.com/hugosantanna/clo-author)
(MIT). See `CLAUDE.md` for the project entry point and
`master_supporting_docs/PCAOB_Inspection_Research_Discussion_Notes_v1.md`
for the design document.

---

## Research Program

Five candidate papers, sequenced for the next ~30 months:

| # | Idea | Mechanism | Outcome unit |
|---|---|---|---|
| **C** | EDGAR information spillovers from inspection releases *(first paper)* | Information diffusion via investor co-search | Client firm |
| **E** | LLM textual mining of inspection narratives → restatement prediction | Measurement / NLP exposure score | Client firm |
| **A** | Office-level workforce-strategy responses to deficiencies | Local labour-market reallocation | Audit office |
| **B** | Cross-office spillovers within Big 4 networks | Internal-QC and reputation transmission | Audit office |
| **D** | Audit-committee-network transmission of Part II disclosures | Director-network governance channel | Client firm |

The setting connects to Roh (2026, *TAR*) "When Large Employers Come
to Town" as a conceptual template, applied to a labour-intensive
professional-services industry where labour *is* the production
technology.

**Current focus:** Idea C scoping. See
`quality_reports/plans/2026-04-29_idea_c_scoping.md`.

---

## Repository Layout

```
Pcaob_Inspections/
├── CLAUDE.md                    # Project entry point (read first)
├── MEMORY.md                    # Session memory
├── .claude/                     # Agents, skills, rules, references, hooks
├── Bibliography_base.bib        # Project bibliography
├── paper/                       # LaTeX manuscript (source of truth)
├── data/                        # raw/ and cleaned/ (parquet outputs gitignored)
├── scripts/python/              # Analysis code (Python; pyproject.toml)
├── quality_reports/             # Plans, session logs, reviews, scores
├── master_supporting_docs/      # Project context (research notes, data sources)
├── explorations/                # Research sandbox
├── templates/                   # Document templates
└── guide/                       # Upstream clo-author user manual
```

---

## How the Workflow Operates

This is the clo-author scaffold: a Claude Code agent system organised
into worker–critic pairs (creators write; critics score, never edit),
ten slash commands, weighted quality gates (80/90/95), and 30
journal profiles. Open Claude Code in this repo and start with:

```text
Read CLAUDE.md and continue from the current focus
(quality_reports/plans/2026-04-29_idea_c_scoping.md).
```

Or invoke a slash command directly, e.g.:

```text
/discover literature "PCAOB inspection report release as information event for EDGAR co-search behaviour"
```

The full slash-command and agent reference is in `guide/` (rendered
as a Quarto site in the upstream repo) and summarised in `CLAUDE.md`.

---

## Tooling

| Tool | Purpose | Install |
|---|---|---|
| [Claude Code](https://docs.anthropic.com/en/docs/claude-code) | Agent runtime | `npm install -g @anthropic-ai/claude-code` |
| Python ≥ 3.11 | Analysis (pandas / polars / duckdb) | see `scripts/python/pyproject.toml` |
| XeLaTeX | Paper compilation | TeX Live or MacTeX |
| WRDS access | Audit Analytics, Compustat, CRSP, IBES, BoardEx | institutional |

Python environment setup:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e scripts/python[dev]
```

---

## Attribution

This scaffold is adapted from
[hugosantanna/clo-author](https://github.com/hugosantanna/clo-author)
at commit `65176f7` (v4.2.0, 2026-04-17), which is itself a fork of
[Pedro Sant'Anna's claude-code-my-workflow](https://github.com/pedrohcgs/claude-code-my-workflow).
All upstream agents, rules, hooks, and templates are reused under
the MIT License. See `LICENSE`.

The PCAOB-Inspections-specific content — research notes, bibliography,
plans, and Python tooling — is original work by Oliver.

---

## License

MIT.
