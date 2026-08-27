"""Parse the official Catalonia first-assignment degree cutoffs."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import fitz

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from etl.admissions.normalize import normalize_record  # noqa: E402

SOURCE_URL = "https://universitats.gencat.cat/web/.content/02_preinscripcio/enllac-documents/notes-de-tall/Notes-tall-1a-assignacio_juny_2025_v3.pdf"
PDF = Path("data/raw/admissions/cataluna/2025-2026/notes-tall-1a-assignacio-juny-2025.pdf")
OUTPUT = Path("data/processed/admissions/cataluna-2025-2026.json")
REPORT = Path("data/processed/admissions/cataluna-2025-2026-quality.json")
CODE_RE = re.compile(r"^(\d{5})\s+(.+)$")
NUMBER_RE = re.compile(r"\b([0-9]{1,2},[0-9]{3})\b")


def parse() -> tuple[list[dict], dict]:
    records: list[dict] = []
    rejected: list[dict] = []
    doc = fitz.open(PDF)
    for page_number, page in enumerate(doc, 1):
        rows: list[tuple[str, list[str]]] = []
        current: tuple[str, list[str]] | None = None
        for line in (page.get_text() or "").splitlines():
            text = re.sub(r"\s+", " ", line.strip())
            match = CODE_RE.match(text)
            if match:
                if current:
                    rows.append(current)
                current = (match.group(1), [match.group(2)])
            elif current:
                current[1].append(text)
        if current:
            rows.append(current)
        for code, row_lines in rows:
            text = re.sub(r"\s+", " ", " ".join(row_lines))
            if "TÍTOLS PROPIS" in text or "ESTUDIS DE GRAU" in text:
                continue
            cutoff_match = NUMBER_RE.search(text)
            if not cutoff_match:
                rejected.append({"page": page_number, "code": code, "reason": "NO_PAU_CUTOFF", "raw": text})
                continue
            prefix = text[:cutoff_match.start()].strip()
            context_match = re.search(r"\(([^()]*)\)\s+([A-Za-z][A-Za-z0-9+\-/]*(?:\s*/\s*[A-Za-z][A-Za-z0-9+\-/]*)*)$", prefix)
            if not context_match:
                rejected.append({"page": page_number, "code": code, "reason": "TITLE_OR_CITY_UNRESOLVED", "raw": text})
                continue
            city, university = context_match.groups()
            degree = prefix[:context_match.start()].strip()
            if "�" in degree or not degree or not city:
                rejected.append({"page": page_number, "code": code, "reason": "MALFORMED_NAME", "raw": text})
                continue
            records.append(normalize_record({
                "community": "Cataluña", "university": university.strip(), "campus": city,
                "degree_code": code, "degree": degree, "academic_year": "2025-2026",
                "admission_round": "assignment_1", "admission_group": "group_1",
                "cutoff_score": cutoff_match.group(1).replace(",", "."), "source_url": SOURCE_URL,
                "source_page": page_number,
            }))
    keys = [(r["degree_code"], r["campus"], r["university"], r["cutoff_score"]) for r in records]
    report = {"source_url": SOURCE_URL, "academic_year": "2025-2026", "records": len(records), "rejected_rows": len(rejected), "duplicates": len(keys) - len(set(keys)), "checks": {"cutoff_between_0_and_14": all(0 <= r["cutoff_score"] <= 14 for r in records), "no_replacement_glyph_in_names": all("�" not in (r["degree"] + r["university"] + r["campus"]) for r in records), "assignment_explicit": all(r["admission_round"] == "assignment_1" for r in records), "no_duplicate_keys": len(keys) == len(set(keys))}, "rejections": rejected}
    return records, report


if __name__ == "__main__":
    rows, quality = parse()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REPORT.write_text(json.dumps(quality, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(rows), "rejected_rows": quality["rejected_rows"], "duplicates": quality["duplicates"], "checks": quality["checks"]}, ensure_ascii=False))
