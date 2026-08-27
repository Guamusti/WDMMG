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
| Integridad del modelo | Migraciones de prórrogas, transferencias, aliases y candidatos de merge aplicadas en PostgreSQL local | Completo para el esquema |
| Exportaciones | CSV de presupuesto, contratos, empresas, organismos y convocatorias con fallback JSONL | Completo para las muestras cargadas |
| Indicadores de contratación | Licitador único, modificaciones y descuento comparable frente a presupuesto base | Completo para campos publicados |

## Puntos que no se marcan como completados

- CONPREL Access no se extrae porque el entorno no dispone de un lector compatible.
- No se calcula gasto por habitante con población 2024 y ejecución autonómica de mayo de 2026: los periodos no son compatibles.
- No se presenta una comunidad autónoma agregada desde el campo INE cuando la respuesta no devuelve todos sus municipios.
- La cobertura completa de 17 CCAA y municipios requiere nuevas descargas oficiales y validación de sus esquemas.
- El despliegue público requiere configurar un destino de hosting; el proyecto no contiene todavía `.openai/hosting.json`.
- El acceso a CONPREL sigue bloqueado en este entorno: no hay proveedor ACE ni controlador Access compatible para leer el `.accdb` oficial.

## Comandos de verificación

```text
python -m pytest -q  # 64 passed, 2 skipped en la auditoría del 27/08/2026
npm run build
git diff --check
```

Las cifras de contratos, adjudicaciones, presupuestos y subvenciones permanecen separadas por entidad, unidad, periodo y fuente.
