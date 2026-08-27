"""Parse the official University of Cantabria July 2025/2026 cutoffs."""
from __future__ import annotations
import json
import re
from pathlib import Path
import sys
import fitz

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from etl.admissions.normalize import normalize_record  # noqa: E402

SOURCE_URL = "https://web.unican.es/estudiantesuc/Documents/Estad%C3%ADsticas/Grado/Estad%C3%ADsticas%20de%20Ordenaci%C3%B3n%20Acad%C3%A9mica/7%20Notas%20de%20corte.pdf"
PDF = Path("data/raw/admissions/cantabria/2025-2026/notas-de-corte-unican-2025-2026.pdf")
OUTPUT = Path("data/processed/admissions/cantabria-2025-2026.json")
REPORT = Path("data/processed/admissions/cantabria-2025-2026-quality.json")
TITLE_RE = re.compile(r"^(Doble Grado en|Grado en)\s+(.+)$", re.I)
NUMBER_RE = re.compile(r"(?<!\d)(\d{1,2}[,.]\d{1,3})(?!\d)")


def clean_title(value: str) -> tuple[str, str]:
    text = re.sub(r"\s+", " ", value).strip()
    match = TITLE_RE.match(text)
    is_double = text.lower().startswith("doble grado en")
    if match:
        text = match.group(2)
    campus = "Santander"
    campus_match = re.search(r"\(([^)]+)\)", text)
    if campus_match and campus_match.group(1).lower() in {"santander", "torrelavega"}:
        campus = campus_match.group(1).title()
    if is_double:
        text = "Doble grado en " + text
    return text, campus


def parse() -> tuple[list[dict], dict]:
    lines = [line.strip() for page in fitz.open(PDF) for line in page.get_text().splitlines() if line.strip()]
    records: list[dict] = []
    rejected: list[dict] = []
    index = 0
    while index < len(lines):
        title_match = TITLE_RE.match(lines[index])
        if not title_match:
            index += 1
            continue
        title, campus = clean_title(lines[index])
        score = None
        for candidate in lines[index + 1:index + 4]:
            scores = NUMBER_RE.findall(candidate)
            if scores:
                score = scores[-1].replace(",", ".")
                break
        if score is None:
            rejected.append({"line": index + 1, "title": title, "reason": "MISSING_JULY_CUTOFF"})
        else:
            records.append(normalize_record({"community": "Cantabria", "university": "Universidad de Cantabria", "campus": campus, "degree": title, "academic_year": "2025-2026", "admission_round": "last_call", "admission_group": "general", "cutoff_score": score, "source_url": SOURCE_URL, "source_page": 1, "source_row": index + 1}))
        index += 1
    keys = [(r["degree"], r["campus"], r["academic_year"], r["admission_round"], r["admission_group"]) for r in records]
    report = {"source_url": SOURCE_URL, "academic_year": "2025-2026", "records": len(records), "rejected_rows": len(rejected), "duplicates": len(keys) - len(set(keys)), "round": "July cutoff / last_call", "checks": {"cutoff_between_0_and_14": all(0 <= r["cutoff_score"] <= 14 for r in records), "no_replacement_glyph_in_names": all("�" not in r["degree"] for r in records), "last_call_round_explicit": all(r["admission_round"] == "last_call" for r in records), "general_group_explicit": all(r["admission_group"] == "group_1" for r in records), "no_duplicate_keys": len(keys) == len(set(keys))}, "rejections": rejected}
    return records, report


if __name__ == "__main__":
    rows, quality = parse(); OUTPUT.parent.mkdir(parents=True, exist_ok=True); OUTPUT.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"); REPORT.write_text(json.dumps(quality, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"); print(json.dumps({"records": len(rows), "rejected_rows": quality["rejected_rows"], "duplicates": quality["duplicates"], "checks": quality["checks"]}, ensure_ascii=False))
