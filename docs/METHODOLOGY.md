# Metodología del MVP

## Alcance

El MVP utiliza un subconjunto real y trazable de ofertas públicas de la Comunidad de Madrid para el curso académico `2025-2026`. La nota mostrada es la nota ordinaria del grupo 1 cuando existe una cifra numérica.

## Nota de corte

La nota de corte es la del último estudiante admitido en un proceso y grupo determinados. No es la nota media de acceso. La publicación regional presenta distintos grupos y convocatorias; por consistencia, esta interfaz usa la columna ordinaria del grupo 1.

## Percentil

Para una oferta con nota `x`, se ordenan las `n` ofertas cargadas con escala 14 y nota válida. El percentil mostrado es:

`round(100 × (número de ofertas con nota <= x - 0,5) / n)`

Los empates ocupan la misma posición conceptual. El resultado expresa posición entre ofertas, no entre alumnos de Selectividad.

## Limitaciones

- El catálogo visible es una muestra de validación y no todo Madrid.
- Los campos de plazas solo aparecen cuando la fuente utilizada los documenta explícitamente.
- No se mezclan datos de universidades privadas sin una tabla oficial comparable.
- La nota orienta: no garantiza admisión en el futuro.
