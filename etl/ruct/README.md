# RUCT

`python etl/ruct/download_ruct.py` conserva los códigos oficiales de las seis
universidades públicas madrileñas.

`python etl/ruct/match_madrid_degrees.py` consulta el RUCT oficial para sus
títulos de Grado activos, conserva las respuestas en
`data/raw/ruct/madrid-degrees/` y genera coincidencias en
`data/processed/ruct/madrid-degree-matches.json`.

Solo se acepta una coincidencia exacta tras normalización y única dentro de
la universidad. La normalización incluye un conjunto pequeño y documentado de
equivalencias lingüísticas (género, preposición y la errata
`mineralúrgia/mineralúrgica`) auditadas contra los títulos descargados. Las
ofertas sin coincidencia o con coincidencia ambigua se mantienen como
`pending`; no se asignan códigos por similitud. Para las coincidencias
aceptadas también se conservan la ficha de detalle, los centros RUCT, la rama,
el campo de estudio y los créditos publicados.

Cada oferta también conserva `program_type` (`degree`, `double_degree`,
`special_program`, `international_program` o `alliance_program`) y, solo para
dobles grados estructurales, `component_names`. Los guiones de idioma dentro de
paréntesis se excluyen de la separación. En la extracción actual hay 374 grados
simples, 60 dobles, 21 programas especiales, 2 internacionales y 1 de alianza.
Esta clasificación describe la oferta de admisión; no inventa un código RUCT
para el programa conjunto cuando el registro oficial no lo publica de forma
unívoca.

Cada pendiente conserva `pending_reason` y el informe de calidad las agrupa por
motivo: doble grado sin título único, programa especial/internacional/alianza
sin código unívoco, título ambiguo o ausencia de coincidencia exacta tras
normalización.
