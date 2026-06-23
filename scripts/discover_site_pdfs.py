#!/usr/bin/env python3
"""Discover publicly linked PDF URLs on a website.

Examples:
  python scripts/discover_site_pdfs.py --start-url https://www.languagekey.com
  python scripts/discover_site_pdfs.py --start-url https://www.languagekey.com/business_email.pdf --max-pages 200
"""

from __future__ import annotations

import argparse
import collections
import json
import sys
import time
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable
from urllib.parse import urljoin, urlparse, urlunparse
from urllib.request import Request, urlopen


USER_AGENT = "bmail-pdf-discovery/1.0 (+https://github.com/incognia/bmail)"


class LinkExtractor(HTMLParser):
    """Extract href/src style links from HTML."""

    def __init__(self) -> None:
        super().__init__()
        self.links: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_map = {k.lower(): v for k, v in attrs if v}
        if tag.lower() in {"a", "link"} and "href" in attrs_map:
            self.links.add(attrs_map["href"])
        if tag.lower() in {"img", "script", "iframe", "embed", "source"} and "src" in attrs_map:
            self.links.add(attrs_map["src"])


def normalize_url(url: str, base: str | None = None) -> str | None:
    if base:
        url = urljoin(base, url)
    parsed = urlparse(url.strip())
    if parsed.scheme not in {"http", "https"}:
        return None
    clean = parsed._replace(fragment="")
    return urlunparse(clean)


def is_pdf_url(url: str) -> bool:
    path = urlparse(url).path.lower()
    return path.endswith(".pdf")


def is_same_domain(url: str, seed_netloc: str) -> bool:
    netloc = urlparse(url).netloc.lower()
    seed = seed_netloc.lower()
    return netloc == seed or netloc.endswith("." + seed)


def fetch_url(url: str, timeout: float) -> tuple[str | None, bytes]:
    req = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=timeout) as resp:
        ctype = resp.headers.get("Content-Type")
        data = resp.read()
        return ctype, data


def decode_html(data: bytes) -> str:
    for enc in ("utf-8", "latin-1"):
        try:
            return data.decode(enc, errors="ignore")
        except UnicodeDecodeError:
            continue
    return data.decode(errors="ignore")


def crawl_for_pdfs(
    seeds: Iterable[str],
    *,
    max_pages: int,
    max_depth: int,
    same_domain_only: bool,
    timeout: float,
    delay: float,
) -> tuple[list[str], int]:
    seed_list = list(seeds)
    if not seed_list:
        return [], 0

    seed_netloc = urlparse(seed_list[0]).netloc
    queue: collections.deque[tuple[str, int]] = collections.deque((u, 0) for u in seed_list)
    visited_pages: set[str] = set()
    found_pdfs: set[str] = set()

    while queue and len(visited_pages) < max_pages:
        url, depth = queue.popleft()
        if url in visited_pages:
            continue
        if same_domain_only and not is_same_domain(url, seed_netloc):
            continue

        visited_pages.add(url)

        try:
            ctype, data = fetch_url(url, timeout=timeout)
        except Exception:
            continue

        ctype_low = (ctype or "").lower()
        if is_pdf_url(url) or "application/pdf" in ctype_low or data.startswith(b"%PDF-"):
            found_pdfs.add(url)
            continue

        if "text/html" not in ctype_low and ctype is not None:
            continue

        html = decode_html(data)
        parser = LinkExtractor()
        parser.feed(html)

        for raw_link in parser.links:
            normalized = normalize_url(raw_link, base=url)
            if not normalized:
                continue
            if same_domain_only and not is_same_domain(normalized, seed_netloc):
                continue
            if is_pdf_url(normalized):
                found_pdfs.add(normalized)
                continue
            if depth < max_depth and normalized not in visited_pages:
                queue.append((normalized, depth + 1))

        if delay > 0:
            time.sleep(delay)

    return sorted(found_pdfs), len(visited_pages)


