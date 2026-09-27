"""Render docs/executive_brief.md to docs/executive_brief.pdf (capstone: max 2 pages).

    docker compose --profile dev run --rm notebook python scripts/build_brief_pdf.py
"""

from __future__ import annotations

import pathlib
import re

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import ListFlowable, ListItem, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC, OUT = ROOT / "docs" / "executive_brief.md", ROOT / "docs" / "executive_brief.pdf"

ss = getSampleStyleSheet()
BODY = ParagraphStyle("b", parent=ss["BodyText"], fontSize=8.6, leading=10.6, spaceAfter=3)
H1 = ParagraphStyle("h1", parent=ss["Title"], fontSize=14, leading=17, spaceAfter=2, alignment=0)
H2 = ParagraphStyle("h2", parent=ss["Heading2"], fontSize=10.5, leading=13, spaceBefore=5, spaceAfter=2,
                    textColor=colors.HexColor("#1f3a5f"))
CELL = ParagraphStyle("c", parent=BODY, fontSize=7.8, leading=9.4, spaceAfter=0)


def inline(t: str) -> str:
    t = t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\\*", "\x00")
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<i>\1</i>", t)
    t = re.sub(r"`(.+?)`", r"<font face='Courier'>\1</font>", t)
    return t.replace("\x00", "*")


def build() -> None:
    lines = SRC.read_text(encoding="utf-8").splitlines()
    story, i = [], 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("# "):
            story.append(Paragraph(inline(ln[2:]), H1))
        elif ln.startswith("## "):
            story.append(Paragraph(inline(ln[3:]), H2))
        elif ln.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                if not re.match(r"^\|[\s\-|]+\|$", lines[i]):
                    rows.append([Paragraph(inline(c.strip()), CELL) for c in lines[i].strip("|").split("|")])
                i += 1
            tbl = Table(rows, repeatRows=1, hAlign="LEFT")
            tbl.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8eef5")),
                                     ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
                                     ("VALIGN", (0, 0), (-1, -1), "TOP"),
                                     ("TOPPADDING", (0, 0), (-1, -1), 1.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5)]))
            story += [tbl, Spacer(1, 3)]
            continue
        elif re.match(r"^(\d+\.|-) ", ln):
            items, ordered = [], ln[0].isdigit()
            while i < len(lines) and re.match(r"^(\d+\.|-) ", lines[i]):
                items.append(ListItem(Paragraph(inline(re.sub(r"^(\d+\.|-) ", "", lines[i])), BODY), leftIndent=10))
                i += 1
            story.append(ListFlowable(items, bulletType="1" if ordered else "bullet", leftIndent=12,
                                      bulletFontSize=8))
            continue
        elif ln.strip():
            story.append(Paragraph(inline(ln), BODY))
        i += 1
    doc = SimpleDocTemplate(str(OUT), pagesize=A4, leftMargin=1.6 * cm, rightMargin=1.6 * cm,
                            topMargin=1.3 * cm, bottomMargin=1.3 * cm, title="Executive Brief — Promotion Targeting")
    doc.build(story)
    print("wrote", OUT.relative_to(ROOT))


if __name__ == "__main__":
    build()
