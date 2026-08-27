from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import psycopg


SOURCE_URL = "https://contrataciondelsectorpublico.gob.es/sindicacion/sindicacion_643/licitacionesPerfilesContratanteCompleto3.atom"


def load(path: Path, database_url: str) -> int:
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    with psycopg.connect(database_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO data_sources (name, institution, source_type, source_url, format, update_frequency, coverage_description)
                VALUES ('Licitaciones PLACSP', 'Dirección General del Patrimonio del Estado', 'procurement', %s, 'ATOM/XML', 'continua', 'Perfiles de contratante alojados en PLACSP')
                ON CONFLICT (source_url) DO NOTHING
            """, (SOURCE_URL,))
            cursor.execute("SELECT id FROM data_sources WHERE source_url = %s", (SOURCE_URL,))
            source_id = cursor.fetchone()[0]
            run_id = rows[0].get("ingestion_run_id", datetime.now(timezone.utc).isoformat()) if rows else "empty"
            cursor.execute("INSERT INTO ingestion_runs (source_id, status, source_version, records_downloaded, records_created) VALUES (%s,'success',%s,1,%s) RETURNING id", (source_id, run_id, len(rows)))
            ingestion_id = cursor.fetchone()[0]
            for row in rows:
                authority_id = None
                authority = row.get("contracting_authority")
                if authority:
                    normalized = " ".join(authority.lower().split())
                    cursor.execute("SELECT id FROM public_entities WHERE normalized_name = %s LIMIT 1", (normalized,))
                    found = cursor.fetchone()
                    if found:
                        authority_id = found[0]
                    else:
                        cursor.execute("INSERT INTO public_entities (name, normalized_name, entity_type, administration_level, source_id, source_record_id) VALUES (%s,%s,'public_entity','unknown',%s,%s) RETURNING id", (authority, normalized, source_id, authority))
                        authority_id = cursor.fetchone()[0]
                cursor.execute("""
                    INSERT INTO contracts (procurement_id, title, contracting_authority_id, contract_type, procedure_type, status, estimated_value, base_tender_budget, publication_date, is_minor, source_id, source_url, source_record_id, ingestion_run_id)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,FALSE,%s,%s,%s,%s)
                    ON CONFLICT (source_id, source_record_id) DO UPDATE SET title=EXCLUDED.title, status=EXCLUDED.status, estimated_value=EXCLUDED.estimated_value, base_tender_budget=EXCLUDED.base_tender_budget, source_url=EXCLUDED.source_url
                """, (row.get("procurement_id"), row.get("title"), authority_id, row.get("contract_type"), row.get("procedure_type"), row.get("status"), row.get("estimated_value"), row.get("base_tender_budget"), row.get("publication_date") or None, source_id, row.get("source_url"), row.get("source_record_id"), ingestion_id))
                cursor.execute("SELECT id FROM contracts WHERE source_id = %s AND source_record_id = %s", (source_id, row.get("source_record_id")))
                contract_id = cursor.fetchone()[0]
                cursor.execute("DELETE FROM contract_lots WHERE contract_id = %s", (contract_id,))
                for lot in row.get("lots", []):
                    cursor.execute("INSERT INTO contract_lots (contract_id, lot_number, title, budget, estimated_value) VALUES (%s,%s,%s,%s,%s)", (contract_id, lot.get("lot_number"), lot.get("title"), lot.get("budget"), lot.get("estimated_value")))
    return len(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Carga licitaciones PLACSP normalizadas en PostgreSQL.")
    parser.add_argument("--input", default="data/processed/placsp/contracts.jsonl")
    parser.add_argument("--database-url", default=os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:55432/dinero_publico"))
    args = parser.parse_args()
    print({"records_loaded": load(Path(args.input), args.database_url)})


if __name__ == "__main__":
    main()
