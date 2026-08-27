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

## IGAE / ejecución AGE

```bash
python -m etl.budgets.igae_extract --url "URL_XLSX_IGAE"
```

El extractor lee los XLSX oficiales sin convertir importes a `float`, conserva hojas, filas, columnas originales, unidad (`miles de euros`) y provenance. Es una capa de aterrizaje: la clasificación económica/funcional y los estados contables se normalizarán después de validar todas las hojas.

## Estados

Cada ejecución debe terminar en `success`, `partial` o `failed`, con contadores y errores. No se sobrescriben payloads raw: su nombre incluye el instante de ejecución.

## Sincronización del entorno

`iniciar.bat` sincroniza primero la rama publicada mediante `git pull --ff-only` y después inicia API y frontend. Si existen cambios locales incompatibles, Git no los sobreescribe: se muestra un aviso y se inicia la copia local.
