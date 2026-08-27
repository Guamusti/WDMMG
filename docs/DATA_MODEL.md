# Modelo de datos MVP

El modelo está diseñado para que una base PostgreSQL pueda crecer sin crear columnas específicas por ministerio o año.

## Entidades principales

- `public_entities`: organismos y administraciones con jerarquía `parent_id`.
- `recipient_entities`: empresas y beneficiarios; matching por NIF/identificador antes que nombre.
- `budget_records`: una fila por dimensión presupuestaria y periodo; admite `budget_origin_year` e `is_extended_budget` para identificar prórrogas solo cuando la fuente lo publica.
- `transfers`: conserva origen, destino, gasto bruto y gasto consolidado, además de marcar si la relación es interna, externa o desconocida. No se calcula consolidación sin una relación oficial.
- `public_entity_aliases`, `recipient_aliases` y `entity_merge_candidates`: soportan nombres alternativos y revisión humana; nunca ejecutan fusiones automáticas por similitud textual.
- `source_files`: registra cada fichero raw por fuente, URL, fecha de recuperación, SHA-256, versión y clave de almacenamiento. Permite reprocesar una descarga sin depender de la fila transformada.
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

`db/004_analytics_views.sql` añade vistas analíticas no materializadas para la cadena presupuestaria y los totales de organismos y receptores. Se actualizan automáticamente con cada carga y mantienen contratos/adjudicaciones separados de ejecución/pagos.
