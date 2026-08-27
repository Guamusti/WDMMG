# ETL

Los ingestors iniciales están en `etl/placsp` y `etl/bdns`. No contienen URLs inventadas: se pasan explícitamente para que el operador seleccione el feed o servicio oficial documentado.

## PLACSP

```bash
python -m etl.placsp.ingest --feed-url "URL_ATOM_OFICIAL"
```

El proceso guarda el payload raw, calcula SHA-256, extrae una fila por `entry` ATOM y conserva `source_record_id`, URL, fecha de recuperación y `ingestion_run_id`. El parser CODICE conserva lotes, normaliza `TenderResult` (ganador, NIF, fecha, ofertas e importes) y registra `ContractModification` como eventos separados; quedan por ampliar otros tipos de actualización y versionado contra los XSD.

## BDNS

```bash
python -m etl.bdns.ingest --url "ENDPOINT_BDNS_OFICIAL"
```

El límite de servicio y el contrato técnico se configuran por entorno. Si la respuesta es XML/WSDL, el raw se conserva sin fingir una normalización JSON; el siguiente paso es seleccionar el servicio de convocatorias o concesiones y mapearlo contra su XSD.

### Concesiones BDNS

```bash
python -m etl.bdns.concessions --grant-code "925963"

python -m etl.bdns.load_concessions --input data/processed/bdns/concessions.jsonl
```

El ingestor recorre páginas de hasta 100 elementos, guarda cada respuesta raw con su hash y produce `data/processed/bdns/concessions.jsonl`. El segundo comando carga esas concesiones en `grant_awards`, relacionándolas con la convocatoria y el beneficiario cuando existen. La carga es repetible por `source_record_id`: volver a procesar la misma concesión no crea otra fila. Convocatoria y concesión permanecen como entidades separadas; una respuesta vacía se conserva como cero registros de esa consulta, no como prueba de que no existan concesiones en toda la BDNS.

El cliente `etl.bdns.client.BDNS20Client` centraliza las lecturas de servicios BDNS/BDNS20: aplica un intervalo mínimo entre peticiones, conserva caché raw por URL con hash y marca `cache_hit` en la metadata. Ante un `429` detiene la ejecución con el `Retry-After` disponible para que el operador pueda reintentarlo sin saturar el servicio. La paginación de concesiones limita cada página a 100 registros y permite configurar `--min-interval` y `--cache-ttl`.

La normalización compartida de entidades elimina diferencias de espacios, mayúsculas, separadores de NIF/CIF y formatos de euros españoles antes de resolver relaciones. El valor original se conserva en el payload raw; normalizar no borra ni convierte silenciosamente un importe ilegible.

## IGAE / ejecución AGE

```bash
python -m etl.budgets.igae_extract --url "URL_XLSX_IGAE"
```

El extractor lee los XLSX oficiales sin convertir importes a `float`, conserva hojas, filas, columnas originales, unidad (`miles de euros`) y provenance. Es una capa de aterrizaje: la clasificación económica/funcional y los estados contables se normalizarán después de validar todas las hojas.

### CONPREL y formato Access

La descarga oficial `Presupuestos2026.accdb` dentro de `eell-2026.zip` se ha validado por URL, tamaño y hash, pero la extracción queda bloqueada en este entorno: Python es de 64 bits y no tiene proveedor ACE/OLE DB; el controlador ODBC Access de 32 bits instalado tampoco reconoce el archivo y devuelve `Cannot open database`. Hasta disponer de un lector compatible, la API conserva el estado `blocked_reader` y no publica importes locales.

Para las hojas de ejecución por secciones/capítulos/inversiones genera además `execution-2026-05.jsonl`, separando crédito definitivo, gasto comprometido, obligaciones reconocidas y pagos. La API local expone ese aterrizaje en `/api/budgets` y calcula el resumen de `/api/overview` solo cuando el fichero existe. El resultado sigue marcado como provisional y conserva flags de calidad.

## PostgreSQL local

Para reprocesar los aterrizajes disponibles sin descargar nada nuevo:

```bash
python -m etl.run_available --dry-run
python -m etl.run_available
```

El runner salta entradas ausentes y devuelve un resultado JSON por dataset. No marca como actualizado un origen que no tenga un aterrizaje local.

```bash
docker compose up -d postgres
psql "postgresql://postgres:postgres@localhost:55432/dinero_publico" -f db/001_initial_schema.sql
psql "postgresql://postgres:postgres@localhost:55432/dinero_publico" -f db/002_seed_sources.sql
python -m etl.budgets.load_postgres
```

El cargador usa una transacción, crea la fuente AGE y la entidad piloto, conserva la unidad de origen y es repetible por `source_id + source_record_id`. El compose publica PostgreSQL en `localhost:55432` para evitar colisiones con instalaciones locales.

## Estados

Cada ejecución debe terminar en `success`, `partial` o `failed`, con contadores y errores. No se sobrescriben payloads raw: su nombre incluye el instante de ejecución.

## Sincronización del entorno

`iniciar.bat` sincroniza primero la rama publicada mediante `git pull --ff-only` y después inicia API y frontend. Si existen cambios locales incompatibles, Git no los sobreescribe: se muestra un aviso y se inicia la copia local.
