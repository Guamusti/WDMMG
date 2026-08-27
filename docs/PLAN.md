# Plan de ejecución del Atlas Universitario

Este documento convierte la especificación inicial del proyecto en un plan de trabajo operativo. Es la referencia que seguiremos para pasar de este MVP madrileño a una página completa, trazable y escalable.

## Principios no negociables

1. Exactitud antes que cobertura: una oferta no entra si no puede relacionarse con una fuente y un identificador fiable.
2. Cada cifra conserva curso, definición, fuente y fecha de recuperación.
3. Nota de corte, nota media, plazas, solicitudes, matriculados, egresados, abandono, afiliación y salario son campos distintos.
4. No se muestran valores inventados ni se rellenan huecos con estimaciones silenciosas.
5. No habrá un ranking opaco único: las comparaciones se basarán en métricas individuales explicadas.
6. Cada iteración debe dejar el proyecto arrancable con `iniciar.bat` y pasar el build de producción.

## Fase 0 — Base del producto (completada)

- [x] SPA React/Vite con diseño editorial responsive.
- [x] Buscador y filtro por carrera, universidad, ciudad y rama.
- [x] Comparador de hasta cuatro ofertas.
- [x] Percentil reproducible sobre ofertas con nota válida y escala común.
- [x] Fuente, definición y limitaciones documentadas.
- [x] Lanzador Windows `iniciar.bat`.
- [x] Mapa interactivo Leaflet + OpenStreetMap.

## Fase 1 — Madrid verificable (en curso)

Objetivo: cubrir las seis universidades públicas de Madrid y sus titulaciones oficiales de grado del curso 2025–2026.

- [x] Catálogo inicial ampliado a 40 ofertas reales para la interfaz.
- [x] Catálogo de la interfaz desacoplado en `src/data/madrid.js`.
- [x] UAH, UAM, UC3M, UCM, UPM y URJC representadas.
- [x] Color del mapa explicado: cada color identifica una universidad, con leyenda y tooltip.
- [x] Descargar y conservar el PDF oficial en `data/raw/`.
- [x] Crear parser reproducible para la publicación regional (`etl/admissions/madrid/`).
- [x] Extraer 458 filas públicas limpias con universidad, página y fila fuente; descartar filas contaminadas por el layout y validar con informe de calidad.
- [x] Endurecer la detección reproducible de nombres contaminados por el layout PDF, regenerar la trazabilidad RUCT a partir del extracto limpio y hacer que el smoke test valide el tamaño del catálogo procesado.
- [ ] Completar el catálogo de grados y dobles grados de las seis universidades.
- [x] Incorporar códigos oficiales de universidad y créditos/cursos presentes en la fuente regional; títulos y centros RUCT siguen pendientes de matching individual.
- [x] Añadir una ficha de detalle trazable para una oferta.
- [x] Añadir una vista exploratoria de universidad con sus ofertas cargadas.
- [x] Añadir páginas navegables y compartibles de oferta, universidad y grado.
- [x] Mostrar en la ruta de titulación el resumen agregado de ofertas, distribución de notas y referencia laboral de campo con granularidad explícita.
- [x] Añadir metadatos SEO básicos dinámicos por ruta (título, descripción y canonical).
- [x] Integrar filtros por universidad, rama, ciudad y tipo de grado con modo unión/intersección y subir “Tu nota” al inicio.
- [x] Añadir páginas completas indexables de detalle de universidad, grado y ciudad con metadatos SEO.

Criterio de terminado: buscar una carrera madrileña, localizar todas sus ofertas públicas cargadas, abrir fuente y ver nota, curso, campus, universidad y percentil sin ambigüedad.

Las rutas actuales del MVP son `/oferta/<id>`, `/universidad/<sigla>` y `/grado/<slug>`. El catálogo sigue siendo una selección validada, no todavía el censo completo de grados madrileños.

## Fase 2 — Modelo y persistencia

