# RUCT

`python etl/ruct/download_ruct.py` conserva los códigos oficiales de las seis
universidades públicas madrileñas.

`python etl/ruct/match_madrid_degrees.py` consulta el RUCT oficial para sus
títulos de Grado activos, conserva las respuestas en
`data/raw/ruct/madrid-degrees/` y genera coincidencias en
`data/processed/ruct/madrid-degree-matches.json`.

Solo se acepta una coincidencia exacta tras normalización y única dentro de
la universidad. Las ofertas sin coincidencia o con coincidencia ambigua se
mantienen como `pending`; no se asignan códigos por similitud. Para las
coincidencias aceptadas también se conservan la ficha de detalle, los centros
RUCT, la rama, el campo de estudio y los créditos publicados.
