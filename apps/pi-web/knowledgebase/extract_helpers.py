"""
Shared helpers for Siemens PLC PDF extraction.
Used by prescan.py and individual extraction agents.
"""

import json
import re
from pathlib import Path

import fitz  # PyMuPDF
import pdfplumber


KB_DIR = Path(__file__).parent


def get_toc(pdf_path: str) -> list[dict]:
    """Extract table of contents from a PDF using PyMuPDF.
    Returns list of {level, title, page} dicts (page is 1-based)."""
    doc = fitz.open(pdf_path)
    toc = doc.get_toc(simple=True)
    doc.close()
    return [{"level": lvl, "title": title, "page": pg} for lvl, title, pg in toc]


def extract_pages(pdf_path: str, start: int, end: int) -> str:
    """Extract text from a page range (1-based inclusive) using PyMuPDF.
    Returns concatenated text with page markers."""
    doc = fitz.open(pdf_path)
    parts = []
    start_idx = max(0, start - 1)
    end_idx = min(len(doc), end)
    for i in range(start_idx, end_idx):
        page = doc[i]
        text = page.get_text("text")
        if text.strip():
            parts.append(f"\n--- Page {i + 1} ---\n{text}")
    doc.close()
    return "\n".join(parts)


def extract_tables_from_pages(pdf_path: str, start: int, end: int) -> list[dict]:
    """Extract tables from a page range (1-based inclusive) using pdfplumber.
    Returns list of {page, rows} where rows is list of lists."""
    tables = []
    with pdfplumber.open(pdf_path) as pdf:
        start_idx = max(0, start - 1)
        end_idx = min(len(pdf.pages), end)
        for i in range(start_idx, end_idx):
            page = pdf.pages[i]
            page_tables = page.extract_tables()
            for tbl in page_tables:
                if tbl and len(tbl) > 1:
                    # Clean None values
                    cleaned = []
                    for row in tbl:
                        cleaned.append([str(cell).strip() if cell else "" for cell in row])
                    tables.append({"page": i + 1, "rows": cleaned})
    return tables


def search_toc(toc: list[dict], keywords: list[str]) -> list[dict]:
    """Search TOC entries for keyword matches (case-insensitive).
    Returns matching entries with added 'matched_keyword' field."""
    matches = []
    for entry in toc:
        title_lower = entry["title"].lower()
        for kw in keywords:
            if kw.lower() in title_lower:
                matches.append({**entry, "matched_keyword": kw})
                break
    return matches


def rows_to_markdown_table(rows: list[list[str]], header: bool = True) -> str:
    """Convert a list of rows to a Markdown table string.
    First row is treated as header if header=True."""
    if not rows:
        return ""

    # Calculate column widths
    col_count = max(len(r) for r in rows)
    # Pad rows to uniform width
    padded = []
    for row in rows:
        padded.append(row + [""] * (col_count - len(row)))

    # Build markdown
    lines = []
    for i, row in enumerate(padded):
        line = "| " + " | ".join(cell.replace("|", "\\|").replace("\n", " ") for cell in row) + " |"
        lines.append(line)
        if i == 0 and header:
            sep = "| " + " | ".join("---" for _ in row) + " |"
            lines.append(sep)

    return "\n".join(lines)


def get_page_count(pdf_path: str) -> int:
    """Get total page count of a PDF."""
    doc = fitz.open(pdf_path)
    count = len(doc)
    doc.close()
    return count


def keyword_search_pages(pdf_path: str, keywords: list[str], max_pages: int = None) -> dict[str, list[int]]:
    """Search full text of each page for keywords.
    Returns {keyword: [page_numbers]} (1-based)."""
    doc = fitz.open(pdf_path)
    results = {kw: [] for kw in keywords}
    limit = max_pages or len(doc)
    for i in range(min(len(doc), limit)):
        text = doc[i].get_text("text").lower()
        for kw in keywords:
            if kw.lower() in text:
                results[kw].append(i + 1)
    doc.close()
    return results


def toc_section_page_ranges(toc: list[dict], total_pages: int) -> list[dict]:
    """Add 'end_page' to each TOC entry based on next entry at same or higher level."""
    enriched = []
    for i, entry in enumerate(toc):
        end_page = total_pages
        for j in range(i + 1, len(toc)):
            if toc[j]["level"] <= entry["level"]:
                end_page = toc[j]["page"] - 1
                break
        enriched.append({**entry, "end_page": max(entry["page"], end_page)})
    return enriched
