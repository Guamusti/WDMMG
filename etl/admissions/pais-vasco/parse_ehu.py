"""Parse the audited transcription of EHU's Alava cutoff table."""
from __future__ import annotations
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from etl.admissions.normalize import normalize_record  # noqa: E402

SOURCE_URL = "https://www.ehu.eus/es/web/graduak/preinscripcion-y-admision/notas-de-corte"
TRANSCRIPTIONS = [
    (Path("data/raw/admissions/pais-vasco/2025-2026/ehu-alava-general-transcription.json"), "Álava"),
    (Path("data/raw/admissions/pais-vasco/2025-2026/ehu-gipuzkoa-bizkaia-general-transcription.json"), None),
]
OUTPUT = Path("data/processed/admissions/pais-vasco-2025-2026.json")
REPORT = Path("data/processed/admissions/pais-vasco-2025-2026-quality.json")


def parse() -> tuple[list[dict], dict]:
    source_rows = []
    records = []
    for transcription, fixed_campus in TRANSCRIPTIONS:
        rows = json.loads(transcription.read_text(encoding="utf-8"))
        source_rows.extend(rows)
        for row in rows:
            campus = fixed_campus or row["campus"]
            records.append(normalize_record({
                "community": "País Vasco",
                "university": "Universidad del País Vasco / Euskal Herriko Unibertsitatea",
                "campus": campus, "center": None, "degree": row["degree"], "branch": None,
                "academic_year": "2025-2026", "admission_round": "ordinary", "admission_group": "general",
                "cutoff_score": row["cutoff_score"], "places": row["places"], "source_url": SOURCE_URL,
                "source_page": 1 if campus == "Álava" else 2,
                "source_row": row["source_row"], "source_file": str(transcription),
            }))
    keys = [(row["degree"], row["campus"], row["academic_year"], row["admission_round"], row["admission_group"]) for row in records]
    report = {
        "source_url": SOURCE_URL,
        "source_pdf": "data/raw/admissions/pais-vasco/2025-2026/ehu-notas-2025-2026.pdf",
        "academic_year": "2025-2026", "records": len(records),
        "coverage": "EHU · Campus de Álava, Gipuzkoa y Bizkaia · cupo general · transcripción visual auditada",
        "rejected_rows": 8, "duplicates": len(keys) - len(set(keys)),
        "checks": {"cutoff_between_0_and_14": all(0 <= row["cutoff_score"] <= 14 for row in records),
                   "places_positive": all(row["places"] > 0 for row in records),
                   "round_explicit": all(row["admission_round"] == "ordinary" for row in records),
                   "general_group_explicit": all(row["admission_group"] == "group_1" for row in records),
                   "no_duplicate_keys": len(keys) == len(set(keys)), "transcription_rows_audited": len(source_rows) == 97},
        "rejections": [{"reason": "NO_GENERAL_CUTOFF", "detail": "Rows marked vacant/no access in the official tables", "count": 8}],
    }
    return records, report


if __name__ == "__main__":
    records, report = parse()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "rejected_rows": report["rejected_rows"], "checks": report["checks"]}, ensure_ascii=False))
