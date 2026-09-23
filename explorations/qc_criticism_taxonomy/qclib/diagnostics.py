"""Feasibility diagnostics: reliability, co-occurrence, lexical distinctiveness, unsupervised structure.

Maps to the go/no-go gates in quality_reports/plans/2026-09-23_qc_criticism_classification_feasibility.md.
"""

from __future__ import annotations

import re
from collections import Counter

import numpy as np
import pandas as pd
from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import adjusted_rand_score, cohen_kappa_score, normalized_mutual_info_score

TOKEN = re.compile(r"[a-z][a-z\-]{2,}")
STOP = frozenset(
    {
        "the",
        "and",
        "that",
        "for",
        "with",
        "its",
        "this",
        "was",
        "were",
        "are",
        "has",
        "have",
        "had",
        "not",
        "does",
        "did",
        "from",
        "which",
        "firm",
        "firm's",
        "audit",
        "audits",
        "auditor",
        "engagement",
        "engagements",
        "issuer",
        "issuers",
        "quality",
        "control",
        "system",
        "reasonable",
        "assurance",
        "provide",
        "provides",
        "policies",
        "procedures",
        "board",
        "pcaob",
        "inspection",
        "report",
        "part",
    }
)


# --- Reliability -------------------------------------------------------------------------------


def cohen_kappa(a: pd.Series, b: pd.Series) -> float:
    """Cohen's κ on aligned nominal labels; NaN if fewer than 2 paired observations."""
    mask = a.notna() & b.notna()
    if mask.sum() < 2:
        return float("nan")
    return float(cohen_kappa_score(a[mask].astype(str), b[mask].astype(str)))


def krippendorff_alpha_nominal(ratings: pd.DataFrame) -> float:
    """Krippendorff's α (nominal) for a units × coders frame; missing ratings allowed.

    Implements the coincidence-matrix formula (Krippendorff 2011, "Computing Krippendorff's Alpha").
    """
    values = sorted({v for v in ratings.stack().dropna().astype(str)})
    if len(values) < 2:
        return float("nan")
    idx = {v: i for i, v in enumerate(values)}
    o = np.zeros((len(values), len(values)), dtype=np.float64)
    for _, row in ratings.iterrows():
        vals = [idx[str(v)] for v in row.dropna()]
        m = len(vals)
        if m < 2:
            continue
        counts = np.bincount(vals, minlength=len(values)).astype(np.float64)
        o += (np.outer(counts, counts) - np.diag(counts)) / (m - 1)
    n_c = o.sum(axis=1)
    n = n_c.sum()
    if n <= 1:
        return float("nan")
    d_o = n - np.trace(o)
    d_e = (n * n - np.sum(n_c**2)) / (n - 1)
    return float(1.0 - d_o / d_e) if d_e > 0 else float("nan")


def multilabel_kappas(a: pd.Series, b: pd.Series, labels: list[str]) -> pd.DataFrame:
    """Per-label κ treating each code as a binary present/absent judgement."""
    rows = []
    for lab in labels:
        xa = a.apply(lambda s, lab=lab: lab in s)
        xb = b.apply(lambda s, lab=lab: lab in s)
        prevalence = float((xa | xb).mean())
        kappa = cohen_kappa(xa, xb) if xa.nunique() + xb.nunique() > 2 else float("nan")
        rows.append({"label": lab, "prevalence_either": prevalence, "kappa": kappa})
    return pd.DataFrame(rows)


# --- Co-occurrence ------------------------------------------------------------------------------


def family_indicators(codes: pd.Series, code_family: dict[str, str], families: list[str]) -> pd.DataFrame:
    """Units × families 0/1 frame from a Series of code lists (any-label)."""
    fam_sets = codes.apply(lambda cs: {code_family[c] for c in cs if c in code_family})
    return pd.DataFrame({f: fam_sets.apply(lambda s, f=f: int(f in s)) for f in families}, index=codes.index)


def phi_matrix(ind: pd.DataFrame) -> pd.DataFrame:
    """Pairwise φ (Pearson on binaries); NaN where a family has no variance."""
    return ind.astype(np.float64).corr(method="pearson")


def lift_matrix(ind: pd.DataFrame) -> pd.DataFrame:
    """Observed / expected co-occurrence under independence."""
    x = ind.to_numpy(dtype=np.float64)
    n = x.shape[0]
    joint = x.T @ x / n
    marg = x.mean(axis=0)
    with np.errstate(divide="ignore", invalid="ignore"):
        lift = joint / np.outer(marg, marg)
    return pd.DataFrame(lift, index=ind.columns, columns=ind.columns)


# --- Lexical distinctiveness --------------------------------------------------------------------


def tokenize(text: str) -> list[str]:
    return [t for t in TOKEN.findall(text.lower()) if t not in STOP]


def weighted_log_odds(
    texts: pd.Series, groups: pd.Series, prior_mass: float = 500.0, top_n: int = 12
) -> pd.DataFrame:
    """Monroe, Colaresi & Quinn (2008) log-odds with informative Dirichlet prior; top z per group."""
    counts = {g: Counter() for g in groups.unique()}
    for t, g in zip(texts, groups, strict=True):
        counts[g].update(tokenize(t))
    total = Counter()
    for c in counts.values():
        total.update(c)
    n_all = sum(total.values())
    if n_all == 0:
        return pd.DataFrame(columns=["group", "term", "z"])
    alpha = {w: prior_mass * c / n_all for w, c in total.items()}
    a0 = prior_mass
    out = []
    for g, cg in counts.items():
        n_g = sum(cg.values())
        n_r = n_all - n_g
        rows = []
        for w, a in alpha.items():
            y_g, y_r = cg.get(w, 0), total[w] - cg.get(w, 0)
            d = np.log((y_g + a) / (n_g + a0 - y_g - a)) - np.log((y_r + a) / (n_r + a0 - y_r - a))
            rows.append((w, d / np.sqrt(1.0 / (y_g + a) + 1.0 / (y_r + a))))
        rows.sort(key=lambda r: -r[1])
        out.extend({"group": g, "term": w, "z": float(z)} for w, z in rows[:top_n])
    return pd.DataFrame(out)


# --- Unsupervised structure ---------------------------------------------------------------------


def unsupervised_alignment(
    texts: pd.Series, labels: pd.Series, rng: np.random.Generator, n_perm: int = 1000, seed: int = 0
) -> dict:
    """TF-IDF → NMF (k = #labels) → argmax cluster; NMI/ARI vs labels with a permutation null."""
    k = labels.nunique()
    if len(texts) < 3 * k or k < 2:
        return {"k": k, "n": len(texts), "nmi": float("nan"), "ari": float("nan"), "p_value": float("nan")}
    tfidf = TfidfVectorizer(stop_words="english", min_df=2, ngram_range=(1, 2), sublinear_tf=True)
    x = tfidf.fit_transform(texts)
    w = NMF(n_components=k, init="nndsvda", random_state=seed, max_iter=500).fit_transform(x)
    clusters = w.argmax(axis=1)
    y = labels.to_numpy()
    nmi = normalized_mutual_info_score(y, clusters)
    null = np.empty(n_perm, dtype=np.float64)
    for b in range(n_perm):
        null[b] = normalized_mutual_info_score(rng.permutation(y), clusters)
    return {
        "k": k,
        "n": len(texts),
        "nmi": float(nmi),
        "ari": float(adjusted_rand_score(y, clusters)),
        "null_p95": float(np.quantile(null, 0.95)),
        "p_value": float((1 + np.sum(null >= nmi)) / (1 + n_perm)),
    }
