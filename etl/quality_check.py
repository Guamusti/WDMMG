"""Dependency-free quality gate for committed processed admissions data."""
import json
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
        if "�" in " ".join(str(row.get(field, "")) for field in ("degree", "university", "campus")):
            raise AssertionError(f"{path}:{index}: replacement glyph in name")
    return len(rows)


total = sum(check(path) for path in DATASETS)
print(f"Quality gate passed: {len(DATASETS)} datasets, {total} rows")
