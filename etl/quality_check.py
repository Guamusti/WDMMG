"""Dependency-free quality gate for committed processed admissions data."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATASETS = [
    ROOT / "data/processed/admissions/madrid-2025-2026.json",
    ROOT / "data/processed/admissions/galicia-2025-2026.json",
    ROOT / "data/processed/admissions/aragon-2025-2026.json",
    ROOT / "data/processed/admissions/cataluna-2025-2026.json",
    ROOT / "data/processed/admissions/national-2025-2026.json",
]
REQUIRED = {"academic_year", "admission_round", "admission_group", "cutoff_score"}
RUCT_MATCHES = ROOT / "data/processed/ruct/madrid-degree-matches.json"
OUTCOME_ENROLMENT = ROOT / "data/processed/outcomes/madrid-university-enrolment-2023-2024.json"
MADRID_UNIVERSITIES = {"UAH", "UAM", "UC3M", "UCM", "UPM", "URJC"}
KNOWN_BRANCHES = {"", "Artes y Humanidades", "Ciencias", "Ciencias de la Salud", "Ciencias Sociales y Jurídicas", "Ingeniería y Arquitectura", "Rama pendiente de separación"}


def check(path: Path) -> int:
    rows = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(rows, list) or not rows:
        raise AssertionError(f"{path}: expected a non-empty list")
    for index, row in enumerate(rows):
        missing = REQUIRED - row.keys()
        if missing:
            raise AssertionError(f"{path}:{index}: missing {sorted(missing)}")
        if row["academic_year"] != "2025-2026":
            raise AssertionError(f"{path}:{index}: unexpected academic year")
        if not 0 <= float(row["cutoff_score"]) <= 14:
            raise AssertionError(f"{path}:{index}: cutoff outside 0-14")
        source_text = " ".join(str(row.get(field, "")) for field in ("degree", "university", "campus", "degree_name_source", "university_name_source", "branch_name_source", "raw_row"))
        if "�" in source_text:
            raise AssertionError(f"{path}:{index}: replacement glyph in name")
        degree = str(row.get("degree_name_source") or row.get("degree") or "")
        if re.search(r"(?:https?://|\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b|\b\d{3,}\b)", degree):
            raise AssertionError(f"{path}:{index}: contaminated degree name: {degree}")
        branch = str(row.get("branch_name_source") or row.get("branch") or "")
        if branch not in KNOWN_BRANCHES:
            raise AssertionError(f"{path}:{index}: unknown branch: {branch}")
    return len(rows)


total = sum(check(path) for path in DATASETS)
matches = json.loads(RUCT_MATCHES.read_text(encoding="utf-8"))
if len(matches) != 459 or len({row["admission_id"] for row in matches}) != len(matches):
    raise AssertionError("RUCT matches: expected 459 unique Madrid admission rows")
for row in matches:
    if row["status"] == "matched" and not re.fullmatch(r"\d{7}", str(row["ruct_degree_code"])):
        raise AssertionError(f"RUCT match without a seven-digit title code: {row['admission_id']}")
    if row["status"] == "matched" and not row.get("ruct_centers"):
        raise AssertionError(f"RUCT match without an official center: {row['admission_id']}")
    for center in row.get("ruct_centers", []):
        if not re.fullmatch(r"\d{8}", str(center.get("code", ""))) or not center.get("name"):
            raise AssertionError(f"Invalid RUCT center in match: {row['admission_id']}")
enrolment = json.loads(OUTCOME_ENROLMENT.read_text(encoding="utf-8"))
if enrolment.get("academic_year") != "2023-2024" or enrolment.get("granularity") != "Universidad · grados presenciales":
    raise AssertionError("Enrolment context: unexpected year or granularity")
if set(enrolment.get("universities", {})) != MADRID_UNIVERSITIES:
    raise AssertionError("Enrolment context: expected six Madrid public universities")
if any(not isinstance(value, int) or value <= 0 for value in enrolment["universities"].values()):
    raise AssertionError("Enrolment context: values must be positive integers")
print(f"Quality gate passed: {len(DATASETS)} datasets, {total} rows, {len(matches)} RUCT matches")
