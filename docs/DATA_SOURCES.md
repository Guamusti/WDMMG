# Fuentes de datos

## Registro de Universidades, Centros y Títulos (RUCT)

- Organismo: Ministerio de Ciencia, Innovación y Universidades.
- URL: https://www.ciencia.gob.es/Universidades/RUCT.html
- Uso previsto: registro maestro de universidades, centros, títulos oficiales, códigos y estado.
- Granularidad: universidad, centro y título.
- Limitación: la consulta pública no sustituye a un export histórico; el ingestor debe conservar la evidencia de cada consulta.
- Estado: consulta reproducible de títulos de Grado activa para las seis universidades públicas madrileñas; el matching de centros y las coincidencias no exactas siguen pendientes.
- Distribución estructurada auxiliar de códigos de universidad: https://datos.canarias.es/api/estadisticas/structural-resources/v1.0/codelists/ISTAC/CL_RUCT_UNIVERSIDADES/01.000/codes.csv?fields=+description
- Estado actual: códigos de universidad y 361 coincidencias únicas de títulos están conservados en `data/processed/ruct/`, junto con centro, rama, campo y créditos cuando la ficha los publica; las 97 ofertas restantes quedan pendientes por falta de coincidencia exacta o ambigüedad. Dos ambigüedades se resolvieron por campus contra el centro RUCT oficial; el censo completo de centros requiere ampliar la consulta.
- La API local une ese extracto con las filas de admisión por `madrid:<índice>` y expone el código, campo, centros y enlace RUCT en la ficha; el smoke test comprueba que este enriquecimiento no se pierde al pasar por el proxy.

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

## Notas de corte — Andalucía

- Organismo: Distrito Único Andaluz de la Junta de Andalucía.
- Publicación de referencia: consulta oficial de notas de corte de años anteriores, curso de acceso 2025/2026.
- Fuente oficial: https://www.juntadeandalucia.es/economiaconocimientoempresasyuniversidad/sguit/index.php?d=g_not_cor_anteriores_top.php&q=grados
- Estado: respuesta HTML conservada en `data/raw/admissions/andalucia/2025-2026/`; parser reproducible en `etl/admissions/andalucia/` y extracto separado en `data/processed/admissions/andalucia-2025-2026.json`.
- Cobertura validada: 581 observaciones de nueve universidades públicas. Se carga únicamente la nota general (`Gral.`), con rama y centro conservados; 38 filas incompletas se registran como rechazadas.

## Notas de corte — Cantabria

- Organismo: Universidad de Cantabria.
- Publicación de referencia: notas de corte del curso 2025/2026, con columnas de junio y julio.
- Fuente oficial: https://web.unican.es/estudiantesuc/Documents/Estad%C3%ADsticas/Grado/Estad%C3%ADsticas%20de%20Ordenaci%C3%B3n%20Acad%C3%A9mica/7%20Notas%20de%20corte.pdf
- Estado: PDF conservado en `data/raw/admissions/cantabria/2025-2026/`; parser reproducible en `etl/admissions/cantabria/` y extracto separado en `data/processed/admissions/cantabria-2025-2026.json`.
- Cobertura validada: 37 ofertas. Se conserva la nota de julio como `last_call` del cupo general y no se presenta como una primera adjudicación.

## Catálogo nacional de trabajo

- `data/processed/admissions/national-2025-2026.json` reúne observaciones procesadas de doce comunidades: Madrid (458), Galicia (333), Aragón (73), Cataluña (549), Andalucía (581), Castilla y León (122), Cantabria (37), Navarra (41), Asturias (68), Illes Balears (296), Canarias (69: 51 de la ULPGC y 18 de la ULL) y La Rioja (12).
- `national-2025-2026-quality.json` valida curso único, escala 0–14, ronda/grupo presentes y ausencia de duplicados de observación. La cobertura de rama es parcial y la de campo RUCT también, por lo que el catálogo no se presenta como ranking nacional único.

## Notas de corte — Canarias

