# Admisión nacional

`data/sources/admissions-spain.json` es el inventario de cobertura por
comunidad. `verified` significa que se ha localizado una publicación oficial
con formato y rondas identificables; `pending` no se carga en la aplicación.

Los ingestors deben pasar sus filas por `normalize_record` y conservar los
campos específicos de la fuente junto a `academic_year`, `admission_round`,
`admission_group` y `cutoff_score`. Una nota de corte sin ronda o grupo no se
mezcla con otra comparable.

## Galicia

`python etl/admissions/galicia/download_galicia.py` conserva la publicación
oficial del CIUG y `python etl/admissions/galicia/parse_galicia.py` genera el
extracto procesado de 2025-2026. El parser lee los bloques visuales del PDF
para no cruzar campus en páginas con dos columnas, conserva ronda y grupo de
acceso, y rechaza títulos con glifos no decodificables.

## Aragón

`python etl/admissions/aragon/download_aragon.py` conserva el PDF de la
adjudicación ordinaria de la Universidad de Zaragoza y
`python etl/admissions/aragon/parse_aragon.py` genera el extracto de
2025-2026. Se extrae la columna de cupo general, se conserva la provincia
como campus y se descartan filas sin nombre o nota válida.

## Andalucía

`python etl/admissions/andalucia/download_andalucia.py` conserva la respuesta
HTML de la consulta oficial de notas de corte del Distrito Único Andaluz y
`python etl/admissions/andalucia/parse_andalucia.py` genera el extracto de
2025-2026. Se carga exclusivamente la columna de acceso general (`Gral.`),
conserva rama, universidad y centro, y rechaza filas incompletas.

## Castilla y León

`python etl/admissions/castilla-leon/download_castilla_leon.py` conserva el
PDF oficial de notas de corte de la Universidad de León y
`python etl/admissions/castilla-leon/parse_castilla_leon.py` genera el
extracto de 2025-2026. La cobertura es parcial: se carga la nota general de
las ofertas publicadas por esa universidad y se mantienen las filas con
campus/centro identificables.

## Cantabria

`python etl/admissions/cantabria/download_cantabria.py` conserva el PDF
oficial de la Universidad de Cantabria y `python
etl/admissions/cantabria/parse_cantabria.py` genera el extracto de
2025-2026. Se carga la nota de julio del cupo general como `last_call`,
separada de una primera adjudicación, porque es la dimensión que publica la
fuente.

## Navarra

`python etl/admissions/navarra/download_navarra.py` conserva la sexta lista
oficial de admitidos de la UPNA del 10 de septiembre de 2025 y `python
etl/admissions/navarra/parse_navarra.py` genera el extracto de 2025-2026.
El parser conserva el cupo general, separa las marcas de convocatoria
extraordinaria y normaliza los títulos en castellano; la fuente no publica
rama ni centro para este listado y esos campos permanecen ausentes.

## Asturias

`python etl/admissions/asturias/download_asturias.py` conserva la tabla
publicada en el dominio institucional de la Universidad de Oviedo y `python
etl/admissions/asturias/parse_asturias.py` genera el extracto de 2025-2026.
Se cargan 68 ofertas de la primera fase de julio, con cupo general y plazas;
la tabla no publica rama ni centro normalizados.

## Illes Balears

`python etl/admissions/illes-balears/download_uib.py` conserva el índice y las
páginas oficiales por titulación de la UIB y `python
etl/admissions/illes-balears/parse_uib.py` genera el extracto de 2025-2026.
Se carga exclusivamente la vía PAU/CFGS y se conservan los procesos JUN/EXT,
grupo, lista de espera y fecha de publicación.

## Canarias · ULPGC

`data/raw/admissions/canarias/2025-2026/ulpgc-notas-corte-2025-2026.html`
conserva la página oficial de notas de corte de la Universidad de Las Palmas
de Gran Canaria y `python etl/admissions/canarias/parse_ulpgc.py` genera el
extracto `data/processed/admissions/canarias-ulpgc-2025-2026.json`. Se carga
la primera asignación del cupo general, se conservan las cinco ramas publicadas
y se excluyen solo las filas sin nota general (`--`), manteniendo el alcance
parcial: la Universidad de La Laguna aún no está integrada.

## La Rioja

`python etl/admissions/la-rioja/download_unirioja.py` conserva el libro XLSX
oficial de transparencia de la Universidad de La Rioja y `python
etl/admissions/la-rioja/parse_unirioja.py` genera el extracto de 2025-2026.
Se carga la nota inicial de la convocatoria ordinaria del cupo general, se
mantienen rama y campus, y se rechazan las titulaciones marcadas como `SNC`
(sin nota de corte).

## País Vasco · EHU

`python etl/admissions/pais-vasco/parse_ehu.py` genera el extracto de 2025-2026
desde la transcripción JSON revisada visualmente del PDF oficial. La cobertura
actual es explícita: Campus de Álava, Gipuzkoa y Bizkaia, cupo general, 97
ofertas; las filas sin nota general se conservan como rechazos.

## Catálogo nacional de trabajo

`build_national_catalog.py` reúne los extractos procesados de Madrid, Galicia,
Aragón, Cataluña, Andalucía, Castilla y León, Cantabria, Navarra, Asturias,
Illes Balears, Canarias (ULPGC y ULL) y La Rioja en
`data/processed/admissions/`.
Conserva la procedencia regional y genera un informe de comparabilidad; no
rellena ramas, RUCT ni métricas que una fuente no publique.
