"""Build the ULL 2025-2026 cutoff extract from an audited PDF transcription."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from etl.admissions.normalize import normalize_record  # noqa: E402

SOURCE_URL = "https://www.ull.es/admision-becas/pau/notas-de-corte/"
TRANSCRIPTION = Path("data/raw/admissions/canarias/2025-2026/ull-general-cutoff-transcription.json")
OUTPUT = Path("data/processed/admissions/canarias-ull-2025-2026.json")
REPORT = Path("data/processed/admissions/canarias-ull-2025-2026-quality.json")


def parse() -> tuple[list[dict], dict]:
    source = json.loads(TRANSCRIPTION.read_text(encoding="utf-8"))
    records = []
    for index, (branch, degree, score, campus) in enumerate(source["rows"], 1):
        records.append(normalize_record({
            "community": "Canarias",
            "university": "Universidad de La Laguna",
            "campus": campus or "Tenerife",
            "center": "Centro adscrito Nª Sra. de Candelaria" if "Centro adscrito" in degree else None,
            "degree": degree,
            "branch": branch,
            "academic_year": "2025-2026",
            "admission_round": "last_call",
            "admission_group": "general",
            "cutoff_score": score,
            "places": None,
            "source_url": SOURCE_URL,
            "source_page": 2,
            "source_row": index,
            "source_date": source["cutoff_date"],
            "source_file": str(TRANSCRIPTION),
        }))
    keys = [(row["degree"], row["campus"], row["academic_year"], row["admission_round"], row["admission_group"]) for row in records]
    report = {
        "source_url": SOURCE_URL,
        "academic_year": "2025-2026",
        "records": len(records),
        "rejected_rows": 0,
        "duplicates": len(keys) - len(set(keys)),
        "round": "corte final orientativa · 30 septiembre 2025",
        "coverage": "ULL · cupo general · 18 filas transcritas del PDF oficial; tabla sin capa estructurada",
        "transcription_audited": True,
        "checks": {
            "cutoff_between_0_and_14": all(0 <= row["cutoff_score"] <= 14 for row in records),
            "no_replacement_glyph_in_names": all("�" not in row["degree"] for row in records),
            "last_call_explicit": all(row["admission_round"] == "last_call" for row in records),
            "general_group_explicit": all(row["admission_group"] == "group_1" for row in records),
            "no_duplicate_keys": len(keys) == len(set(keys)),
            "expected_row_count": len(records) == 18,
        },
    }
    return records, report


if __name__ == "__main__":
    rows, report = parse()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(rows), "checks": report["checks"]}, ensure_ascii=False))
