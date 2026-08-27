-- Atlas Universitario · esquema inicial PostgreSQL.
-- Las coordenadas se mantienen como lat/lon para poder ejecutar la migración
-- en PostgreSQL limpio; PostGIS puede añadirse después sin cambiar el modelo.
CREATE TABLE IF NOT EXISTS academic_years (
  id bigserial PRIMARY KEY, label varchar(9) NOT NULL UNIQUE, start_year smallint NOT NULL, end_year smallint NOT NULL,
  CHECK (end_year = start_year + 1)
);
CREATE TABLE IF NOT EXISTS geographies (
  id bigserial PRIMARY KEY, country_code varchar(2) NOT NULL DEFAULT 'ES', autonomous_community varchar(120), province varchar(120), municipality varchar(120), latitude numeric(8,5), longitude numeric(8,5)
);
CREATE TABLE IF NOT EXISTS universities (
  id bigserial PRIMARY KEY, official_code varchar(32) UNIQUE, name varchar(240) NOT NULL, short_name varchar(32), university_type varchar(40), ownership varchar(20)
);
CREATE TABLE IF NOT EXISTS campuses (
  id bigserial PRIMARY KEY, official_code varchar(32) UNIQUE, university_id bigint NOT NULL REFERENCES universities(id), geography_id bigint REFERENCES geographies(id), name varchar(240) NOT NULL
);
CREATE TABLE IF NOT EXISTS centers (
  id bigserial PRIMARY KEY, official_code varchar(32) UNIQUE, university_id bigint NOT NULL REFERENCES universities(id), campus_id bigint REFERENCES campuses(id), name varchar(240) NOT NULL, affiliated boolean NOT NULL DEFAULT false
);
CREATE TABLE IF NOT EXISTS degrees (
  id bigserial PRIMARY KEY, official_code varchar(40) UNIQUE, name varchar(240) NOT NULL, normalized_name varchar(240) NOT NULL, level varchar(30) NOT NULL DEFAULT 'grado', branch varchar(120), field varchar(160), ects numeric(6,2)
);
CREATE TABLE IF NOT EXISTS degree_components (
  degree_id bigint NOT NULL REFERENCES degrees(id), component_degree_id bigint NOT NULL REFERENCES degrees(id), position smallint NOT NULL, PRIMARY KEY (degree_id, component_degree_id)
);
CREATE TABLE IF NOT EXISTS degree_offerings (
  id bigserial PRIMARY KEY, degree_id bigint NOT NULL REFERENCES degrees(id), university_id bigint NOT NULL REFERENCES universities(id), center_id bigint REFERENCES centers(id), campus_id bigint REFERENCES campuses(id), academic_year_id bigint NOT NULL REFERENCES academic_years(id), modality varchar(40), language varchar(80), UNIQUE (degree_id, university_id, center_id, campus_id, academic_year_id)
);
CREATE TABLE IF NOT EXISTS admission_cutoffs (
  id bigserial PRIMARY KEY, degree_offering_id bigint NOT NULL REFERENCES degree_offerings(id), academic_year_id bigint NOT NULL REFERENCES academic_years(id), round varchar(60), admission_group varchar(80), cutoff_score numeric(6,3), scale_max numeric(5,2) NOT NULL DEFAULT 14, UNIQUE (degree_offering_id, academic_year_id, round, admission_group)
);
CREATE TABLE IF NOT EXISTS admission_demand (
  id bigserial PRIMARY KEY, degree_offering_id bigint NOT NULL REFERENCES degree_offerings(id), academic_year_id bigint NOT NULL REFERENCES academic_years(id), applications integer, admitted integer, enrolled integer
);
CREATE TABLE IF NOT EXISTS student_statistics (
  id bigserial PRIMARY KEY, degree_offering_id bigint REFERENCES degree_offerings(id), university_id bigint REFERENCES universities(id), academic_year_id bigint NOT NULL REFERENCES academic_years(id), metric varchar(80) NOT NULL, value numeric(12,4), unit varchar(20), population varchar(120)
);
CREATE TABLE IF NOT EXISTS graduate_statistics (
  id bigserial PRIMARY KEY, degree_offering_id bigint REFERENCES degree_offerings(id), university_id bigint REFERENCES universities(id), academic_year_id bigint NOT NULL REFERENCES academic_years(id), metric varchar(80) NOT NULL, value numeric(12,4), unit varchar(20), cohort_label varchar(120)
);
CREATE TABLE IF NOT EXISTS academic_performance (
  id bigserial PRIMARY KEY, degree_offering_id bigint REFERENCES degree_offerings(id), university_id bigint REFERENCES universities(id), academic_year_id bigint NOT NULL REFERENCES academic_years(id), metric varchar(80) NOT NULL, value numeric(12,4), unit varchar(20), population varchar(120)
);
CREATE TABLE IF NOT EXISTS employment_outcomes (
  id bigserial PRIMARY KEY, degree_offering_id bigint REFERENCES degree_offerings(id), university_id bigint REFERENCES universities(id), field varchar(160), academic_year_id bigint NOT NULL REFERENCES academic_years(id), years_after_graduation smallint, metric varchar(80) NOT NULL, value numeric(14,4), unit varchar(30), CHECK (years_after_graduation IS NULL OR years_after_graduation BETWEEN 0 AND 10)
);
CREATE TABLE IF NOT EXISTS tuition_fees (
  id bigserial PRIMARY KEY, degree_offering_id bigint REFERENCES degree_offerings(id), academic_year_id bigint NOT NULL REFERENCES academic_years(id), price_per_ect numeric(10,2), enrollment_total numeric(10,2), experimentality varchar(80)
);
CREATE TABLE IF NOT EXISTS data_sources (
  id bigserial PRIMARY KEY, name varchar(240) NOT NULL, institution varchar(240), url text NOT NULL, format varchar(40), granularity varchar(120), coverage text, limitations text
);
CREATE TABLE IF NOT EXISTS ingestion_runs (
  id bigserial PRIMARY KEY, source_id bigint NOT NULL REFERENCES data_sources(id), started_at timestamptz NOT NULL DEFAULT now(), finished_at timestamptz, status varchar(30) NOT NULL, input_checksum varchar(128), records_read integer, records_loaded integer, quality_summary jsonb
);
CREATE TABLE IF NOT EXISTS data_quality_flags (
  id bigserial PRIMARY KEY, ingestion_run_id bigint NOT NULL REFERENCES ingestion_runs(id), entity_type varchar(80) NOT NULL, record_key varchar(240), flag_code varchar(80) NOT NULL, severity varchar(20) NOT NULL, details text
);
CREATE TABLE IF NOT EXISTS university_aliases (
  id bigserial PRIMARY KEY, university_id bigint NOT NULL REFERENCES universities(id), alias varchar(240) NOT NULL, source_id bigint REFERENCES data_sources(id), UNIQUE (university_id, alias)
);
CREATE TABLE IF NOT EXISTS provenance (
  id bigserial PRIMARY KEY, entity_type varchar(80) NOT NULL, entity_id bigint NOT NULL, source_id bigint NOT NULL REFERENCES data_sources(id), source_record_id varchar(240), source_url text, retrieved_at timestamptz NOT NULL DEFAULT now(), ingestion_run_id bigint REFERENCES ingestion_runs(id)
);
CREATE INDEX IF NOT EXISTS idx_offerings_year ON degree_offerings(academic_year_id);
CREATE INDEX IF NOT EXISTS idx_cutoffs_score ON admission_cutoffs(cutoff_score);
CREATE INDEX IF NOT EXISTS idx_provenance_entity ON provenance(entity_type, entity_id);