- Organismo: Universidad de Las Palmas de Gran Canaria (ULPGC).
- Fuente primaria: [notas de corte de acceso ULPGC](https://sie.ulpgc.es/notascorte).
- Extracto: primera asignación, cupo general, curso 2025–2026; 51 filas con nota publicada de 57 filas mostradas.
- Se mantienen las ramas publicadas por cada bloque de la tabla y el campus/isla cuando figura en el título. La cobertura de Canarias incluye ya las dos universidades públicas; la tabla ULL se conserva como transcripción auditada porque el PDF no tiene capa estructurada.

### Universidad de La Laguna

- Fuente primaria: [notas de corte ULL](https://www.ull.es/admision-becas/pau/notas-de-corte/).
- Extracto: 18 filas del cupo general, fecha de corte 30/09/2025; PDF original y transcripción auditable en `data/raw/admissions/canarias/2025-2026/`.

## Notas de corte — País Vasco

- Organismo: Euskal Herriko Unibertsitatea / Universidad del País Vasco (EHU/UPV).
- Fuente oficial: https://www.ehu.eus/es/web/graduak/preinscripcion-y-admision/notas-de-corte
- Publicación de referencia: “Notas de admisión para el curso 2025-2026”.
- Estado: el PDF original se conserva en `data/raw/admissions/pais-vasco/2025-2026/ehu-notas-2025-2026.pdf`, pero es un escaneado sin capa de texto; los extractores estructurados no devuelven filas y no se incorpora al catálogo hasta disponer de OCR revisado o una fuente tabular equivalente.

## Inserción laboral — límite de granularidad

- La tabla oficial de base media de cotización del SIIU está publicada por tipo/modalidad de universidad, campo de estudio, sexo, años desde el egreso e indicador; no ofrece en este corte un código de titulación individual para cruzarlo de forma segura con cada oferta: https://estadisticas.universidades.gob.es/jaxiPx/Tabla.htm?L=0&file=Base_cotizacion_Sexo_Campo_Grado_Total.px&path=%2FUniversitaria%2FInsercion_laboral%2F2024%2FGRADO%2FCAP6_BMC%2F%2Fl0%2F&type=pcaxis
- Por eso la interfaz muestra afiliación y base de cotización como referencia del campo cuando existe, y mantiene salario medio/mediano y resultados específicos de carrera como `No disponible` hasta disponer de una dimensión compatible.

## Notas de corte — Navarra

- Organismo: Universidad Pública de Navarra.
- Fuente primaria: [UPNA, notas de corte y simulador](https://www.unavarra.es/sites/estudios/acceso-y-admision/admision-en-estudios-de-grado/notas-de-corte-y-simulador.html).
- Extracto: PDF oficial de la sexta lista de admitidos del 10 de septiembre de 2025, 41 ofertas, cupo general.
- El asterisco de la fuente se conserva como `extraordinary`; el resto de filas se guarda como `last_call`. La publicación no ofrece rama ni centro, por lo que esos campos quedan ausentes.

## Notas de corte — Asturias

- Organismo: Universidad de Oviedo.
- Fuente primaria alojada en el dominio institucional: [notas de acceso de julio de 2025](https://torres.epv.uniovi.es/centon/notas-acceso-oviedo-25.html).
- Extracto: primera fase de julio del curso 2025–2026, 68 ofertas, cupo general y plazas publicadas.
- La tabla no ofrece rama ni centro normalizados; esos campos quedan ausentes y el campus se conserva como Oviedo salvo la sede indicada en el nombre.

## Notas de corte — Illes Balears

- Organismo: Universitat de les Illes Balears.
- Fuente primaria: [UIB, notas de corte](https://estudis.uib.es/estudis-de-grau/com-hi-pots-accedir/admissio/notes-de-tall).
- Extracto: páginas oficiales por titulación, vía PAU y Ciclos Formativos, con procesos `JUN` y `EXT` del curso 2025–2026.
- Se conservan 296 observaciones, grupo publicado, posición de lista de espera, proceso y fecha. La fuente no publica rama RUCT ni centro normalizados en esta tabla.

## SIIU / estadísticas universitarias

- Organismo: Ministerio competente en universidades.
- Rendimiento/éxito/evaluación: https://estadisticas.universidades.gob.es/jaxiPx/Datos.htm?file=Rendimiento_Exito_Eval_Grado_Univ.px&path=%2FUniversitaria%2FIndicadores%2F2024%2F1_Grado%2Fl0%2F
- Abandono de estudios: https://estadisticas.universidades.gob.es/jaxiPx/Datos.htm?file=Abandono_Grado_Univ.px&path=%2FUniversitaria%2FIndicadores%2F2023%2F1_Grado%2Fl0%2F
- Graduación: https://estadisticas.universidades.gob.es/jaxiPx/Datos.htm?file=Graduacion_Grado_Univ.px&path=%2FUniversitaria%2FIndicadores%2F2023%2F1_Grado%2Fl0%2F
- Inserción laboral/base de cotización: https://estadisticas.universidades.gob.es/jaxiPx/Tabla.htm?L=0&file=Base_cotizacion_Sexo_Campo_Grado_Total.px&path=%2FUniversitaria%2FInsercion_laboral%2F2024%2FGRADO%2FCAP6_BMC%2F%2Fl0%2F&type=pcaxis
- Definiciones aplicadas: rendimiento = créditos superados / matriculados; abandono y graduación se interpretan por cohorte y duración publicadas por SIIU.
- Auditoría de granularidad: las tablas SIIU de rendimiento y abandono consultadas tienen dimensiones de universidad, ámbito de estudio, sexo, indicador y periodo; no publican un código RUCT de titulación en este corte. Por eso el Atlas muestra estos valores como contexto institucional o de campo y no los atribuye a una oferta individual. Referencias: [rendimiento por universidad y ámbito](https://estadisticas.universidades.gob.es/jaxiPx/Datos.htm?file=Rendimiento_Exito_Eval_Grado_Univ.px&path=%2FUniversitaria%2FIndicadores%2F2024%2F1_Grado%2Fl0%2F) y [abandono por universidad y ámbito](https://estadisticas.universidades.gob.es/jaxiPx/Datos.htm?file=Abandono_Grado_Univ.px&path=%2FUniversitaria%2FIndicadores%2F2023%2F1_Grado%2Fl0%2F).
- Limitación: una base media de cotización es un indicador administrativo de afiliación, no un salario medio ni mediano. Se requiere cargar el cruce por ámbito de estudio antes de atribuirlo a una carrera concreta.
- Estado: la interfaz muestra contexto universitario con etiqueta de cobertura y deja como no disponible lo que aún no está cargado a nivel de titulación. La primera referencia de ámbito para Informática (cohorte 2017–2018, cuatro años después) se conserva en `src/data/outcomes.js` y se usa para filtrar/ordenar sin presentarla como salario de una oferta. La tarjeta enlaza la referencia publicada por Fundación CYD y el registro SIIU.
- Cobertura laboral actual: el extracto `data/processed/outcomes/field-employment-2018-2019-four-years.json` añade Informática, ADE, Economía, Derecho, Medicina, Enfermería, Sociología y Periodismo para la cohorte 2018–2019, cuatro años después (2023). Se muestra como contexto de campo de estudio y permite ordenar por base media de cotización cuando existe.
- La base media de cotización no es salario medio, mediano ni neto; el nombre y la limitación se mantienen visibles en cada ficha. No se infieren valores de 1, 2 o 3 años para un campo cuando el extracto integrado no los publica de forma comparable.
- La ficha incluye además la serie nacional agregada a 1, 2, 3 y 4 años en `data/processed/outcomes/employment-national-series-2018-2019.json`. Sirve para leer la progresión general de la cohorte, no para atribuir esa evolución a la carrera o universidad seleccionada.
- La cobertura temporal se audita en `data/processed/outcomes/employment-coverage.json`: el último dato oficial publicado es la cohorte 2019–2020 (análisis hasta 2024, publicación del 13/03/2026), mientras que el extracto reproducible integrado en la interfaz corresponde a 2018–2019 (análisis 2023). Esta diferencia queda separada para no presentar el extracto anterior como si fuera la última actualización.
- La estadística oficial mide afiliación y bases de cotización de personas afiliadas a la Seguridad Social; la base media de cotización es una aproximación administrativa a la retribución bruta anual bajo unas condiciones concretas, no un salario medio, mediano o neto. La metodología oficial documenta también que la afiliación se observa en marzo y sigue la cohorte hasta cuatro años después.
- Las dobles titulaciones, combinaciones e internacionales no heredan el dato de un campo individual aunque su nombre contenga “Derecho”, “Economía” o “Informática”; se dejan sin cruce laboral para evitar una atribución engañosa.
- El contexto académico de Madrid se conserva además como extracto procesado en `data/processed/outcomes/madrid-university-context-2022-2023.json`, incluyendo curso, granularidad, fuente y limitación.
- Ese extracto incorpora la nota media de admisión del alumnado de nuevo ingreso por universidad (2022–2023), procedente de la tabla SIIU de nota media por rama; se presenta solo como contexto universitario y no como nota del expediente o de una carrera.
- También incorpora el número de estudiantes de nuevo ingreso por universidad (2022–2023), ambos sexos y todos los campos de estudio; es un contexto de tamaño institucional, no de una oferta individual.
- La ficha enlaza ambas tablas SIIU desde la propia tarjeta: nota media de admisión (`3_6_NI_Nota_media_Sex_Rama_Univ.px`) y nuevo ingreso (`3_4_Mat_Sex_Nac_Amb_Univ.px`). Mantener ambos conceptos separados evita confundir una media institucional con una nota de corte o con el expediente del estudiante.
- Matriculados en grado presencial: conjunto de datos abiertos de la Comunidad de Madrid, curso 2023–2024 (el CSV etiqueta el curso por su año final). El extracto procesado está en `data/processed/outcomes/madrid-university-enrolment-2023-2024.json` y se reconstruye con `etl/outcomes/ingest_madrid_enrolment.py`. Es un total de universidad, no de titulación, y excluye grados no presenciales.
- Egresados en grado presencial: conjunto de datos abiertos de la Comunidad de Madrid, curso 2023–2024 (el CSV etiqueta el curso por su año final). El extracto procesado está en `data/processed/outcomes/madrid-university-graduates-2023-2024.json` y se reconstruye con `etl/outcomes/ingest_madrid_graduates.py`. Es un recuento institucional, no una tasa de graduación ni un resultado de una titulación.
- Internacionalización: `data/processed/outcomes/madrid-international-2022-2023.json` conserva los estudiantes internacionales entrantes de las seis universidades públicas madrileñas en 2022–2023. Incluye grado, máster y doctorado, por lo que se muestra solo como contexto institucional; no equivale a movilidad saliente, Erasmus ni a una oportunidad de una carrera concreta. Fuente: `Entrada_Univ.px` del SIIU.
- Movilidad saliente: `data/processed/outcomes/madrid-mobility-outgoing-2021-2022.json` conserva el total de estudiantes de las seis universidades que salen mediante programas de movilidad en 2021–2022. Es un recuento institucional de movilidad, no una tasa de participación, una plaza Erasmus disponible ni un resultado de una carrera.
- Ratio de movilidad: `data/processed/outcomes/madrid-mobility-ratio-2021-2022.json` conserva el cociente SIIU entre entrantes y salientes por programas de movilidad para cada universidad. Un valor superior a 1 indica más entrantes que salientes en esa definición y curso; no es una valoración de calidad ni una probabilidad individual.

## Geografía

- Fuente prevista: códigos oficiales de comunidades autónomas, provincias y municipios del INE/administración pública.
- Uso: normalizar municipio, provincia y CCAA; coordenadas se conservarán separadas de los nombres.
- Estado: coordenadas de mapa MVP son una representación de interfaz; deben reemplazarse por geometrías/códigos oficiales en la siguiente iteración.
