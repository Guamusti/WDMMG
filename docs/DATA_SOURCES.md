# Fuentes oficiales — investigación inicial

Fecha de comprobación: 27/08/2026. Las rutas y frecuencias deben volver a validarse antes de cada ingesta. Este documento distingue disponibilidad publicada de datos efectivamente importados en el MVP.

## Resumen operativo

| Fuente | URL oficial | Formato / método | Cobertura y frecuencia | Estado MVP |
|---|---|---|---|---|
| Central de Información Económico-Financiera | [Hacienda](https://www.hacienda.gob.es/es-ES/CDI/Paginas/centraldeinformacion.aspx) | Portal de catálogo y enlaces a bases, informes y descargas | AGE, Seguridad Social, CCAA y entidades locales; anual, mensual, trimestral según conjunto | Documentada |
| Ejecución AGE | [IGAE: extracto](https://www.igae.pap.hacienda.gob.es/sitios/igae/es-ES/Contabilidad/ContabilidadPublica/CPE/EjecucionPresupuestaria/Paginas/imextractoejecucion.aspx) / [operaciones](https://www.igae.pap.hacienda.gob.es/sitios/igae/es-ES/Contabilidad/ContabilidadPublica/CPE/EjecucionPresupuestaria/paginas/imoperacionesejecucion.aspx) | XLS para cuadros y PDF para publicación | Ejecución de ingresos, modificaciones y gastos; mensual; histórico desde 2001/2003 según publicación | Parser y carga AGE activos; muestra mayo 2026 |
| Clasificación funcional del gasto | [IGAE: Cuenta General del Estado 2024](https://www.igae.pap.hacienda.gob.es/sitios/igae/es-ES/Contabilidad/ContabilidadPublica/CPE/EjecucionPresupuestaria/Documents/C.G.E.%202024.pdf) | PDF, tabla de gasto realizado por política | Gasto consolidado del Estado por finalidad; anual; incluye Pensiones, Sanidad, Educación e Infraestructuras | Usada en la portada, fechada 2024 |
| Presupuestos CCAA | [Central de Información](https://www.hacienda.gob.es/es-ES/CDI/Paginas/centraldeinformacion.aspx) / [CIMCANET](https://serviciostelematicosext.hacienda.gob.es/SGCIEF/Cimcanet/aspx/consulta/consulta.aspx) | XLS de ejecución mensual y bases de datos | Proyectos, presupuestos, ejecución y liquidación; periodicidad variable | Muestra de ejecución mayo 2026 normalizada; cobertura completa pendiente |
| Presupuestos y ejecución local | [Entidades locales](https://www.hacienda.gob.es/es-ES/CDI/Paginas/centraldeinformacion.aspx) | Base de datos / descargas del portal de Hacienda | Presupuestos, ejecución trimestral, liquidación, deuda y coste efectivo; periodicidad variable | Pendiente |
| Contratación PLACSP | [Datos abiertos](https://contrataciondelestado.es/wps/portal/DatosAbiertos) · [OpenPLACSP (manual)](https://contrataciondelestado.es/datosabiertos/DGPE_PLACSP_OpenPLACSP_v.2.2.pdf) | ZIP de feeds ATOM/XML; CODICE y extensiones; descarga incremental por sindicaciones | Licitaciones y actualizaciones cronológicas; excluye menores en algunos conjuntos; feeds paginados | Parser, carga incremental y filtros activos; muestra publicada |
| BDNS / SNPSAP | [Portal SNPSAP](https://www.infosubvenciones.es/bdnstrans/es/index) · [API base v2.1](https://www.infosubvenciones.es/bdnstrans/GE/es/api/v2.1) · [Documentación BDNS20](https://www.oficinavirtual.pap.hacienda.gob.es/sitios/oficinavirtual/en-GB/CatalogoSistemasInformacion/TESEOnet/Paginas/Documentaci%C3%B3n.aspx) | Servicios web XML/WSDL/XSD y exportaciones JSON/XML/CSV/XLSX del portal | Convocatorias, concesiones, pagos, reintegros, planes; actualización continua | API oficial de convocatorias y concesiones activa; carga local parcial |
| INE / IGN | [API JSON INE](https://www.ine.es/dyngs/DAB/index.htm?cid=1099) / [población municipal](https://www.ine.es/dyngs/INEbase/operacion.htm?c=Estadistica_C&cid=1254736177011&idp=1254734710990&menu=resultados) / [WFS de unidades administrativas](https://www.ign.es/wfs-inspire/unidades-administrativas?request=GetCapabilities&service=WFS) / [OGC API IGN](https://api-features.ign.es/collections/administrativeboundary?f=json) | API JSON, ficheros Excel, WFS y OGC API Features | Población oficial municipal a 1 de enero; códigos y geometrías CCAA, provincias y municipios | Población municipal 2024 consultable en vivo; mapa CCAA servido desde snapshot simplificado IGN; provincias/municipios pendientes; gasto por habitante pendiente |
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

## Snapshot geográfico publicado

El mapa de comunidades usa una derivación simplificada del servicio OGC del IGN para no descargar geometrías pesadas en cada visita. La fuente de origen y el recurso publicado quedan identificados así:

| Recurso | Captura | SHA-256 | Licencia/fuente |
|---|---|---|---|
| `data/processed/geo/community-boundaries.json` | 27/08/2026 | `CA026C4C9422FC21AFA41E22F5280ADDEECE71F9E4A2E72C0F97F6A89893BA0B` | [API OGC IGN](https://api-features.ign.es/collections/administrativeboundary?f=json); consultar condiciones del servicio |

La simplificación solo afecta a la visualización. Este recurso no se utiliza para calcular población, gasto ni superficies.
