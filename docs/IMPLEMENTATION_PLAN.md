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
- [x] Revisar con datos reales que el alcance piloto cubre el criterio de éxito; test integrado organismo → expediente → adjudicatario → fuente oficial.

## Fase 1 — Fuentes oficiales y cobertura

Referencia MD: secciones 11, 12, 13, 14, 35, 42, 55 y 62.B–D.

- [x] Documentar Hacienda/IGAE, PLACSP, BDNS, INE e inventarios públicos.
- [x] Registrar URL, formato, cobertura, frecuencia, campos y limitaciones conocidas.
- [x] Descargar una muestra real de cada fuente prioritaria; PLACSP, BDNS, IGAE y CCAA disponibles en `data/raw/`.
- [~] Guardar muestras/fixtures con fecha, hash y licencia; manifiesto versionado en `docs/OFFICIAL_SAMPLES.md`, raw grande fuera de Git y fixtures de parser estructurales pendientes de publicar como artefactos separados.
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
- [~] Añadir índices y vistas materializadas para agregaciones; índices base e incrementales creados, vistas materializadas pendientes de una cobertura más amplia.

Entregables: `db/001_initial_schema.sql`, `db/002_seed_sources.sql`, `docs/DATA_MODEL.md`.

## Fase 3 — ETL reproducible y calidad de datos

Referencia MD: secciones 6, 7, 10, 13, 34, 40, 41, 43, 44 y 55.

- [x] Crear estructura `etl/shared`, `etl/placsp` y `etl/bdns`.
- [x] Implementar descarga raw con reintentos, timestamp y SHA-256.
- [x] Implementar registro `ingestion_run_id` en salidas normalizadas.
- [x] Implementar parser inicial de entradas ATOM/XML PLACSP.
- [x] Conservar XML BDNS sin fingir un mapeo cuando falta el servicio/XSD concreto.
- [~] Añadir parser completo CODICE para licitaciones, lotes, adjudicaciones y eventos; licitaciones, lotes y `TenderResult` ya se extraen, quedan eventos/versionado.
- [x] Añadir cliente BDNS20 por servicio, paginación, throttling y cache; cliente común con caché raw por URL, intervalo mínimo, tratamiento de `429` y paginación de concesiones configurable.
- [~] Implementar normalización NIF/CIF, nombres, fechas, euros y códigos; utilidades compartidas aplicadas a entidades PLACSP/BDNS, validación de control NIF/CIF y formatos españoles de euro añadidas, faltan validadores específicos de cada fuente.
- [~] Implementar flags de calidad: duplicados, fechas, IDs, importes y ejercicios; flags por registro añadidos a PLACSP y auditoría agregada activa, falta consolidar duplicados entre versiones y fuentes.
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
- [~] Importar lotes y adjudicaciones con adjudicatarios canónicos; lotes y `contract_awards` ya tienen loader y parser, falta validar la carga completa contra otra muestra real.
- [ ] Configurar el servicio BDNS oficial de convocatorias.
- [x] Configurar endpoint oficial BDNS de convocatoria y descargar una respuesta JSON real (`925963`).
- [~] Normalizar y cargar convocatorias BDNS; 1 convocatoria real cargada y repetible, endpoint y vista inicial activos, filtros y concesiones pendientes.
- [~] Configurar el servicio BDNS oficial de concesiones; consulta live activa con paginación y caché de 5 minutos, ingestor JSONL y loader PostgreSQL repetible disponibles, falta ingesta masiva de convocatorias con concesiones.
- [~] Importar muestras reales con URLs de origen; PLACSP y 1 convocatoria BDNS importadas.
- [x] Verificar que ningún contrato/subvención se presenta como pago presupuestario; test de integridad semántica añadido sobre las respuestas API.
- [x] Publicar estado y fecha de actualización de cada dataset; cobertura visible con fechas de IGAE, PLACSP y CCAA, y ausencia explícita cuando no existe.

## Fase 5 — Presupuesto y ejecución AGE piloto

Referencia MD: secciones 4, 5, 11, 16, 17, 20, 23, 30, 31, 32, 33, 36, 42, 56, 58, 59 y 62.H–I.

