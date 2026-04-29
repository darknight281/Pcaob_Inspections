# Master Supporting Documents

Project-context documents for the PCAOB Inspections research program.
These are inputs to (not outputs of) the Claude Code workflow — agents
read them when scoping discovery, strategy, and analysis.

## Index

| Document | Purpose |
|---|---|
| `PCAOB_Inspection_Research_Discussion_Notes_v1.md` | Canonical project-context document. Five candidate research ideas (A–E) with detailed walkthroughs, the four-dataset mapping pipeline, the unit-of-analysis framework, the Roh (2026) connection, suggested sequencing, and the supervisor-discussion question set. **Baseline for all subsequent work.** |
| `data_sources.md` | Per-dataset access status (PCAOB reports, Form AP, Audit Analytics, Compustat/CRSP/IBES, EDGAR logs, BoardEx, LinkedIn). |
| `supporting_papers/` | PDF copies of key references when downloaded. |
| `supporting_slides/` | Slide decks from related work. |

## Versioning convention

Discussion documents are versioned in-filename (`_v1`, `_v2`, ...).
The `v1` notes are the supervisor-discussion baseline. Major
revisions (e.g., after the next supervisor session, or after a
substantive idea pivot) should ship as `_v2`, with the prior version
preserved.

## How agents consume these docs

- The **librarian** (literature review) uses these to anchor existing
  citations and identify gaps.
- The **strategist** (identification design) uses §3 (data pipeline)
  and §6 (unit of analysis) when proposing the empirical design.
- The **explorer** (data exploration) uses `data_sources.md` to
  scope what's actually accessible.