- [x] Preparar migración PostgreSQL con `universities`, `campuses`, `centers`, `degrees`, `degree_offerings`, `academic_years` y `admission_cutoffs` (`db/migrations/001_initial.sql`).
- [x] Incluir en la migración `data_sources`, `ingestion_runs`, `provenance` y `data_quality_flags`.
- [x] Añadir reporte reproducible de calidad del extracto madrileño (`etl/shared/quality_report.py`).
- [x] Matching por código RUCT para las seis universidades públicas de Madrid; alias solo como apoyo auditado.
- [ ] Matching de códigos RUCT de títulos y centros.
- [x] Matching conservador de títulos RUCT para las ofertas madrileñas con coincidencia exacta única; las ambiguas/no encontradas quedan pendientes y auditadas.
- [x] Clasificar la oferta RUCT entre grado simple, doble grado, programa especial, internacional o de alianza; conservar componentes solo cuando el separador es estructural.
- [x] Centros RUCT, rama, campo y créditos recuperados desde las fichas de los 359 títulos emparejados; el censo completo de centros y ofertas sigue pendiente.
- [x] Preparar vistas materializadas para percentiles y cobertura (`db/migrations/002_views.sql`).
- [x] API interna con filtros básicos, paginación, fuente y URLs compartibles (`api/server.mjs`); el launcher selecciona puerto libre.
- [x] Proxy Vite mismo-origen para `/api/*`, con el puerto de API heredado por el único proceso frontend del launcher.
- [x] Launcher idempotente: reutiliza una pareja saludable frontend/API, valida el contrato de Atlas y evita procesos duplicados o proxies desincronizados.
- [x] Endpoint nacional separado (`/api/national-offers`) y cobertura agregada (`/api/coverage`) con filtro por comunidad y procedencia preservada.
- [x] Explorador conectado a la API con fallback local para preservar el arranque si el servicio no está disponible.
- [x] La API conserva el enriquecimiento RUCT de cada oferta (título, campo, centros y ficha oficial) al servir el catálogo del frontend.
- [x] La ficha distingue visualmente la identificación RUCT verificada de una oferta pendiente, sin ocultar ni completar por similitud.
- [x] Caché de JSON de la API invalidada por `mtime`, manteniendo disponibles las actualizaciones del catálogo sin lecturas repetidas.
- [x] Validación HTTP con ETag/304 y `Cache-Control` para no retransmitir catálogos sin cambios.

Criterio de terminado: una ingestión limpia reconstruye la misma interfaz y cada registro permite responder “¿de dónde sale este dato?”.

## Fase 3 — Toda España: admisión

- [x] Inventario por comunidad autónoma de organismo, URL, formato, rondas y cobertura (verificadas o pendientes explícitas).
- [ ] Ingestores priorizando API, CSV, XLS/XLSX, JSON y PDF estructurado.
- [x] Normalización de cursos como `YYYY-YYYY`.
- [x] Primer ingestor regional adicional reproducible (Galicia), conservando ronda y grupo; ampliar a tres comunidades y completar la cobertura nacional.
- [x] Segundo ingestor regional reproducible (Aragón), con provincia, convocatoria y cupo general conservados; faltan el modelo común de cupos y la integración nacional.
- [x] Catálogo nacional de trabajo reproducible con los extractos de Madrid, Galicia, Aragón, Cataluña y Andalucía, informe de comparabilidad y procedencia regional.
- [x] Tercer ingestor regional adicional (Cataluña), con primera asignación, código de estudio, centro/población y cupo PAU/CFGS conservados.
- [x] Cuarto ingestor regional adicional (Andalucía), con consulta oficial 2025-2026, nota general, rama, centro y nueve universidades públicas conservados.
- [x] Quinto ingestor regional adicional (Castilla y León), con PDF oficial 2025-2026 y 49 ofertas de la Universidad de León conservadas como cobertura parcial explícita.
- [x] Sexta cobertura oficial adicional dentro de Castilla y León, con el segundo listado ordinario 2025-2026 de la Universidad de Salamanca y 73 ofertas conservadas.
- [x] Séptimo ingestor regional adicional (Cantabria), con nota de julio como `last_call` y 37 ofertas de la Universidad de Cantabria conservadas.
- [x] Octavo ingestor regional adicional (Navarra), con PDF oficial de la UPNA, 41 ofertas, cupo general y marcas extraordinarias conservadas.
- [x] Noveno ingestor regional adicional (Asturias), con tabla institucional de la Universidad de Oviedo, 68 ofertas, primera fase de julio y plazas conservadas.
- [x] Décimo ingestor regional adicional (Illes Balears), con páginas oficiales de la UIB, procesos JUN/EXT y 296 observaciones de PAU/CFGS conservadas.
- [x] Separación de grupo, convocatoria, ronda inicial y nota final en el modelo nacional; cada fuente conserva solo las dimensiones que publica y las ausencias quedan explícitas.
- [x] Exponer convocatoria y cupo como filtros aplicables en `/espana`, manteniendo sus valores originales por fila.
- [x] Percentiles nacionales, regionales, por rama y por campo RUCT cuando existe una clasificación oficial; el catálogo mantiene cobertura parcial y no infiere campos ausentes.
- [x] Percentiles nacional, por comunidad, rama y campo RUCT sobre las observaciones cargadas en `/espana`, con el ámbito de comparación indicado en cada fila.
- [x] Explorador nacional inicial de notas, mapa orientativo y “qué puedo estudiar con mi nota” para las diez comunidades procesadas; percentiles comparables visibles según cobertura.
- [x] Explorador nacional inicial `/espana` con búsqueda, comunidad, nota/tolerancia, orden, procedencia, estado de cobertura y carga completa del catálogo; el mapa sigue siendo orientativo.

