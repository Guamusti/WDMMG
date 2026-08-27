# Plan maestro de implementación

Este plan convierte el documento de requisitos `Prompt para Codex — Dinero Público España.md` en trabajo verificable. Se actualizará después de cada avance y es la referencia operativa del proyecto.

Estados: `[x]` completado, `[~]` parcial/en curso, `[ ]` pendiente.

## Fase 0 — Alcance, inspección y definición del MVP

Referencia MD: secciones 0, 1, 2, 3, 49, 61, 62 y 63.

- [x] Inspeccionar el repositorio y confirmar stack inicial.
- [x] Elegir AGE como administración piloto.
- [x] Separar presupuesto, ejecución, contratos y subvenciones.
- [x] Definir que no se presentan cifras hasta tener ingesta validada.
- [x] Definir criterio de éxito vertical: administración → empresa → contrato → fuente.
- [ ] Revisar con datos reales que el alcance piloto cubre el criterio de éxito.

## Fase 1 — Fuentes oficiales y cobertura

Referencia MD: secciones 11, 12, 13, 14, 35, 42, 55 y 62.B–D.

- [x] Documentar Hacienda/IGAE, PLACSP, BDNS, INE e inventarios públicos.
- [x] Registrar URL, formato, cobertura, frecuencia, campos y limitaciones conocidas.
- [ ] Descargar una muestra real de cada fuente prioritaria.
- [ ] Guardar muestras/fixtures con fecha, hash y licencia.
- [~] Verificar campos contra documentación vigente; falta validar con descargas de datos.
- [~] Completar matriz de cobertura efectiva por año y administración; ya se ha validado una descarga AGE de mayo de 2026.

Entregable: `docs/DATA_SOURCES.md`.

## Fase 2 — Modelo de datos y trazabilidad

Referencia MD: secciones 4, 5, 6, 8, 9, 10, 12, 13, 15, 16, 40, 41 y 43.

- [x] Diseñar entidades públicas, receptores, geografía, fuentes e ingestas.
- [x] Diseñar `budget_records` multidimensional, sin columnas por ministerio/año.
- [x] Separar `budget_execution` de la dotación presupuestaria.
- [x] Separar contratos, lotes, adjudicaciones y eventos/versiones.
- [x] Separar convocatorias y concesiones BDNS.
- [x] Añadir provenance y `raw_payload`/hash cuando proceda.
- [x] Crear migración inicial PostgreSQL.
- [x] Crear seed de fuentes oficiales.
- [x] Añadir constraints/validaciones específicas por fuente (URLs, códigos oficiales y provenance).
- [~] Añadir índices y vistas materializadas para agregaciones; índices base ya creados.

Entregables: `db/001_initial_schema.sql`, `db/002_seed_sources.sql`, `docs/DATA_MODEL.md`.

## Fase 3 — ETL reproducible y calidad de datos

Referencia MD: secciones 6, 7, 10, 13, 34, 40, 41, 43, 44 y 55.

- [x] Crear estructura `etl/shared`, `etl/placsp` y `etl/bdns`.
- [x] Implementar descarga raw con reintentos, timestamp y SHA-256.
- [x] Implementar registro `ingestion_run_id` en salidas normalizadas.
- [x] Implementar parser inicial de entradas ATOM/XML PLACSP.
- [x] Conservar XML BDNS sin fingir un mapeo cuando falta el servicio/XSD concreto.
- [ ] Añadir parser completo CODICE para licitaciones, lotes, adjudicaciones y eventos.
- [ ] Añadir cliente BDNS20 por servicio, paginación, throttling y cache.
- [ ] Implementar normalización NIF/CIF, nombres, fechas, euros y códigos.
- [ ] Implementar flags de calidad: duplicados, fechas, IDs, importes y ejercicios.
- [~] Añadir tests unitarios del parser y IO; faltan fixtures descargados de producción.
- [x] Inspeccionar una descarga XLSX real de ejecución AGE (9 hojas, mayo de 2026).

Entregables: `etl/`, `requirements.txt`, `docs/ETL.md`.

## Fase 4 — Importación real de contratación y subvenciones

Referencia MD: secciones 6, 7, 10, 13, 18, 26, 27, 28, 29, 33, 46, 47, 57, 58 y 62.G.

