from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from etl.shared.io import download, write_jsonl


def main() -> None:
    parser = argparse.ArgumentParser(description="Conserva y normaliza una respuesta BDNS proporcionada por el endpoint oficial.")
    parser.add_argument("--url", required=True, help="Endpoint/documento oficial BDNS habilitado para el entorno")
    parser.add_argument("--raw-dir", default="data/raw/bdns")
    parser.add_argument("--out", default="data/processed/bdns/records.jsonl")
    args = parser.parse_args()

    run_id = datetime.now(timezone.utc).strftime("bdns-%Y%m%dT%H%M%SZ")
    raw_path = Path(args.raw_dir) / f"{run_id}.payload"
    metadata = download(args.url, raw_path)
    payload = raw_path.read_bytes()
    try:
        decoded = json.loads(payload.decode("utf-8"))
        items = decoded.get("content", decoded if isinstance(decoded, list) else [decoded])
    except (UnicodeDecodeError, json.JSONDecodeError):
        # BDNS20 publica contratos XML/WSDL; conservamos el payload intacto hasta
        # seleccionar el servicio concreto y su XSD en la configuración.
        items = []

    records = []
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        source_record_id = str(item.get("id") or item.get("bdnsCode") or index)
        records.append({
            "bdns_code": item.get("bdnsCode") or item.get("codigoBDNS"),
            "title": item.get("title") or item.get("denominacion"),
            "source_record_id": source_record_id,
            "source_url": args.url,
            "retrieved_at": metadata["retrieved_at"],
            "ingestion_run_id": run_id,
            "raw_payload_sha256": hashlib.sha256(payload).hexdigest(),
            "raw_record": item,
        })
    write_jsonl(records, Path(args.out))
    print({"run_id": run_id, "records_downloaded": 1, "records_created": len(records), "raw": metadata, "xml_payload": not records})


if __name__ == "__main__":
    main()
