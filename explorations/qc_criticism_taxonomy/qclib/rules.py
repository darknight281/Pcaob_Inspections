"""Dictionary (regex) coder for criticism units and firm responses.

This is the transparent baseline against which the LLM and human coders are compared. It follows
codebook.md where a rule can be mechanised: multi-label codes (P7), the primary code taken from the
main assertion (P1), form (A.5), and explicit causal language (P6).
"""

from __future__ import annotations

import re

from qclib.config import Taxonomy, compile_all

SENTENCE_SPLIT = re.compile(r"(?<=[.;])\s+(?=[A-Z(])")
ASSERTION = re.compile(r"reasonable assurance|system of quality control|does not provide", re.IGNORECASE)
ASSERTION_WEIGHT = 3


def split_sentences(text: str) -> list[str]:
    """Crude sentence splitter adequate for PCAOB prose."""
    return [s for s in SENTENCE_SPLIT.split(text) if s.strip()]


def code_hits(text: str, tax: Taxonomy) -> dict[str, int]:
    """Number of pattern matches per code (codes with zero hits omitted)."""
    hits = {c: sum(len(p.findall(text)) for p in pats) for c, pats in tax.code_patterns.items()}
    return {c: n for c, n in hits.items() if n > 0}


def first_position(text: str, code: str, tax: Taxonomy) -> int:
    """Character offset of the code's first pattern match (len(text) if none)."""
    starts = [m.start() for p in tax.code_patterns[code] if (m := p.search(text))]
    return min(starts, default=len(text))


def _primary(text: str, total: dict[str, int], assertion: dict[str, int], tax: Taxonomy) -> str:
    """Highest weight; ties go to the code stated first (codebook P1), then taxonomy order."""
    fam_rank = {f: i for i, f in enumerate(tax.primary_tiebreak)}
    code_rank = {c: i for i, c in enumerate(tax.codes)}

    def key(c: str) -> tuple[int, int, int, int]:
        weight = total[c] + ASSERTION_WEIGHT * assertion.get(c, 0)
        return (-weight, first_position(text, c, tax), fam_rank[tax.code_family[c]], code_rank[c])

    return min(total, key=key)


def classify_form(text: str, tax: Taxonomy) -> str:
    """DESIGN / OPERATION / PATTERN / UNCLEAR; first matching form in taxonomy order wins."""
    for form, pats in tax.form_patterns.items():
        if any(p.search(text) for p in pats):
            return form
    return "UNCLEAR"


def root_cause(text: str, tax: Taxonomy) -> tuple[bool, str]:
    """(stated?, family of the clause following the first causal marker)."""
    for sent in split_sentences(text):
        for p in tax.root_cause_patterns:
            m = p.search(sent)
            if m:
                hits = code_hits(sent[m.end() :], tax)
                if not hits:
                    return True, "NONE"
                fam_hits: dict[str, int] = {}
                for c, n in hits.items():
                    fam_hits[tax.code_family[c]] = fam_hits.get(tax.code_family[c], 0) + n
                return True, max(fam_hits, key=fam_hits.get)
    return False, "NONE"


def classify_unit(text: str, tax: Taxonomy, is_boilerplate: bool = False) -> dict:
    """Rule-based coding of one criticism unit, same fields as the LLM coder."""
    if is_boilerplate:
        return {
            "codes": ["OTHER"],
            "primary_code": "OTHER",
            "primary_family": "OTHER",
            "form": "UNCLEAR",
            "root_cause_stated": False,
            "root_cause_family": "NONE",
        }
    total = code_hits(text, tax)
    if not total:
        codes, primary = ["OTHER"], "OTHER"
    else:
        sentences = split_sentences(text)
        first_assert = next((s for s in sentences if ASSERTION.search(s)), sentences[0] if sentences else "")
        assertion = code_hits(first_assert, tax)
        primary = _primary(text, total, assertion, tax)
        codes = [c for c in tax.codes if c in total]
    stated, rc_family = root_cause(text, tax)
    return {
        "codes": codes,
        "primary_code": primary,
        "primary_family": tax.code_family[primary],
        "form": classify_form(text, tax),
        "root_cause_stated": stated,
        "root_cause_family": rc_family,
    }


def classify_response(text: str, tax: Taxonomy) -> dict:
    """Rule-based coding of a firm response (codebook Part B)."""
    cfg = tax.raw["responses"]
    stance = "NONE"
    for label in ("CONTEST", "ACCEPT_WITH_CONTEXT", "ACCEPT"):
        if any(p.search(text) for p in compile_all(cfg["stance"][label])):
            stance = label
            break
    actions = [a for a, pats in cfg["actions"].items() if any(p.search(text) for p in compile_all(pats))]
    n_specific = sum(len(p.findall(text)) for p in compile_all(cfg["specific_markers"]))
    return {
        "stance": stance,
        "actions": actions or ["ACT_NONE_SPECIFIC"],
        "specificity": "SPECIFIC" if n_specific >= 2 else "GENERIC",
        "mentions_root_cause": any(p.search(text) for p in compile_all(cfg["root_cause_markers"])),
    }