Criterio de terminado: el filtro España permite comparar solo ofertas metodológicamente compatibles y muestra cobertura por comunidad.

## Fase 4 — Estudiantes y resultados académicos

- [ ] Integrar SIIU para matriculados, nuevo ingreso, egresados y series históricas.
- [x] Definir el contrato de métricas y mostrar rendimiento, abandono y graduación con definición, curso y granularidad visible.
- [x] Externalizar el primer extracto procesado de contexto académico de las seis universidades públicas de Madrid, con fuente y limitación.
- [x] Añadir nota media de admisión del nuevo ingreso por universidad (curso 2022–2023), diferenciada explícitamente de la nota media del expediente y de la oferta.
- [x] Añadir número de estudiantes de nuevo ingreso por universidad (2022–2023), con fuente y granularidad agregada visibles.
- [x] Añadir primer extracto reproducible de matriculados en grados presenciales por universidad (curso 2023–2024), separado de nuevo ingreso y de la oferta.
- [x] Añadir primer extracto reproducible de egresados en grados presenciales por universidad (curso 2023–2024), separado de la tasa de graduación.
- [x] Auditar la granularidad SIIU disponible: rendimiento y abandono por universidad/ámbito se mantienen como contexto, porque este corte no ofrece código de titulación para atribución individual.
- [ ] Cargar los valores por ámbito/titulación y comparar oferta, universidad, rama y España sin mezclar granularidades.

Criterio de terminado: cada métrica académica tiene tooltip de definición, curso y cobertura.

## Fase 5 — Inserción laboral

- [x] Integrar afiliación por cohorte y años desde graduación; la ficha conserva la cohorte, los años desde el egreso y la limitación de granularidad.
- [x] Añadir una referencia laboral de ámbito para Informática, con cohorte, definición y fuente visibles; no se atribuye automáticamente a una titulación.
- [x] Añadir referencias laborales agregadas para Informática, ADE, Economía, Derecho, Medicina, Enfermería, Sociología y Periodismo, con cobertura explícita de campo y cohorte.
- [x] Mantener separado el concepto de salario frente a afiliación y base media de cotización; la ficha ya indica “no disponible” mientras falte el cruce por ámbito.
- [x] Mostrar 1, 2, 3 y 4 años después cuando existan datos comparables; la ficha expone la serie nacional y la separa del campo de estudio.
- [x] Mostrar la evolución nacional disponible a 1, 2, 3 y 4 años, separada de la referencia del campo y sin extrapolarla a una carrera.
- [x] Evitar llamar “salario” a una base de cotización.
- [x] Registrar la cohorte oficial más reciente y separar su fecha de publicación del extracto local reproducible en `data/processed/outcomes/employment-coverage.json`.

Criterio de terminado: una oferta puede compararse por resultados laborales sin convertir una cifra administrativa en una promesa de empleo.

## Fase 6 — Coste e internacionalización

