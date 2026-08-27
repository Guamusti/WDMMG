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
OUTCOME_GRADUATES = ROOT / "data/processed/outcomes/madrid-university-graduates-2023-2024.json"
OUTCOME_INTERNATIONAL = ROOT / "data/processed/outcomes/madrid-international-2022-2023.json"
OUTCOME_EMPLOYMENT = ROOT / "data/processed/outcomes/field-employment-2018-2019-four-years.json"
OUTCOME_EMPLOYMENT_SERIES = ROOT / "data/processed/outcomes/employment-national-series-2018-2019.json"
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
graduates = json.loads(OUTCOME_GRADUATES.read_text(encoding="utf-8"))
if graduates.get("academic_year") != "2023-2024" or graduates.get("granularity") != "Universidad · grados presenciales":
    raise AssertionError("Graduate context: unexpected year or granularity")
if set(graduates.get("universities", {})) != MADRID_UNIVERSITIES:
    raise AssertionError("Graduate context: expected six Madrid public universities")
if any(not isinstance(value, int) or value <= 0 for value in graduates["universities"].values()):
    raise AssertionError("Graduate context: values must be positive integers")
international = json.loads(OUTCOME_INTERNATIONAL.read_text(encoding="utf-8"))
if international.get("academic_year") != "2022-2023" or international.get("metric") != "international_entrants_total":
    raise AssertionError("International context: unexpected year or metric")
if set(international.get("values", {})) != MADRID_UNIVERSITIES:
    raise AssertionError("International context: expected six Madrid public universities")
if not international.get("definition") or not international.get("source_url"):
    raise AssertionError("International context: definition and source are required")
if any(not isinstance(value, int) or value <= 0 for value in international["values"].values()):
    raise AssertionError("International context: values must be positive integers")
employment = json.loads(OUTCOME_EMPLOYMENT.read_text(encoding="utf-8"))
required_fields = {"informatica", "ade", "economia", "derecho", "medicina", "enfermeria", "sociologia", "periodismo"}
if employment.get("cohort") != "2018–2019 · cuatro años después · 2023" or employment.get("granularity") != "Campo de estudio · España":
    raise AssertionError("Employment context: unexpected cohort or granularity")
if set(employment.get("fields", {})) != required_fields:
    raise AssertionError("Employment context: expected field coverage is incomplete")
for field, metrics in employment["fields"].items():
    if not metrics.get("label") or not 0 <= metrics["affiliation4"] <= 100 or metrics["contributionBase4"] <= 0:
        raise AssertionError(f"Employment context: invalid metrics for {field}")
series = json.loads(OUTCOME_EMPLOYMENT_SERIES.read_text(encoding="utf-8"))
years = series.get("years_after_graduation")
if years != [1, 2, 3, 4] or series.get("granularity") != "España · todos los ámbitos · tipo de universidad":
    raise AssertionError("Employment series: expected national four-year context")
for metric in ("affiliation", "indefinite", "full_time", "university_group", "contribution_base"):
    for scope in ("total", "public", "private"):
        values = series.get(metric, {}).get(scope)
        if not isinstance(values, list) or len(values) != 4 or any(not isinstance(value, (int, float)) or value < 0 for value in values):
            raise AssertionError(f"Employment series: invalid {metric}/{scope}")
print(f"Quality gate passed: {len(DATASETS)} datasets, {total} rows, {len(matches)} RUCT matches")
