"""Project paths and taxonomy loading. All paths are relative to the repository root
(or to QC_WORKDIR when that environment variable is set)."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import yaml

EXPL_DIR = Path(__file__).resolve().parents[1]
ROOT = EXPL_DIR.parents[1]

TAXONOMY_PATH = EXPL_DIR / "taxonomy.yaml"
CODEBOOK_PATH = EXPL_DIR / "codebook.md"

# QC_WORKDIR redirects all data and outputs (used by the end-to-end smoke test).
_WORKDIR = os.environ.get("QC_WORKDIR")
if _WORKDIR:
    RAW_DIR = Path(_WORKDIR) / "raw"
    CLEAN_DIR = Path(_WORKDIR) / "cleaned"
    OUT_DIR = Path(_WORKDIR) / "output"
else:
    RAW_DIR = ROOT / "data" / "raw" / "pcaob" / "qc_released"
    CLEAN_DIR = ROOT / "data" / "cleaned" / "pcaob"
    OUT_DIR = EXPL_DIR / "output"
FIG_DIR = OUT_DIR / "figures"

REPORTS_INDEX = RAW_DIR / "qc_reports_index.csv"
UNITS_PATH = CLEAN_DIR / "qc_units.parquet"
RESPONSES_PATH = CLEAN_DIR / "qc_responses.parquet"
UNITS_RULES_PATH = CLEAN_DIR / "qc_units_rules.parquet"
RESPONSES_RULES_PATH = CLEAN_DIR / "qc_responses_rules.parquet"
LLM_DIR = CLEAN_DIR / "llm"
MANUAL_UNITS_PATH = RAW_DIR / "qc_units_manual.csv"
HUMAN_CODES_PATH = OUT_DIR / "coding_sample_coded.csv"

FORMS = ("DESIGN", "OPERATION", "PATTERN", "UNCLEAR")
FLAGS = re.IGNORECASE | re.DOTALL


@dataclass(frozen=True)
class Taxonomy:
    """Parsed taxonomy.yaml with compiled regexes."""

    raw: dict
    families: tuple[str, ...]
    code_family: dict[str, str]
    code_patterns: dict[str, tuple[re.Pattern, ...]]
    form_patterns: dict[str, tuple[re.Pattern, ...]]
    root_cause_patterns: tuple[re.Pattern, ...]
    primary_tiebreak: tuple[str, ...]

    @property
    def codes(self) -> tuple[str, ...]:
        return tuple(self.code_family)

    @property
    def substantive_families(self) -> tuple[str, ...]:
        return tuple(f for f in self.families if f != "OTHER")


def compile_all(patterns: list[str]) -> tuple[re.Pattern, ...]:
    """Compile a list of regex strings with the project flags."""
    return tuple(re.compile(p, FLAGS) for p in patterns)


@lru_cache(maxsize=4)
def load_taxonomy(path: Path = TAXONOMY_PATH) -> Taxonomy:
    """Load and compile the taxonomy; `OTHER` is appended as a code of its own."""
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    code_family = {c: spec["family"] for c, spec in raw["codes"].items()}
    code_family["OTHER"] = "OTHER"
    code_patterns = {c: compile_all(spec["patterns"]) for c, spec in raw["codes"].items()}
    form_patterns = {f: compile_all(p) for f, p in raw["forms"].items()}
    return Taxonomy(
        raw=raw,
        families=tuple(raw["families"]),
        code_family=code_family,
        code_patterns=code_patterns,
        form_patterns=form_patterns,
        root_cause_patterns=compile_all(raw["root_cause_patterns"]),
        primary_tiebreak=tuple(raw["primary_tiebreak"]),
    )


def is_annual_firm(firm_name: str, tax: Taxonomy | None = None) -> bool:
    """Approximate annually-inspected status from the firm name."""
    tax = tax or load_taxonomy()
    return any(p.search(firm_name or "") for p in compile_all(tax.raw["annual_firm_patterns"]))
