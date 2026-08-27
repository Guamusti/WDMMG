"""Common normalization primitives for autonomous-community admission files."""
import re

YEAR = re.compile(r"(20\d{2})\s*[-/]\s*(20\d{2})")


def academic_year(value):
    match = YEAR.search(str(value or ""))
    if not match:
        raise ValueError(f"Invalid academic year: {value!r}")
    start, end = map(int, match.groups())
    if end != start + 1:
        raise ValueError(f"Non-consecutive academic year: {value!r}")
    return f"{start:04d}-{end:04d}"


def cutoff(value):
    if value in (None, ""):
        return None
    number = float(str(value).replace(",", "."))
    if not 0 <= number <= 14:
        raise ValueError(f"Cutoff outside 0-14: {value!r}")
    return number


def admission_round(value):
    text = str(value or "").strip().lower()
    aliases = {"ord": "ordinary", "ordinaria": "ordinary", "ordinaria": "ordinary", "ext": "extraordinary", "extraordinaria": "extraordinary", "definitiva": "definitive", "última": "last_call", "ultima": "last_call"}
    return aliases.get(text, text or "unknown")


def admission_group(value):
    text = str(value or "").strip().lower()
    return {"grupo 1": "group_1", "group 1": "group_1", "general": "group_1", "cupo general": "group_1"}.get(text, text or "unknown")


def normalize_record(record):
    """Normalize shared fields while leaving source-specific fields untouched."""
    normalized = dict(record)
    normalized["academic_year"] = academic_year(record.get("academic_year"))
    normalized["cutoff_score"] = cutoff(record.get("cutoff_score"))
    normalized["admission_round"] = admission_round(record.get("admission_round"))
    normalized["admission_group"] = admission_group(record.get("admission_group"))
    return normalized


if __name__ == "__main__":
    assert normalize_record({"academic_year": "2025/2026", "cutoff_score": "10,175", "admission_round": "Ord", "admission_group": "Grupo 1"})["cutoff_score"] == 10.175
    print("Admission normalization smoke test: ok")
