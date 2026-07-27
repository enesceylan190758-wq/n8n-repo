#!/usr/bin/env python3
"""Nefalix_Urun_Mimarisi.md → PDF (kapak + gerçek tablolar + Türkçe font).

Usage:
  /usr/bin/python3 execution/generate-urun-aktarim-pdf.py
  /usr/bin/python3 execution/generate-urun-aktarim-pdf.py --input docs/foo.md --output docs/foo.pdf
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

from fpdf import FPDF
from fpdf.enums import TableCellFillMode
from fpdf.fonts import FontFace

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_IN = ROOT / "docs" / "Nefalix_Urun_Mimarisi.md"
DEFAULT_OUT = ROOT / "docs" / "Nefalix_Urun_Mimarisi.pdf"
FONT_PATH = Path("/Library/Fonts/Arial Unicode.ttf")

INK = (24, 33, 52)
HEAD = (17, 45, 92)
MUTED = (95, 105, 120)
LINE = (205, 210, 220)
CODE_BG = (243, 245, 248)
TABLE_HEAD_BG = (228, 233, 242)


class NefalixPdf(FPDF):
    show_footer = True

    def footer(self):
        if not self.show_footer:
            return
        self.set_y(-13)
        self.set_font("Nefalix", "", 8)
        self.set_text_color(*MUTED)
        self.cell(0, 8, f"Nefalix Ürün Mimarisi — sayfa {self.page_no()}", align="C")


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


def split_cells(row: str) -> list[str]:
    return [strip_md_inline(c) for c in row.strip().strip("|").split("|")]


def parse_markdown(md: str) -> list[tuple[str, object]]:
    """Blocks: (kind, payload). kinds: h1 h2 h3 body bullet code hr table(list rows)."""
    blocks: list[tuple[str, object]] = []
    in_code = False
    skip_mermaid = False
    table_buf: list[list[str]] = []

    def flush_table():
        nonlocal table_buf
        if table_buf:
            blocks.append(("table", table_buf))
            table_buf = []

    for raw in md.splitlines():
        line = raw.rstrip()
        if line.strip().startswith("```"):
            flush_table()
            fence = line.strip()
            lang = fence[3:].strip().lower()
            if not in_code:
                in_code = True
                skip_mermaid = lang.startswith("mermaid")
                if skip_mermaid:
                    blocks.append(("body", "[Akış diyagramı: kaynak MD’de mermaid — Arif MD/GitHub’da görür]"))
            else:
                in_code = False
                skip_mermaid = False
            continue
        if in_code:
            if skip_mermaid:
                continue
            blocks.append(("code", line))
            continue
        if is_table_row(line):
            if not is_table_sep(line):
                table_buf.append(split_cells(line))
            continue
        flush_table()

        s = line.strip()
        if not s:
            blocks.append(("body", ""))
        elif line.startswith("# "):
            blocks.append(("h1", strip_md_inline(line[2:])))
        elif line.startswith("## "):
            blocks.append(("h2", strip_md_inline(line[3:])))
        elif line.startswith("### "):
            blocks.append(("h3", strip_md_inline(line[4:])))
        elif s.startswith("---"):
            blocks.append(("hr", ""))
        elif s.startswith("- ") or s.startswith("* "):
            blocks.append(("bullet", strip_md_inline(s[2:])))
        elif re.match(r"^\d+\.\s", s):
            blocks.append(("bullet", strip_md_inline(s)))
        else:
            blocks.append(("body", strip_md_inline(line)))

    flush_table()
    return blocks


def add_cover(pdf: NefalixPdf, meta: dict[str, str]) -> None:
    pdf.show_footer = False
    pdf.add_page()
    pdf.set_fill_color(*HEAD)
    pdf.rect(0, 0, pdf.w, 8, style="F")

    pdf.set_y(80)
    pdf.set_font("Nefalix", "B", 26)
    pdf.set_text_color(*HEAD)
    pdf.multi_cell(0, 13, "Nefalix", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Nefalix", "B", 20)
    pdf.set_text_color(*INK)
    pdf.multi_cell(0, 11, "Ürün Mimarisi", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(10)
    pdf.set_draw_color(*LINE)
    pdf.line(pdf.w / 2 - 30, pdf.get_y(), pdf.w / 2 + 30, pdf.get_y())
    pdf.ln(12)

    pdf.set_font("Nefalix", "", 12)
    pdf.set_text_color(*MUTED)
    for key in ("Sürüm", "Tarih", "Hedef okuyucu"):
        if key in meta:
            pdf.multi_cell(0, 8, f"{key}: {meta[key]}", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_y(-50)
    pdf.set_font("Nefalix", "", 10)
    pdf.multi_cell(0, 6, "n8n altyapısından Next.js altyapısına geçiş için\ntek kaynak ürün ve iş kuralı aktarımı", align="C", new_x="LMARGIN", new_y="NEXT")


def extract_meta(blocks: list[tuple[str, object]]) -> dict[str, str]:
    meta: dict[str, str] = {}
    for kind, payload in blocks[:12]:
        if kind == "body" and isinstance(payload, str) and ":" in payload:
            key, _, val = payload.partition(":")
            key = key.strip()
            if key in ("Sürüm", "Tarih", "Hedef okuyucu", "Pilot klinik"):
                meta[key] = val.strip()
    return meta


def render_table(pdf: NefalixPdf, rows: list[list[str]]) -> None:
    if not rows:
        return
    ncols = max(len(r) for r in rows)
    norm = [r + [""] * (ncols - len(r)) for r in rows]

    pdf.set_font("Nefalix", "", 8.5)
    pdf.set_text_color(*INK)
    pdf.set_draw_color(*LINE)
    pdf.set_line_width(0.2)
    pdf.set_fill_color(*TABLE_HEAD_BG)

    headings = FontFace(family="Nefalix", emphasis="BOLD", color=HEAD, fill_color=TABLE_HEAD_BG)
    with pdf.table(
        borders_layout="ALL",
        cell_fill_mode=TableCellFillMode.NONE,
        line_height=5.2,
        padding=1.6,
        text_align="LEFT",
        first_row_as_headings=True,
        headings_style=headings,
    ) as table:
        for i, row in enumerate(norm):
            tr = table.row()
            for cell in row:
                tr.cell(cell)
    pdf.ln(2)


def build_pdf(blocks: list[tuple[str, object]], out_path: Path) -> None:
    if not FONT_PATH.is_file():
        raise SystemExit(f"Font bulunamadı: {FONT_PATH}")

    pdf = NefalixPdf(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.set_margins(18, 16, 18)
    pdf.add_font("Nefalix", "", str(FONT_PATH))
    pdf.add_font("Nefalix", "B", str(FONT_PATH))

    meta = extract_meta(blocks)
    add_cover(pdf, meta)
    pdf.add_page()  # kapağın footer'ı bu çağrıda basılır; bayrak hâlâ kapalı
    pdf.show_footer = True

    w = pdf.w - pdf.l_margin - pdf.r_margin
    seen_title = False

    for kind, payload in blocks:
        if kind == "h1":
            # Belge başlığı kapakta zaten var; içerikte tekrar etme
            if not seen_title:
                seen_title = True
                continue
            pdf.set_font("Nefalix", "B", 17)
            pdf.set_text_color(*HEAD)
            pdf.ln(4)
            pdf.multi_cell(w, 9, str(payload), new_x="LMARGIN", new_y="NEXT")
            pdf.ln(2)
        elif kind == "h2":
            if pdf.get_y() > pdf.h - 60:
                pdf.add_page()
            pdf.ln(5)
            pdf.set_font("Nefalix", "B", 14)
            pdf.set_text_color(*HEAD)
            pdf.multi_cell(w, 8, str(payload), new_x="LMARGIN", new_y="NEXT")
            pdf.set_draw_color(*LINE)
            pdf.line(pdf.l_margin, pdf.get_y() + 0.5, pdf.l_margin + w, pdf.get_y() + 0.5)
            pdf.ln(3)
        elif kind == "h3":
            if pdf.get_y() > pdf.h - 45:
                pdf.add_page()
            pdf.ln(3)
            pdf.set_font("Nefalix", "B", 11.5)
            pdf.set_text_color(*INK)
            pdf.multi_cell(w, 7, str(payload), new_x="LMARGIN", new_y="NEXT")
            pdf.ln(1)
        elif kind == "hr":
            pdf.ln(2)
        elif kind == "bullet":
            pdf.set_font("Nefalix", "", 10)
            pdf.set_text_color(*INK)
            x = pdf.l_margin
            pdf.set_x(x)
            pdf.multi_cell(w - 4, 5.6, f"•  {payload}", new_x="LMARGIN")
            pdf.ln(0.5)
        elif kind == "code":
            pdf.set_font("Nefalix", "", 8.5)
            pdf.set_text_color(60, 68, 80)
            pdf.set_fill_color(*CODE_BG)
            pdf.multi_cell(w, 5, str(payload) if str(payload).strip() else " ", fill=True, new_x="LMARGIN", new_y="NEXT")
        elif kind == "table":
            render_table(pdf, payload)  # type: ignore[arg-type]
        else:  # body
            text = str(payload)
            if not text:
                pdf.ln(2.5)
                continue
            pdf.set_font("Nefalix", "", 10)
            pdf.set_text_color(*INK)
            pdf.multi_cell(w, 5.8, text, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(0.8)

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