- [x] Localizar el portal oficial y la documentación del feed; falta ampliar a otras sindicaciones.
- [x] Configurar sindicacion 643 oficial y descargar feed ATOM real.
- [x] Importar 387 licitaciones PLACSP reales en JSONL y PostgreSQL.
- [x] Importar una muestra real y auditar el conteo raw/parseado/normalizado: 387 entradas, 382 contratos canónicos.
- [~] Resolver contratos ordinarios, menores y actualizaciones sin duplicar; sindicacion 643 importada y 5 IDs repetidos/actualizados.
- [~] Importar lotes y adjudicaciones con adjudicatarios canónicos; lotes PLACSP cargados y visibles en detalle, adjudicaciones pendientes.
- [ ] Configurar el servicio BDNS oficial de convocatorias.
- [x] Configurar endpoint oficial BDNS de convocatoria y descargar una respuesta JSON real (`925963`).
- [~] Normalizar y cargar convocatorias BDNS; 1 convocatoria real cargada y repetible, endpoint y vista inicial activos, filtros y concesiones pendientes.
- [ ] Configurar el servicio BDNS oficial de concesiones.
- [~] Importar muestras reales con URLs de origen; PLACSP y 1 convocatoria BDNS importadas.
- [ ] Verificar que ningún contrato/subvención se presenta como pago presupuestario.
- [ ] Publicar estado y fecha de actualización de cada dataset.

## Fase 5 — Presupuesto y ejecución AGE piloto

Referencia MD: secciones 4, 5, 11, 16, 17, 20, 23, 30, 31, 32, 33, 36, 42, 56, 58, 59 y 62.H–I.

- [x] Seleccionar XLS estructurado de presupuesto y ejecución AGE.
- [x] Descargar muestra mensual y documentar estructura real.
- [~] Extraer filas del XLSX a JSONL auditable; falta normalización contable completa.
- [~] Normalizar hojas GTOS 001/002/004 a campos de ejecución separados; cargadas en PostgreSQL, falta validar totales completos.
- [x] Detectar periodo desde cabeceras y marcar anomalías contables sin eliminar registros.
- [x] Añadir cargador transaccional PostgreSQL para el JSONL IGAE y entorno Docker local.
- [x] Verificar carga repetida sin duplicados: 91 `budget_records` y 91 `budget_execution`.
- [ ] Parsear clasificación orgánica, económica y funcional/programas.
- [~] Importar crédito inicial, modificaciones, definitivo, comprometido, obligaciones y pagos; ejecución AGE cargada, crédito inicial/modificaciones detallados pendientes.
- [ ] Conservar periodo, estado provisional/avance/definitivo y versión.
- [ ] Modelar presupuestos prorrogados y `budget_origin_year`.
- [ ] Modelar cambios de nombre/jerarquía administrativa con IDs estables.
- [ ] Validar relaciones contables sin eliminar anomalías.
- [ ] Calcular ejecución y pago únicamente con denominadores válidos.
- [x] Publicar cobertura efectiva AGE.

## Fase 6 — API, búsqueda y agregaciones

Referencia MD: secciones 17, 18, 19, 22, 23, 24, 26, 27, 28, 29, 30, 32, 33, 34, 39, 46 y 47.

- [x] Crear scaffold local de `/api/health`, `/api/overview`, `/api/contracts` y `/api/search`.
- [x] Conectar `/api/overview` y `/api/budgets` al aterrizaje IGAE real disponible.
- [x] Evitar doble conteo en el resumen IGAE excluyendo filas TOTAL de la suma de capítulos.
- [x] Conectar API a PostgreSQL, manteniendo JSONL como fallback explícito.
- [~] Implementar endpoints de presupuestos, entidades, programas, empresas, contratos, subvenciones y geografía; presupuestos, contratos y convocatorias BDNS activos.
- [x] Implementar filtros server-side y paginación.
- [x] Implementar filtros server-side y paginación básica para contratos.
- [x] Implementar buscador global multi-entidad para contratos, convocatorias BDNS y partidas IGAE.
- [ ] Implementar agregaciones separadas por magnitud.
- [x] Implementar exportación CSV de la consulta exacta para contratos, convocatorias y presupuesto.
- [x] Persistir búsqueda y vista activa en query params para compartir exploraciones.
- [ ] Añadir cache/preagregaciones sin enviar datasets completos al navegador.

## Fase 7 — UI MVP conectada a datos reales

Referencia MD: secciones 19–30, 36–38, 45, 47, 48, 59, 60 y 63.

