"""Parse official Distrito Único Andaluz 2025 general cutoffs."""
from __future__ import annotations
import json
import re
from html.parser import HTMLParser
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from etl.admissions.normalize import normalize_record  # noqa: E402

SOURCE_URL = "https://www.juntadeandalucia.es/economiaconocimientoempresasyuniversidad/sguit/index.php?d=g_not_cor_anteriores_top.php&q=grados"
HTML = Path("data/raw/admissions/andalucia/2025-2026/notas-de-corte-general-2025-2026.html")
OUTPUT = Path("data/processed/admissions/andalucia-2025-2026.json")
REPORT = Path("data/processed/admissions/andalucia-2025-2026-quality.json")
SCORE_RE = re.compile(r"\b([0-9]{1,2},[0-9]{3})\b")
BRANCHES = {"SD": "Ciencias de la Salud", "AYH": "Artes y Humanidades", "C": "Ciencias", "IYA": "Ingeniería y Arquitectura", "SYJ": "Ciencias Sociales y Jurídicas"}
UNIVERSITIES = {name: f"Universidad de {name.title()}" for name in ("ALMERÍA", "CÁDIZ", "CÓRDOBA", "GRANADA", "HUELVA", "JAÉN", "MÁLAGA", "SEVILLA")}
UNIVERSITIES["PABLO DE OLAVIDE"] = "Universidad Pablo de Olavide"
UNIVERSITIES["P. OLAVIDE"] = "Universidad Pablo de Olavide"


class TableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(); self.in_tr = False; self.in_td = False; self.parts: list[str] = []; self.cells: list[list[str]] = []; self.rows: list[list[list[str]]] = []
    def handle_starttag(self, tag: str, _attrs) -> None:
        if tag == "tr": self.in_tr = True; self.cells = []
        elif tag == "td" and self.in_tr: self.in_td = True; self.parts = [""]
        elif tag == "hr" and self.in_td: self.parts.append("")
        elif tag == "br" and self.in_td: self.parts[-1] += " "
    def handle_endtag(self, tag: str) -> None:
        if tag == "td" and self.in_td: self.cells.append([" ".join(part.split()) for part in self.parts]); self.in_td = False
        elif tag == "tr" and self.in_tr:
            if self.cells: self.rows.append(self.cells)
            self.in_tr = False
    def handle_data(self, data: str) -> None:
        if self.in_td and self.parts: self.parts[-1] += data


def parse() -> tuple[list[dict], dict]:
    parser = TableParser(); parser.feed(HTML.read_bytes().decode("iso-8859-1"))
    records: list[dict] = []; rejected: list[dict] = []
    for row_number, cells in enumerate(parser.rows, 1):
        if len(cells) < 3: continue
        metadata = cells[0][0]; degree = cells[1][-1].strip(" -") if len(cells[1]) > 1 else ""; score = SCORE_RE.search(cells[2][0] if cells[2] else "")
        match = re.fullmatch(r"2025\s*\|\s*(.+?)\s*\|\s*(SD|AYH|C|IYA|SYJ)", metadata)
        if not match or not degree or not score:
            if metadata.startswith("2025"): rejected.append({"row": row_number, "metadata": metadata, "degree": degree, "reason": "INCOMPLETE"})
            continue
        raw_university, branch_code = match.groups()
        records.append(normalize_record({"community": "Andalucía", "university": UNIVERSITIES.get(raw_university.strip(), raw_university.title()), "campus": None, "center": cells[1][0], "degree": degree, "branch": BRANCHES[branch_code], "academic_year": "2025-2026", "admission_round": "ordinary", "admission_group": "general", "cutoff_score": score.group(1).replace(",", "."), "source_url": SOURCE_URL, "source_page": row_number}))
    keys = [(r["university"], r["center"], r["degree"], r["branch"], r["academic_year"], r["admission_round"], r["admission_group"]) for r in records]
    report = {"source_url": SOURCE_URL, "academic_year": "2025-2026", "records": len(records), "rejected_rows": len(rejected), "duplicates": len(keys) - len(set(keys)), "universities": sorted({r["university"] for r in records}), "checks": {"cutoff_between_0_and_14": all(0 <= r["cutoff_score"] <= 14 for r in records), "no_replacement_glyph_in_names": all("�" not in (r["degree"] + r["university"]) for r in records), "ordinary_round_explicit": all(r["admission_round"] == "ordinary" for r in records), "general_group_explicit": all(r["admission_group"] == "group_1" for r in records), "branch_explicit": all(r["branch"] in BRANCHES.values() for r in records), "no_duplicate_keys": len(keys) == len(set(keys))}, "rejections": rejected}
    return records, report


if __name__ == "__main__":
    rows, quality = parse(); OUTPUT.parent.mkdir(parents=True, exist_ok=True); OUTPUT.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"); REPORT.write_text(json.dumps(quality, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"); print(json.dumps({"records": len(rows), "rejected_rows": quality["rejected_rows"], "duplicates": quality["duplicates"], "checks": quality["checks"]}, ensure_ascii=False))
