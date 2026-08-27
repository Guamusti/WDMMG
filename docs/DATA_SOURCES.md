# Fuentes de datos

## Registro de Universidades, Centros y Títulos (RUCT)

- Organismo: Ministerio de Ciencia, Innovación y Universidades.
- URL: https://www.ciencia.gob.es/Universidades/RUCT.html
- Uso previsto: registro maestro de universidades, centros, títulos oficiales, códigos y estado.
- Granularidad: universidad, centro y título.
- Limitación: la consulta pública no sustituye a un export histórico; el ingestor debe conservar la evidencia de cada consulta.
- Estado: consulta reproducible de títulos de Grado activa para las seis universidades públicas madrileñas; el matching de centros y las coincidencias no exactas siguen pendientes.
- Distribución estructurada auxiliar de códigos de universidad: https://datos.canarias.es/api/estadisticas/structural-resources/v1.0/codelists/ISTAC/CL_RUCT_UNIVERSIDADES/01.000/codes.csv?fields=+description
- Estado actual: códigos de universidad y 330 coincidencias únicas de títulos están conservados en `data/processed/ruct/`, junto con centro, rama, campo y créditos cuando la ficha los publica; las 129 ofertas restantes quedan pendientes por falta de coincidencia exacta o ambigüedad. El censo completo de centros requiere ampliar la consulta.

## Notas de corte — Comunidad de Madrid

- Organismo: Comunidad de Madrid, Centro de Información y Asesoramiento Universitario.
- Fuente editorial: https://www.comunidad.madrid/educacion/publicaciones-interes-universitario
- Publicación de referencia: “Notas de acceso de las titulaciones universitarias oficiales de la Comunidad de Madrid. Curso 2025-2026”.
- Formato observado: PDF/HTML publicado por la Comunidad; contiene código, titulación, grupos de acceso y columnas ordinaria/extraordinaria.
- Estado: PDF conservado en `data/raw/`, parser reproducible en `etl/admissions/madrid/` y muestra integrada en la interfaz. El matching contra RUCT sigue pendiente.

## Notas institucionales complementarias

- UC3M: https://www.uc3m.es/ss/Satellite/UC3MInstitucional/es/TextoMixta/1371206740815/Notas_de_corte
- URJC: publicación institucional de notas 2025/2026 enlazada desde sus páginas de admisión.
- Uso: validar campus y ofertas específicas cuando la publicación regional no expone el contexto con suficiente detalle.

## Notas de corte — Galicia

- Organismo: Comisión Interuniversitaria de Galicia (CIUG).
- Publicación de referencia: “Notas de corte 2025” para el curso 2025-2026.
- Fuente: https://ciug.gal/PDF/2025/ACCESO/notas_de_corte_2025.pdf
- Estado: PDF conservado en `data/raw/admissions/galicia/2025-2026/`; parser reproducible en `etl/admissions/galicia/` y extracto separado en `data/processed/admissions/galicia-2025-2026.json`.
- Cobertura validada: 194 titulaciones en seis campus y 333 observaciones con ronda ordinaria/extraordinaria. No se mezcla aún con el catálogo de Madrid hasta completar el modelo nacional común y el matching RUCT.

## Notas de corte — Aragón

- Organismo: Universidad de Zaragoza.
- Publicación de referencia: adjudicación ordinaria de julio de 2025 para el curso 2025-2026.
- Fuente: https://academico.unizar.es/sites/academico/files/archivos/acceso/admisgrado/corte/grados2526j.pdf
- Estado: PDF conservado en `data/raw/admissions/aragon/2025-2026/`; parser reproducible en `etl/admissions/aragon/` y extracto separado en `data/processed/admissions/aragon-2025-2026.json`.
- Cobertura validada: 73 ofertas de la Universidad de Zaragoza en cuatro provincias/campus. Se carga únicamente la columna de cupo general y la convocatoria ordinaria; las restantes columnas de cupos requieren su modelado explícito antes de comparar.

## Notas de corte — Cataluña

