"""Write the anonymized manuscript text and PDF from results.json."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from cityenergy.experiment import manuscript_text  # noqa: E402

TITLE = "One shared electricity-interval width does not transfer across buildings"


def write_pdf(path: Path, text: str) -> int:
    from fpdf import FPDF

    pdf = FPDF(format="A4")
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.set_title(TITLE)
    pdf.set_author("")
    pdf.set_creator("")
    pdf.set_subject("")
    pdf.add_page()
    pdf.set_font("Times", size=11)
    for block in text.split("\n\n"):
        heading = block.split("\n", 1)[0]
        if heading == TITLE or heading[:1].isdigit() or heading in {"Abstract", "References"}:
            pdf.set_font("Times", style="B", size=12 if heading != TITLE else 14)
            pdf.multi_cell(0, 7, heading)
            pdf.ln(1)
            rest = block.split("\n", 1)[1] if "\n" in block else ""
            pdf.set_font("Times", size=11)
            if rest:
                pdf.multi_cell(0, 6, rest)
        else:
            pdf.set_font("Times", size=11)
            pdf.multi_cell(0, 6, block)
        pdf.ln(2)
    if pdf.page > 6:
        raise RuntimeError(f"manuscript is {pdf.page} pages; the call allows 6")
    path.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(path)
    return pdf.page


def main() -> None:
    payload = json.loads((ROOT / "results" / "results.json").read_text(encoding="utf-8"))
    text = manuscript_text(payload)
    article = ROOT / "article"
    article.mkdir(parents=True, exist_ok=True)
    (article / "manuscript.txt").write_text(text, encoding="utf-8", newline="\n")
    pages = write_pdf(article / "manuscript.pdf", text)
    print(f"{article / 'manuscript.pdf'} ({pages} pages)")


if __name__ == "__main__":
    main()