def build_download_name(url: str) -> str:
    parsed = urlparse(url)
    name = Path(parsed.path).name
    if not name:
        name = "downloaded.pdf"
    if not name.lower().endswith(".pdf"):
        name = f"{name}.pdf"
    return name


def download_pdfs(urls: list[str], downloads_dir: Path, timeout: float) -> list[dict[str, str]]:
    downloads_dir.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, str]] = []

    for url in urls:
        base_name = build_download_name(url)
        target = downloads_dir / base_name
        stem = target.stem
        suffix = target.suffix
        counter = 1
        while target.exists():
            target = downloads_dir / f"{stem}-{counter}{suffix}"
            counter += 1

        try:
            req = Request(url, headers={"User-Agent": USER_AGENT})
            with urlopen(req, timeout=timeout) as resp:
                data = resp.read()
            target.write_bytes(data)
            results.append({"url": url, "file": str(target), "status": "downloaded"})
        except Exception as exc:
            results.append({"url": url, "file": str(target), "status": "error", "error": str(exc)})

    return results


def build_seeds(start_url: str) -> list[str]:
    seeds: list[str] = []
    normalized = normalize_url(start_url)
    if not normalized:
        return seeds
    seeds.append(normalized)

    parsed = urlparse(normalized)
    if parsed.path.lower().endswith(".pdf"):
        site_root = f"{parsed.scheme}://{parsed.netloc}/"
        parent = normalized.rsplit("/", 1)[0] + "/"
        for candidate in (site_root, parent):
            if candidate not in seeds:
                seeds.append(candidate)
    return seeds


def main() -> None:
    parser = argparse.ArgumentParser(description="Discover publicly linked PDF URLs on a website.")
    parser.add_argument("--start-url", required=True, help="Initial URL to start crawling from.")
    parser.add_argument("--max-pages", type=int, default=200, help="Max pages to fetch (default: 200).")
    parser.add_argument("--max-depth", type=int, default=3, help="Max crawl depth from seeds (default: 3).")
    parser.add_argument("--timeout", type=float, default=12.0, help="HTTP timeout seconds (default: 12).")
    parser.add_argument("--delay", type=float, default=0.0, help="Delay between requests in seconds (default: 0).")
    parser.add_argument(
        "--allow-external",
        action="store_true",
        help="Allow crawling links outside the start URL domain.",
    )
    parser.add_argument(
        "--downloads-dir",
        default="downloads",
        help="Directory where discovered PDFs will be downloaded (default: downloads).",
    )
    parser.add_argument(
        "--no-download",
        action="store_true",
        help="Only discover URLs; do not download files.",
    )
    parser.add_argument(
        "--json-output",
        default="",
        help="Optional output path for JSON results. If omitted, JSON is printed to stdout.",
    )
    args = parser.parse_args()

    seeds = build_seeds(args.start_url)
    if not seeds:
        raise SystemExit(f"Invalid --start-url: {args.start_url}")

    pdfs, visited = crawl_for_pdfs(
        seeds,
        max_pages=args.max_pages,
        max_depth=args.max_depth,
        same_domain_only=not args.allow_external,
        timeout=args.timeout,
        delay=args.delay,
    )

    downloads_dir = Path(args.downloads_dir)
    download_results: list[dict[str, str]] = []
    if not args.no_download and pdfs:
        download_results = download_pdfs(pdfs, downloads_dir=downloads_dir, timeout=args.timeout)

    result = {
        "start_url": args.start_url,
        "seed_urls": seeds,
        "visited_pages": visited,
        "pdf_urls_found": len(pdfs),
        "pdf_urls": pdfs,
        "downloads_dir": str(downloads_dir),
        "downloads": download_results,
    }

    payload = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.json_output:
        Path(args.json_output).write_text(payload, encoding="utf-8")
    else:
        sys.stdout.write(payload)


if __name__ == "__main__":
    main()