- [x] Crear portada editorial, selector de año, búsqueda y navegación base.
- [x] Crear treemap interactivo conectado a capítulos IGAE reales.
- [x] Crear tabla de contratos y vista metodológica.
- [x] Conectar overview a agregaciones IGAE reales, mostrando periodo, unidad y estado.
- [~] Construir vista inicial AGE: overview, ratio de lectura rápida y detalle de capítulo conectados; faltan niveles contables completos.
- [x] Añadir en portada el desglose funcional comprensible de la Cuenta General del Estado 2024.
- [x] Sustituir las tarjetas iniciales por una rueda interactiva con porcentajes grandes y leyenda accesible.
- [ ] Construir vista de empresa con contratos y subvenciones.
- [~] Construir vista de contrato con lotes, eventos y fuente oficial; detalle base y enlace a ficha PLACSP activos, lotes/eventos pendientes.
- [~] Construir vista de subvención con convocatoria/concesiones; vista de convocatorias activa, concesiones pendientes.
- [ ] Añadir presupuesto → ejecución con definiciones y estados.
- [~] Priorizar políticas de gasto reconocibles (pensiones, infraestructuras, sanidad, educación) sobre el detalle de contratación.
- [ ] Añadir tooltips de conceptos técnicos.
- [x] Priorizar ratios comprensibles en portada sin atribuir causalidad no demostrada.
- [x] Traducir titulares contables a lenguaje ciudadano y reservar la precisión técnica para el contexto.
- [~] Añadir patrón de drill-down visual; el nivel inferior queda bloqueado hasta disponer de una relación padre-hijo oficial.
- [x] Añadir estados loading/error/empty para la tabla de contratos.
- [ ] Revisar responsive, accesibilidad y rendimiento.

## Fase 8 — Ampliación territorial y entidades

Referencia MD: secciones 9, 11, 12, 24, 25, 32, 35, 50 y 51.

- [ ] Incorporar presupuestos y ejecución de CCAA.
- [ ] Incorporar presupuestos, ejecución y liquidación local.
- [ ] Incorporar inventario de entidades públicas y jerarquías.
- [ ] Incorporar geografía, códigos territoriales y población INE.
- [ ] Añadir CCAA, provincias y municipios a filtros y páginas.
- [ ] Añadir mapa España → CCAA → provincia → municipio.
- [ ] Calcular gasto por habitante solo con población y periodo compatibles.
- [ ] Medir cobertura real: completa, parcial, no disponible, en procesamiento.

## Fase 9 — Históricos, comparador y exploración avanzada

Referencia MD: secciones 21, 22, 24, 25, 30, 31, 32, 33, 35, 46, 47 y 57.

- [ ] Añadir series históricas y evolución durante el ejercicio.
- [ ] Añadir comparador de administraciones/territorios.
- [ ] Añadir nominal €/habitante y documentar cualquier € constante.
- [ ] Añadir explorador jerárquico de partidas y descarga CSV.
- [ ] Añadir indicadores descriptivos: concentración, ofertas, menores y ejecución.
- [~] Permitir abrir el dataset subyacente desde cada indicador; fichas oficiales y exportación activas.
- [ ] Añadir URLs compartibles y SEO para exploraciones importantes.

## Fase 10 — Consolidación, relaciones y escala

Referencia MD: secciones 8, 10, 27, 34, 39, 48, 50, 51, 52, 53, 58 y 59.

- [ ] Modelar transferencias internas/externas y consolidación oficial.
- [ ] Evitar doble conteo entre Estado, CCAA y entidades receptoras.
- [ ] Implementar aliases, candidatos de merge y revisión humana.
- [ ] Implementar red administración ↔ empresa con agregación/progressive loading.
- [ ] Implementar “Sigue el dinero” solo con relaciones verificables.
- [ ] Añadir índices, particionado, vistas materializadas y jobs incrementales.
- [ ] Preparar object storage para raw y reprocesado.
- [ ] Expandir de AGE a 17 CCAA y después a 8.000+ municipios.

## Fase 11 — QA, transparencia y operación

Referencia MD: secciones 34, 35, 36, 37, 38, 39, 41, 42, 44, 45, 54, 55, 56, 60, 61 y 63.

- [ ] Tests de parsers con fixtures oficiales.
- [ ] Tests de normalización y validaciones contables.
- [ ] Tests de API y permisos de descarga.
- [ ] Tests end-to-end frontend → API → datos → fuente.
- [x] Página pública de cobertura y actualización.
- [ ] Página de metodología completa y glosario.
- [ ] Monitorización de fallos, cambios de esquema y retrasos de fuentes.
- [ ] Jobs según frecuencia real comprobada, no asumida.
- [ ] Revisión de accesibilidad, seguridad, privacidad y licencias.
- [ ] Deploy reproducible y guía de mantenimiento.
- [ ] Evaluación final contra el criterio de éxito del MVP.

