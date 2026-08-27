"""Parse UIB 2025-2026 PAU/CFGS cutoff processes from official degree pages."""
from __future__ import annotations
import html
import json
import re
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from etl.admissions.normalize import normalize_record  # noqa: E402

SOURCE_URL = "https://estudis.uib.es/es/estudis-de-grau/com-hi-pots-accedir/admissio/notes-de-tall"
ROOT = Path("data/raw/admissions/illes-balears/2025-2026")
OUTPUT = Path("data/processed/admissions/illes-balears-2025-2026.json")
REPORT = Path("data/processed/admissions/illes-balears-2025-2026-quality.json")
ROW_RE = re.compile(r"<tr>(.*?)</tr>", re.I | re.S)
CELL_RE = re.compile(r"<td[^>]*>(.*?)</td>", re.I | re.S)
SCORE_RE = re.compile(r"^\d{1,2},\d{3}$")


def text(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html.unescape(value))).strip()


def title_from_page(page: str) -> str:
    match = re.search(r"<h2[^>]*>\s*Notas de corte de\s*(.*?)</h2>", page, re.I | re.S)
    return text(match.group(1)) if match else ""


def group_from_cell(cell: str) -> str:
    match = re.search(r"<a[^>]*>(.*?)</a>", cell, re.I | re.S)
    return text(match.group(1)) if match else ""


def parse() -> tuple[list[dict], dict]:
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    records: list[dict] = []
    rejected: list[dict] = []
    for item in manifest:
        raw_page = Path(item["file"]).read_bytes()
        try:
            page = raw_page.decode("utf-8")
        except UnicodeDecodeError:
            page = raw_page.decode("cp1252")
        degree = title_from_page(page)
        start = page.find('id="2025-26GEN_content"')
        next_section = page.find('id="2025-26', start + 1) if start >= 0 else -1
        section = page[start:next_section if next_section >= 0 else len(page)] if start >= 0 else ""
        rows = ROW_RE.findall(section)
        if not degree or not rows:
            rejected.append({"url": item["url"], "reason": "NO_2025_26_GENERAL_SECTION", "degree": degree})
            continue
        campus = "Palma"
        campus_match = re.search(r"\ben\s+(Menorca|Ibiza)\b", degree, re.I)
        if campus_match:
            campus = campus_match.group(1).title()
        for row_number, row in enumerate(rows[1:], 1):
            cells = CELL_RE.findall(row)
            if len(cells) < 5:
                continue
            cutoff = text(cells[0]).replace(" ", "")
            process = text(cells[3])
            source_date = text(cells[4])
            if not SCORE_RE.match(cutoff) or not re.search(r"\((?:JUN|EXT)\)", process, re.I) or not source_date.endswith("2025"):
                continue
            group = group_from_cell(cells[1])
            round_name = "extraordinary" if "EXT" in process.upper() else "ordinary"
            records.append(normalize_record({"community": "Illes Balears", "university": "Universitat de les Illes Balears", "campus": campus, "center": None, "degree": degree, "academic_year": "2025-2026", "admission_round": round_name, "admission_group": "general", "source_group": group or None, "waitlist_position": text(cells[2]) or None, "source_process": process, "source_date": source_date, "cutoff_score": cutoff.replace(",", "."), "source_url": item["url"], "source_page": 1, "source_row": row_number}))
    keys = [(row["degree"], row["campus"], row["admission_round"], row["source_group"], row["source_process"], row["source_date"], row["cutoff_score"], row["source_url"]) for row in records]
    report = {"source_url": SOURCE_URL, "academic_year": "2025-2026", "records": len(records), "rejected_pages": len(rejected), "duplicates": len(keys) - len(set(keys)), "scope": "PAU y Ciclos Formativos · processes marked JUN/EXT", "checks": {"cutoff_between_0_and_14": all(0 <= row["cutoff_score"] <= 14 for row in records), "round_explicit": all(row["admission_round"] in {"ordinary", "extraordinary"} for row in records), "general_group_explicit": all(row["admission_group"] == "group_1" for row in records), "no_replacement_glyph_in_names": all("�" not in row["degree"] for row in records), "no_duplicate_keys": len(keys) == len(set(keys))}, "rejections": rejected}
    return records, report


if __name__ == "__main__":
    rows, quality = parse()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REPORT.write_text(json.dumps(quality, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(rows), "rejected_pages": quality["rejected_pages"], "duplicates": quality["duplicates"], "checks": quality["checks"]}, ensure_ascii=False))
