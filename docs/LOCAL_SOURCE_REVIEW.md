# Revisión de fuente de entidades locales

Fecha de comprobación: 27/08/2026.

## Fuente localizada

CONPREL, del Ministerio de Hacienda, publica los datos de avance de los presupuestos de 2026 por entidad local en un fichero comprimido con una base de datos Access:

`https://serviciostelematicosext.hacienda.gob.es/SGFAL/CONPREL/Consulta/DescargaFichero?CCAA=&TipoDato=Presupuestos&Ejercicio=2026&TipoPublicacion=Access`

La página oficial describe este recurso como “Datos por Entidad Local. Máximo nivel de desglose (ACCESS)” y lo marca como actualizado el 30/07/2026.

## Muestra descargada

- Fichero: `Presupuestos2026.accdb` dentro del ZIP.
- Tamaño del ZIP descargado: 23.361.446 bytes.
- SHA-256 del ZIP: `0011b1f08d96150bcbd25c7c71c4043eec19b6dab5fe814d7aadc8002303272a`.
- Estado: fuente oficial localizada y descarga reproducible; **datos aún no cargados**.

## Decisión de ingesta

La aplicación no presenta cifras locales hasta identificar las tablas, claves de entidad, comunidad autónoma, municipio, ejercicio, tipo de dato y unidad monetaria. El parser debe conservar el identificador original, diferenciar presupuesto de liquidación y registrar el hash de la descarga. La base Access se mantiene fuera de Git por tamaño; el hash y la URL permiten reproducirla.

Fuente de consulta: [CONPREL — Presupuestos y Liquidaciones de Entidades Locales](https://serviciostelematicosext.hacienda.gob.es/SGFAL/CONPREL?acc=null&cd_camp=null).
