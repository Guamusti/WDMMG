from __future__ import annotations

import argparse
import hashlib
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZipFile

from etl.shared.io import download, write_jsonl

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main", "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def shared_strings(z: ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in z.namelist():
        return []
    root = ET.fromstring(z.read("xl/sharedStrings.xml"))
    return ["".join(item.itertext()).strip() for item in root.findall("m:si", NS)]


def cell_value(cell: ET.Element, strings: list[str]) -> str | None:
    value = cell.find("m:v", NS)
    if value is None:
        inline = cell.find("m:is", NS)
        return "".join(inline.itertext()).strip() if inline is not None else None
    raw = value.text
    if cell.attrib.get("t") == "s" and raw is not None:
        return strings[int(raw)]
    return raw


def sheet_names(z: ZipFile) -> list[tuple[str, str]]:
    workbook = ET.fromstring(z.read("xl/workbook.xml"))
    rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    targets = {rel.attrib["Id"]: rel.attrib["Target"] for rel in rels}
    result = []
    for sheet in workbook.find("m:sheets", NS):
        target = targets[sheet.attrib[f"{{{NS['r']}}}id"]]
        result.append((sheet.attrib["name"], "xl/" + target.lstrip("/")))
    return result


def parse_workbook(path: Path, source_url: str, run_id: str) -> list[dict]:
    with ZipFile(path) as archive:
        strings = shared_strings(archive)
        records = []
        for sheet_name, sheet_path in sheet_names(archive):
            root = ET.fromstring(archive.read(sheet_path))
            for row in root.findall(".//m:row", NS):
                values = {cell.attrib["r"]: cell_value(cell, strings) for cell in row.findall("m:c", NS)}
                values = {key: value for key, value in values.items() if value not in (None, "")}
                if not values:
                    continue
                label = next((value for key, value in values.items() if re.match(r"^[A-Z]+", key) and isinstance(value, str) and not value.replace('.', '', 1).replace('-', '', 1).isdigit()), None)
                records.append({
                    "sheet": sheet_name,
                    "row_number": int(row.attrib.get("r", "0")),
                    "label": label,
                    "columns": values,
                    "unit": "miles de euros",
                    "fiscal_year": 2026,
                    "period": "2026-05",
                    "source_url": source_url,
                    "source_record_id": f"{sheet_name}:{row.attrib.get('r', '0')}",
                    "retrieved_at": datetime.now(timezone.utc).isoformat(),
                    "ingestion_run_id": run_id,
                    "raw_workbook_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                })
    return records


def main() -> None:
    parser = argparse.ArgumentParser(description="Extrae filas auditables del Excel oficial de ejecución AGE publicado por IGAE.")
    parser.add_argument("--url", required=True, help="URL oficial de un XLSX de IGAE")
    parser.add_argument("--raw-dir", default="data/raw/igae")
    parser.add_argument("--out", default="data/processed/igae/extract-2026-05.jsonl")
    args = parser.parse_args()
    run_id = datetime.now(timezone.utc).strftime("igae-%Y%m%dT%H%M%SZ")
    raw_path = Path(args.raw_dir) / f"{run_id}.xlsx"
    metadata = download(args.url, raw_path)
    records = parse_workbook(raw_path, args.url, run_id)
    write_jsonl(records, Path(args.out))
    print({"run_id": run_id, "sheets": len({row['sheet'] for row in records}), "records_created": len(records), "raw": metadata})


if __name__ == "__main__":
    main()
