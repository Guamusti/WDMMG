# Admisión nacional

`data/sources/admissions-spain.json` es el inventario de cobertura por
comunidad. `verified` significa que se ha localizado una publicación oficial
con formato y rondas identificables; `pending` no se carga en la aplicación.

Los ingestors deben pasar sus filas por `normalize_record` y conservar los
campos específicos de la fuente junto a `academic_year`, `admission_round`,
`admission_group` y `cutoff_score`. Una nota de corte sin ronda o grupo no se
mezcla con otra comparable.
