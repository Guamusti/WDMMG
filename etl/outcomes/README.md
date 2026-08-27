# Inserción laboral

`data/processed/outcomes/informatica-2017-2018.json` conserva una referencia
laboral agregada para el ámbito de Informática. La fuente publicada combina
indicadores del SIIU y la Fundación CYD; por eso la aplicación muestra la
granularidad, cohorte y limitación junto a cada valor.

La `base de cotización` no es salario medio, salario mediano ni salario neto.
Hasta disponer de un cruce verificable por titulación y cohorte, estos datos no
se atribuyen a una carrera concreta: sirven para comparar el ámbito de estudio.

## Matriculados en Madrid

`ingest_madrid_enrolment.py` descarga el CSV oficial de la Comunidad de Madrid y
reconstruye `data/processed/outcomes/madrid-university-enrolment-2023-2024.json`.
El dato representa el total de estudiantes matriculados en grados presenciales
por universidad; el año 2024 de la fuente corresponde al curso 2023-2024.

## Egresados en Madrid

`ingest_madrid_graduates.py` descarga el CSV oficial de egresados y reconstruye
`data/processed/outcomes/madrid-university-graduates-2023-2024.json`.
Es un recuento institucional de grados presenciales: no debe leerse como tasa
de graduación ni como resultado de una titulación concreta.

## Inserción laboral por campo

`data/processed/outcomes/field-employment-2018-2019-four-years.json` conserva
referencias de ocho campos de estudio para la cohorte 2018-2019, cuatro años
después. La aplicación puede ordenar por base media de cotización, siempre
mostrándola como indicador administrativo agregado y no como salario de una
oferta concreta.

La serie `employment-national-series-2018-2019.json` conserva los indicadores
nacionales comparables a 1, 2, 3 y 4 años. Se presenta como contexto general y
no sustituye al dato del campo de estudio.

La diferencia entre la última publicación oficial y el extracto local se conserva
en `data/processed/outcomes/employment-coverage.json`. No se actualizan cifras
por inferencia: hasta cargar y validar la nueva tabla, la interfaz mantiene la
cohorte reproducible anterior y lo indica como contexto.
