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
- [x] Extraer 497 filas públicas con universidad, página y fila fuente; validar con informe de calidad.
- [ ] Completar el catálogo de grados y dobles grados de las seis universidades.
- [ ] Incorporar códigos oficiales, créditos, cursos y centros desde la fuente.
- [x] Añadir una ficha de detalle trazable para una oferta.
- [x] Añadir una vista exploratoria de universidad con sus ofertas cargadas.
- [x] Añadir páginas navegables y compartibles de oferta, universidad y grado.
- [x] Añadir metadatos SEO básicos dinámicos por ruta (título, descripción y canonical).
- [x] Integrar filtros por universidad, rama, ciudad y tipo de grado con modo unión/intersección y subir “Tu nota” al inicio.
- [ ] Añadir páginas completas indexables de detalle de universidad y grado con metadatos SEO.

Criterio de terminado: buscar una carrera madrileña, localizar todas sus ofertas públicas cargadas, abrir fuente y ver nota, curso, campus, universidad y percentil sin ambigüedad.

Las rutas actuales del MVP son `/oferta/<id>`, `/universidad/<sigla>` y `/grado/<slug>`. El catálogo sigue siendo una selección validada, no todavía el censo completo de grados madrileños.

## Fase 2 — Modelo y persistencia

- [x] Preparar migración PostgreSQL con `universities`, `campuses`, `centers`, `degrees`, `degree_offerings`, `academic_years` y `admission_cutoffs` (`db/migrations/001_initial.sql`).
- [x] Incluir en la migración `data_sources`, `ingestion_runs`, `provenance` y `data_quality_flags`.
- [x] Añadir reporte reproducible de calidad del extracto madrileño (`etl/shared/quality_report.py`).
- [ ] Matching por código RUCT; alias solo como apoyo auditado.
- [ ] Vistas materializadas para métricas y percentiles.
- [ ] API interna con filtros, paginación y URLs compartibles.

Criterio de terminado: una ingestión limpia reconstruye la misma interfaz y cada registro permite responder “¿de dónde sale este dato?”.

## Fase 3 — Toda España: admisión

- [ ] Inventario por comunidad autónoma de organismo, URL, formato, rondas y cobertura.
- [ ] Ingestores priorizando API, CSV, XLS/XLSX, JSON y PDF estructurado.
- [ ] Normalización de cursos como `YYYY-YYYY`.
- [ ] Separación de grupo, convocatoria, ronda inicial y nota final.
- [ ] Percentiles nacionales, regionales, por rama y por ámbito.
- [ ] Explorador nacional de notas, mapa y “qué puedo estudiar con mi nota”.

Criterio de terminado: el filtro España permite comparar solo ofertas metodológicamente compatibles y muestra cobertura por comunidad.

## Fase 4 — Estudiantes y resultados académicos

- [ ] Integrar SIIU para matriculados, nuevo ingreso, egresados y series históricas.
- [x] Definir el contrato de métricas y mostrar rendimiento, abandono y graduación con definición, curso y granularidad visible.
- [ ] Cargar los valores por ámbito/titulación y comparar oferta, universidad, rama y España sin mezclar granularidades.

Criterio de terminado: cada métrica académica tiene tooltip de definición, curso y cobertura.

## Fase 5 — Inserción laboral

- [ ] Integrar afiliación por cohorte y años desde graduación.
- [x] Mantener separado el concepto de salario frente a afiliación y base media de cotización; la ficha ya indica “no disponible” mientras falte el cruce por ámbito.
- [ ] Mostrar 1, 2, 3 y 4 años después cuando existan datos comparables.
- [ ] Evitar llamar “salario” a una base de cotización.

Criterio de terminado: una oferta puede compararse por resultados laborales sin convertir una cifra administrativa en una promesa de empleo.

## Fase 6 — Coste e internacionalización

- [ ] Precios públicos por ECTS, matrícula y experimentalidad.
- [ ] Internacionalización y movilidad con cobertura explícita.
- [ ] Mantener becas, Erasmus y coste de vida como módulos separados.

## Fase 7 — Producto completo

- [ ] Home, buscador global, mapa, página de grado, universidad, oferta y ciudad.
- [ ] Comparador de ofertas y universidades.
- [ ] Descargas CSV de filtros actuales.
- [x] Descarga CSV de los resultados actuales de Madrid.
- [ ] Cobertura de datos visible.
- [ ] SEO de páginas con datos reales, sin contenido repetitivo.
- [ ] Accesibilidad, rendimiento, caché, paginación y responsive.

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
