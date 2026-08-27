# Muestras oficiales reproducibles

Registro de las muestras raw usadas para validar el MVP. Las descargas grandes permanecen fuera del repositorio (`data/raw/` está ignorado); se comprueba su identidad mediante tamaño y SHA-256 antes de reprocesarlas.

| Dataset | Fichero local | Fecha | Bytes | SHA-256 | Fuente / licencia |
|---|---|---:|---:|---|---|
| PLACSP sindicacion 643 | `data/raw/placsp/placsp-20260827T170013Z.atom` | 2026-08-27 | 12.910.585 | `20789C8B349B6F40DC166F748838FEC2659B3523EE8445BC49ACA75391323DA0` | [Portal de datos abiertos PLACSP](https://contrataciondelestado.es/wps/portal/DatosAbiertos); condiciones del portal |
| BDNS convocatoria 925963 | `data/raw/bdns/convocatoria-925963.json` | 2026-08-27 | 2.668 | `86FDA8D7B1EEADB83F8990EC7EBC4D74FAFFBC0E03E3B01B2EDAAC51DC32BCF8` | [SNPSAP / BDNS](https://www.infosubvenciones.es/bdnstrans/es/index); condiciones del servicio |
| IGAE ejecución AGE mayo 2026 | `data/raw/igae/igae-20260827T151648Z.xlsx` | 2026-08-27 | 57.027 | `40D81AAF53B6A3413CDBD846B52D1B24F6650289F9CF3406608194A6190DFB77` | [IGAE](https://www.igae.pap.hacienda.gob.es/); fuente oficial |
| CCAA ejecución mayo 2026 | `data/raw/ccaa/ccaa-execution-2026-05.xlsx` | 2026-08-27 | 89.301 | `DAC2A9AD5E7EE58ED09ABD661FF9FE8EECE0D8F09E69DC863EA73106179C1D11` | [CIMCANET](https://serviciostelematicosext.hacienda.gob.es/SGCIEF/Cimcanet/aspx/consulta/consulta.aspx); fuente oficial |

Las fixtures pequeñas de parser en `tests/` son estructurales y sintéticas; no sustituyen estas muestras de producción. El raw conserva la respuesta original y el pipeline conserva `retrieved_at`, `ingestion_run_id` y el hash por registro.
