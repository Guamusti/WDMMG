from __future__ import annotations

import argparse
import json
import os
from datetime import date, datetime, timezone
from pathlib import Path

import psycopg


SOURCE_URL = "https://www.infosubvenciones.es/bdnstrans/GE/es/api/v2.1/convocatoria/925963"


def iso_date(value: str | None) -> date | None:
    if not value:
        return None
    return datetime.strptime(value, "%d/%m/%Y").date()


def load(path: Path, database_url: str) -> int:
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    with psycopg.connect(database_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO data_sources (name,institution,source_type,source_url,format,update_frequency,coverage_description) VALUES ('BDNS convocatoria','IGAE','grants',%s,'JSON','continua','Convocatorias SNPSAP') ON CONFLICT (source_url) DO NOTHING", (SOURCE_URL,))
            cursor.execute("SELECT id FROM data_sources WHERE source_url=%s", (SOURCE_URL,))
            source_id = cursor.fetchone()[0]
            run = rows[0].get("ingestion_run_id", datetime.now(timezone.utc).isoformat()) if rows else "empty"
            cursor.execute("INSERT INTO ingestion_runs (source_id,status,source_version,records_downloaded,records_created) VALUES (%s,'success',%s,1,%s) RETURNING id", (source_id, run, len(rows)))
            ingestion_id = cursor.fetchone()[0]
            for row in rows:
                cursor.execute("""
                    INSERT INTO grant_calls (bdns_code,title,registration_date,purpose,source_id,source_url,source_record_id,ingestion_run_id)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                    ON CONFLICT (bdns_code) DO UPDATE SET title=EXCLUDED.title, registration_date=EXCLUDED.registration_date, purpose=EXCLUDED.purpose, source_url=EXCLUDED.source_url
                """, (row.get("bdns_code"), row.get("title"), iso_date(row.get("registration_date")), row.get("purpose"), source_id, row.get("source_url"), row.get("source_record_id"), ingestion_id))
    return len(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Carga convocatorias BDNS normalizadas en PostgreSQL.")
    parser.add_argument("--input", default="data/processed/bdns/records.jsonl")
    parser.add_argument("--database-url", default=os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:55432/dinero_publico"))
    args = parser.parse_args()
    print({"records_loaded": load(Path(args.input), args.database_url)})


if __name__ == "__main__":
    main()
