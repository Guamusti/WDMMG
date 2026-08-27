# Auditoría de cierre del MVP

Fecha de revisión: 27/08/2026

## Evidencia verificada

| Bloque | Evidencia | Estado |
| --- | --- | --- |
| Portada y rueda funcional | `/api/policies`, rueda interactiva, desglose padre/hijo y CSV | Completo |
| Ejecución AGE | `/api/overview`, `/api/history`, `/api/budgets` y datos IGAE versionados | Completo para el piloto AGE |
| Contratos PLACSP | 387 expedientes cargados; adjudicaciones, lotes y eventos persistidos | Completo para la muestra importada |
| Empresas | Fichas, contratos, organismos e indicadores de adjudicación | Completo para PLACSP |
| BDNS | Convocatoria real, consulta paginada de concesiones e ingestor/loader repetible | Parcial: falta carga masiva validada |
| CCAA | 17 comunidades, total, ranking, comparación, mapa IGN y exportación | Parcial: avance autonómico, no cobertura completa |
| INE | Búsqueda municipal y agregación provincial oficial | Parcial: sin gasto local compatible |
| Calidad y frescura | `/api/quality`, `/api/coverage`, fechas de recuperación/importación y `/api/metrics` cacheado | Completo para datasets conectados |
| Operación local | `iniciar.bat`, API, Vite, build y GitHub `master` | Completo |

## Puntos que no se marcan como completados

- CONPREL Access no se extrae porque el entorno no dispone de un lector compatible.
- No se calcula gasto por habitante con población 2024 y ejecución autonómica de mayo de 2026: los periodos no son compatibles.
- No se presenta una comunidad autónoma agregada desde el campo INE cuando la respuesta no devuelve todos sus municipios.
- La cobertura completa de 17 CCAA y municipios requiere nuevas descargas oficiales y validación de sus esquemas.
- El despliegue público requiere configurar un destino de hosting; el proyecto no contiene todavía `.openai/hosting.json`.

## Comandos de verificación

```text
python -m pytest -q
npm run build
git diff --check
```

Las cifras de contratos, adjudicaciones, presupuestos y subvenciones permanecen separadas por entidad, unidad, periodo y fuente.