- [x] Seleccionar XLS estructurado de presupuesto y ejecución AGE.
- [x] Descargar muestra mensual y documentar estructura real.
- [~] Extraer filas del XLSX a JSONL auditable; periodo leído de cabecera y códigos/nombres separados cuando existen, falta normalización contable completa.
- [~] Normalizar hojas GTOS 001/002/004 a campos de ejecución separados; cargadas en PostgreSQL, falta validar totales completos.
- [x] Detectar periodo desde cabeceras y marcar anomalías contables sin eliminar registros.
- [x] Añadir cargador transaccional PostgreSQL para el JSONL IGAE y entorno Docker local.
- [x] Verificar carga repetida sin duplicados: 91 `budget_records` y 91 `budget_execution`.
- [ ] Parsear clasificación orgánica, económica y funcional/programas.
- [~] Importar crédito inicial, modificaciones, definitivo, comprometido, obligaciones y pagos; ejecución AGE cargada, crédito inicial/modificaciones detallados pendientes.
- [~] Conservar periodo, estado provisional/avance/definitivo y versión; las filas IGAE ya conservan periodo, estado y versión derivada del hash, faltan versiones históricas completas y estados definitivos de todos los ejercicios.
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
- [x] Implementar agregaciones separadas por magnitud mediante `/api/metrics`, con unidades, periodos y fuentes diferenciados.
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
- [x] Construir vista de empresa con contratos y subvenciones; contratos PLACSP activos y subvenciones separadas hasta disponer de concesiones persistidas.
- [x] Construir vista de contrato con lotes, eventos y fuente oficial; ficha interactiva, lotes y línea temporal CODICE activas.
- [~] Construir vista de subvención con convocatoria/concesiones; vista de convocatorias activa, concesiones pendientes.
- [x] Añadir presupuesto → ejecución con definiciones y estados en el detalle de cada capítulo.
- [~] Priorizar políticas de gasto reconocibles (pensiones, infraestructuras, sanidad, educación) sobre el detalle de contratación.
- [x] Añadir tooltips de conceptos técnicos en el detalle de ejecución de capítulos.
- [x] Priorizar ratios comprensibles en portada sin atribuir causalidad no demostrada.
- [x] Traducir titulares contables a lenguaje ciudadano y reservar la precisión técnica para el contexto.
- [~] Añadir patrón de drill-down visual; el nivel inferior queda bloqueado hasta disponer de una relación padre-hijo oficial.
- [x] Añadir estados loading/error/empty para la tabla de contratos.
- [~] Revisar responsive, accesibilidad y rendimiento; foco visible, navegación móvil, estados y `prefers-reduced-motion` activos, auditoría visual/WCAG completa pendiente.

## Fase 8 — Ampliación territorial y entidades

Referencia MD: secciones 9, 11, 12, 24, 25, 32, 35, 50 y 51.

- [~] Incorporar presupuestos y ejecución de CCAA; muestra mensual de 17 comunidades normalizada, falta carga completa.
- [~] Incorporar presupuestos, ejecución y liquidación local; fuente Access 2026 localizada y descargada, parser bloqueado por ausencia de lector Access compatible en el entorno.
- [~] Incorporar inventario de entidades públicas y jerarquías; inventario de organismos contratantes con contratos PLACSP publicado, jerarquías completas pendientes.
- [~] Incorporar geografía, códigos territoriales y población INE; búsqueda municipal y agregación provincial oficial activas.
- [~] Añadir CCAA, provincias y municipios a filtros y páginas; CCAA, municipio y provincia ya explorables, falta integrarlo en filtros de gasto.
- [~] Añadir mapa España → CCAA → provincia → municipio; mapa de límites CCAA del IGN activo con carga diferida, simplificación y cache en proceso, faltan provincias/municipios.
- [ ] Calcular gasto por habitante solo con población y periodo compatibles.
- [x] Medir cobertura real: completa, parcial, no disponible, en procesamiento.

## Fase 9 — Históricos, comparador y exploración avanzada

Referencia MD: secciones 21, 22, 24, 25, 30, 31, 32, 33, 35, 46, 47 y 57.

