"""Portal fields for AIEI 2027. The manuscript PDF stays anonymous."""

from __future__ import annotations

import re

PORTAL_URL = "https://aiei2027.org/submission.html"
COPYRIGHT_FORM_URL = "https://www.e3s-conferences.org/doc_journal/woc/publication_right_form.pdf"
PDF_GUIDELINES_URL = "https://www.e3s-conferences.org/doc_journal/woc/pdf_guidelines.pdf"
TRACK = "Artificial Intelligence for Smart Energy Systems"
PAPER_KIND = "Full paper"
MAX_PDF_BYTES = 10 * 1024 * 1024
MAX_PAGES_WITHOUT_EXTRA_FEE = 5
CALL_PAGE_LIMIT = 6

AUTHOR_NAME = "Mohammad Parsa Sohrabi"
AUTHOR_EMAIL = "oil.ms.sohrabi@gmail.com"
AUTHOR_AFFILIATION = "Parsa International Group, Istanbul, Türkiye; Petro Pala Toos"

_IDENTITY = ("sohrabi", "petro", "oil.ms")


def section_body(manuscript: str, heading: str) -> str:
    for block in manuscript.split("\n\n"):
        if block.startswith(heading + "\n"):
            return block.split("\n", 1)[1].strip()
    raise ValueError(f"manuscript has no {heading} section")


def portal_sheet(manuscript: str) -> str:
    """Text for the conference form. Author names stay out of the PDF."""
    title = manuscript.split("\n", 1)[0].strip()
    abstract = section_body(manuscript, "Abstract")
    keywords = section_body(manuscript, "Keywords")
    lines = [
        f"Portal: {PORTAL_URL}",
        f"Kind: {PAPER_KIND}",
        f"Track: {TRACK}",
        f"Title: {title}",
        "",
        "Abstract:",
        abstract,
        "",
        f"Keywords: {keywords}",
        "",
        "Authors, entered in the portal form only:",
        f"1. {AUTHOR_NAME}",
        f"Email: {AUTHOR_EMAIL}",
        f"Affiliation: {AUTHOR_AFFILIATION}",
        f"Corresponding author email: {AUTHOR_EMAIL}",
        f"Corresponding author affiliation: {AUTHOR_AFFILIATION}",
        "",
        "Files:",
        "- article/manuscript.pdf (anonymized, no author metadata)",
        f"- Signed copyright form, downloaded from {COPYRIGHT_FORM_URL}",
        f"- Camera-ready format notes, if accepted: {PDF_GUIDELINES_URL}",
        "",
        "The copyright form is not signed in this repository.",
        "Nothing in this repository has been uploaded.",
        "",
    ]
    return "\n".join(lines)


def _page_count(pdf: bytes) -> int | None:
    found = re.search(br"/Count (\d+)", pdf)
    if found is None:
        return None
    return int(found.group(1))


def package_problems(manuscript: str, portal: str, pdf: bytes) -> list[str]:
    """Return submission gaps that this repository can still close."""
    problems: list[str] = []
    title = manuscript.split("\n", 1)[0].strip()
    if not title:
        problems.append("manuscript has no title")
    if "A language model assisted with wording. It is not an author." not in manuscript:
        problems.append("manuscript does not disclose the language-model wording assist")
    lowered = manuscript.lower()
    pdf_lower = pdf.lower()
    for token in _IDENTITY:
        if token in lowered:
            problems.append(f"manuscript text contains {token}")
        if token.encode("utf-8") in pdf_lower:
            problems.append(f"manuscript PDF contains {token}")
    pages = _page_count(pdf)
    if pages is None:
        problems.append("PDF page count is missing")
    elif pages < 1 or pages > CALL_PAGE_LIMIT:
        problems.append(f"PDF has {pages} pages; the call allows {CALL_PAGE_LIMIT}")
    elif pages > MAX_PAGES_WITHOUT_EXTRA_FEE:
        problems.append(f"PDF has {pages} pages; page 6 adds the extra-page fee")
    if len(pdf) > MAX_PDF_BYTES:
        problems.append("PDF exceeds the 10 MiB portal limit")
    if f"Title: {title}" not in portal:
        problems.append("portal sheet title does not match the manuscript")
    if section_body(manuscript, "Abstract") not in portal:
        problems.append("portal sheet is missing the manuscript abstract")
    if TRACK not in portal:
        problems.append("portal sheet is missing the conference track")
    if AUTHOR_EMAIL not in portal:
        problems.append("portal sheet is missing the corresponding email")
    if "The copyright form is not signed in this repository." not in portal:
        problems.append("portal sheet does not keep the copyright form unsigned")
    if "Nothing in this repository has been uploaded." not in portal:
        problems.append("portal sheet claims an upload")
    return problems
