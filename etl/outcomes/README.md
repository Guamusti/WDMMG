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
