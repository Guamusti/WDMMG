"""Parse the University of Oviedo's published 2025-2026 cutoff table."""
from __future__ import annotations
import html
import json
import re
from html.parser import HTMLParser
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from etl.admissions.normalize import normalize_record  # noqa: E402

SOURCE_URL = "https://torres.epv.uniovi.es/centon/notas-acceso-oviedo-25.html"
HTML_FILE = Path("data/raw/admissions/asturias/2025-2026/notas-acceso-oviedo-julio-2025.html")
OUTPUT = Path("data/processed/admissions/asturias-2025-2026.json")
REPORT = Path("data/processed/admissions/asturias-2025-2026-quality.json")
SCORE_RE = re.compile(r"^\d{1,2}[,.]\d{1,3}$")


class TableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_row = False
        self.in_cell = False
        self.rows: list[list[str]] = []
        self.current: list[str] = []
        self.text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "tr":
            self.in_row = True
            self.current = []
        elif tag in {"td", "th"} and self.in_row:
            self.in_cell = True
            self.text = []

    def handle_data(self, data: str) -> None:
        if self.in_cell:
            self.text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag in {"td", "th"} and self.in_cell:
            self.current.append(re.sub(r"\s+", " ", html.unescape("".join(self.text))).strip())
            self.in_cell = False
        elif tag == "tr" and self.in_row:
            if self.current:
                self.rows.append(self.current)
            self.in_row = False


def parse() -> tuple[list[dict], dict]:
    parser = TableParser()
    parser.feed(HTML_FILE.read_text(encoding="utf-8"))
    records: list[dict] = []
    rejected: list[dict] = []
    for index, row in enumerate(parser.rows[1:], 1):
        if len(row) < 3 or not SCORE_RE.match(row[2]):
            rejected.append({"row": index, "raw": row, "reason": "MISSING_OR_INVALID_CUTOFF"})
            continue
        degree = row[0].replace(" /", " / ").replace("  ", " ").strip()
        campus_match = re.search(r"\(([^)]+)\)", degree)
        campus = campus_match.group(1).replace("Facultad de ", "").replace("Facultad ", "").strip() if campus_match else "Oviedo"
        records.append(normalize_record({"community": "Asturias", "university": "Universidad de Oviedo", "campus": campus, "center": None, "degree": degree, "academic_year": "2025-2026", "admission_round": "first_call", "admission_group": "general", "cutoff_score": row[2].replace(",", "."), "places": int(row[1]), "source_url": SOURCE_URL, "source_page": 1, "source_row": index}))
    keys = [(row["degree"], row["campus"], row["academic_year"], row["admission_round"], row["admission_group"]) for row in records]
    report = {"source_url": SOURCE_URL, "academic_year": "2025-2026", "records": len(records), "rejected_rows": len(rejected), "duplicates": len(keys) - len(set(keys)), "round": "first phase of July 2025", "checks": {"cutoff_between_0_and_14": all(0 <= row["cutoff_score"] <= 14 for row in records), "places_positive": all(row["places"] > 0 for row in records), "no_replacement_glyph_in_names": all("�" not in row["degree"] for row in records), "round_explicit": all(row["admission_round"] == "first_call" for row in records), "general_group_explicit": all(row["admission_group"] == "group_1" for row in records), "no_duplicate_keys": len(keys) == len(set(keys))}, "rejections": rejected}
    return records, report


if __name__ == "__main__":
    rows, quality = parse()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REPORT.write_text(json.dumps(quality, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(rows), "rejected_rows": quality["rejected_rows"], "duplicates": quality["duplicates"], "checks": quality["checks"]}, ensure_ascii=False))
