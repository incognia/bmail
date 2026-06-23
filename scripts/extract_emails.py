#!/usr/bin/env python3
"""Extract business-email examples from a PDF into templates/example_*.txt files.

Usage example:
  python scripts/extract_emails.py \
    --pdf docs/business_email.pdf \
    --output-dir templates \
    --page-offset -1
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from pypdf import PdfReader


@dataclass
class ExampleRecord:
    page_adjusted: int
    source_page_raw: int
    from_value: str
    to_value: str
    subject: str
    from_to_status: str
    body_lines: list[str]


NOISE_EXACT_SUBSTRINGS = [
    "Published by: The Language Key Ltd",
    "Business English Training Consultants in Hong Kong since 1994",
    "http://www.languagekey.com",
    "enquiry@languagekey.com",
    "FREE TRIAL / PROMO click image",
    "Business Email: Language, Structure and Style",
]

NOISE_LINE_PATTERNS = [
    re.compile(r"(?i)^model email(\b.*)?$"),
    re.compile(r"(?i)^table of contents"),
    re.compile(r"(?i)^opening and referencing$"),
    re.compile(r"(?i)^making enquiries$"),
    re.compile(r"(?i)^informing and notifying$"),
    re.compile(r"(?i)^replies to requests$"),
    re.compile(r"(?i)^clarifying and confirming$"),
    re.compile(r"(?i)^giving advice and making suggestions$"),
    re.compile(r"(?i)^making arrangements$"),
    re.compile(r"(?i)^addressing problems and mistakes$"),
    re.compile(r"(?i)^confirming orders and prices$"),
    re.compile(r"(?i)^general business writing skills$"),
    re.compile(r"(?i)^\(writing to a superior\)$"),
    re.compile(r"(?i)^\(writing to subordinates\)$"),
]

BODY_STOP_PATTERNS = [
    re.compile(r"(?i)^developing a more formal style"),
    re.compile(r"(?i)^writing to a superior or subordinate$"),
    re.compile(r"(?i)^writing to a colleague on the same level$"),
]

RE_SUBJECT = re.compile(r"(?i)^(?:[-•\u2022]\s*)?subject:\s*(.+)\s*$")
RE_FROM = re.compile(r"(?i)^(?:[-•\u2022]\s*)?from:\s*(.+)\s*$")
RE_TO = re.compile(r"(?i)^(?:[-•\u2022]\s*)?to:\s*(.+)\s*$")
BOOK_REFERENCE = (
    "Chris. Business Email: Language, Structure and Style. "
    "The Language Key Ltd, 2015. PDF, 108 pp. Disponible en: http://www.languagekey.com"
)


def normalize_line(line: str) -> str:
    return re.sub(r"\s+", " ", line).strip()


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "no-subject"


def clean_page_lines(raw_text: str) -> list[str]:
    lines: list[str] = []
    for raw in raw_text.splitlines():
        s = normalize_line(raw)
        if not s:
            continue
        if any(token in s for token in NOISE_EXACT_SUBSTRINGS):
            continue
        if re.fullmatch(r"\d+", s):
            continue
        if any(p.search(s) for p in NOISE_LINE_PATTERNS):
            continue
        lines.append(s)
    return lines


def clean_body_lines(lines: Iterable[str]) -> list[str]:
    out: list[str] = []
    prev = None
    for ln in lines:
        s = normalize_line(ln)
        if not s:
            continue
        if any(p.search(s) for p in NOISE_LINE_PATTERNS):
            continue
        if any(p.search(s) for p in BODY_STOP_PATTERNS):
            break
        if RE_FROM.match(s) or RE_TO.match(s) or RE_SUBJECT.match(s):
            continue
        if s == prev:
            continue
        out.append(s)
        prev = s
    return out


def extract_examples(pdf_path: Path, page_offset: int) -> list[ExampleRecord]:
    reader = PdfReader(str(pdf_path))
    records: list[ExampleRecord] = []
    seen: set[tuple[int, str, str]] = set()

    for page_num, page in enumerate(reader.pages, start=1):
        page_lines = clean_page_lines(page.extract_text() or "")
        if not page_lines:
            continue

        subject_positions = [i for i, ln in enumerate(page_lines) if RE_SUBJECT.match(ln)]
        if not subject_positions:
            continue

        for pos, idx in enumerate(subject_positions):
            match_subj = RE_SUBJECT.match(page_lines[idx])
            if not match_subj:
                continue

            subject = normalize_line(match_subj.group(1))
            page_adjusted = max(0, page_num + page_offset)

            # Find From/To around Subject (nearby window)
            from_value = "N/A"
            to_value = "N/A"
            w_start = max(0, idx - 6)
            w_end = min(len(page_lines), idx + 7)
            for j in range(w_start, w_end):
                m_from = RE_FROM.match(page_lines[j])
                m_to = RE_TO.match(page_lines[j])
                if m_from and from_value == "N/A":
                    from_value = normalize_line(m_from.group(1)) or "N/A"
                if m_to and to_value == "N/A":
                    to_value = normalize_line(m_to.group(1)) or "N/A"

            end = subject_positions[pos + 1] if pos + 1 < len(subject_positions) else len(page_lines)
            body_raw = page_lines[idx + 1 : end]
            body_lines = clean_body_lines(body_raw)
            if len(body_lines) < 2:
                continue

            dedupe_key = (page_adjusted, subject.lower(), " ".join(body_lines[:3]).lower())
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)

            records.append(
                ExampleRecord(
                    page_adjusted=page_adjusted,
                    source_page_raw=page_num,
                    from_value=from_value,
                    to_value=to_value,
                    subject=subject,
                    from_to_status="extracted" if from_value != "N/A" and to_value != "N/A" else "n_a",
                    body_lines=body_lines,
                )
            )

    return records


def write_examples(
    output_dir: Path, records: list[ExampleRecord], source_pdf: str, book_reference: str, clean_output: bool
) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    if clean_output:
        for f in output_dir.glob("example_*.txt"):
            f.unlink()

    used: dict[str, int] = {}
    written: list[Path] = []

    for rec in sorted(records, key=lambda r: (r.page_adjusted, r.subject.lower())):
        base = f"example_{rec.page_adjusted:03d}_{slugify(rec.subject)}"
        n = used.get(base, 0) + 1
        used[base] = n
        filename = f"{base}.txt" if n == 1 else f"{base}-{n}.txt"
        path = output_dir / filename

        content = [
            f"Source: {book_reference}",
            f"SourceFile: {source_pdf}",
            f"Page: {rec.page_adjusted}",
            f"From: {rec.from_value}",
            f"To: {rec.to_value}",
            f"Subject: {rec.subject}",
            f"FromToStatus: {rec.from_to_status}",
            "---",
            *rec.body_lines,
            "",
        ]
        path.write_text("\n".join(content), encoding="utf-8")
        written.append(path)

    return written


def rebuild_index(output_dir: Path, index_name: str, source_pdf: str, book_reference: str) -> Path:
    files = sorted(output_dir.glob("example_*.txt"))
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
        pnum = int(re.search(r"\d+", page).group(0)) if re.search(r"\d+", page) else 999
        rows.append((pnum, f.name, page, frm, to, subject, status))

    rows.sort(key=lambda r: (r[0], r[1]))
    total = len(rows)
    na_count = total - with_count

    out_lines = [
        "Business Email Examples Index",
        f"Source: {book_reference}",
        f"SourceFile: {source_pdf}",
        "Page numbering adjusted: cover = 000 (offset -1 from extraction page)",
        f"Total examples: {total}",
        f"With From/To: {with_count}",
        f"With From/To as N/A: {na_count}",
        "",
    ]
    for _, name, page, frm, to, subject, status in rows:
        out_lines.append(
            f"- {name} | page {page} | From: {frm} | To: {to} | Subject: {subject} | status: {status}"
        )
    out_lines.append("")

    index_path = output_dir / index_name
    index_path.write_text("\n".join(out_lines), encoding="utf-8")
    return index_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract email examples from a business-email PDF.")
    parser.add_argument("--pdf", default="docs/business_email.pdf", help="Path to source PDF.")
    parser.add_argument("--output-dir", default="templates", help="Directory where example_*.txt will be generated.")
    parser.add_argument("--index-name", default="business_email_examples_index.txt", help="Index filename inside output-dir.")
    parser.add_argument("--page-offset", type=int, default=-1, help="Page offset (default -1 for cover=000 numbering).")
    parser.add_argument(
        "--clean-output",
        action="store_true",
        default=True,
        help="Remove existing example_*.txt before writing new ones (default: true).",
    )
    parser.add_argument(
        "--no-clean-output",
        action="store_false",
        dest="clean_output",
        help="Keep existing example files and append with collision suffixes.",
    )
    args = parser.parse_args()

    pdf_path = Path(args.pdf)
    if not pdf_path.exists():
        raise SystemExit(f"PDF not found: {pdf_path}")

    output_dir = Path(args.output_dir)
    source_pdf_rel = str(pdf_path).replace(str(Path.cwd()) + "/", "")

    records = extract_examples(pdf_path=pdf_path, page_offset=args.page_offset)
    written = write_examples(
        output_dir=output_dir,
        records=records,
        source_pdf=source_pdf_rel,
        book_reference=BOOK_REFERENCE,
        clean_output=args.clean_output,
    )
    index_path = rebuild_index(
        output_dir=output_dir,
        index_name=args.index_name,
        source_pdf=source_pdf_rel,
        book_reference=BOOK_REFERENCE,
    )

    extracted = sum(1 for r in records if r.from_to_status == "extracted")
    na_count = len(records) - extracted
    print(f"examples_written={len(written)}")
    print(f"with_from_to={extracted}")
    print(f"with_na={na_count}")
    print(f"index_file={index_path}")


if __name__ == "__main__":
    main()
