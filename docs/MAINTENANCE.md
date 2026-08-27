# Mantenimiento del MVP

## Arranque local

En Windows, hacer doble clic en `iniciar.bat`. El script ejecuta `git pull --ff-only`, comprueba las dependencias y levanta:

- frontend Vite en `http://localhost:5173/`;
- API Node en `http://localhost:8787/`.

La API necesita PostgreSQL solo para las consultas importadas; si no está disponible, los endpoints compatibles usan el fallback JSONL documentado.

## Validación antes de publicar

```text
npm run build
python -m pytest -q
```

El primer comando comprueba el bundle de producción. Los tests cubren endpoints, exportaciones CSV, fuentes de datos, relaciones de fichas, headers básicos y un smoke frontend→API.

## Flujo de datos

Los archivos normalizados viven bajo `data/processed/` y los originales bajo `data/raw/`. La mayoría de descargas se mantienen fuera de Git por tamaño; los snapshots que sostienen una funcionalidad reproducible se fuerzan explícitamente al repositorio y llevan fuente, periodo y hash en el registro de ingesta.

No se deben mezclar presupuesto, ejecución, contratos, convocatorias o concesiones en una única suma. Cuando una fuente no ofrece un nivel de detalle, la interfaz debe mostrarlo como pendiente o no disponible.

## Actualización

1. Descargar desde la URL oficial con el ingestor correspondiente.
2. Revisar periodo, unidad, número de filas y hash.
3. Ejecutar parser, tests y `npm run build`.
4. Revisar `/api/coverage` y `/api/quality`.
5. Documentar cambios y publicar un commit separado.
