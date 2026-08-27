# Fuentes de datos

## Registro de Universidades, Centros y Títulos (RUCT)

- Organismo: Ministerio de Ciencia, Innovación y Universidades.
- URL: https://www.ciencia.gob.es/Universidades/RUCT.html
- Uso previsto: registro maestro de universidades, centros, títulos oficiales, códigos y estado.
- Granularidad: universidad, centro y título.
- Limitación: la consulta pública no sustituye a un export histórico; el ingestor debe conservar la evidencia de cada consulta.
- Estado: arquitectura preparada; ingestor pendiente.
- Distribución estructurada auxiliar de códigos de universidad: https://datos.canarias.es/api/estadisticas/structural-resources/v1.0/codelists/ISTAC/CL_RUCT_UNIVERSIDADES/01.000/codes.csv?fields=+description
- Estado actual: códigos de las seis universidades públicas madrileñas enlazados y conservados en `data/processed/ruct/`; el CSV bruto y la URL se mantienen como evidencia. Los códigos de títulos/centros requieren consulta RUCT individual y no se infieren por nombre.

## Notas de corte — Comunidad de Madrid

- Organismo: Comunidad de Madrid, Centro de Información y Asesoramiento Universitario.
- Fuente editorial: https://www.comunidad.madrid/educacion/publicaciones-interes-universitario
- Publicación de referencia: “Notas de acceso de las titulaciones universitarias oficiales de la Comunidad de Madrid. Curso 2025-2026”.
- Formato observado: PDF/HTML publicado por la Comunidad; contiene código, titulación, grupos de acceso y columnas ordinaria/extraordinaria.
- Estado: PDF conservado en `data/raw/`, parser reproducible en `etl/admissions/madrid/` y muestra integrada en la interfaz. El matching contra RUCT sigue pendiente.

## Notas institucionales complementarias

- UC3M: https://www.uc3m.es/ss/Satellite/UC3MInstitucional/es/TextoMixta/1371206740815/Notas_de_corte
- URJC: publicación institucional de notas 2025/2026 enlazada desde sus páginas de admisión.
- Uso: validar campus y ofertas específicas cuando la publicación regional no expone el contexto con suficiente detalle.

## Notas de corte — Galicia

- Organismo: Comisión Interuniversitaria de Galicia (CIUG).
- Publicación de referencia: “Notas de corte 2025” para el curso 2025-2026.
- Fuente: https://ciug.gal/PDF/2025/ACCESO/notas_de_corte_2025.pdf
- Estado: PDF conservado en `data/raw/admissions/galicia/2025-2026/`; parser reproducible en `etl/admissions/galicia/` y extracto separado en `data/processed/admissions/galicia-2025-2026.json`.
- Cobertura validada: 194 titulaciones en seis campus y 333 observaciones con ronda ordinaria/extraordinaria. No se mezcla aún con el catálogo de Madrid hasta completar el modelo nacional común y el matching RUCT.

## Notas de corte — Aragón

- Organismo: Universidad de Zaragoza.
- Publicación de referencia: adjudicación ordinaria de julio de 2025 para el curso 2025-2026.
- Fuente: https://academico.unizar.es/sites/academico/files/archivos/acceso/admisgrado/corte/grados2526j.pdf
- Estado: PDF conservado en `data/raw/admissions/aragon/2025-2026/`; parser reproducible en `etl/admissions/aragon/` y extracto separado en `data/processed/admissions/aragon-2025-2026.json`.
- Cobertura validada: 73 ofertas de la Universidad de Zaragoza en cuatro provincias/campus. Se carga únicamente la columna de cupo general y la convocatoria ordinaria; las restantes columnas de cupos requieren su modelado explícito antes de comparar.

## Catálogo nacional de trabajo

- `data/processed/admissions/national-2025-2026.json` reúne 865 observaciones procesadas de tres comunidades: Madrid (459), Galicia (333) y Aragón (73).
- `national-2025-2026-quality.json` valida curso único, escala 0–14, ronda/grupo presentes y ausencia de duplicados de observación. La cobertura de rama es parcial (398/865), por lo que el catálogo no se presenta aún como ranking nacional.

## SIIU / estadísticas universitarias

- Organismo: Ministerio competente en universidades.
- Rendimiento/éxito/evaluación: https://estadisticas.universidades.gob.es/jaxiPx/Datos.htm?file=Rendimiento_Exito_Eval_Grado_Univ.px&path=%2FUniversitaria%2FIndicadores%2F2024%2F1_Grado%2Fl0%2F
- Abandono de estudios: https://estadisticas.universidades.gob.es/jaxiPx/Datos.htm?file=Abandono_Grado_Univ.px&path=%2FUniversitaria%2FIndicadores%2F2023%2F1_Grado%2Fl0%2F
- Graduación: https://estadisticas.universidades.gob.es/jaxiPx/Datos.htm?file=Graduacion_Grado_Univ.px&path=%2FUniversitaria%2FIndicadores%2F2023%2F1_Grado%2Fl0%2F
- Inserción laboral/base de cotización: https://estadisticas.universidades.gob.es/jaxiPx/Tabla.htm?L=0&file=Base_cotizacion_Sexo_Campo_Grado_Total.px&path=%2FUniversitaria%2FInsercion_laboral%2F2024%2FGRADO%2FCAP6_BMC%2F%2Fl0%2F&type=pcaxis
- Definiciones aplicadas: rendimiento = créditos superados / matriculados; abandono y graduación se interpretan por cohorte y duración publicadas por SIIU.
- Limitación: una base media de cotización es un indicador administrativo de afiliación, no un salario medio ni mediano. Se requiere cargar el cruce por ámbito de estudio antes de atribuirlo a una carrera concreta.
- Estado: la interfaz muestra contexto universitario con etiqueta de cobertura y deja como no disponible lo que aún no está cargado a nivel de titulación. La primera referencia de ámbito para Informática (cohorte 2017–2018, cuatro años después) se conserva en `src/data/outcomes.js` y se usa para filtrar/ordenar sin presentarla como salario de una oferta. La tarjeta enlaza la referencia publicada por Fundación CYD y el registro SIIU.
- El contexto académico de Madrid se conserva además como extracto procesado en `data/processed/outcomes/madrid-university-context-2022-2023.json`, incluyendo curso, granularidad, fuente y limitación.

## Geografía

- Fuente prevista: códigos oficiales de comunidades autónomas, provincias y municipios del INE/administración pública.
- Uso: normalizar municipio, provincia y CCAA; coordenadas se conservarán separadas de los nombres.
- Estado: coordenadas de mapa MVP son una representación de interfaz; deben reemplazarse por geometrías/códigos oficiales en la siguiente iteración.
