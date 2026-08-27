"""Parse the official University of Salamanca second 2025/2026 list."""
from __future__ import annotations
import json
import re
from pathlib import Path
import sys
import fitz

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from etl.admissions.normalize import normalize_record  # noqa: E402

SOURCE_URL = "https://comunicacion.usal.es/sites/comunicacion.usal.es/files/180725_2___Listado_Notas_de_corte_2025_2026..pdf"
PDF = Path("data/raw/admissions/castilla-leon/2025-2026/notas-de-corte-usal-2025-2026.pdf")
OUTPUT = Path("data/processed/admissions/salamanca-2025-2026.json")
REPORT = Path("data/processed/admissions/salamanca-2025-2026-quality.json")
TITLE_RE = re.compile(r"^(?:Grado en |Doble Titulación de Grado(?: en)? |Doble Grado en )", re.I)
NUMBER_RE = re.compile(r"(?<!\d)(\d{1,2}[,.]\d{1,3})(?!\d)")


def clean_title(value: str) -> tuple[str, str | None]:
    text = re.sub(r"\s+", " ", value).strip(" -")
    is_double = text.lower().startswith(("doble titulación", "doble grado"))
    text = TITLE_RE.sub("", text).strip()
    for old, new in {"Dir.": "Dirección", "Adm.": "Administración", "Púb.": "Pública", "Ing.": "Ingeniería", "Admón.": "Administración", "Empresas y": "Empresas y"}.items():
        text = re.sub(rf"\b{re.escape(old)}", new, text, flags=re.I)
    campus_match = re.search(r"\((Ávila|Salamanca|Zamora|Béjar)\)", text, re.I)
    campus = campus_match.group(1).title() if campus_match else "Salamanca"
    text = re.sub(r"\s+", " ", text).strip()
    text = text.replace("Dirección Empresas", "Dirección de Empresas").replace("y en Recursos Humanos", "y Recursos Humanos").replace("))", ")")
    return (("Doble grado en " if is_double else "") + text, campus)


def parse() -> tuple[list[dict], dict]:
    lines = [line.strip() for page in fitz.open(PDF) for line in page.get_text().splitlines() if line.strip()]
    records: list[dict] = []
    rejected: list[dict] = []
    title_lines: list[str] = []
    for line_number, line in enumerate(lines, 1):
        if line.lower().startswith(("grado en ", "doble titulación", "doble grado")):
            title_lines = [line]
            continue
        if not title_lines:
            continue
        scores = NUMBER_RE.findall(line)
        if not scores:
            title_lines.append(line)
            continue
        title, campus = clean_title(" ".join(title_lines))
        raw_score = scores[-1].replace(",", ".")
        if "�" in title or not title:
            rejected.append({"line": line_number, "title": title, "reason": "MALFORMED_TITLE"})
        else:
            records.append(normalize_record({"community": "Castilla y León", "university": "Universidad de Salamanca", "campus": campus, "center": None, "degree": title, "academic_year": "2025-2026", "admission_round": "ordinary", "admission_group": "general", "cutoff_score": raw_score, "source_url": SOURCE_URL, "source_page": 1, "source_row": line_number}))
        title_lines = []
    keys = [(r["campus"], r["degree"], r["source_row"]) for r in records]
    report = {"source_url": SOURCE_URL, "academic_year": "2025-2026", "list": "second ordinary list", "records": len(records), "rejected_rows": len(rejected), "duplicates": len(keys) - len(set(keys)), "checks": {"cutoff_between_0_and_14": all(0 <= r["cutoff_score"] <= 14 for r in records), "no_replacement_glyph_in_names": all("�" not in r["degree"] for r in records), "ordinary_round_explicit": all(r["admission_round"] == "ordinary" for r in records), "general_group_explicit": all(r["admission_group"] == "group_1" for r in records), "no_duplicate_keys": len(keys) == len(set(keys))}, "rejections": rejected}
    return records, report


if __name__ == "__main__":
    rows, quality = parse(); OUTPUT.parent.mkdir(parents=True, exist_ok=True); OUTPUT.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"); REPORT.write_text(json.dumps(quality, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"); print(json.dumps({"records": len(rows), "rejected_rows": quality["rejected_rows"], "duplicates": quality["duplicates"], "checks": quality["checks"]}, ensure_ascii=False))
