"""Parse the official Universidad de La Rioja cutoff workbook."""
from __future__ import annotations

import json
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from etl.admissions.normalize import normalize_record  # noqa: E402

SOURCE_URL = (
    "https://www.unirioja.es/administracion-y-servicios/"
    "area-academica-y-de-coordinacion/transparencia-estudiantes/"
)
WORKBOOK = Path("data/raw/admissions/la-rioja/2025-2026/unirioja-notas-corte-2025-2026.xlsx")
OUTPUT = Path("data/processed/admissions/la-rioja-2025-2026.json")
REPORT = Path("data/processed/admissions/la-rioja-2025-2026-quality.json")
NS = {"main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}

BRANCHES = {
    "201": "Ciencias Sociales y Jurídicas",
    "202": "Ciencias Sociales y Jurídicas",
    "203": "Ciencias Sociales y Jurídicas",
    "204": "Ciencias Sociales y Jurídicas",
    "205": "Ciencias Sociales y Jurídicas",
    "206": "Ciencias Sociales y Jurídicas",
    "207": "Ciencias Sociales y Jurídicas",
    "301": "Ciencias de la Salud",
    "601": "Artes y Humanidades",
    "602": "Artes y Humanidades",
    "603": "Artes y Humanidades",
    "701": "Ciencias",
    "702": "Ciencias",
    "703": "Ciencias",
    "801": "Ingeniería y Arquitectura",
    "802": "Ingeniería y Arquitectura",
    "803": "Ingeniería y Arquitectura",
    "804": "Ingeniería y Arquitectura",
    "805": "Ingeniería y Arquitectura",
}


def workbook_rows(path: Path) -> list[list[str | float | None]]:
    """Read the first worksheet using only the Python standard library."""
    with zipfile.ZipFile(path) as archive:
        shared: list[str] = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            for item in root.findall("main:si", NS):
                shared.append("".join(node.text or "" for node in item.iter() if node.tag.endswith("}t")))
        sheet = ET.fromstring(archive.read("xl/worksheets/sheet1.xml"))
        rows: list[list[str | float | None]] = []
        for row in sheet.findall("main:sheetData/main:row", NS):
            cells: dict[int, str | float | None] = {}
            for cell in row.findall("main:c", NS):
                ref = cell.attrib.get("r", "A1")
                column = 0
                for char in re.match(r"[A-Z]+", ref).group(0):
                    column = column * 26 + ord(char) - 64
                column -= 1
                value = cell.find("main:v", NS)
                raw = value.text if value is not None else None
                if raw is None:
                    result: str | float | None = None
                elif cell.attrib.get("t") == "s":
                    result = shared[int(raw)]
                else:
                    try:
                        result = float(raw)
                    except ValueError:
                        result = raw
                cells[column] = result
            if cells:
                rows.append([cells.get(index) for index in range(max(cells) + 1)])
    return rows


def parse() -> tuple[list[dict], dict]:
    rows = workbook_rows(WORKBOOK)
    if not rows or rows[0][-1] != "2025-26":
        raise ValueError("Unexpected Universidad de La Rioja workbook header")
    records: list[dict] = []
    rejected: list[dict] = []
    for index, row in enumerate(rows[1:], 2):
        label = str(row[0] or "").strip()
        cutoff = row[-1] if row else None
        if not label:
            continue
        match = re.match(r"(\d{3})\s*G\s+Grado en (.+)$", label)
        if not match or not isinstance(cutoff, (int, float)):
            rejected.append({"row": index, "raw": row, "reason": "SNC_OR_NON_DEGREE"})
            continue
        code, degree = match.groups()
        records.append(normalize_record({
            "community": "La Rioja",
            "university": "Universidad de La Rioja",
            "campus": "Logroño",
            "center": None,
            "degree": degree,
            "branch": BRANCHES[code],
            "academic_year": "2025-2026",
            "admission_round": "ordinary",
            "admission_group": "general",
            "cutoff_score": cutoff,
            "places": None,
            "source_url": SOURCE_URL,
            "source_page": 1,
            "source_row": index,
            "source_file": str(WORKBOOK),
            "source_degree_code": f"{code}G",
        }))
    keys = [(row["degree"], row["academic_year"], row["admission_round"], row["admission_group"]) for row in records]
    report = {
        "source_url": SOURCE_URL,
        "academic_year": "2025-2026",
        "records": len(records),
        "rejected_rows": len(rejected),
        "duplicates": len(keys) - len(set(keys)),
        "round": "ordinary initial cutoff before list decreases",
        "checks": {
            "cutoff_between_0_and_14": all(0 <= row["cutoff_score"] <= 14 for row in records),
            "round_explicit": all(row["admission_round"] == "ordinary" for row in records),
            "general_group_explicit": all(row["admission_group"] == "group_1" for row in records),
            "branch_explicit": all(row["branch"] in set(BRANCHES.values()) for row in records),
            "no_duplicate_keys": len(keys) == len(set(keys)),
            "snc_rows_rejected": len(rejected) == 8,
        },
        "rejections": rejected,
    }
    return records, report


if __name__ == "__main__":
    parsed, quality = parse()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(parsed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REPORT.write_text(json.dumps(quality, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(parsed), "rejected_rows": quality["rejected_rows"], "checks": quality["checks"]}, ensure_ascii=False))
