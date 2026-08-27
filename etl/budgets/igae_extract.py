from __future__ import annotations

import argparse
import hashlib
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
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
            fiscal_year, period = workbook_period(root, strings)
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
                    "fiscal_year": fiscal_year,
                    "period": period,
                    "source_url": source_url,
                    "source_record_id": f"{sheet_name}:{row.attrib.get('r', '0')}",
                    "retrieved_at": datetime.now(timezone.utc).isoformat(),
                    "ingestion_run_id": run_id,
                    "raw_workbook_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                })
    return records


def numeric(value: str | None) -> str | None:
    if value in (None, "", "-"):
        return None
    return value


def quality_flags(final_credit: str | None, committed: str | None, recognized: str | None, paid: str | None) -> list[str]:
    values = [("committed_exceeds_final", committed, final_credit), ("recognized_exceeds_committed", recognized, committed), ("paid_exceeds_recognized", paid, recognized)]
    flags = []
    for flag, child, parent in values:
        if child is not None and parent is not None and child != "-" and parent != "-":
            try:
                if Decimal(child) > Decimal(parent):
                    flags.append(flag)
            except InvalidOperation:
                flags.append("unparseable_amount")
    return flags


def workbook_period(root: ET.Element, strings: list[str]) -> tuple[int, str]:
    # La fecha y el ejercicio aparecen en las primeras filas de cabecera.
    header_values = []
    for row in root.findall(".//m:row", NS):
        if int(row.attrib.get("r", "0")) > 3:
            continue
        for cell in row.findall("m:c", NS):
            value = cell_value(cell, strings)
            if value:
                header_values.append(value)
    text = " ".join(header_values).upper()
    months = {"ENERO": "01", "FEBRERO": "02", "MARZO": "03", "ABRIL": "04", "MAYO": "05", "JUNIO": "06", "JULIO": "07", "AGOSTO": "08", "SEPTIEMBRE": "09", "OCTUBRE": "10", "NOVIEMBRE": "11", "DICIEMBRE": "12"}
    month = next((number for name, number in months.items() if name in text), "00")
    year = next((int(value) for value in re.findall(r"\b20\d{2}\b", text) if 2000 <= int(value) <= 2100), 0)
    return year, f"{year}-{month}" if year and month != "00" else "unknown"


def parse_execution_workbook(path: Path, source_url: str, run_id: str) -> list[dict]:
    """Map the AGE execution sheets without collapsing accounting concepts."""
    levels = {"GTOS 001": "section", "GTOS 004": "chapter", "GTOS 002": "investment_section"}
    with ZipFile(path) as archive:
        strings = shared_strings(archive)
        result = []
        for sheet_name, sheet_path in sheet_names(archive):
            if sheet_name not in levels:
                continue
            root = ET.fromstring(archive.read(sheet_path))
            fiscal_year, period = workbook_period(root, strings)
            for row in root.findall(".//m:row", NS):
                values = {cell.attrib["r"]: cell_value(cell, strings) for cell in row.findall("m:c", NS)}
                label = values.get(f"A{row.attrib.get('r')}")
                if not label or row.attrib.get("r", "0") in {"1", "2", "3"}:
                    continue
                classification_code, separator, classification_name = label.partition(".")
                if not separator or not classification_code.strip().isdigit():
                    classification_code, classification_name = None, label
                result.append({
                    "fiscal_year": fiscal_year,
                    "period": period,
                    "classification_level": levels[sheet_name],
                    "classification_label": label.strip(),
                    "classification_code": classification_code.strip() if classification_code else None,
                    "classification_name": classification_name.strip() if classification_name else label.strip(),
                    "final_credit": numeric(values.get(f"B{row.attrib.get('r')}")),
                    "committed_amount": numeric(values.get(f"C{row.attrib.get('r')}")),
                    "recognized_amount": numeric(values.get(f"D{row.attrib.get('r')}")),
                    "paid_amount": numeric(values.get(f"E{row.attrib.get('r')}")),
                    "unit": "miles de euros",
                    "data_status": "provisional",
                    "period_state": "provisional",
                    "dataset_version": f"igae-{fiscal_year}-{period}-{hashlib.sha256(path.read_bytes()).hexdigest()[:12]}",
                    "source_url": source_url,
                    "source_record_id": f"{sheet_name}:{row.attrib.get('r')}",
                    "retrieved_at": datetime.now(timezone.utc).isoformat(),
                    "ingestion_run_id": run_id,
                    "raw_workbook_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                    "quality_flags": (["missing_final_credit"] if numeric(values.get(f"B{row.attrib.get('r')}")) is None else []) + quality_flags(
                        numeric(values.get(f"B{row.attrib.get('r')}")), numeric(values.get(f"C{row.attrib.get('r')}")), numeric(values.get(f"D{row.attrib.get('r')}")), numeric(values.get(f"E{row.attrib.get('r')}"))
                    ),
                })
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Extrae filas auditables del Excel oficial de ejecución AGE publicado por IGAE.")
    parser.add_argument("--url", required=True, help="URL oficial de un XLSX de IGAE")
    parser.add_argument("--raw-dir", default="data/raw/igae")
    parser.add_argument("--out", default="data/processed/igae/extract-2026-05.jsonl")
    parser.add_argument("--normalized-out", default="data/processed/igae/execution-2026-05.jsonl")
    args = parser.parse_args()
    run_id = datetime.now(timezone.utc).strftime("igae-%Y%m%dT%H%M%SZ")
    raw_path = Path(args.raw_dir) / f"{run_id}.xlsx"
    metadata = download(args.url, raw_path)
    records = parse_workbook(raw_path, args.url, run_id)
    write_jsonl(records, Path(args.out))
    execution = parse_execution_workbook(raw_path, args.url, run_id)
    write_jsonl(execution, Path(args.normalized_out))
    print({"run_id": run_id, "sheets": len({row['sheet'] for row in records}), "raw_records": len(records), "execution_records": len(execution), "raw": metadata})


if __name__ == "__main__":
    main()
