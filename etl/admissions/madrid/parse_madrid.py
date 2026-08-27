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
ECTS_END = re.compile(r"\b(?:180|200|210|216|220|225|230|240|270|300|330|345|354|360|366|378|381|390|417)(?:\+\d+)?\s+\d+\b")
BRANCHES = (
    "Ciencias Sociales y Jurídicas",
    "Ingeniería y Arquitectura",
    "Artes y Humanidades",
    "Ciencias de la Salud",
    "Ciencias",
)
DEGREE_NOISE = re.compile(r"^(?:www\.|info@|tel\.?\s*:|c/\s|avda\.?\s|paseo\s|centro\s|ces\s|eu\s|de la\s|«)", re.IGNORECASE)
LAYOUT_REPAIRS = {
    "(Guadalajara) 5,561 7,72 240 4": "Magisterio de Educación Primaria (bilingüe - inglés) (Guadalajara)",
    "de Empresas 10,436 5,00 345 5": "Ingeniería Informática - Administración y Dirección de Empresas",
    "(Campus de Montegancedo) Ingeniería en Tecnologías Industriales 12,114 5,00 240 4": "Ingeniería en Tecnologías Industriales (Campus de Montegancedo)",
    "direccion@cesdonbosco.com Maestro de Educación Infantil - Maestro Educación 5,000 5,00 5,000 5,00 5,00 360 5": "Maestro de Educación Infantil - Maestro Educación Primaria",
}
UNIVERSITY_BY_PAGE = {
    2: 'Universidad de Alcalá', 3: 'Universidad Carlos III de Madrid',
    4: 'Universidad Autónoma de Madrid', 5: 'Universidad Politécnica de Madrid',
    6: 'Universidad Complutense de Madrid', 7: 'Universidad Complutense de Madrid',
    8: 'Universidad Rey Juan Carlos', 9: 'Universidad Rey Juan Carlos',
}
RUCT_CODE_BY_UNIVERSITY = {'Universidad de Alcalá': '029', 'Universidad Autónoma de Madrid': '023', 'Universidad Carlos III de Madrid': '036', 'Universidad Complutense de Madrid': '010', 'Universidad Politécnica de Madrid': '025', 'Universidad Rey Juan Carlos': '056'}


def clean(value):
    return re.sub(r"\s+", " ", str(value or "")).strip()


def clean_branch(value):
    """Keep only a known branch name; PDF layout text must never leak into it."""
    branch = clean(value)
    branch = re.sub(r"^Rama de conocimiento de\s+", "", branch, flags=re.IGNORECASE)
    for known in BRANCHES:
        if branch.startswith(known):
            return known
    return "Rama pendiente de separación" if branch else ""


def split_rows(line):
    """Split rows accidentally joined by the PDF's side-by-side layout."""
    candidates = list(re.finditer(SCORE_3, line))
    if not candidates:
        return []
    rows = []
    cursor = 0
    for candidate in candidates:
        if candidate.start() < cursor:
            continue
        end = ECTS_END.search(line, candidate.end())
        if not end:
            continue
        rows.append(line[cursor:end.end()].strip())
        cursor = end.end()
    return rows


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
            for source_line in (page.extract_text(layout=False) or "").splitlines():
                line = clean(source_line)
                branch_match = re.match(r"^Rama de conocimiento de (.+)$", line, re.IGNORECASE)
                if branch_match:
                    branch = branch_match.group(1)
                    continue
                for row_line in split_rows(line):
                    match = ROW.match(row_line)
                    if not match:
                        continue
                    degree_name, cutoff_value, group_2, ects, years = match.groups()
                    degree_name = LAYOUT_REPAIRS.get(row_line, degree_name)
                    # A number in the title means the PDF column extractor has
                    # leaked an address, centre marker or another table cell.
                    # Real degree names are kept only when they are text-only.
                    if degree_name.lower() in {"titulaciones oficiales", "titulación"} or re.search(r"\d", degree_name) or DEGREE_NOISE.search(degree_name):
                        continue
                    records.append({
                        "academic_year": "2025-2026",
                        "admission_round": "ordinary",
                        "admission_group": "group_1",
                    "university_name_source": UNIVERSITY_BY_PAGE.get(page_number),
                    "university_ruct_code": RUCT_CODE_BY_UNIVERSITY.get(UNIVERSITY_BY_PAGE.get(page_number)),
                        "branch_name_source": clean_branch(branch),
                        "degree_name_source": degree_name,
                        "cutoff_score": float(cutoff_value.replace(",", ".")),
                        "group_2_score_source": float(group_2.replace(",", ".")),
                        "ects_source": float(ects.replace(",", ".")),
                        "duration_years_source": int(years),
                        "score_scale_max": 14,
                        "source_page": page_number,
                        "source_file": str(SOURCE).replace("\\", "/"),
                        "raw_row": row_line,
                    })
    unique = list({(record["source_page"], record["raw_row"]): record for record in records}.values())
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(json.dumps(unique, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Parsed {len(unique)} numeric rows into {TARGET}")


if __name__ == "__main__":
    parse()
