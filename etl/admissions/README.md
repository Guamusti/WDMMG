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

## Catálogo nacional de trabajo

`python etl/admissions/build_national_catalog.py` reúne los extractos
procesados de Madrid, Galicia, Aragón, Cataluña y Andalucía en
`data/processed/admissions/`.
Conserva la procedencia regional y genera un informe de comparabilidad; no
rellena ramas, RUCT ni métricas que una fuente no publique.