- [x] Añadir series históricas y evolución durante el ejercicio; abril y mayo de 2026 validados como cortes AGE compatibles.
- [x] Añadir comparador de administraciones/territorios; dos CCAA seleccionables con diferencia absoluta.
- [ ] Añadir nominal €/habitante y documentar cualquier € constante.
- [~] Añadir explorador jerárquico de partidas y descarga CSV; rueda/drill-down y exportación funcional activas, subpartidas solo cuando la fuente las publica.
- [~] Añadir indicadores descriptivos: ejecución, ranking territorial, relatos y concentración de adjudicatarios activos; ofertas y menores pendientes.
- [~] Permitir abrir el dataset subyacente desde cada indicador; fichas oficiales y exportación activas.
- [x] Añadir URLs compartibles y SEO para exploraciones importantes; query params y metadatos sociales/base y dinámicos activos.

## Fase 10 — Consolidación, relaciones y escala

Referencia MD: secciones 8, 10, 27, 34, 39, 48, 50, 51, 52, 53, 58 y 59.

- [ ] Modelar transferencias internas/externas y consolidación oficial.
- [ ] Evitar doble conteo entre Estado, CCAA y entidades receptoras.
- [ ] Implementar aliases, candidatos de merge y revisión humana.
- [~] Implementar red administración ↔ empresa con agregación/progressive loading; recorrido verificado visible en fichas de contrato.
- [~] Implementar “Sigue el dinero” solo con relaciones verificables; órgano → expediente → adjudicatario activo en PLACSP.
- [~] Añadir índices, particionado, vistas materializadas y jobs incrementales; índices y vistas analíticas base creados, particionado/materialización/jobs incrementales pendientes de escala y frecuencia validadas.
- [ ] Preparar object storage para raw y reprocesado.
- [ ] Expandir de AGE a 17 CCAA y después a 8.000+ municipios.

## Fase 11 — QA, transparencia y operación

Referencia MD: secciones 34, 35, 36, 37, 38, 39, 41, 42, 44, 45, 54, 55, 56, 60, 61 y 63.

- [ ] Tests de parsers con fixtures oficiales.
- [~] Tests de normalización y validaciones contables; endpoint visible de calidad con duplicados, IDs ausentes y alertas.
- [x] Tests de API y permisos de descarga; endpoints JSON y CSV cubiertos.
- [~] Tests end-to-end frontend → API → datos → fuente; smoke frontend/API activo, comprobación visual automatizada completa pendiente.
- [x] Página pública de cobertura y actualización.
- [x] Página de metodología completa y glosario.
- [~] Monitorización inicial de calidad y cobertura mediante `/api/quality`; monitorización histórica y de esquema pendiente.
- [ ] Jobs según frecuencia real comprobada, no asumida.
- [~] Revisión de accesibilidad, seguridad, privacidad y licencias; foco visible de teclado, estados y cabeceras básicas API activo, auditoría WCAG/licencias completa pendiente.
- [~] Deploy reproducible y guía de mantenimiento; `iniciar.bat` y `docs/MAINTENANCE.md` activos, despliegue público pendiente.
- [ ] Evaluación final contra el criterio de éxito del MVP.

## Estado global actual

