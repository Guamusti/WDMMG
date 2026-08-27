"""Parse the official UPNA last available 2025-2026 cutoff list."""
from __future__ import annotations
import json
import re
from pathlib import Path
import sys
import fitz

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from etl.admissions.normalize import normalize_record  # noqa: E402

SOURCE_URL = "https://www2.unavarra.es/gesadj/Estudios/acceso_matricula/notas_corte/2025/NOTASDECORTE2025-10septiembre.pdf"
PDF = Path("data/raw/admissions/navarra/2025-2026/notas-corte-upna-10-septiembre-2025.pdf")
OUTPUT = Path("data/processed/admissions/navarra-2025-2026.json")
REPORT = Path("data/processed/admissions/navarra-2025-2026-quality.json")
SCORE_RE = re.compile(r"^(\d{1,2}[,.]\d{1,3})(\*)?$")
LANGUAGE_MARKERS = ("ingeniaritza", "eta ", "zientzia", "hezkuntzako", "administrazioa", "zuzendaritza", "zuzenbidea", "erizaintza", "medikuntza", "biomedikoa", "ekonomia", "datuen", "bioteknologia", "gizarte", "harremanak", "ondarea", "irakasletza", "telekomunikazioaren", "elikagaien")


def clean_title(value: str) -> str:
    text = re.sub(r"\s+", " ", value).strip()
    text = re.sub(r"^GRADUA\s+", "", text, flags=re.I)
    text = re.sub(r"^(?:GRADO|DOBLE GRADO)\s+EN\s+", "", text, flags=re.I)
    return text.title() if text.isupper() else text


def spanish_title(block: list[str]) -> str:
    """Take the Spanish title from the block before a score, skipping Basque."""
    candidates = [line for line in block if not any(marker in line.lower() for marker in LANGUAGE_MARKERS)]
    if not candidates:
        return ""
    # Wrapped Spanish titles are the final two lines in the visual text block.
    title = candidates[-1]
    if len(candidates) >= 2 and (block[-1] == candidates[-1] and len(candidates[-1].split()) <= 2):
        title = f"{candidates[-2]} {candidates[-1]}"
    return clean_title(title)


def parse() -> tuple[list[dict], dict]:
    lines = [line.strip() for page in fitz.open(PDF) for line in page.get_text().splitlines() if line.strip()]
    records: list[dict] = []
    rejected: list[dict] = []
    score_indexes = [index for index, line in enumerate(lines) if SCORE_RE.match(line.replace(" ", ""))]
    for score_index in score_indexes:
        score_match = SCORE_RE.match(lines[score_index].replace(" ", ""))
        if not score_match:
            continue
        previous_score = max((candidate for candidate in score_indexes if candidate < score_index), default=4)
        title = spanish_title(lines[previous_score + 1:score_index])
        if not title:
            rejected.append({"line": score_index + 1, "title": "", "reason": "MISSING_TITLE"})
            continue
        round_name = "extraordinary" if score_match.group(2) else "last_call"
        records.append(normalize_record({"community": "Navarra", "university": "Universidad Pública de Navarra", "campus": "Pamplona", "center": None, "degree": title, "academic_year": "2025-2026", "admission_round": round_name, "admission_group": "general", "cutoff_score": score_match.group(1).replace(",", "."), "source_url": SOURCE_URL, "source_page": 1, "source_row": score_index + 1}))
    keys = [(row["degree"], row["cutoff_score"], row["academic_year"], row["admission_round"], row["admission_group"]) for row in records]
    report = {"source_url": SOURCE_URL, "academic_year": "2025-2026", "records": len(records), "rejected_rows": len(rejected), "duplicates": len(keys) - len(set(keys)), "round": "6th list · 10 September 2025; extraordinary marks preserved", "checks": {"cutoff_between_0_and_14": all(0 <= row["cutoff_score"] <= 14 for row in records), "no_replacement_glyph_in_names": all("�" not in row["degree"] for row in records), "admission_round_explicit": all(row["admission_round"] in {"last_call", "extraordinary"} for row in records), "general_group_explicit": all(row["admission_group"] == "group_1" for row in records), "no_duplicate_keys": len(keys) == len(set(keys))}, "rejections": rejected}
    return records, report


if __name__ == "__main__":
    rows, quality = parse()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REPORT.write_text(json.dumps(quality, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(rows), "rejected_rows": quality["rejected_rows"], "duplicates": quality["duplicates"], "checks": quality["checks"]}, ensure_ascii=False))
