from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from etl.shared.io import download, write_jsonl


BASE_URL = "https://www.infosubvenciones.es/bdnstrans/api/concesiones/busqueda"


def text_value(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, dict):
        for key in ("nombre", "name", "descripcion", "description", "valor"):
            if value.get(key):
                return str(value[key]).strip()
        return None
    return str(value).strip() or None


def parse_page(payload: dict[str, Any], code: str, source_url: str, retrieved_at: str, run_id: str, raw_sha256: str) -> list[dict[str, Any]]:
    records = []
    for index, item in enumerate(payload.get("content", [])):
        if not isinstance(item, dict):
            continue
        source_record_id = str(item.get("codConcesion") or item.get("id") or f"{code}-{index}")
        records.append({
            "bdns_code": code,
            "beneficiary": text_value(item.get("beneficiario") or item.get("beneficiary")),
            "amount": item.get("importe", item.get("amount")),
            "award_date": item.get("fechaConcesion", item.get("awardDate")),
            "instrument": text_value(item.get("instrumento") or item.get("instrument")),
            "purpose": text_value(item.get("finalidad") or item.get("purpose")),
            "source_url": source_url,
            "source_record_id": source_record_id,
            "retrieved_at": retrieved_at,
            "ingestion_run_id": run_id,
            "raw_payload_sha256": raw_sha256,
            "raw_record": item,
        })
    return records


def ingest(code: str, raw_dir: Path, out: Path, page_size: int = 100, max_pages: int = 100) -> dict[str, Any]:
    run_id = datetime.now(timezone.utc).strftime("bdns-concesiones-%Y%m%dT%H%M%SZ")
    records: list[dict[str, Any]] = []
    pages = 0
    for page in range(max_pages):
        endpoint = f"{BASE_URL}?numeroConvocatoria={code}&pageSize={page_size}&page={page}"
        raw_path = raw_dir / f"{run_id}-page-{page}.payload"
        metadata = download(endpoint, raw_path)
        payload = json.loads(raw_path.read_text(encoding="utf-8"))
        page_records = parse_page(payload, code, endpoint, metadata["retrieved_at"], run_id, metadata["sha256"])
        records.extend(page_records)
        pages += 1
        if len(page_records) < page_size or not payload.get("content"):
            break
    write_jsonl(records, out)
    return {"run_id": run_id, "pages": pages, "records_created": len(records), "output": str(out)}


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingiere concesiones BDNS por páginas desde el servicio oficial.")
    parser.add_argument("--grant-code", required=True)
    parser.add_argument("--raw-dir", default="data/raw/bdns/concesiones")
    parser.add_argument("--out", default="data/processed/bdns/concessions.jsonl")
    parser.add_argument("--page-size", type=int, default=100)
    parser.add_argument("--max-pages", type=int, default=100)
    args = parser.parse_args()
    print(ingest(args.grant_code, Path(args.raw_dir), Path(args.out), min(100, max(1, args.page_size)), max(1, args.max_pages)))


if __name__ == "__main__":
    main()
