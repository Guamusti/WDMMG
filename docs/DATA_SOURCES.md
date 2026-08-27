# Fuentes de datos

## Registro de Universidades, Centros y Títulos (RUCT)

- Organismo: Ministerio de Ciencia, Innovación y Universidades.
- URL: https://www.ciencia.gob.es/Universidades/RUCT.html
- Uso previsto: registro maestro de universidades, centros, títulos oficiales, códigos y estado.
- Granularidad: universidad, centro y título.
- Limitación: la consulta pública no sustituye a un export histórico; el ingestor debe conservar la evidencia de cada consulta.
- Estado: arquitectura preparada; ingestor pendiente.

## Notas de corte — Comunidad de Madrid

- Organismo: Comunidad de Madrid, Centro de Información y Asesoramiento Universitario.
- Fuente editorial: https://www.comunidad.madrid/educacion/publicaciones-interes-universitario
- Publicación de referencia: “Notas de acceso de las titulaciones universitarias oficiales de la Comunidad de Madrid. Curso 2025-2026”.
- Formato observado: PDF/HTML publicado por la Comunidad; contiene código, titulación, grupos de acceso y columnas ordinaria/extraordinaria.
- Estado: muestra integrada en la interfaz; ingestor PDF/HTML pendiente.

## Notas institucionales complementarias

- UC3M: https://www.uc3m.es/ss/Satellite/UC3MInstitucional/es/TextoMixta/1371206740815/Notas_de_corte
- URJC: publicación institucional de notas 2025/2026 enlazada desde sus páginas de admisión.
- Uso: validar campus y ofertas específicas cuando la publicación regional no expone el contexto con suficiente detalle.

## SIIU / estadísticas universitarias

- Organismo: Ministerio competente en universidades.
- Uso previsto: matrícula, nuevo ingreso, egresados, rendimiento, abandono, movilidad e inserción laboral.
- Estado: no se muestran cifras en el MVP hasta fijar dataset, definición, granularidad y cobertura temporal.

## Geografía

- Fuente prevista: códigos oficiales de comunidades autónomas, provincias y municipios del INE/administración pública.
- Uso: normalizar municipio, provincia y CCAA; coordenadas se conservarán separadas de los nombres.
- Estado: coordenadas de mapa MVP son una representación de interfaz; deben reemplazarse por geometrías/códigos oficiales en la siguiente iteración.
