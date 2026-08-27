"""Parse the official CIUG 2025 cutoff publication conservatively.

The PDF is kept as the source of record. Rows whose extracted title contains
an undecodable glyph are rejected instead of being silently repaired.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import fitz

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from etl.admissions.normalize import normalize_record  # noqa: E402


SOURCE_URL = "https://ciug.gal/PDF/2025/ACCESO/notas_de_corte_2025.pdf"
PDF = Path("data/raw/admissions/galicia/2025-2026/notas-de-corte-galicia-2025-2026.pdf")
OUTPUT = Path("data/processed/admissions/galicia-2025-2026.json")
REPORT = Path("data/processed/admissions/galicia-2025-2026-quality.json")
ROW_RE = re.compile(r"^(\d{5})\s+(.+)$")
CUTOFF_RE = re.compile(r"\b(Ord\.|Ext\.)(?:\s+([A-Z]))?\s+([0-9]{1,2},[0-9]{3})")


def parse() -> tuple[list[dict], dict]:
    records: list[dict] = []
    rejected: list[dict] = []
    doc = fitz.open(PDF)
    page_context = {
        1: ("Universidade de Vigo", {"left": "Campus de Ourense", "right": "Campus de Pontevedra"}),
        2: ("Universidade de Vigo", {"left": "Campus de Vigo"}),
        3: ("Universidade de Santiago de Compostela", {"left": "Campus de Santiago"}),
        4: ("Universidade de Santiago de Compostela", {"left": "Campus de Lugo"}),
        5: ("Universidade da Coruña", {"left": "Campus da Coruña"}),
        6: ("Universidade da Coruña", {"left": "Campus de Ferrol"}),
    }

    for page_number, page in enumerate(doc, 1):
        university, campuses = page_context[page_number]
        blocks = sorted(page.get_text("blocks"), key=lambda block: (block[1], block[0]))
        for block in blocks:
            column = "left" if block[0] < page.rect.width / 2 else "right"
            campus = campuses.get(column, campuses["left"])
            lines = [line.strip() for line in block[4].splitlines() if line.strip()]
            current: tuple[str, str, list[str]] | None = None

            def consume(row: tuple[str, str, list[str]] | None) -> None:
                if not row:
                    return
                code, title, detail_lines = row
                rest = " ".join(detail_lines)
                full_rest = f"{title} {rest}"
                first_marker = re.search(r"\b(?:Ord\.|Ext\.)", full_rest)
                if not first_marker:
                    rejected.append({"page": page_number, "code": code, "title": title, "reason": "NO_CUTOFF"})
                    return
                title_clean = re.sub(r"\s+", " ", title.lstrip("- ")).strip()
                if "�" in title_clean or not title_clean:
                    rejected.append({"page": page_number, "code": code, "title": title_clean, "reason": "MALFORMED_TITLE"})
                    return
                for marker, group, raw_cutoff in CUTOFF_RE.findall(rest):
                    records.append(normalize_record({
                        "community": "Galicia",
                        "university": university,
                        "campus": campus,
                        "degree_code": code,
                        "degree": title_clean,
                        "academic_year": "2025-2026",
                        "admission_round": "ordinary" if marker == "Ord." else "extraordinary",
                        "admission_group": group or "general",
                        "cutoff_score": raw_cutoff.replace(",", "."),
                        "source_url": SOURCE_URL,
                        "source_page": page_number,
                    }))

            for line in lines:
                match = ROW_RE.match(line)
                if match:
                    consume(current)
                    code, title = match.groups()
                    current = (code, title, [])
                elif current:
                    current[2].append(line)
            consume(current)

    report = {
        "source_url": SOURCE_URL,
        "academic_year": "2025-2026",
        "records": len(records),
        "rejected_rows": len(rejected),
        "rejections": rejected,
        "checks": {
            "cutoff_between_0_and_14": all(0 <= float(r["cutoff_score"]) <= 14 for r in records),
            "no_replacement_glyph_in_names": all("�" not in (r["degree"] + r["university"] + r["campus"]) for r in records),
            "rounds_explicit": all(r["admission_round"] in {"ordinary", "extraordinary"} for r in records),
        },
    }
    return records, report


if __name__ == "__main__":
    rows, quality = parse()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REPORT.write_text(json.dumps(quality, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(rows), "rejected_rows": quality["rejected_rows"], "checks": quality["checks"]}, ensure_ascii=False))
