from __future__ import annotations

import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import ListFlowable, ListItem, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "paper.md"
OUTPUT = ROOT / "ml-intern-lab-agentic-ml-reporting-preprint.pdf"


def clean_inline(text: str) -> str:
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return text.strip()


def blocks(markdown: str) -> list[tuple[str, object]]:
    lines = markdown.splitlines()
    out: list[tuple[str, object]] = []
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        if not stripped:
            i += 1
            continue
        if stripped.startswith("# "):
            out.append(("title", clean_inline(stripped[2:])))
            i += 1
            continue
        if stripped.startswith("## "):
            out.append(("h2", clean_inline(stripped[3:])))
            i += 1
            continue
        if stripped.startswith("|"):
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i].strip())
                i += 1
            out.append(("table", table_lines))
            continue
        if stripped.startswith("- "):
            items = []
            while i < len(lines) and lines[i].strip().startswith("- "):
                items.append(clean_inline(lines[i].strip()[2:]))
                i += 1
            out.append(("list", items))
            continue
        if stripped.startswith("```"):
            code = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code.append(lines[i])
                i += 1
            i += 1
            out.append(("code", "\n".join(code)))
            continue
        para = [stripped]
        i += 1
        while i < len(lines):
            nxt = lines[i].strip()
            if not nxt:
                i += 1
                break
            if nxt.startswith(("# ", "## ", "- ", "|", "```")):
                break
            para.append(nxt)
            i += 1
        out.append(("p", clean_inline(" ".join(para))))
    return out


def make_table(table_lines: list[str], styles) -> Table:
    rows = []
    for raw in table_lines:
        cells = [clean_inline(cell.strip()) for cell in raw.strip("|").split("|")]
        rows.append(cells)
    rows = [row for row in rows if not all(set(cell) <= {"-"} for cell in row)]
    max_cols = max(len(row) for row in rows)
    widths = [6.7 * inch / max_cols] * max_cols
    data = [[Paragraph(cell, styles["BodySmall"]) for cell in row] for row in rows]
    table = Table(data, repeatRows=1, colWidths=widths)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E8EEF7")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#18324A")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#C8D3E1")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("PADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    return table


def build_pdf() -> Path:
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="PaperTitle", parent=styles["Title"], fontSize=19, leading=23, alignment=TA_CENTER, textColor=colors.HexColor("#18324A"), spaceAfter=8))
    styles.add(ParagraphStyle(name="Author", parent=styles["Normal"], fontSize=11, leading=14, alignment=TA_CENTER, textColor=colors.HexColor("#47627E"), spaceAfter=14))
    styles.add(ParagraphStyle(name="BodyPaper", parent=styles["BodyText"], fontSize=10.5, leading=14, textColor=colors.HexColor("#202B38"), spaceAfter=8))
    styles.add(ParagraphStyle(name="BodySmall", parent=styles["BodyText"], fontSize=9, leading=11, textColor=colors.HexColor("#202B38")))
    styles.add(ParagraphStyle(name="H2Paper", parent=styles["Heading2"], fontSize=14, leading=17, textColor=colors.HexColor("#18324A"), spaceBefore=12, spaceAfter=6))
    styles.add(ParagraphStyle(name="CodeBlock", parent=styles["Code"], fontName="Courier", fontSize=8.5, leading=10.5, backColor=colors.HexColor("#F6F8FA"), borderPadding=6, spaceAfter=8))

    story = []
    title_done = False
    author_done = False
    for kind, payload in blocks(SOURCE.read_text(encoding="utf-8")):
        if kind == "title" and not title_done:
            story.append(Paragraph(str(payload), styles["PaperTitle"]))
            title_done = True
            continue
        if kind == "p" and title_done and not author_done:
            story.append(Paragraph(str(payload).replace("  ", "<br/>"), styles["Author"]))
            author_done = True
            continue
        if kind == "h2":
            story.append(Paragraph(str(payload), styles["H2Paper"]))
        elif kind == "p":
            story.append(Paragraph(str(payload), styles["BodyPaper"]))
        elif kind == "list":
            story.append(ListFlowable([ListItem(Paragraph(item, styles["BodyPaper"])) for item in payload], bulletType="bullet", leftIndent=18))
        elif kind == "table":
            story.append(make_table(payload, styles))
            story.append(Spacer(1, 8))
        elif kind == "code":
            story.append(Paragraph(str(payload).replace("\n", "<br/>"), styles["CodeBlock"]))

    doc = SimpleDocTemplate(str(OUTPUT), pagesize=letter, rightMargin=0.72 * inch, leftMargin=0.72 * inch, topMargin=0.7 * inch, bottomMargin=0.7 * inch, title="ML Intern Lab")
    doc.build(story)
    return OUTPUT


if __name__ == "__main__":
    print(build_pdf())
