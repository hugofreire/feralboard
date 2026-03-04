#!/usr/bin/env python3
"""
Pre-scan all Siemens PLC PDFs to produce prescan.json.
Gives extraction agents a precise roadmap of page ranges and sections.
"""

import json
from pathlib import Path
from extract_helpers import (
    get_toc, get_page_count, keyword_search_pages,
    search_toc, toc_section_page_ranges, KB_DIR
)

COMM_KEYWORDS = [
    "modbus", "profinet", "profibus", "ethernet", "tcp", "udp",
    "opc", "opc-ua", "opc ua", "s7 comm", "put/get", "open user",
    "communication", "network", "connection", "web server",
    "snmp", "ntp", "smtp", "ftp", "http",
]

IO_KEYWORDS = [
    "i/o", "input", "output", "analog", "digital",
    "module", "signal board", "signal module",
    "addressing", "address", "data type",
]

ADDRESSING_KEYWORDS = [
    "address", "addressing", "memory", "variable memory", "vm",
    "data block", "db", "register", "mapping", "v memory",
    "process image", "peripheral",
]

ALL_KEYWORDS = list(set(COMM_KEYWORDS + IO_KEYWORDS + ADDRESSING_KEYWORDS))

# Map filenames to product family + doc type
PDF_METADATA = {
    "Manual-LOGO-2020.pdf": {"family": "LOGO! 8", "doc_type": "system_manual"},
    "Help_en-US_en-US.pdf": {"family": "LOGO! 8", "doc_type": "soft_comfort_help"},
    "S71200_G2_system_manual_en-US.pdf": {"family": "S7-1200 G2", "doc_type": "system_manual"},
    "S71200_G2_manual_update_en-US_en-US.pdf": {"family": "S7-1200 G2", "doc_type": "manual_update"},
    "s71500_et200mp_system_manual_en-US_en-US.pdf": {"family": "S7-1500 / ET 200MP", "doc_type": "system_manual"},
    "et200sp_cpu1510sp_1_pn_manual_en-US_en-US.pdf": {"family": "ET 200SP", "doc_type": "cpu_manual"},
    "s7300_module_data_manual_en-US_en-US.pdf": {"family": "S7-300", "doc_type": "module_data"},
    "S7-300_IHB_e.pdf": {"family": "S7-300", "doc_type": "hardware_installation"},
    "424ish_e.pdf": {"family": "S7-400", "doc_type": "hardware_installation"},
    "module_data_en_en-US.pdf": {"family": "S7-400", "doc_type": "module_data"},
    "s7200_system_manual_en-US.pdf": {"family": "S7-200", "doc_type": "system_manual"},
    "s7-200-smart-system-manual-en-us.pdf": {"family": "S7-200 SMART", "doc_type": "system_manual"},
}


def prescan_pdf(filename: str) -> dict:
    pdf_path = str(KB_DIR / filename)
    meta = PDF_METADATA.get(filename, {"family": "unknown", "doc_type": "unknown"})

    page_count = get_page_count(pdf_path)
    toc = get_toc(pdf_path)
    toc_with_ranges = toc_section_page_ranges(toc, page_count)

    # Keyword matches in TOC
    comm_toc_hits = search_toc(toc_with_ranges, COMM_KEYWORDS)
    io_toc_hits = search_toc(toc_with_ranges, IO_KEYWORDS)
    addr_toc_hits = search_toc(toc_with_ranges, ADDRESSING_KEYWORDS)

    # Full-text keyword search (sample — every 5th page for speed on large docs)
    kw_page_hits = keyword_search_pages(pdf_path, ALL_KEYWORDS)

    # Consolidate page ranges with communication content
    comm_pages = set()
    for hits in [comm_toc_hits, addr_toc_hits]:
        for h in hits:
            for p in range(h["page"], h.get("end_page", h["page"]) + 1):
                comm_pages.add(p)
    for kw in COMM_KEYWORDS + ADDRESSING_KEYWORDS:
        comm_pages.update(kw_page_hits.get(kw, []))

    return {
        "filename": filename,
        "family": meta["family"],
        "doc_type": meta["doc_type"],
        "page_count": page_count,
        "toc_entry_count": len(toc),
        "toc": toc_with_ranges,
        "comm_toc_sections": comm_toc_hits,
        "io_toc_sections": io_toc_hits,
        "addressing_toc_sections": addr_toc_hits,
        "keyword_page_hits": {k: v for k, v in kw_page_hits.items() if v},
        "comm_relevant_pages": sorted(comm_pages),
        "comm_relevant_page_count": len(comm_pages),
    }


def main():
    results = {}
    pdfs = sorted(KB_DIR.glob("*.pdf"))
    for pdf in pdfs:
        print(f"Scanning {pdf.name}...")
        results[pdf.name] = prescan_pdf(pdf.name)
        print(f"  -> {results[pdf.name]['page_count']} pages, "
              f"{results[pdf.name]['toc_entry_count']} TOC entries, "
              f"{results[pdf.name]['comm_relevant_page_count']} comm-relevant pages")

    out_path = KB_DIR / "prescan.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nWrote {out_path} ({len(results)} PDFs)")


if __name__ == "__main__":
    main()
