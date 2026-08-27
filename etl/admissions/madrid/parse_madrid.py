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
SCORE_3 = r"\d{1,2}[,.]\d{3}(?:\(\d+\))?"
SCORE_2 = r"\d{1,2}[,.]\d{2}(?:\(\d+\))?"
SCORE_ANY = r"\d{1,2}[,.]\d{2,3}(?:\(\d+\))?"
ROW = re.compile(rf"^(.+?)\s+({SCORE_3})\s+({SCORE_2})(?:\s+{SCORE_ANY}){{0,5}}\s+(\d+(?:[,.]\d+)?)\s+(\d+)\s*$")
UNIVERSITY_BY_PAGE = {
    2: 'Universidad de Alcalá', 3: 'Universidad Carlos III de Madrid',
    4: 'Universidad Autónoma de Madrid', 5: 'Universidad Politécnica de Madrid',
    6: 'Universidad Complutense de Madrid', 7: 'Universidad Complutense de Madrid',
    8: 'Universidad Rey Juan Carlos', 9: 'Universidad Rey Juan Carlos',
}


def clean(value):
    return re.sub(r"\s+", " ", str(value or "")).strip()


def score(value):
    match = SCORE.match(clean(value))
    return float(match.group(1).replace(",", ".")) if match else None


def parse():
    records = []
    with pdfplumber.open(SOURCE) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            # extract_text(layout=True) loses rows when the PDF has two tables
            # side by side. The normal reading order keeps each visible row intact
            # and the expanded expression also supports five access groups.
            branch = None
            for line in (page.extract_text(layout=False) or "").splitlines():
                line = clean(line)
                branch_match = re.match(r"^Rama de conocimiento de (.+)$", line, re.IGNORECASE)
                if branch_match:
                    branch = branch_match.group(1)
                    continue
                match = ROW.match(line)
                if not match:
                    continue
                degree_name, cutoff_value, group_2, ects, years = match.groups()
                if degree_name.lower() in {"titulaciones oficiales", "titulación"}:
                    continue
                records.append({
                    "academic_year": "2025-2026",
                    "admission_round": "ordinary",
                    "admission_group": "group_1",
                    "university_name_source": UNIVERSITY_BY_PAGE.get(page_number),
                    "branch_name_source": branch,
                    "degree_name_source": degree_name,
                    "cutoff_score": float(cutoff_value.replace(",", ".")),
                    "group_2_score_source": float(group_2.replace(",", ".")),
                    "ects_source": float(ects.replace(",", ".")),
                    "duration_years_source": int(years),
                    "score_scale_max": 14,
                    "source_page": page_number,
                    "source_file": str(SOURCE).replace("\\", "/"),
                    "raw_row": line,
                })
    unique = list({(record["source_page"], record["raw_row"]): record for record in records}.values())
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(json.dumps(unique, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Parsed {len(unique)} numeric rows into {TARGET}")


if __name__ == "__main__":
    parse()