## Estado global actual

**Fase 4/7 — Importación real y UI MVP conectada, en curso.**

La base documental, el modelo PostgreSQL, el scaffold ETL, la API local y la interfaz inicial existen. La UI ya consume IGAE, PLACSP y la muestra BDNS cargada; el siguiente trabajo es ampliar niveles contables, relaciones y cobertura sin mezclar magnitudes.

## Registro de avances

| Fecha | Avance | Commit |
|---|---|---|
| 27/08/2026 | Bootstrap UI, documentación inicial, modelo SQL y ETL base | `0e8f5ae` |
| 27/08/2026 | Limpieza de caches Python | `de34dfe` |
| 27/08/2026 | API local y arranque frontend/API | `181ffea` |
| 27/08/2026 | `iniciar.bat` sincroniza GitHub antes de arrancar | `6de774e` |
| 27/08/2026 | Endpoints oficiales concretos, campos PLACSP y tests estructurales | `29c2741` |
| 27/08/2026 | Corrección de prioridad del identificador de expediente PLACSP; tests verdes | `5de8f23` |
| 27/08/2026 | Extractor real IGAE: 9 hojas, 392 filas y 91 registros de ejecución | `49b52a6` |
| 27/08/2026 | API y frontend conectados al resumen IGAE real; agregado sin filas TOTAL | `e6c2f61` |
| 27/08/2026 | Cargador PostgreSQL verificado en Docker: 91 filas y segunda carga sin duplicados | `fcf047d` |
| 27/08/2026 | Dependencia psycopg declarada para el cargador | `73c97ea` |
| 27/08/2026 | API consulta PostgreSQL real para overview y presupuestos | `8419c64` |
| 27/08/2026 | Contratos frontend conectados a API; eliminadas filas estáticas ficticias | `19e9ece` |
| 27/08/2026 | Validación de periodo IGAE y flags contables; 91 filas procesadas, 10 marcadas | `61fea32` |
| 27/08/2026 | Cargador PostgreSQL IGAE y entorno Docker local; carga repetida sin duplicados | `en curso` |
| 27/08/2026 | Feed PLACSP real cargado en PostgreSQL: 387 entradas, 382 contratos canónicos | `76d5ba7` |
| 27/08/2026 | BDNS real: convocatoria 925963 normalizada y carga repetida sin duplicados | `0def8b7` |
| 27/08/2026 | Portada con ratios IGAE verificables y treemap por capítulos reales; drill-down del nivel inferior disponible | `en curso` |
| 27/08/2026 | Endpoint y vista inicial BDNS; convocatoria real 925963 visible desde la navegación | `en curso` |
| 27/08/2026 | Buscador global PostgreSQL con resultados etiquetados por PLACSP, BDNS e IGAE | `en curso` |
| 27/08/2026 | Endpoint y página de cobertura con conteos efectivos: 91 IGAE, 382 PLACSP y 1 BDNS | `en curso` |
| 27/08/2026 | Exportación CSV con filtros para contratos PLACSP, convocatorias BDNS y presupuesto IGAE | `en curso` |
| 27/08/2026 | Revisión de lenguaje: “de cada 1 € previsto, 0,29 € ya se han pagado” y capítulos con nombres comprensibles | `en curso` |
| 27/08/2026 | Segunda pasada de UX: portada, fuentes, reparto y desglose reescritos para lenguaje ciudadano | `en curso` |
| 27/08/2026 | Portada prioriza políticas de gasto IGAE 2024: pensiones, infraestructuras, sanidad, educación y drill-down de pensiones | `en curso` |
| 27/08/2026 | Drill-down ciudadano ampliado: Pensiones, Deuda pública y Transferencias con subpartidas publicadas por IGAE | `en curso` |
| 27/08/2026 | Rueda interactiva como visual principal del reparto funcional | `en curso` |
| 27/08/2026 | Porcentajes de partidas ampliados como lectura visual principal, también en el drill-down | `en curso` |
| 27/08/2026 | Corrección de legibilidad del donut: nombres largos fuera del gráfico y porcentaje limpio en el centro | `en curso` |
| 27/08/2026 | La portada arranca con Pensiones seleccionada (32,1%) y el detalle es accesible con `aria-live` | `en curso` |
| 27/08/2026 | URL compartible para búsqueda y vista activa | `en curso` |
| 27/08/2026 | Detalle base de contrato y enlace directo a ficha oficial PLACSP | `en curso` |
| 27/08/2026 | Parser y cargador PLACSP conservan lotes; 399 lotes vinculados a 81 expedientes | `en curso` |
