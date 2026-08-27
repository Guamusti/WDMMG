"""Parse Madrid's official cutoff PDF into a reviewable JSON extract.

The parser deliberately keeps the source page and the original row. It only
normalizes rows where the first score is numeric; ambiguous rows remain in the
raw PDF for manual review rather than being silently discarded into the app.
"""
import json
import re
from pathlib import Path

import pdfplumber

SOURCE = Path("data/raw/admissions/madrid/2025-2026/notas-de-corte-madrid-2025-2026.pdf")
TARGET = Path("data/processed/admissions/madrid-2025-2026.json")
SCORE = re.compile(r"^\s*(\d{1,2}[,.]\d{3})\s*$")
ROW = re.compile(r"^(.+?)\s+(\d{1,2}[,.]\d{3})\s+(\d{1,2}[,.]\d{2})\s+(\d+(?:[,.]\d+)?)\s+(\d+)\s*$")


def clean(value):
    return re.sub(r"\s+", " ", str(value or "")).strip()


def score(value):
    match = SCORE.match(clean(value))
    return float(match.group(1).replace(",", ".")) if match else None


def parse():
    records = []
    with pdfplumber.open(SOURCE) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            # The official PDF uses two side-by-side tables on several pages.
            # Parse each half independently so rows from the two tables cannot merge.
            midpoint = page.width / 2
            columns = [page.crop((0, 0, midpoint + 8, page.height)), page.crop((midpoint - 8, 0, page.width, page.height))]
            for column in columns:
                for line in (column.extract_text(layout=True) or "").splitlines():
                    match = ROW.match(clean(line))
                    if not match:
                        continue
                    degree_name, cutoff_value, group_2, ects, years = match.groups()
                    if degree_name.lower() in {"titulaciones oficiales", "titulación"}:
                        continue
                    records.append({
                        "academic_year": "2025-2026",
                        "admission_round": "ordinary",
                        "admission_group": "group_1",
                        "degree_name_source": degree_name,
                        "cutoff_score": float(cutoff_value.replace(",", ".")),
                        "group_2_score_source": float(group_2.replace(",", ".")),
                        "ects_source": float(ects.replace(",", ".")),
                        "duration_years_source": int(years),
                        "score_scale_max": 14,
                        "source_page": page_number,
                        "source_file": str(SOURCE).replace("\\", "/"),
                        "raw_row": clean(line),
                    })
    unique = list({(record["source_page"], record["raw_row"]): record for record in records}.values())
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(json.dumps(unique, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Parsed {len(unique)} numeric rows into {TARGET}")


if __name__ == "__main__":
    parse()
