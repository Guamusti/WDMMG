# Modelo de datos MVP

El modelo está diseñado para que una base PostgreSQL pueda crecer sin crear columnas específicas por ministerio o año.

## Entidades principales

- `public_entities`: organismos y administraciones con jerarquía `parent_id`.
- `recipient_entities`: empresas y beneficiarios; matching por NIF/identificador antes que nombre.
- `budget_records`: una fila por dimensión presupuestaria y periodo.
- `budget_execution`: estados de ejecución separados de la dotación presupuestaria.
- `contracts`, `contract_lots`, `contract_awards`, `contract_events`.
- `grant_calls`, `grant_awards`.
- `geographies`, `data_sources`, `source_files`, `ingestion_runs`.

## Reglas contables

`initial_amount + modifications_amount ≈ final_amount` solo cuando la fuente lo permita. `execution_rate = recognized_amount / final_amount`; `payment_rate = paid_amount / recognized_amount`. Contratos y subvenciones no se suman al gasto ejecutado. Las transferencias tienen tipo y flags de consolidación para evitar doble conteo.

## Provenance

Toda entidad importada debe poder volver a su registro de origen mediante `source_id`, `source_record_id`, `source_url`, `retrieved_at`, `dataset_version` e `ingestion_run_id`. Las anomalías viven en `data_quality_flags`, no se eliminan silenciosamente.

## Próximo paso técnico

Las consultas públicas principales tienen índices incrementales en `db/003_performance_indexes.sql`: organismos por nombre/jerarquía, relaciones organismo-contrato-empresa, convocatorias/concesiones y búsquedas presupuestarias. La migración es idempotente; no sustituye futuras vistas materializadas cuando aumente la cobertura.
