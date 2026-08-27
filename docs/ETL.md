# ETL

Los ingestors iniciales están en `etl/placsp` y `etl/bdns`. No contienen URLs inventadas: se pasan explícitamente para que el operador seleccione el feed o servicio oficial documentado.

## PLACSP

```bash
python -m etl.placsp.ingest --feed-url "URL_ATOM_OFICIAL"
```

El proceso guarda el payload raw, calcula SHA-256, extrae una fila por `entry` ATOM y conserva `source_record_id`, URL, fecha de recuperación y `ingestion_run_id`. La extensión CODICE tiene estructuras anidadas y requerirá ampliar los mapeos contra los XSD antes de importar adjudicaciones a producción.

## BDNS

```bash
python -m etl.bdns.ingest --url "ENDPOINT_BDNS_OFICIAL"
```

El límite de servicio y el contrato técnico se configuran por entorno. Si la respuesta es XML/WSDL, el raw se conserva sin fingir una normalización JSON; el siguiente paso es seleccionar el servicio de convocatorias o concesiones y mapearlo contra su XSD.

## Estados

Cada ejecución debe terminar en `success`, `partial` o `failed`, con contadores y errores. No se sobrescriben payloads raw: su nombre incluye el instante de ejecución.
