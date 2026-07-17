#!/usr/bin/env python3
"""Nefalix_Urun_ve_Mimari_Aktarim.md → PDF (Türkçe font).

Usage:
  /usr/bin/python3 execution/generate-urun-aktarim-pdf.py
  /usr/bin/python3 execution/generate-urun-aktarim-pdf.py --input docs/foo.md --output docs/foo.pdf
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

from fpdf import FPDF

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_IN = ROOT / "docs" / "Nefalix_Urun_ve_Mimari_Aktarim.md"
DEFAULT_OUT = ROOT / "docs" / "Nefalix_Urun_ve_Mimari_Aktarim.pdf"
FONT_PATH = Path("/Library/Fonts/Arial Unicode.ttf")


class NefalixPdf(FPDF):
    def footer(self):
        self.set_y(-12)
        self.set_font("Nefalix", "", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 8, f"Nefalix Ürün + Mimari Aktarım — s. {self.page_no()}", align="C")


def strip_md_inline(text: str) -> str:
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = text.replace("**", "").replace("`", "")
    return text.strip()


def is_table_row(line: str) -> bool:
    s = line.strip()
    return s.startswith("|") and s.endswith("|") and "|" in s[1:-1]


def is_table_sep(line: str) -> bool:
    s = line.strip()
    if not is_table_row(s):
        return False
    inner = s.strip("|").replace("|", "").strip()
    return bool(inner) and all(c in "-: " for c in inner)


def parse_markdown(md: str) -> list[tuple[str, str]]:
    """Return list of (kind, text). kind: h1|h2|h3|body|bullet|code|table."""
    blocks: list[tuple[str, str]] = []
    in_code = False
    table_buf: list[str] = []

    def flush_table():
        nonlocal table_buf
        if not table_buf:
            return
        rows = [r for r in table_buf if not is_table_sep(r)]
        for row in rows:
            cells = [c.strip() for c in row.strip().strip("|").split("|")]
            blocks.append(("table", " | ".join(strip_md_inline(c) for c in cells)))
        table_buf = []

    for raw in md.splitlines():
        line = raw.rstrip()
        if line.strip().startswith("```"):
            if in_code:
                in_code = False
            else:
                flush_table()
                in_code = True
            continue
        if in_code:
            blocks.append(("code", line))
            continue
        if is_table_row(line):
            table_buf.append(line)
            continue
        flush_table()

        if not line.strip():
            blocks.append(("body", ""))
            continue
        if line.startswith("# "):
            blocks.append(("h1", strip_md_inline(line[2:])))
        elif line.startswith("## "):
            blocks.append(("h2", strip_md_inline(line[3:])))
        elif line.startswith("### "):
            blocks.append(("h3", strip_md_inline(line[4:])))
        elif line.startswith("---"):
            blocks.append(("hr", ""))
        elif line.lstrip().startswith("- ") or line.lstrip().startswith("* "):
            blocks.append(("bullet", strip_md_inline(line.lstrip()[2:])))
        elif re.match(r"^\d+\.\s", line.lstrip()):
            blocks.append(("bullet", strip_md_inline(line.lstrip())))
        else:
            blocks.append(("body", strip_md_inline(line)))

    flush_table()
    return blocks


def build_pdf(blocks: list[tuple[str, str]], out_path: Path) -> None:
    if not FONT_PATH.is_file():
        raise SystemExit(f"Font bulunamadı: {FONT_PATH}")

    pdf = NefalixPdf(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_font("Nefalix", "", str(FONT_PATH))
    pdf.add_font("Nefalix", "B", str(FONT_PATH))
    pdf.add_page()

    w = pdf.w - pdf.l_margin - pdf.r_margin

    for kind, text in blocks:
        if kind == "hr":
            pdf.ln(2)
            pdf.set_draw_color(200, 200, 200)
            pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
            pdf.ln(4)
            continue
        if kind == "body" and not text:
            pdf.ln(2)
            continue

        if kind == "h1":
            pdf.ln(4)
            pdf.set_font("Nefalix", "B", 16)
            pdf.set_text_color(15, 23, 42)
            pdf.multi_cell(w, 9, text)
            pdf.ln(2)
        elif kind == "h2":
            pdf.ln(3)
            pdf.set_font("Nefalix", "B", 13)
            pdf.set_text_color(30, 58, 95)
            pdf.multi_cell(w, 8, text)
            pdf.ln(1)
        elif kind == "h3":
            pdf.ln(2)
            pdf.set_font("Nefalix", "B", 11)
            pdf.set_text_color(51, 65, 85)
            pdf.multi_cell(w, 7, text)
        elif kind == "bullet":
            pdf.set_font("Nefalix", "", 9)
            pdf.set_text_color(30, 30, 30)
            pdf.multi_cell(w, 5, f"• {text}")
        elif kind == "code":
            pdf.set_font("Nefalix", "", 8)
            pdf.set_text_color(60, 60, 60)
            pdf.multi_cell(w, 4.5, text)
        elif kind == "table":
            pdf.set_font("Nefalix", "", 8)
            pdf.set_text_color(30, 30, 30)
            pdf.multi_cell(w, 5, text)
        else:
            pdf.set_font("Nefalix", "", 9)
            pdf.set_text_color(30, 30, 30)
            pdf.multi_cell(w, 5, text)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(out_path))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, default=DEFAULT_IN)
    ap.add_argument("--output", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()
    md = args.input.read_text(encoding="utf-8")
    blocks = parse_markdown(md)
    build_pdf(blocks, args.output)
    print(f"PDF yazıldı: {args.output} ({args.output.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
