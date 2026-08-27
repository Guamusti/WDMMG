"""Parse the official University of Zaragoza ordinary cutoff PDF."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import fitz

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from etl.admissions.normalize import normalize_record  # noqa: E402

SOURCE_URL = "https://academico.unizar.es/sites/academico/files/archivos/acceso/admisgrado/corte/grados2526j.pdf"
PDF = Path("data/raw/admissions/aragon/2025-2026/grados2526j.pdf")
OUTPUT = Path("data/processed/admissions/aragon-2025-2026.json")
REPORT = Path("data/processed/admissions/aragon-2025-2026-quality.json")
PROVINCES = {"ZARAGOZA", "LA ALMUNIA", "HUESCA", "TERUEL"}
NUMBER_RE = re.compile(r"\b([0-9]{1,2},[0-9]{3})\b")


def parse() -> tuple[list[dict], dict]:
    records: list[dict] = []
    rejected: list[dict] = []
    province = ""
    doc = fitz.open(PDF)
    for page_number, page in enumerate(doc, 1):
        lines: dict[tuple[int, int], list[tuple[float, str]]] = {}
        for x0, y0, _x1, _y1, text, block, line, _word in page.get_text("words"):
            lines.setdefault((block, line), []).append((x0, text))
        ordered = sorted(lines.items())
        for index, (_key, words) in enumerate(ordered):
            words.sort()
            text = re.sub(r"\s+", " ", " ".join(word for _x, word in words).strip())
            upper = text.upper()
            if upper in PROVINCES:
                province = text.title() if upper != "LA ALMUNIA" else "La Almunia"
                continue
            if not province or not text or upper.startswith(("TITULACIONES", "CUPO", "NOTAS ", "ADJUDICACIÓN", "FECHA:", "(1)", "PV =", "PNV =", "NPV =", "NPNV =", "DEPORTISTAS", "45 AÑOS", "25 AÑOS")):
                continue
            if upper in {"GENERAL", "TITULADOS", "DISCAPAC.", "MAYORES", "ZARAGOZA", "LA ALMUNIA", "HUESCA", "TERUEL"}:
                continue
            # The extractor places the title and score on consecutive visual lines.
            numeric_words = [(x, word) for x, word in words if x > 400 and NUMBER_RE.fullmatch(word)]
            if not numeric_words and any(x < 400 for x, _word in words) and index + 1 < len(ordered):
                next_words = ordered[index + 1][1]
                numeric_words = [(x, word) for x, word in next_words if x > 400 and NUMBER_RE.fullmatch(word)]
            if not any(x < 400 for x, _word in words):
                continue
            match = NUMBER_RE.fullmatch(numeric_words[0][1]) if numeric_words else None
            if not match:
                continue
            degree = re.sub(r"\s+", " ", " ".join(word for x, word in words if x < 400)).strip(" -")
            if len(degree) < 4 or "�" in degree:
                rejected.append({"page": page_number, "province": province, "degree": degree, "reason": "MALFORMED_TITLE"})
                continue
            records.append(normalize_record({
                "community": "Aragón",
                "university": "Universidad de Zaragoza",
                "campus": province,
                "degree": degree.title(),
                "academic_year": "2025-2026",
                "admission_round": "ordinary",
                "admission_group": "general",
                "cutoff_score": match.group(1).replace(",", "."),
                "source_url": SOURCE_URL,
                "source_page": page_number,
            }))
    keys = [(r["campus"], r["degree"], r["admission_round"], r["admission_group"]) for r in records]
    report = {
        "source_url": SOURCE_URL,
        "academic_year": "2025-2026",
        "records": len(records),
        "rejected_rows": len(rejected),
        "duplicates": len(keys) - len(set(keys)),
        "provinces": sorted(set(r["campus"] for r in records)),
        "checks": {
            "cutoff_between_0_and_14": all(0 <= r["cutoff_score"] <= 14 for r in records),
            "no_replacement_glyph_in_names": all("�" not in (r["degree"] + r["university"] + r["campus"]) for r in records),
            "ordinary_round_explicit": all(r["admission_round"] == "ordinary" for r in records),
            "no_duplicate_keys": len(keys) == len(set(keys)),
        },
        "rejections": rejected,
    }
    return records, report


if __name__ == "__main__":
    rows, quality = parse()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REPORT.write_text(json.dumps(quality, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(rows), "rejected_rows": quality["rejected_rows"], "duplicates": quality["duplicates"], "checks": quality["checks"]}, ensure_ascii=False))
