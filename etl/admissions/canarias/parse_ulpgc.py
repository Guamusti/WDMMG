"""Parse ULPGC's official 2025-2026 general-quota cutoff tables."""
from __future__ import annotations

import json
import re
import sys
from io import StringIO
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from etl.admissions.normalize import normalize_record

SOURCE_URL = "https://sie.ulpgc.es/notascorte"
HTML_FILE = Path("data/raw/admissions/canarias/2025-2026/ulpgc-notas-corte-2025-2026.html")
OUTPUT = Path("data/processed/admissions/canarias-ulpgc-2025-2026.json")
REPORT = Path("data/processed/admissions/canarias-ulpgc-2025-2026-quality.json")
BRANCHES = ["Artes y Humanidades", "Ciencias de la Salud", "Ingeniería y Arquitectura", "Ciencias Sociales y Jurídicas", "Ciencias"]


def clean(value: object) -> str:
    return re.sub(r"\s+", " ", str(value)).replace("�", "").strip()


def parse() -> tuple[list[dict], dict]:
    tables = pd.read_html(StringIO(HTML_FILE.read_text(encoding="utf-8")))
    records: list[dict] = []
    rejected: list[dict] = []
    for table_index, table in enumerate(tables):
        branch = BRANCHES[table_index] if table_index < len(BRANCHES) else "Rama pendiente de separación"
        for row_index, row in table.iterrows():
            degree = clean(row.iloc[0])
            raw_score = clean(row.iloc[1]).replace(",", ".")
            if not degree or raw_score in {"", "--", "-", "nan"}:
                rejected.append({"table": table_index + 1, "row": int(row_index) + 1, "degree": degree, "reason": "MISSING_GENERAL_CUTOFF"})
                continue
            try:
                score = float(raw_score)
            except ValueError:
                rejected.append({"table": table_index + 1, "row": int(row_index) + 1, "degree": degree, "reason": "INVALID_GENERAL_CUTOFF"})
                continue
            island = re.search(r"\((Fuerteventura|Gran Canaria|Lanzarote)\)", degree)
            campus = island.group(1) if island else "Gran Canaria"
            records.append(normalize_record({
                "community": "Canarias",
                "university": "Universidad de Las Palmas de Gran Canaria",
                "campus": campus,
                "center": None,
                "degree": degree,
                "branch": branch,
                "academic_year": "2025-2026",
                "admission_round": "first_call",
                "admission_group": "general",
                "cutoff_score": score,
                "places": None,
                "source_url": SOURCE_URL,
                "source_page": 1,
                "source_table": table_index + 1,
                "source_row": int(row_index) + 1,
            }))
    keys = [(r["degree"], r["campus"], r["academic_year"], r["admission_round"], r["admission_group"]) for r in records]
    report = {
        "source_url": SOURCE_URL,
        "academic_year": "2025-2026",
        "records": len(records),
        "rejected_rows": len(rejected),
        "duplicates": len(keys) - len(set(keys)),
        "round": "first assignment · general quota",
        "coverage": "ULPGC · 57 published rows; rows without a general-quota score are excluded",
        "checks": {
            "cutoff_between_0_and_14": all(0 <= row["cutoff_score"] <= 14 for row in records),
            "no_replacement_glyph_in_names": all("�" not in row["degree"] for row in records),
            "admission_round_explicit": all(row["admission_round"] == "first_call" for row in records),
            "general_group_explicit": all(row["admission_group"] == "group_1" for row in records),
            "no_duplicate_keys": len(keys) == len(set(keys)),
        },
        "rejections": rejected,
    }
    return records, report


if __name__ == "__main__":
    rows, report = parse()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(rows), "rejected_rows": report["rejected_rows"], "duplicates": report["duplicates"], "checks": report["checks"]}, ensure_ascii=False))
