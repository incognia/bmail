#!/usr/bin/env python3
"""Rebuild templates/business_email_examples_index.txt from existing example_*.txt files.

Usage:
  python scripts/rebuild_index.py --templates-dir templates
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

BOOK_REFERENCE = (
    "Richards, David. Business Email: Language, Structure and Style. "
    "Published by: The Language Key Ltd. Disponible en: https://www.languagekey.com/business_email.pdf"
)


def rebuild_index(templates_dir: Path, index_name: str) -> Path:
    files = sorted(templates_dir.glob("example_*.txt"))
    rows = []
    with_count = 0

    for f in files:
        lines = f.read_text(encoding="utf-8").splitlines()
        page = next((ln.split(":", 1)[1].strip() for ln in lines if ln.startswith("Page:")), "N/A")
        frm = next((ln.split(":", 1)[1].strip() for ln in lines if ln.startswith("From:")), "N/A")
        to = next((ln.split(":", 1)[1].strip() for ln in lines if ln.startswith("To:")), "N/A")
        subject = next((ln.split(":", 1)[1].strip() for ln in lines if ln.startswith("Subject:")), "N/A")
        status = next((ln.split(":", 1)[1].strip() for ln in lines if ln.startswith("FromToStatus:")), "n_a")
        if status == "extracted":
            with_count += 1
        page_num = int(re.search(r"\d+", page).group(0)) if re.search(r"\d+", page) else 999
        rows.append((page_num, f.name, page, frm, to, subject, status))

    rows.sort(key=lambda r: (r[0], r[1]))
    total = len(rows)
    na_count = total - with_count

    output = [
        "Business Email Examples Index",
        f"Source: {BOOK_REFERENCE}",
        "SourceFile: docs/business_email.pdf",
        "Page numbering adjusted: cover = 000 (offset -1 from extraction page)",
        f"Total examples: {total}",
        f"With From/To: {with_count}",
        f"With From/To as N/A: {na_count}",
        "",
    ]
    for _, name, page, frm, to, subject, status in rows:
        output.append(
            f"- {name} | page {page} | From: {frm} | To: {to} | Subject: {subject} | status: {status}"
        )
    output.append("")

    index_path = templates_dir / index_name
    index_path.write_text("\n".join(output), encoding="utf-8")
    return index_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Rebuild index from example_*.txt files.")
    parser.add_argument("--templates-dir", default="templates", help="Directory containing example_*.txt files.")
    parser.add_argument("--index-name", default="business_email_examples_index.txt", help="Index filename.")
    args = parser.parse_args()

    templates_dir = Path(args.templates_dir)
    if not templates_dir.exists():
        raise SystemExit(f"Templates directory not found: {templates_dir}")

    index_path = rebuild_index(templates_dir=templates_dir, index_name=args.index_name)
    print(f"index_file={index_path}")


if __name__ == "__main__":
    main()