- [x] Precios públicos por ECTS, matrícula y experimentalidad en Madrid, asignados solo cuando el nivel está documentado.
- [x] Internacionalización y movilidad con cobertura explícita.
- [x] Integrar estudiantes internacionales entrantes por universidad (2022–2023), con definición, granularidad y fuente visibles; la movilidad saliente y por titulación siguen pendientes.
- [x] Integrar recuento de movilidad internacional saliente por universidad (2021–2022), con fuente y definición separadas de los entrantes; la movilidad por titulación sigue pendiente.
- [x] Añadir el ratio institucional entrantes/salientes de movilidad (2021–2022), manteniendo la fórmula y las limitaciones visibles.
- [x] Mantener becas, Erasmus y coste de vida como módulos separados; la ficha distingue coste, movilidad y el módulo de ayudas/vivienda pendiente.

## Fase 7 — Producto completo

- [x] Home, buscador global, mapa, página de grado, universidad, oferta y ciudad; el smoke test cubre también el explorador nacional y el comparador.
- [x] Ruta de ciudad `/ciudad/<slug>` con ofertas verificables y enlaces a cada detalle.
- [x] Comparador de hasta cuatro ofertas y comparador de hasta cuatro universidades de Madrid, con notas y métricas agregadas etiquetadas.
- [x] Filtro de base media de cotización por umbral (25.000 €, 30.000 € y 35.000 €), con opción sin dato y ordenación separada de la nota de corte.
- [x] Descargas CSV de filtros actuales (incluye columnas laborales cuando existe una referencia compatible).
- [x] Descarga CSV de los resultados actuales de Madrid.
- [x] Metodología visible dentro de la interfaz con definiciones y limitaciones.
- [x] Calculadora PAU sobre 14 con nota de acceso, dos ponderaciones y fórmula visible.
- [x] Cobertura de datos visible.
- [x] Quality gate reproducible para datos procesados y build (`etl/quality_check.py` + GitHub Actions), regenerando antes el informe madrileño para evitar cifras desfasadas.
- [x] Smoke test reproducible de frontend, API, contrato nacional y caché HTTP (`npm run smoke`).
- [x] Verificación visual de home, catálogo completo, navegación a oferta y `/espana` sin errores de consola.
- [x] SEO de páginas con datos reales, sin contenido repetitivo: metadatos dinámicos y JSON-LD específico para oferta, universidad, titulación, ciudad, explorador nacional y comparador.
- [x] Añadir datos estructurados JSON-LD específicos para ofertas, universidades, titulaciones y ciudades con catálogo real.
- [x] Metadatos específicos para el explorador nacional `/espana`, con cobertura y limitaciones reales.
- [ ] Accesibilidad, rendimiento, caché, paginación y responsive.
- [x] Carga diferida del mapa Leaflet para reducir el bundle inicial; el resto de la auditoría de rendimiento sigue pendiente.
- [x] Caché HTTP del API de catálogos mediante ETag/304; quedan pendientes auditoría completa y caché de assets.
- [x] Paginación del explorador nacional a 50 resultados por página, con reinicio al aplicar filtros; quedan caché, rendimiento y auditoría completa.
- [x] Foco visible de teclado y respeto de `prefers-reduced-motion` en la interfaz; quedan auditoría WCAG, rendimiento, caché y paginación.
- [x] Tablas principales con nombre accesible (`caption`), encabezados por columna (`scope`) y ocultación visual no semántica reutilizable.
- [x] Separar datos y dependencias del mapa en chunks cacheables para reducir el bundle inicial y evitar redescargas completas.
- [x] Contrato automático de accesibilidad para tablas, foco, movimiento reducido, diálogos, estados anunciables y responsive (`npm run audit:accessibility`).
- [x] Contrato automático de rendimiento y caché de assets: bundle inicial, nombres con hash y code-splitting de mapa/explorador (`npm run audit:performance`).

## Bucle de trabajo de cada cambio

1. Revisar fuente y modelo antes de editar la UI.
2. Añadir o actualizar datos con provenance.
3. Actualizar documentación y limitaciones.
4. Implementar la experiencia mínima que expone esos datos.
5. Ejecutar `npm run build`.
6. Probar `iniciar.bat` y verificar la instancia local.
7. Commit descriptivo y push a `main`.

## Definición final de “totalmente funcional”

La página estará completa cuando una persona pueda empezar en España o una CCAA, buscar una carrera o universidad, filtrar y ordenar ofertas, ver mapa y detalle, entender cada métrica, comparar hasta cuatro opciones, consultar histórico y fuente, descargar el resultado y repetir el recorrido con datos reproducibles.
