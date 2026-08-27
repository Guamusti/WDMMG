from __future__ import annotations

import argparse
import json
import os
from datetime import date, datetime, timezone
from pathlib import Path

import psycopg


SOURCE_URL = "https://www.infosubvenciones.es/bdnstrans/api/concesiones/busqueda"


def parse_date(value: str | None) -> date | None:
    if not value:
        return None
    for pattern in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(value, pattern).date()
        except ValueError:
            pass
    return None


def load(path: Path, database_url: str) -> int:
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not rows:
        return 0
    code = rows[0].get("bdns_code")
    with psycopg.connect(database_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO data_sources (name,institution,source_type,source_url,format,update_frequency,coverage_description) VALUES ('BDNS concesiones','IGAE','grants',%s,'JSON','continua','Concesiones publicadas por convocatoria') ON CONFLICT (source_url) DO NOTHING", (SOURCE_URL,))
            cursor.execute("SELECT id FROM data_sources WHERE source_url=%s", (SOURCE_URL,))
            source_id = cursor.fetchone()[0]
            run_id = rows[0].get("ingestion_run_id", datetime.now(timezone.utc).isoformat())
            cursor.execute("INSERT INTO ingestion_runs (source_id,status,source_version,records_downloaded,records_created) VALUES (%s,'success',%s,1,%s) RETURNING id", (source_id, run_id, len(rows)))
            ingestion_id = cursor.fetchone()[0]
            source_records = [row.get("source_record_id") for row in rows if row.get("source_record_id")]
            cursor.execute("DELETE FROM grant_awards WHERE source_id=%s AND source_record_id = ANY(%s)", (source_id, source_records))
            cursor.execute("SELECT id FROM grant_calls WHERE bdns_code=%s", (code,))
            call = cursor.fetchone()
            call_id = call[0] if call else None
            for row in rows:
                beneficiary_id = None
                name = (row.get("beneficiary") or "").strip()
                if name:
                    normalized = " ".join(name.lower().split())
                    cursor.execute("SELECT id FROM recipient_entities WHERE normalized_name=%s LIMIT 1", (normalized,))
                    found = cursor.fetchone()
                    if found:
                        beneficiary_id = found[0]
                    else:
                        cursor.execute("INSERT INTO recipient_entities (name,normalized_name,entity_type,source_id,source_record_id) VALUES (%s,%s,'beneficiary',%s,%s) RETURNING id", (name, normalized, source_id, row.get("source_record_id")))
                        beneficiary_id = cursor.fetchone()[0]
                cursor.execute("INSERT INTO grant_awards (grant_call_id,beneficiary_id,amount,award_date,instrument,purpose,source_id,source_record_id,ingestion_run_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)", (call_id, beneficiary_id, row.get("amount"), parse_date(row.get("award_date")), row.get("instrument"), row.get("purpose"), source_id, row.get("source_record_id"), ingestion_id))
    return len(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Carga concesiones BDNS normalizadas en PostgreSQL.")
    parser.add_argument("--input", default="data/processed/bdns/concessions.jsonl")
    parser.add_argument("--database-url", default=os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:55432/dinero_publico"))
    args = parser.parse_args()
    print({"records_loaded": load(Path(args.input), args.database_url)})


if __name__ == "__main__":
    main()
