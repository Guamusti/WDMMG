"""Parse the official University of León general cutoffs for 2025/2026."""
from __future__ import annotations
import json
import re
from pathlib import Path
import sys
import fitz

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from etl.admissions.normalize import normalize_record  # noqa: E402

SOURCE_URL = "https://www.unileon.es/files/2025-11/notas_de_corte_2025nw.pdf"
PDF = Path("data/raw/admissions/castilla-leon/2025-2026/notas-de-corte-unileon-2025-2026.pdf")
OUTPUT = Path("data/processed/admissions/castilla-leon-2025-2026.json")
REPORT = Path("data/processed/admissions/castilla-leon-2025-2026-quality.json")
TITLE_RE = re.compile(r"^(?:G\.?\s*|PCEO\s+G\.?\s*)", re.I)
SCORE_RE = re.compile(r"(?:\*|g|§)?\s*([0-9]{1,2}(?:,[0-9]{1,3})?)$")
DEGREE_START = re.compile(r"^(?:G\.?\s*|PCEO\s+G\.?\s*)", re.I)
CAMPUS_RE = re.compile(r"\((LE[ÓO]N|PONFERRADA)\)", re.I)


def clean_title(title: str) -> tuple[str, str | None]:
    campus_match = CAMPUS_RE.search(title)
    campus = campus_match.group(1).title() if campus_match else None
    text = re.sub(r"\s+", " ", title).strip(" *")
    is_double = text.upper().startswith("PCEO")
    text = TITLE_RE.sub("", text).strip(" *")
    replacements = {
        "CC.": "Ciencias", "ING.": "Ingeniería",
        "ADMÓN.": "Administración", "ADMON.": "Administración",
        "DIRECC.": "Dirección", "REL.": "Relaciones", "G.": "",
    }
    for old, new in replacements.items():
        text = re.sub(rf"\b{re.escape(old)}", new, text, flags=re.I)
    text = re.sub(r"\s+", " ", text).strip(" *")
    text = re.sub(r"^EN\s+", "", text, flags=re.I)
    words = text.lower().title().split()
    small = {"Y", "E", "De", "Del", "La", "El", "En"}
    text = " ".join(word.lower() if index and word in small else word for index, word in enumerate(words))
    return (("Doble grado en " if is_double else "") + text, campus)


def parse() -> tuple[list[dict], dict]:
    lines = [line.strip() for page in fitz.open(PDF) for line in page.get_text().splitlines() if line.strip()]
    records: list[dict] = []
    rejected: list[dict] = []
    center = None
    index = 0
    while index < len(lines):
        line = lines[index]
        if line.upper().startswith(("FACULTAD ", "ESCUELA ")):
            center = line
            index += 1
            continue
        if not DEGREE_START.match(line):
            index += 1
            continue
        if index + 1 >= len(lines) or not re.fullmatch(r"\d+", lines[index + 1]):
            rejected.append({"line": index + 1, "title": line, "reason": "MISSING_PLACES"})
            index += 1
            continue
        title, campus_from_title = clean_title(line)
        score = None
        score_line = None
        for candidate in lines[index + 2:index + 9]:
            match = SCORE_RE.fullmatch(candidate)
            if match:
                score = match.group(1).replace(",", ".")
                score_line = candidate
                break
        if not score or "�" in title:
            rejected.append({"line": index + 1, "title": title, "reason": "MISSING_GENERAL_CUTOFF"})
        else:
            records.append(normalize_record({
                "community": "Castilla y León", "university": "Universidad de León",
                "campus": campus_from_title or "León", "center": center,
                "source_row": index + 1,
                "degree": title, "academic_year": "2025-2026", "admission_round": "ordinary",
                "admission_group": "general", "cutoff_score": score,
                "source_url": SOURCE_URL, "source_page": 1,
            }))
        index += 2
        if score_line:
            index += lines[index:].index(score_line) + 1
    keys = [(r["campus"], r["center"], r["degree"], r["academic_year"], r["admission_round"], r["admission_group"], r["source_row"]) for r in records]
    report = {"source_url": SOURCE_URL, "academic_year": "2025-2026", "records": len(records), "rejected_rows": len(rejected), "duplicates": len(keys) - len(set(keys)), "checks": {"cutoff_between_0_and_14": all(0 <= r["cutoff_score"] <= 14 for r in records), "no_replacement_glyph_in_names": all("�" not in r["degree"] for r in records), "ordinary_round_explicit": all(r["admission_round"] == "ordinary" for r in records), "general_group_explicit": all(r["admission_group"] == "group_1" for r in records), "no_duplicate_keys": len(keys) == len(set(keys))}, "rejections": rejected}
    return records, report


if __name__ == "__main__":
    rows, quality = parse(); OUTPUT.parent.mkdir(parents=True, exist_ok=True); OUTPUT.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"); REPORT.write_text(json.dumps(quality, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"); print(json.dumps({"records": len(rows), "rejected_rows": quality["rejected_rows"], "duplicates": quality["duplicates"], "checks": quality["checks"]}, ensure_ascii=False))
