"""PDF text extraction, QC-section detection, and segmentation into criticism units.

The PCAOB report template changed several times (see master_supporting_docs/pcaob_data_structure.md
§1.3), so detection is pattern-based and configurable in taxonomy.yaml. Every document yields an
extraction log row so coverage (gate G1) can be measured.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import pymupdf

from qclib.config import Taxonomy, compile_all

HEADER_FOOTER = re.compile(
    r"^(page \d+( of \d+)?|\d{1,3}|pcaob release no\.?.*|pcaob\s*\|.*|inspection of .{0,80})$",
    re.IGNORECASE,
)
TOC_LINE = re.compile(r"(\.{3,}\s*|\s)\d{1,3}\s*$")
ENUMERATED_HEADING = re.compile(r"^(?:[A-H]|[IVX]{1,4}|\d{1,2}|[a-h])[\.\)]\s+\S")
MAX_HEADING_CHARS = 160
MIN_UNIT_CHARS = 80
MAX_RESPONSE_CHARS = 20_000


@dataclass
class ExtractionResult:
    """Units, response text, and a log row for one document."""

    units: list[dict] = field(default_factory=list)
    response_text: str | None = None
    log: dict = field(default_factory=dict)


def _clean_block(text: str) -> str:
    text = re.sub(r"-\n(?=[a-z])", "", text)  # de-hyphenate line breaks
    text = re.sub(r"\s*\n\s*", " ", text)
    return re.sub(r"\s{2,}", " ", text).strip()


def pdf_to_blocks(pdf_path: Path) -> list[str]:
    """Return cleaned text blocks (roughly paragraphs) in reading order, minus headers/footers."""
    blocks: list[str] = []
    with pymupdf.open(pdf_path) as doc:
        for page in doc:
            for b in page.get_text("blocks", sort=True):
                if b[6] != 0:  # skip image blocks
                    continue
                text = _clean_block(b[4])
                if text and not HEADER_FOOTER.match(text):
                    blocks.append(text)
    return blocks


def blocks_to_text(blocks: list[str]) -> str:
    """Join blocks with blank lines so paragraph boundaries survive."""
    return "\n\n".join(blocks)


def find_section(
    text: str, starts: tuple[re.Pattern, ...], ends: tuple[re.Pattern, ...], min_chars: int
) -> tuple[int, int] | None:
    """Longest span that begins at a start marker and runs to the next end marker.

    Start markers on table-of-contents lines (paragraph ends in a page number or dot leaders) are
    skipped; any remaining TOC hits produce short spans and lose to the real section.
    """
    end_positions = sorted({m.start() for p in ends for m in p.finditer(text)})
    best: tuple[int, int] | None = None
    for p in starts:
        for m in p.finditer(text):
            para_end = text.find("\n\n", m.end())
            para = text[text.rfind("\n\n", 0, m.start()) + 2 : para_end if para_end != -1 else len(text)]
            if TOC_LINE.search(para):
                continue
            stop = next((e for e in end_positions if e >= m.end()), len(text))
            if stop - m.start() >= min_chars and (best is None or stop - m.start() > best[1] - best[0]):
                best = (m.start(), stop)
    return best


def is_heading(par: str) -> bool:
    """Short line without sentence-final punctuation, or an enumerated short line."""
    if len(par) > MAX_HEADING_CHARS:
        return False
    if ENUMERATED_HEADING.match(par) and len(par) < MAX_HEADING_CHARS:
        return not par.rstrip().endswith((".", ";", ":")) or len(par.split()) <= 12
    return not par.rstrip().endswith((".", ";", ":", ",")) and len(par.split()) <= 14


def _any(patterns: tuple[re.Pattern, ...], text: str) -> bool:
    return any(p.search(text) for p in patterns)


def segment_units(section: str, tax: Taxonomy) -> list[dict]:
    """Split a QC section into criticism units (codebook A.1).

    Headings delimit units when present; otherwise a unit starts at each paragraph with an
    anchor sentence ("reasonable assurance", "system of quality control", ...).
    """
    sec_cfg = tax.raw["section"]
    anchors = compile_all(sec_cfg["anchor_sentences"])
    boiler = compile_all(sec_cfg["boilerplate"])
    pars = [p.strip() for p in section.split("\n\n") if p.strip()]
    if not pars:
        return []

    heading_idx = [i for i, p in enumerate(pars) if i > 0 and is_heading(p)]
    groups: list[tuple[str | None, list[str]]] = []
    if heading_idx:
        preamble = pars[: heading_idx[0]]
        if preamble:
            groups.append((None, preamble))
        bounds = heading_idx + [len(pars)]
        for h, nxt in zip(bounds[:-1], bounds[1:], strict=True):
            groups.append((pars[h], pars[h + 1 : nxt]))
    else:
        current: list[str] = []
        for p in pars:
            if _any(anchors, p) and current:
                groups.append((None, current))
                current = []
            current.append(p)
        if current:
            groups.append((None, current))

    units: list[dict] = []
    for heading, body in groups:
        body_text = " ".join(body).strip()
        if not body_text and heading is None:
            continue
        text = f"{heading}. {body_text}".strip(". ") if heading else body_text
        # Judge anchors/boilerplate on prose only: section titles repeat "system of quality control".
        prose = " ".join(p for p in body if not is_heading(p))
        if heading is None and units and len(body_text) < MIN_UNIT_CHARS and not _any(anchors, prose):
            units[-1]["text"] += " " + text  # fold unheaded fragments into the previous unit
            continue
        units.append(
            {
                "heading": heading,
                "text": text,
                "is_boilerplate": _any(boiler, prose) and not _any(anchors, prose),
            }
        )
    return units


def find_response(text: str, tax: Taxonomy, after: int = 0) -> str | None:
    """Firm response: from the last response marker after `after` to the end (capped)."""
    pats = compile_all(tax.raw["section"]["response_start"])
    hits = [m.start() for p in pats for m in p.finditer(text) if m.start() >= after]
    if not hits:
        return None
    return text[max(hits) :][:MAX_RESPONSE_CHARS]


def extract_text(text: str, tax: Taxonomy, doc_id: str) -> ExtractionResult:
    """Locate the QC section and response in already-extracted text."""
    sec_cfg = tax.raw["section"]
    span = find_section(
        text,
        compile_all(sec_cfg["start"]),
        compile_all(sec_cfg["end"]),
        int(sec_cfg["min_section_chars"]),
    )
    res = ExtractionResult(log={"doc_id": doc_id, "n_chars": len(text), "section_found": span is not None})
    if span is None:
        res.log.update(n_units=0, n_substantive_units=0, response_found=False)
        return res
    units = segment_units(text[span[0] : span[1]], tax)
    for k, u in enumerate(units, start=1):
        u["unit_id"] = f"{doc_id}_u{k:02d}"
        u["doc_id"] = doc_id
    res.units = units
    res.response_text = find_response(text, tax, after=span[0])
    res.log.update(
        section_chars=span[1] - span[0],
        n_units=len(units),
        n_substantive_units=sum(not u["is_boilerplate"] for u in units),
        response_found=res.response_text is not None,
    )
    return res


def extract_document(pdf_path: Path, tax: Taxonomy, doc_id: str) -> ExtractionResult:
    """PDF → blocks → text → section → units (+ response)."""
    try:
        text = blocks_to_text(pdf_to_blocks(pdf_path))
    except (RuntimeError, ValueError, pymupdf.FileDataError) as err:
        return ExtractionResult(log={"doc_id": doc_id, "error": f"{type(err).__name__}: {err}"})
    res = extract_text(text, tax, doc_id)
    res.log["is_scanned_suspect"] = len(text) < 500  # image-only PDFs need OCR
    return res


__all__ = [
    "ExtractionResult",
    "blocks_to_text",
    "extract_document",
    "extract_text",
    "find_response",
    "find_section",
    "is_heading",
    "pdf_to_blocks",
    "segment_units",
]
