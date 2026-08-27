# Fuentes oficiales — investigación inicial

Fecha de comprobación: 27/08/2026. Las rutas y frecuencias deben volver a validarse antes de cada ingesta. Este documento distingue disponibilidad publicada de datos efectivamente importados en el MVP.

## Resumen operativo

| Fuente | URL oficial | Formato / método | Cobertura y frecuencia | Estado MVP |
|---|---|---|---|---|
| Central de Información Económico-Financiera | [Hacienda](https://www.hacienda.gob.es/es-ES/CDI/Paginas/centraldeinformacion.aspx) | Portal de catálogo y enlaces a bases, informes y descargas | AGE, Seguridad Social, CCAA y entidades locales; anual, mensual, trimestral según conjunto | Documentada |
| Ejecución AGE | [IGAE: extracto](https://www.igae.pap.hacienda.gob.es/sitios/igae/es-ES/Contabilidad/ContabilidadPublica/CPE/EjecucionPresupuestaria/Paginas/imextractoejecucion.aspx) / [operaciones](https://www.igae.pap.hacienda.gob.es/sitios/igae/es-ES/Contabilidad/ContabilidadPublica/CPE/EjecucionPresupuestaria/paginas/imoperacionesejecucion.aspx) | XLS para cuadros y PDF para publicación | Ejecución de ingresos, modificaciones y gastos; mensual; histórico desde 2001/2003 según publicación | Pendiente parser XLS |
| Presupuestos CCAA | [Central de Información](https://www.hacienda.gob.es/es-ES/CDI/Paginas/centraldeinformacion.aspx) | Bases de datos e informes enlazados desde Hacienda | Proyectos, presupuestos, ejecución y liquidación; periodicidad variable | Pendiente |
| Presupuestos y ejecución local | [Entidades locales](https://www.hacienda.gob.es/es-ES/CDI/Paginas/centraldeinformacion.aspx) | Base de datos / descargas del portal de Hacienda | Presupuestos, ejecución trimestral, liquidación, deuda y coste efectivo; periodicidad variable | Pendiente |
| Contratación PLACSP | [OpenPLACSP (manual)](https://contrataciondelestado.es/datosabiertos/DGPE_PLACSP_OpenPLACSP_v.2.2.pdf) | ZIP de feeds ATOM/XML; CODICE y extensiones; descarga incremental por sindicaciones | Licitaciones y actualizaciones cronológicas; OpenPLACSP | Pendiente ingestor |
| BDNS / SNPSAP | [Documentación técnica BDNS20](https://www.oficinavirtual.pap.hacienda.gob.es/sitios/oficinavirtual/en-GB/CatalogoSistemasInformacion/TESEOnet/Paginas/Documentaci%C3%B3n.aspx) | Servicios web XML/WSDL/XSD y cargas masivas; requiere revisar acceso de producción | Convocatorias, concesiones, pagos, reintegros, planes; actualización continua | Pendiente cliente |
| INE | [API JSON](https://www.ine.es/dyngs/DAB/index.htm?cid=1099) / [población municipal](https://www.ine.es/dyngs/INEbase/operacion.htm?c=Estadistica_C&cid=1254736177011&idp=1254734710990&menu=resultados) | API JSON y ficheros Excel | Población oficial municipal a 1 de enero; series desde 1996 | Pendiente |
| Inventario de entidades públicas | [Inventario / Central Hacienda](https://www.hacienda.gob.es/es-ES/CDI/Paginas/centraldeinformacion.aspx) | Descarga enlazada desde el portal oficial; validar formato vigente | Sector público institucional estatal y catálogos relacionados | Pendiente |

## Campos que se esperan normalizar

### Hacienda / IGAE

Las publicaciones de ejecución AGE permiten trabajar con ejercicio, periodo, clasificación orgánica/económica/funcional y estados de crédito y ejecución. El ingestor debe conservar los códigos originales y distinguir: crédito inicial, modificaciones, crédito definitivo, autorizado, comprometido, obligaciones reconocidas y pagos. Los XLS son el formato estructurado prioritario; el PDF queda como control visual y último recurso.

### PLACSP

El manual OpenPLACSP describe entradas ATOM/XML cronológicas dentro de ZIP y una referencia al siguiente archivo. El parser debe procesar los ZIP en orden temporal, registrar la URL/identificador del feed y convertir separadamente licitación, lote, adjudicación y eventos. No debe tratar cada actualización como un nuevo contrato.

Campos MVP: expediente, título, órgano contratante, tipo/procedimiento/estado, CPV, importes (valor estimado, presupuesto base, adjudicación), fechas, lotes, adjudicatario, número de ofertas, ubicación, financiación UE y URL oficial.

### BDNS

La documentación oficial lista servicios BDNS20 para consultas de convocatorias, concesiones/pagos/proyectos, reintegros y planes estratégicos, además de WSDL/XSD y cargas masivas. Antes de activar producción hay que verificar autenticación, límites y endpoints publicados. Convocatoria y concesión serán entidades distintas.

## Limitaciones conocidas

- El portal de Hacienda agrupa familias de datos con formatos y periodicidades diferentes; no se debe asumir una API común.
- La ejecución mensual puede ser provisional/avance y las cifras pueden cambiar; se conserva cada versión.
- PLACSP contiene actualizaciones de publicaciones: deduplicación por identificadores y versionado de eventos son obligatorios.
- BDNS puede restringir datos personales; no se intentará completar identificadores ausentes por similitud textual.
- Una adjudicación no equivale automáticamente a obligación reconocida o pago presupuestario.

## Criterio de ingesta

`descargar → guardar raw → parsear → validar → normalizar → upsert → registrar run`. Cada fila financiera conservará `source_id`, `source_record_id`, `source_url`, `retrieved_at`, `dataset_version` e `ingestion_run_id`.