- Organismo: Secretaría de Universidades e Investigación / Canal Universitats de la Generalitat de Catalunya.
- Publicación de referencia: primera asignación de plazas de junio de 2025, publicada el 11/07/2025.
- Fuente oficial: [notas de corte de preinscripción](https://universitats.gencat.cat/ca/preinscripcions/notes-tall) y [PDF de la primera asignación](https://universitats.gencat.cat/web/.content/02_preinscripcio/enllac-documents/notes-de-tall/Notes-tall-1a-assignacio_juny_2025_v3.pdf).
- Estado: PDF conservado en `data/raw/admissions/cataluna/2025-2026/`; parser reproducible en `etl/admissions/cataluna/` y extracto separado en `data/processed/admissions/cataluna-2025-2026.json`.
- Cobertura validada: 549 observaciones con código de estudio, centro/población, primera asignación y cupo PAU/CFGS. Se rechazan 5 filas de maquetación ambigua, registradas en `cataluna-2025-2026-quality.json`, para evitar nombres contaminados.

## Catálogo nacional de trabajo

- `data/processed/admissions/national-2025-2026.json` reúne observaciones procesadas de cuatro comunidades: Madrid (459), Galicia (333), Aragón (73) y Cataluña (549).
- `national-2025-2026-quality.json` valida curso único, escala 0–14, ronda/grupo presentes y ausencia de duplicados de observación. La cobertura de rama es parcial (417/1414) y la de campo RUCT también (322/1414), por lo que el catálogo no se presenta como ranking nacional único.

## SIIU / estadísticas universitarias

- Organismo: Ministerio competente en universidades.
- Rendimiento/éxito/evaluación: https://estadisticas.universidades.gob.es/jaxiPx/Datos.htm?file=Rendimiento_Exito_Eval_Grado_Univ.px&path=%2FUniversitaria%2FIndicadores%2F2024%2F1_Grado%2Fl0%2F
- Abandono de estudios: https://estadisticas.universidades.gob.es/jaxiPx/Datos.htm?file=Abandono_Grado_Univ.px&path=%2FUniversitaria%2FIndicadores%2F2023%2F1_Grado%2Fl0%2F
- Graduación: https://estadisticas.universidades.gob.es/jaxiPx/Datos.htm?file=Graduacion_Grado_Univ.px&path=%2FUniversitaria%2FIndicadores%2F2023%2F1_Grado%2Fl0%2F
- Inserción laboral/base de cotización: https://estadisticas.universidades.gob.es/jaxiPx/Tabla.htm?L=0&file=Base_cotizacion_Sexo_Campo_Grado_Total.px&path=%2FUniversitaria%2FInsercion_laboral%2F2024%2FGRADO%2FCAP6_BMC%2F%2Fl0%2F&type=pcaxis
- Definiciones aplicadas: rendimiento = créditos superados / matriculados; abandono y graduación se interpretan por cohorte y duración publicadas por SIIU.
- Limitación: una base media de cotización es un indicador administrativo de afiliación, no un salario medio ni mediano. Se requiere cargar el cruce por ámbito de estudio antes de atribuirlo a una carrera concreta.
- Estado: la interfaz muestra contexto universitario con etiqueta de cobertura y deja como no disponible lo que aún no está cargado a nivel de titulación. La primera referencia de ámbito para Informática (cohorte 2017–2018, cuatro años después) se conserva en `src/data/outcomes.js` y se usa para filtrar/ordenar sin presentarla como salario de una oferta. La tarjeta enlaza la referencia publicada por Fundación CYD y el registro SIIU.
- El contexto académico de Madrid se conserva además como extracto procesado en `data/processed/outcomes/madrid-university-context-2022-2023.json`, incluyendo curso, granularidad, fuente y limitación.
- Ese extracto incorpora la nota media de admisión del alumnado de nuevo ingreso por universidad (2022–2023), procedente de la tabla SIIU de nota media por rama; se presenta solo como contexto universitario y no como nota del expediente o de una carrera.
- También incorpora el número de estudiantes de nuevo ingreso por universidad (2022–2023), ambos sexos y todos los campos de estudio; es un contexto de tamaño institucional, no de una oferta individual.
- La ficha enlaza ambas tablas SIIU desde la propia tarjeta: nota media de admisión (`3_6_NI_Nota_media_Sex_Rama_Univ.px`) y nuevo ingreso (`3_4_Mat_Sex_Nac_Amb_Univ.px`). Mantener ambos conceptos separados evita confundir una media institucional con una nota de corte o con el expediente del estudiante.
- Matriculados en grado presencial: conjunto de datos abiertos de la Comunidad de Madrid, curso 2023–2024 (el CSV etiqueta el curso por su año final). El extracto procesado está en `data/processed/outcomes/madrid-university-enrolment-2023-2024.json` y se reconstruye con `etl/outcomes/ingest_madrid_enrolment.py`. Es un total de universidad, no de titulación, y excluye grados no presenciales.
- Egresados en grado presencial: conjunto de datos abiertos de la Comunidad de Madrid, curso 2023–2024 (el CSV etiqueta el curso por su año final). El extracto procesado está en `data/processed/outcomes/madrid-university-graduates-2023-2024.json` y se reconstruye con `etl/outcomes/ingest_madrid_graduates.py`. Es un recuento institucional, no una tasa de graduación ni un resultado de una titulación.

## Geografía

- Fuente prevista: códigos oficiales de comunidades autónomas, provincias y municipios del INE/administración pública.
- Uso: normalizar municipio, provincia y CCAA; coordenadas se conservarán separadas de los nombres.
- Estado: coordenadas de mapa MVP son una representación de interfaz; deben reemplazarse por geometrías/códigos oficiales en la siguiente iteración.
