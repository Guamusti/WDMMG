# Modelo de datos inicial

El modelo separa conceptos y evita usar nombres como identificadores.

```text
universities(id, official_code, name, type, ownership)
campuses(id, official_code, university_id, name, municipality_id)
centers(id, official_code, university_id, campus_id, name, affiliated)
degrees(id, official_code, name, normalized_name, level, branch, field, ects)
degree_offerings(id, degree_id, university_id, center_id, campus_id, academic_year, modality, language)
admission_cutoffs(id, degree_offering_id, academic_year, round, admission_group, cutoff_score, scale_max)
data_sources(id, name, institution, url, format, granularity, coverage, limitations)
provenance(record_id, source_id, source_record_id, source_url, retrieved_at, ingestion_run_id)
```

Una oferta concreta es la unidad de comparación. Un grado conceptual puede tener muchas ofertas. Las dobles titulaciones se conservan como grados/ofertas propias y podrán enlazarse con `degree_components`.

En la capa de provenance RUCT, `program_type` clasifica la oferta de admisión y
`component_names` conserva los componentes textuales únicamente cuando el
separador es estructural. Esto permite distinguir un doble grado de una
aclaración de idioma, una mención, un PARS o un programa internacional sin
fusionarlos con un grado simple. El código RUCT solo se asigna cuando existe
una coincidencia exacta normalizada y única; la clasificación no sustituye ese
matching.
