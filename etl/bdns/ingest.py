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
    raw_payload = raw_path.read_bytes()
    try:
        decoded = json.loads(raw_payload.decode("utf-8"))
        if isinstance(decoded, list):
            items = decoded
        elif isinstance(decoded, dict) and "content" in decoded:
            items = decoded["content"]
        else:
            items = [decoded]
    except (UnicodeDecodeError, json.JSONDecodeError):
        # BDNS20 publica contratos XML/WSDL; conservamos el payload intacto hasta
        # seleccionar el servicio concreto y su XSD en la configuración.
        items = []

    records = []
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        convocatoria = item.get("convocatoria", item)
        source_record_id = str(convocatoria.get("codigo-BDNS") or item.get("id") or item.get("bdnsCode") or index)
        records.append({
            "bdns_code": convocatoria.get("codigo-BDNS") or convocatoria.get("bdnsCode") or convocatoria.get("codigoBDNS"),
            "title": convocatoria.get("titulo") or convocatoria.get("title") or convocatoria.get("denominacion"),
            "granting_body": convocatoria.get("desc-organo"),
            "registration_date": convocatoria.get("fecha-registro"),
            "purpose": (convocatoria.get("finalidad") or {}).get("descripcion") if isinstance(convocatoria.get("finalidad"), dict) else None,
            "region": convocatoria.get("region"),
            "source_url": convocatoria.get("permalink-convocatoria") or args.url,
            "source_record_id": source_record_id,
            "retrieved_at": metadata["retrieved_at"],
            "ingestion_run_id": run_id,
            "raw_payload_sha256": hashlib.sha256(raw_payload).hexdigest(),
            "raw_record": item,
        })
    write_jsonl(records, Path(args.out))
    print({"run_id": run_id, "records_downloaded": 1, "records_created": len(records), "raw": metadata, "xml_payload": not records})


if __name__ == "__main__":
    main()
