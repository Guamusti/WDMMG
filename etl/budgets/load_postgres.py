from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import psycopg


SOURCE_URL = "https://www.igae.pap.hacienda.gob.es/sitios/igae/es-ES/Contabilidad/ContabilidadPublica/CPE/EjecucionPresupuestaria/Documents/EXTRACTO%20MAYO%202026%20%28EXCEL%29.xlsx"


def load(path: Path, database_url: str) -> int:
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    with psycopg.connect(database_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO data_sources (name, institution, source_type, source_url, format, update_frequency, coverage_description)
                VALUES ('Ejecución AGE', 'IGAE', 'budget_execution', %s, 'XLSX', 'mensual', 'Ejecución del presupuesto AGE')
                ON CONFLICT DO NOTHING
            """, (SOURCE_URL,))
            cursor.execute("SELECT id FROM data_sources WHERE source_url = %s", (SOURCE_URL,))
            source_id = cursor.fetchone()[0]
            cursor.execute("""
                INSERT INTO public_entities (official_code, name, normalized_name, entity_type, administration_level, source_id, source_record_id)
                VALUES ('AGE', 'Administración General del Estado', 'administracion general del estado', 'AGE', 'central', %s, 'AGE')
                ON CONFLICT DO NOTHING
            """, (source_id,))
            cursor.execute("SELECT id FROM public_entities WHERE official_code = 'AGE'")
            entity_id = cursor.fetchone()[0]
            run_id_text = rows[0]["ingestion_run_id"] if rows else datetime.now(timezone.utc).isoformat()
            cursor.execute("""
                INSERT INTO ingestion_runs (source_id, status, source_version, records_downloaded, records_created)
                VALUES (%s, 'success', %s, 1, %s) RETURNING id
            """, (source_id, run_id_text, len(rows)))
            ingestion_id = cursor.fetchone()[0]
            for row in rows:
                cursor.execute("DELETE FROM budget_records WHERE source_id = %s AND source_record_id = %s", (source_id, row["source_record_id"]))
                cursor.execute("""
                    INSERT INTO budget_records (fiscal_year, period, entity_id, budget_side, economic_code, economic_level, initial_amount, modifications_amount, final_amount, budget_origin_year, is_extended_budget, data_status, source_id, source_record_id, ingestion_run_id)
                    VALUES (%s,%s,%s,'expense',%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id
                """, (row["fiscal_year"], row["period"], entity_id, row["classification_label"], row["classification_level"], row.get("initial_credit"), row.get("budget_modifications"), row["final_credit"], row.get("budget_origin_year"), row.get("is_extended_budget"), row["data_status"], source_id, row["source_record_id"], ingestion_id))
                budget_id = cursor.fetchone()[0]
                cursor.execute("""
                    INSERT INTO budget_execution (budget_record_id, committed_amount, recognized_amount, paid_amount, raw_payload)
                    VALUES (%s,%s,%s,%s,%s)
                """, (budget_id, row["committed_amount"], row["recognized_amount"], row["paid_amount"], json.dumps(row, ensure_ascii=False)))
    return len(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Carga el JSONL normalizado de IGAE en PostgreSQL.")
    parser.add_argument("--input", default="data/processed/igae/execution-2026-05.jsonl")
    parser.add_argument("--database-url", default=os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:55432/dinero_publico"))
    args = parser.parse_args()
    print({"records_loaded": load(Path(args.input), args.database_url)})


if __name__ == "__main__":
    main()
