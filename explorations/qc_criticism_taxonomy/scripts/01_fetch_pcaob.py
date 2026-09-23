"""Step 1 — Collect released QC-criticism reports from pcaobus.org.

Source page: "Firms that Failed to Address Quality Control Criticisms Satisfactorily".

    python explorations/qc_criticism_taxonomy/scripts/01_fetch_pcaob.py   # live fetch
    python .../01_fetch_pcaob.py --html saved_page.html    # page saved from a browser
    python .../01_fetch_pcaob.py --urls my_urls.csv        # CSV with column pdf_url (+ firm_name)
    python .../01_fetch_pcaob.py --follow                  # also crawl linked firm pages

pcaobus.org sits behind Cloudflare. If the live fetch is blocked, save the page from a browser and
use --html. Requests are throttled (≥ 1.5 s apart). Set PCAOB_USER_AGENT to identify the project.
Outputs: data/raw/pcaob/qc_released/*.pdf and qc_reports_index.csv (one row per PDF).
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse

import pandas as pd
import requests
from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from qclib.config import RAW_DIR, REPORTS_INDEX, ROOT  # noqa: E402

LIST_URL = (
    "https://pcaobus.org/oversight/inspections/remediation/"
    "firms-that-failed-to-address-quality-control-criticisms-satisfactorily"
)
USER_AGENT = os.environ.get("PCAOB_USER_AGENT", "Mozilla/5.0 (academic research; PCAOB QC criticism study)")
THROTTLE_SEC = 1.5
YEAR = re.compile(r"(?<!\d)(20[0-2]\d)(?!\d)")
FIRM_PAGE = re.compile(r"/oversight/inspections/firm-inspection-reports/", re.IGNORECASE)


def get(session: requests.Session, url: str) -> requests.Response | None:
    """Throttled GET with up to 3 attempts; returns None on persistent failure."""
    for attempt in range(3):
        time.sleep(THROTTLE_SEC * (attempt + 1))
        try:
            resp = session.get(url, timeout=60)
        except requests.RequestException as err:
            print(f"  ! {url}: {err}")
            continue
        if resp.status_code == 200:
            return resp
        print(f"  ! {url}: HTTP {resp.status_code}")
        if resp.status_code in (403, 404):
            return None
    return None


def parse_links(html: str, base_url: str) -> pd.DataFrame:
    """PDF links (and firm-page links) with the nearest row/list text as firm context."""
    soup = BeautifulSoup(html, "lxml")
    rows = []
    for a in soup.find_all("a", href=True):
        url = urljoin(base_url, a["href"])
        is_pdf = urlparse(url).path.lower().endswith(".pdf")
        if not (is_pdf or FIRM_PAGE.search(url)):
            continue
        container = a.find_parent(["tr", "li", "p"]) or a
        context = " ".join(container.get_text(" ", strip=True).split())
        first_cell = container.find("td") if container.name == "tr" else None
        rows.append(
            {
                "firm_name": (first_cell.get_text(" ", strip=True) if first_cell else "")
                or a.get_text(" ", strip=True),
                "link_text": a.get_text(" ", strip=True),
                "context": context[:400],
                "url": url,
                "is_pdf": is_pdf,
                "year_hint": ";".join(sorted(set(YEAR.findall(context + " " + url)))),
            }
        )
    return (
        pd.DataFrame(rows).drop_duplicates(subset="url")
        if rows
        else pd.DataFrame(columns=["firm_name", "link_text", "context", "url", "is_pdf", "year_hint"])
    )


def rel_to_root(path: Path) -> str:
    """Repository-relative path when possible (portable index), else absolute."""
    return str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)


def report_id(url: str) -> str:
    stem = re.sub(r"[^a-z0-9]+", "-", Path(urlparse(url).path).stem.lower()).strip("-")[:48]
    return f"{stem}-{hashlib.sha1(url.encode()).hexdigest()[:6]}"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--html", type=Path, help="Use a saved copy of the list page instead of fetching it")
    ap.add_argument("--urls", type=Path, help="CSV with a pdf_url column (optional firm_name) to download")
    ap.add_argument("--follow", action="store_true", help="Crawl linked firm pages for further PDFs")
    ap.add_argument("--list-only", action="store_true", help="Write the index without downloading PDFs")
    args = ap.parse_args()

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    if args.urls:
        links = pd.read_csv(args.urls).rename(columns={"pdf_url": "url"})
        links["is_pdf"] = True
        for col in ("firm_name", "link_text", "context", "year_hint"):
            links[col] = links.get(col, "")
    else:
        if args.html:
            html = args.html.read_text(encoding="utf-8", errors="ignore")
        else:
            resp = get(session, LIST_URL)
            if resp is None:
                sys.exit(
                    "List page unreachable (Cloudflare or network). Save it from a browser and rerun with --html."
                )
            html = resp.text
        (RAW_DIR / "list_page_snapshot.html").write_text(html, encoding="utf-8")
        links = parse_links(html, LIST_URL)
        if args.follow:
            extra = []
            for url in links.loc[~links["is_pdf"], "url"]:
                resp = get(session, url)
                if resp is not None:
                    sub = parse_links(resp.text, url)
                    sub["firm_name"] = sub["firm_name"].where(sub["firm_name"] != "", url)
                    extra.append(sub[sub["is_pdf"]])
            if extra:
                links = pd.concat([links, *extra], ignore_index=True).drop_duplicates(subset="url")

    pdfs = links[links["is_pdf"]].copy()
    pdfs["report_id"] = pdfs["url"].map(report_id)
    pdfs["local_path"] = pdfs["report_id"].map(lambda r: rel_to_root(RAW_DIR / f"{r}.pdf"))
    pdfs["downloaded_at"] = ""
    print(f"{len(pdfs)} PDF links found ({(~links['is_pdf']).sum()} non-PDF firm-page links).")

    if not args.list_only:
        for i, row in pdfs.iterrows():
            dest = RAW_DIR / f"{row['report_id']}.pdf"
            if dest.exists() and dest.stat().st_size > 0:
                continue
            resp = get(session, row["url"])
            if resp is not None and resp.content[:4] == b"%PDF":
                dest.write_bytes(resp.content)
                pdfs.at[i, "downloaded_at"] = datetime.now(UTC).isoformat(timespec="seconds")
                print(f"  ✓ {row['report_id']}")
    pdfs.to_csv(REPORTS_INDEX, index=False)
    print(f"Index written: {REPORTS_INDEX}")


if __name__ == "__main__":
    main()
