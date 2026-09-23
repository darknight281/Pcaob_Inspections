"""Offline tests on synthetic fixtures: extraction, rule coder, LLM schema/validation, diagnostics.

No network and no API calls. Run: pytest explorations/qc_criticism_taxonomy/tests
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pymupdf
import pytest
from qclib.config import load_taxonomy
from qclib.diagnostics import (
    cohen_kappa,
    family_indicators,
    krippendorff_alpha_nominal,
    phi_matrix,
    unsupervised_alignment,
    weighted_log_odds,
)
from qclib.extract import extract_document, extract_text, is_heading
from qclib.llm import request_params, unit_schema, validate_unit
from qclib.rules import classify_response, classify_unit

FIXTURE = Path(__file__).parent / "fixtures" / "synthetic_released_report.txt"
SEED = 20260923


@pytest.fixture(scope="module")
def tax():
    return load_taxonomy()


@pytest.fixture(scope="module")
def fixture_text() -> str:
    # Paragraphs in the fixture are separated by blank lines, as blocks_to_text produces.
    return FIXTURE.read_text(encoding="utf-8")


# --- Extraction ---------------------------------------------------------------------------------


def test_section_skips_toc_and_segments_units(fixture_text, tax):
    res = extract_text(fixture_text, tax, "doc1")
    assert res.log["section_found"]
    headings = [u["heading"] for u in res.units]
    assert headings == [None, "A. Engagement Quality Review", "B. Independence", "C. Personnel Management"]
    assert res.units[0]["is_boilerplate"]  # §104(g)(2) preamble
    assert not any(u["is_boilerplate"] for u in res.units[1:])
    assert "Issuer A, the engagement team" not in " ".join(u["text"] for u in res.units)  # Part I excluded
    assert res.response_text and res.response_text.startswith("RESPONSE OF THE FIRM")


def test_heading_detector():
    assert is_heading("A. Engagement Quality Review")
    assert is_heading("Independence")
    assert not is_heading("The firm's policies do not require that partners have appropriate competence.")


def test_pdf_roundtrip(tmp_path, fixture_text, tax):
    pdf = tmp_path / "synthetic.pdf"
    doc = pymupdf.open()
    for par in fixture_text.split("\n\n"):  # one paragraph per page keeps block order deterministic
        assert doc.new_page().insert_textbox(pymupdf.Rect(72, 72, 540, 770), par.strip(), fontsize=10) >= 0
    doc.save(pdf)
    res = extract_document(pdf, tax, "pdf1")
    assert res.log["section_found"], res.log
    assert res.log["n_substantive_units"] >= 3


# --- Rule coder ---------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("text", "primary", "form"),
    [
        (
            "The inspection results indicate that the firm's system of quality control does not provide reasonable "
            "assurance that engagement teams test controls with a review element at a sufficient level of precision.",
            "EXE_CONTROLS",
            "PATTERN",
        ),
        (
            "The firm's policies do not require that an engagement quality review be completed before the firm "
            "grants permission for the client to use its report.",
            "MON_EQR",
            "DESIGN",
        ),
        (
            "Firm personnel did not comply with the firm's policies requiring the reporting of financial holdings.",
            "OBJ_INDEP",
            "OPERATION",
        ),
    ],
)
def test_codebook_examples(tax, text, primary, form):
    out = classify_unit(text, tax)
    assert out["primary_code"] == primary
    assert out["form"] == form


def test_root_cause_and_multilabel(tax):
    text = (
        "Partner evaluations give little weight to audit quality, and the deficiencies observed appear to "
        "result from this emphasis on compensation and promotion."
    )
    out = classify_unit(text, tax)
    assert out["primary_family"] == "INC"
    assert out["root_cause_stated"] and out["root_cause_family"] == "INC"


def test_boilerplate_is_other(tax):
    assert (
        classify_unit("Section 104(g)(2) restricts disclosure.", tax, is_boilerplate=True)["primary_code"]
        == "OTHER"
    )


def test_response_coder(fixture_text, tax):
    resp = fixture_text[fixture_text.index("PART III RESPONSE") :]
    out = classify_response(resp, tax)
    assert out["stance"] == "ACCEPT_WITH_CONTEXT"
    assert {"ACT_TRAINING", "ACT_STAFFING", "ACT_INDEPENDENCE_SYSTEMS", "ACT_ENGAGEMENT_REWORK"} <= set(
        out["actions"]
    )
    assert out["specificity"] == "SPECIFIC" and out["mentions_root_cause"]


# --- LLM helpers (no API call) ------------------------------------------------------------------


def test_schema_and_params(tax):
    schema = unit_schema(tax)
    assert schema["additionalProperties"] is False
    assert set(schema["required"]) == set(schema["properties"])
    assert "MON_EQR" in schema["properties"]["primary_code"]["enum"]
    params = request_params("units", tax, "u1", "some text")
    assert params["system"][0]["cache_control"] == {"type": "ephemeral"}
    assert "<codebook>" in params["system"][0]["text"]
    assert params["output_config"]["format"]["type"] == "json_schema"
    # The system prompt must be identical across items for prompt caching to hit.
    assert params["system"] == request_params("units", tax, "u2", "other text")["system"]


def test_validate_unit_repairs(tax):
    raw = {
        "codes": ["EXE_SUPERV"],
        "primary_code": "MON_EQR",
        "form": "PATTERN",
        "root_cause_stated": False,
        "root_cause_family": "INC",
        "evidence_quote": "not in text",
        "confidence": "high",
        "notes": "",
    }
    clean, issues = validate_unit(raw, tax, "The reviewer did not evaluate judgments.")
    assert clean["codes"][0] == "MON_EQR" and clean["primary_family"] == "MON"
    assert clean["root_cause_family"] == "NONE"
    assert set(issues) == {
        "primary_not_in_codes",
        "root_cause_family_without_statement",
        "quote_not_verbatim",
    }


# --- Diagnostics --------------------------------------------------------------------------------


def test_reliability_stats():
    a = pd.Series(list("AABBC"))
    assert cohen_kappa(a, a) == pytest.approx(1.0)
    ratings = pd.DataFrame({"c1": list("AABBC"), "c2": list("AABBC")})
    assert krippendorff_alpha_nominal(ratings) == pytest.approx(1.0)
    # Krippendorff (2011) worked example, nominal data with missing values: α ≈ 0.743.
    k = pd.DataFrame(
        {
            "A": [1, 2, 3, 3, 2, 1, 4, 1, 2, None, None, None],
            "B": [1, 2, 3, 3, 2, 2, 4, 1, 2, 5, None, 3],
            "C": [None, 3, 3, 3, 2, 3, 4, 2, 2, 5, 1, None],
            "D": [1, 2, 3, 3, 2, 4, 4, 1, 2, 5, 1, None],
        }
    )
    assert krippendorff_alpha_nominal(k) == pytest.approx(0.743, abs=0.001)


def test_structure_diagnostics(tax):
    rng = np.random.default_rng(SEED)
    vocab = {
        "OBJ": "independence financial holdings confirmations tracking personal",
        "MON": "reviewer review significant judgments timely concurring",
        "CAP": "training competence expertise methodology guidance specialists",
    }
    texts, labels = [], []
    for fam, words in vocab.items():
        w = words.split()
        for _ in range(20):
            texts.append(" ".join(rng.choice(w, size=12)))
            labels.append(fam)
    texts, labels = pd.Series(texts), pd.Series(labels)
    ua = unsupervised_alignment(texts, labels, rng, n_perm=200, seed=SEED)
    assert ua["nmi"] > ua["null_p95"] and ua["p_value"] < 0.05
    lo = weighted_log_odds(texts, labels)
    assert lo[lo["group"] == "OBJ"]["term"].head(5).isin(vocab["OBJ"].split()).all()
    ind = family_indicators(
        pd.Series([["OBJ_INDEP"], ["MON_EQR", "EXE_SUPERV"], ["CAP_TRAIN"]]),
        tax.code_family,
        ["OBJ", "MON", "EXE", "CAP"],
    )
    assert ind.shape == (3, 4) and phi_matrix(ind).loc["MON", "EXE"] == pytest.approx(1.0)