**Fase 11/11 — QA, transparencia y operación, en curso.**

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
| 27/08/2026 | Lenguaje de portada simplificado a “¿En qué se gastaron 100 €?” y lectura “DE CADA 100 €” | `en curso` |
| 27/08/2026 | Rueda responsive en móvil y foco visible para teclado en controles principales | `en curso` |
| 27/08/2026 | Glosario ciudadano en Metodología: presupuesto, gasto registrado, dinero pagado y contratos | `en curso` |
| 27/08/2026 | Revisión de gráfico externo: se descarta como fuente no reproducible y se incorpora el desglose oficial de “Resto de políticas” | `en curso` |
| 27/08/2026 | Dataset funcional IGAE 2024 reproducible y endpoint `/api/policies`; 28 políticas y total oficial servidos | `en curso` |
| 27/08/2026 | La rueda consume `/api/policies` con fallback validado; agrupación de partidas principales y “Resto” conservada | `en curso` |
| 27/08/2026 | Metodología ampliada: glosario, separación de datasets, no doble conteo y estados de cobertura | `en curso` |
| 27/08/2026 | Matriz de cobertura efectiva: AGE, gasto funcional, PLACSP, BDNS, CCAA, local, entidades e INE | `en curso` |
| 27/08/2026 | Primera vista territorial conectada: 17 CCAA + total, gasto no financiero acumulado mayo 2026 y estado avance | `en curso` |
| 27/08/2026 | Filtro territorial accesible para consultar todas las CCAA o una comunidad sin mezclarla con AGE | `en curso` |
| 27/08/2026 | Fuente local CONPREL validada: ZIP Access 2026 descargable, hash registrado; parser bloqueado por dependencia de lector Access no instalada | `en curso` |
| 27/08/2026 | Comprobación de lectores Access 32/64 bits; sin proveedor OLE DB ni controlador ODBC disponible para extraer el esquema | `en curso` |
| 27/08/2026 | Cobertura API ampliada: 18 registros CCAA visibles como parcial y fuente local visible como bloqueada por lector | `en curso` |
| 27/08/2026 | La metodología muestra estados de fuente visibles: cargado, parcial, localizado y pendiente de lector | `en curso` |
| 27/08/2026 | El filtro de CCAA se conserva en la URL mediante `ccaa`, permitiendo compartir una comunidad concreta | `en curso` |
| 27/08/2026 | La selección de la rueda se conserva en la URL mediante `partida`, incluyendo el desglose de “Resto de políticas” | `en curso` |
| 27/08/2026 | Comparador territorial: dos CCAA seleccionables, diferencia absoluta en M€ y URL compartible mediante `comparar` | `en curso` |
| 27/08/2026 | Plan de producto para recurrencia y exploración: documento “Descubre en 60 segundos”, fichas, historias y “Sigue el dinero” | `en curso` |
| 27/08/2026 | Primera entrega de crecimiento: panel “Cuatro respuestas rápidas” con datos IGAE, CCAA y PLACSP enlazados a sus vistas | `en curso` |
| 27/08/2026 | Ranking visual de las 17 CCAA por gasto no financiero reconocido, con denominador, fecha y advertencia interpretativa | `en curso` |
| 27/08/2026 | Vista `/api/companies` y navegación “Empresas”: adjudicatarios agregados por contratos e importe publicado, separados de pagos | `en curso` |
| 27/08/2026 | Endpoint de ficha `/api/companies/:id` con resumen e inventario de contratos vinculados; 15 tests verdes | `en curso` |
| 27/08/2026 | Ficha de empresa visible desde la lista: resumen del adjudicatario y contratos vinculados con fuente oficial | `en curso` |
| 27/08/2026 | Ficha de empresa ampliada con número de organismos contratantes vinculados por contratos publicados | `en curso` |
| 27/08/2026 | Endpoint de ficha BDNS `/api/grants/:code` con presupuesto, finalidad, órgano y fuente; 16 tests verdes | `en curso` |
| 27/08/2026 | Ficha BDNS visible e interactiva dentro de la app; muestra presupuesto y deja explícita la ausencia de concesiones cargadas | `en curso` |
| 27/08/2026 | Ficha BDNS visible con presupuesto, finalidad, fechas y enlace oficial; 16 tests verdes | `en curso` |
| 27/08/2026 | Consulta oficial de concesiones por convocatoria: `/api/grants/:code/concesiones`, con estado live y 0 resultados verificados para 925963 | `en curso` |
| 27/08/2026 | Empresas y convocatorias se pueden compartir directamente mediante `empresa` y `convocatoria` en la URL | `en curso` |
| 27/08/2026 | Ficha BDNS consulta concesiones oficiales y distingue resultados, ausencia de concesiones y error de fuente | `en curso` |
| 27/08/2026 | La portada arranca con Pensiones seleccionada (32,1%) y el detalle es accesible con `aria-live` | `en curso` |
| 27/08/2026 | URL compartible para búsqueda y vista activa | `en curso` |
| 27/08/2026 | Detalle base de contrato y enlace directo a ficha oficial PLACSP | `en curso` |
| 27/08/2026 | Parser y cargador PLACSP conservan lotes; 399 lotes vinculados a 81 expedientes | `en curso` |
| 27/08/2026 | Buscador global ampliado a empresas: resultados directos a fichas de adjudicatarios mediante URL compartible | `en curso` |
| 27/08/2026 | Ficha de empresa ampliada con el listado de organismos públicos vinculados a sus contratos publicados | `en curso` |
| 27/08/2026 | Contratos muestran adjudicatario y NIF cuando están disponibles; empresas incorporan exportación CSV filtrable | `en curso` |
| 27/08/2026 | Portada incorpora tres historias descriptivas con cifras grandes, periodo, denominador y enlaces al desglose territorial o funcional | `en curso` |
| 27/08/2026 | Descarga y parseo oficial IGAE abril 2026 validado contra mayo: 91 filas compatibles y endpoint `/api/history` | `en curso` |
| 27/08/2026 | Evolución visual abril→mayo: pagos acumulados por euro de crédito definitivo, con advertencia de unidad y no doble conteo | `en curso` |
| 27/08/2026 | Detalle de capítulo económico con cadena previsto → comprometido → reconocido → pagado y definiciones ciudadanas | `en curso` |
| 27/08/2026 | Indicador de concentración PLACSP: porcentaje del importe acumulado de las cinco empresas principales, con denominador y advertencia interpretativa | `en curso` |
| 27/08/2026 | Ficha interactiva de contrato desde la tabla: presupuesto, procedimiento, fechas, lotes y fuente oficial PLACSP | `en curso` |
| 27/08/2026 | Buscador y fichas de contrato comparten URL mediante `contrato`; una búsqueda abre el segundo nivel dentro de la aplicación | `en curso` |
| 27/08/2026 | Relación verificable PLACSP en ficha: órgano contratante → expediente → adjudicatario, con importe y fuente | `en curso` |
| 27/08/2026 | Control de calidad visible en Metodología y endpoint `/api/quality`: conteos, duplicados, IDs ausentes y alertas por dataset | `en curso` |
| 27/08/2026 | Cabeceras API `nosniff`, `no-referrer`, `no-store` y metadescripción ciudadana; prueba automatizada de seguridad básica | `en curso` |
| 27/08/2026 | Smoke end-to-end frontend/API y guía `docs/MAINTENANCE.md` para arranque, validación y actualización del MVP | `en curso` |
| 27/08/2026 | Primera búsqueda municipal INE en vivo: nombre, código, provincia, comunidad y población oficial 2024; gasto por habitante reservado hasta disponer de ejecución compatible | `en curso` |
| 27/08/2026 | Búsqueda municipal ajustada al filtro GIS del INE y probada con respuesta oficial; estado de carga visible por latencia variable del proveedor | `en curso` |
| 27/08/2026 | Histórico añade variación explícita entre cortes: cambio de euros pagados por euro previsto, manteniendo el denominador | `en curso` |
| 27/08/2026 | Filtros de búsqueda conectados a convocatorias BDNS en la vista y en su exportación CSV | `en curso` |
| 27/08/2026 | Búsqueda municipal INE compartible mediante `municipio`, con recuperación automática de resultados al abrir la URL | `en curso` |
| 27/08/2026 | Tooltips accesibles para previsto, comprometido, gasto reconocido y pagado en el detalle de capítulo | `en curso` |
| 27/08/2026 | Revisión responsive: overflow horizontal controlado, reducción de movimiento respetada y foco visible conservado | `en curso` |
| 27/08/2026 | Diagnóstico reproducible de CONPREL: controlador Access 32-bit disponible no reconoce `Presupuestos2026.accdb`; fuente permanece bloqueada y sin cifras inventadas | `en curso` |
| 27/08/2026 | Localizado WFS oficial IGN para geometrías de CCAA, provincias y municipios; se registra fuente y licencia antes de construir el mapa | `en curso` |
| 27/08/2026 | Simulador ciudadano “Pon tu cifra”: convierte cualquier cantidad en euros por partida y enlaza cada fila con su desglose interactivo | `en curso` |
| 27/08/2026 | Caché en memoria invalidable por `mtime` para JSONL/JSON de la API; reduce lecturas repetidas y conserva actualización automática de ficheros | `en curso` |
| 27/08/2026 | Mapa territorial diferido: endpoint `/api/geography/communities` sirve límites CCAA oficiales IGN simplificados; 18,7 KB entregados al cliente y test de contrato añadido | `en curso` |
| 27/08/2026 | Snapshot versionado de la geometría IGN: el mapa arranca desde `data/processed/geo/community-boundaries.json` y conserva fallback live si falta el recurso | `en curso` |
| 27/08/2026 | Trazabilidad del snapshot geográfico: fecha de captura, SHA-256 y fuente OGC registrados en `docs/DATA_SOURCES.md` | `en curso` |
| 27/08/2026 | QA territorial: `/api/quality` audita la geometría IGN con 50 elementos, 0 IDs ausentes, 0 duplicados y 0 anomalías | `en curso` |
| 27/08/2026 | Integridad semántica: test API confirma que contratos y convocatorias no exponen campos de pagos, compromisos ni crédito presupuestario | `en curso` |
| 27/08/2026 | Exportación del desglose funcional: `/api/export.csv?entity=policies` descarga partidas y subpartidas disponibles sin inventar niveles ausentes | `en curso` |
| 27/08/2026 | SEO base para compartir: metadatos Open Graph/Twitter, idioma español y robots añadidos; test estático de metadatos | `en curso` |
| 27/08/2026 | Metadatos dinámicos en cliente: título y descripción cambian según vista, búsqueda o partida seleccionada al abrir una URL compartida | `en curso` |
| 27/08/2026 | Descubribilidad y acceso directo: `robots.txt` y manifest web en español añadidos, sin asumir dominio de producción | `en curso` |
| 27/08/2026 | Compartición contextual: Open Graph y Twitter Card se actualizan en cliente según vista, búsqueda y partida seleccionada | `en curso` |
| 27/08/2026 | Parser CODICE ampliado: `TenderResult` normaliza código, fecha, ofertas, ganador, NIF e importes sin mezclarlo con pagos; feed real auditado: 234 adjudicaciones y 216 ganadores | `en curso` |
| 27/08/2026 | Eventos CODICE iniciales: `ContractModification` conserva ID, expediente, nota, cambio de duración y duración final; feed real auditado: 5 modificaciones | `en curso` |
| 27/08/2026 | Persistencia de eventos: el cargador PostgreSQL guarda modificaciones en `contract_events` y la ficha API las devuelve junto a los lotes | `en curso` |
| 27/08/2026 | Línea temporal visible de eventos CODICE en la app: identifica modificaciones, fecha e ID, y aclara que no son pagos ni adjudicaciones nuevas | `en curso` |
| 27/08/2026 | Línea temporal sincronizada con la tabla: detecta cambios de `contrato` en la URL sin recargar y actualiza los eventos de la ficha | `en curso` |
| 27/08/2026 | BDNS concesiones: endpoint live admite `page`/`pageSize` y cachea respuestas 5 minutos para explorar más resultados sin repetir llamadas | `en curso` |
| 27/08/2026 | Ingestor BDNS de concesiones: paginación, raw por página, SHA-256, provenance y JSONL separado para concesiones | `en curso` |
| 27/08/2026 | Loader PostgreSQL de concesiones BDNS: relaciona convocatoria/beneficiario, registra `grant_awards` y evita duplicados por `source_record_id` | `en curso` |
| 27/08/2026 | Loader PLACSP persiste `TenderResult` en `contract_awards`, enlaza adjudicatarios por NIF/nombre y asocia lote cuando el feed lo publica | `en curso` |
| 27/08/2026 | Explorador territorial INE ampliado: búsqueda por municipio o provincia, suma provincial explícita y URL compartible | `en curso` |
| 27/08/2026 | Exportación funcional alineada con la rueda: `Resto de políticas` aparece como padre y sus partidas oficiales como subpartidas | `en curso` |
| 27/08/2026 | Tarjetas de cobertura muestran estado y fecha de carga; la fecha procede de `ingestion_runs.finished_at` | `en curso` |
| 27/08/2026 | Auditoría de calidad ampliada: 234 adjudicaciones PLACSP con IDs estables, 28 partidas IGAE y controles de duplicados/importes | `en curso` |
| 27/08/2026 | Fichas de empresa ampliadas con importe medio y mayor adjudicación, calculados desde `contract_awards` y separados de pagos | `en curso` |
| 27/08/2026 | Auditoría de ficha de empresa: indicadores de adjudicación comprobados en PostgreSQL y API, con tests de detalle | `en curso` |
| 27/08/2026 | Control de identificadores PLACSP corregido: 234 adjudicaciones con IDs compuestos estables, 0 duplicados y reprocesado PostgreSQL verificado | `en curso` |
| 27/08/2026 | QA ampliado con validación de fechas e importes no negativos para contratos, adjudicaciones y partidas IGAE; las anomalías se conservan visibles | `en curso` |
| 27/08/2026 | Runner `etl.run_available` y `actualizar_datos.bat` para reprocesar loaders disponibles, con skip explícito de inputs ausentes y salida JSON | `en curso` |
| 27/08/2026 | Auditoría de runtime cierra ficha de contrato y URLs compartibles: lotes/eventos, query params y metadatos dinámicos verificados | `en curso` |
| 27/08/2026 | Endpoint `/api/metrics` con presupuesto, ejecución, adjudicaciones y concesiones separados por unidad, periodo y fuente | `en curso` |
| 27/08/2026 | Portada consume `/api/metrics` en una franja visual de cuatro magnitudes, con periodo/fuente y aviso de separación semántica | `en curso` |
| 27/08/2026 | Cobertura CCAA muestra fecha real de recuperación desde `retrieved_at` y conserva el estado parcial explícito | `en curso` |
| 27/08/2026 | Cobertura IGAE recupera la fecha real de `retrieved_at` cuando PostgreSQL no tiene una ejecución cerrada | `en curso` |
| 27/08/2026 | El mapa IGN sincroniza la comunidad seleccionada con el comparador de gasto autonómico; municipio/provincia permanecen demográficos hasta disponer de gasto compatible | `en curso` |
| 27/08/2026 | `/api/metrics` incorpora caché de 30 segundos y solo entrega agregaciones, evitando enviar tablas completas al navegador | `en curso` |
| 27/08/2026 | Exportación territorial `/api/export.csv?entity=territories` con CCAA, total, periodo, estado, unidad, importe y fuente | `en curso` |
| 27/08/2026 | Comparador territorial incorpora enlaces visibles al CSV subyacente y a la fuente oficial CIMCANET | `en curso` |
| 27/08/2026 | Cada comunidad ofrece una búsqueda etiquetada en contratos PLACSP, diferenciando coincidencia textual de atribución territorial | `en curso` |
| 27/08/2026 | Resumen territorial ampliado con gasto e ingresos no financieros reconocidos y peso de cada CCAA sobre el total publicado | `en curso` |
| 27/08/2026 | Ficha de empresa muestra en pantalla total, media y mayor adjudicación al abrir una URL de empresa | `en curso` |
| 27/08/2026 | Auditoría del plan: se cierran como completados el estado/fecha pública de datasets y las agregaciones separadas por magnitud | `en curso` |
| 27/08/2026 | `/api/coverage` incorpora `checkedAt` para separar la hora de comprobación de la fecha/periodo de cada dato publicado | `en curso` |
| 27/08/2026 | `iniciar.bat` espera una respuesta HTTP real de Vite antes de abrir el navegador, manteniendo `git pull --ff-only` al inicio | `en curso` |
| 27/08/2026 | Cliente BDNS20 común con caché raw por URL, throttling configurable, tratamiento explícito de HTTP 429 y paginación de concesiones | `en curso` |
| 27/08/2026 | Normalización compartida para nombres, NIF/CIF, códigos y euros españoles aplicada a loaders PLACSP/BDNS, conservando siempre el raw | `en curso` |
| 27/08/2026 | Flags de calidad por registro en PLACSP para IDs, fechas, importes y ejercicios; anomalías conservadas junto al raw y cubiertas por tests | `en curso` |
| 27/08/2026 | Explorador INE ampliado a comunidades autónomas con suma oficial de población y número de municipios; mantiene separado el gasto 2026 por incompatibilidad temporal | `en curso` |
| 27/08/2026 | API y UI de población verificadas contra el endpoint oficial del INE para municipio, provincia y comunidad; se evita calcular €/habitante con periodos incompatibles | `en curso` |
| 27/08/2026 | `/api/budgets` añade filtros de nivel/texto y paginación, conservando el fallback JSONL y metadatos de filtros | `en curso` |
| 27/08/2026 | Nueva vista Organismos y endpoint `/api/entities`: ranking de órganos contratantes, contratos, adjudicatarios e importe publicado con alcance explícito | `en curso` |
| 27/08/2026 | Ficha API `/api/entities/:id` con contratos publicados y adjudicatarios vinculados por organismo; relación limitada a evidencia PLACSP | `en curso` |
| 27/08/2026 | Inventario de organismos exportable a CSV, con filtros de búsqueda y las mismas métricas que la vista web | `en curso` |
| 27/08/2026 | Informe `/api/companies/merge-candidates` para posibles coincidencias de nombres; solo propone candidatos y exige revisión humana | `en curso` |
| 27/08/2026 | Manifiesto `docs/OFFICIAL_SAMPLES.md` con cuatro muestras raw oficiales, tamaño, SHA-256, fecha, fuente y alcance de las fixtures | `en curso` |
| 27/08/2026 | Vistas analíticas PostgreSQL `db/004_analytics_views.sql` para cadena presupuestaria y totales de organismos/receptores, sin mezclar pagos y adjudicaciones | `en curso` |
| 27/08/2026 | Runner de actualización con run global, estado por loader, motivo de skip, timestamps y duración; dry-run y ejecución real quedan auditables | `en curso` |
| 27/08/2026 | Extractor IGAE conserva `period_state` y `dataset_version` derivada del SHA-256 del workbook; test con muestra real | `en curso` |
| 27/08/2026 | Extractor IGAE deja de fijar el mes, lee cabeceras reales y separa código/nombre de clasificación; tests con XLSX real | `en curso` |
| 27/08/2026 | `/api/overview?period=YYYY-MM` permite consultar un corte IGAE histórico del mismo ejercicio; verificado con abril de 2026 | `en curso` |
| 27/08/2026 | Selector visible de corte IGAE en la cabecera: abril/mayo 2026, URL compartible y cifras principales sincronizadas con el periodo | `en curso` |
| 27/08/2026 | Resumen de ejecución propaga el periodo también dentro de sus magnitudes; evita titulares ambiguos al cambiar de corte | `en curso` |
| 27/08/2026 | `/api/metrics?period=YYYY-MM` y la franja superior sincronizan presupuesto y ejecución con el corte histórico; contratos y ayudas permanecen separados | `en curso` |
| 27/08/2026 | Explorador contable incorpora búsqueda visible de capítulos sin alterar el denominador: filtrar no convierte los porcentajes en un falso 100% | `en curso` |
| 27/08/2026 | Explorador contable permite alternar capítulos de gasto y secciones administrativas, con búsqueda y porcentaje recalculado solo dentro del nivel elegido | `en curso` |
| 27/08/2026 | Señal visible de adjudicaciones con un único licitador: solo usa el campo publicado por PLACSP y explicita cuántos registros sí lo informan | `en curso` |
| 27/08/2026 | Agregación completa de contratación: `/api/contracts/insights` cuenta licitadores conocidos, adjudicaciones con uno y contratos con modificaciones publicadas | `en curso` |
| 27/08/2026 | Ficha de empresa añade top 5 de organismos adjudicadores por importe y número de contratos, calculado solo desde adjudicaciones PLACSP publicadas | `en curso` |
| 27/08/2026 | Ficha de empresa enlaza internamente a sus expedientes y a búsquedas de organismos, conservando el salto a la fuente oficial PLACSP | `en curso` |
| 27/08/2026 | Contexto territorial al seleccionar una CCAA: población oficial INE 2024 y número de municipios, separado explícitamente del gasto autonómico 2026 | `en curso` |
| 27/08/2026 | Selección territorial ofrece saltos inmediatos a búsquedas de contratos y organismos, etiquetadas como coincidencias textuales y no como atribución de gasto | `en curso` |
| 27/08/2026 | Ranking visible de los 5 organismos con mayor importe adjudicado, contratos y adjudicatarios, con enlace directo a investigar cada organismo | `en curso` |
| 27/08/2026 | Ranking de organismos abre ficha interna por ID estable, con contratos publicados y adjudicatarios enlazables a sus expedientes | `en curso` |
| 27/08/2026 | Criterio vertical del MVP verificado con datos reales: organismo contratante → contrato → adjudicatario → URL oficial PLACSP | `en curso` |
| 27/08/2026 | Migración idempotente `db/003_performance_indexes.sql` para búsquedas de organismos, contratos, empresas, ayudas y presupuestos | `en curso` |
| 27/08/2026 | `/api/quality` añade desglose de flags por tipo y primer registro de ejemplo, además de los contadores agregados | `en curso` |
