-- Dinero Público · modelo normalizado inicial
-- Importes en NUMERIC: nunca usar float para dinero.
CREATE TABLE data_sources (
  id BIGSERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  institution TEXT NOT NULL,
  source_type TEXT NOT NULL,
  source_url TEXT NOT NULL,
  format TEXT,
  update_frequency TEXT,
  coverage_description TEXT,
  known_limitations TEXT,
  is_official BOOLEAN NOT NULL DEFAULT TRUE,
  last_checked_at TIMESTAMPTZ,
  last_imported_at TIMESTAMPTZ
);
CREATE UNIQUE INDEX data_sources_url_idx ON data_sources(source_url);

CREATE TABLE ingestion_runs (
  id BIGSERIAL PRIMARY KEY,
  source_id BIGINT NOT NULL REFERENCES data_sources(id),
  started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  finished_at TIMESTAMPTZ,
  status TEXT NOT NULL CHECK (status IN ('running','success','partial','failed')),
  source_version TEXT,
  records_downloaded INTEGER DEFAULT 0,
  records_created INTEGER DEFAULT 0,
  records_updated INTEGER DEFAULT 0,
  records_skipped INTEGER DEFAULT 0,
  errors JSONB NOT NULL DEFAULT '[]'
);

CREATE TABLE public_entities (
  id BIGSERIAL PRIMARY KEY,
  official_code TEXT,
  tax_id TEXT,
  name TEXT NOT NULL,
  normalized_name TEXT NOT NULL,
  entity_type TEXT NOT NULL,
  administration_level TEXT,
  parent_id BIGINT REFERENCES public_entities(id),
  source_id BIGINT REFERENCES data_sources(id),
  source_record_id TEXT,
  valid_from DATE,
  valid_to DATE
);
CREATE INDEX public_entities_name_idx ON public_entities USING gin (to_tsvector('simple', name));
CREATE UNIQUE INDEX public_entities_tax_id_idx ON public_entities(tax_id) WHERE tax_id IS NOT NULL;
CREATE UNIQUE INDEX public_entities_official_code_idx ON public_entities(official_code) WHERE official_code IS NOT NULL;

CREATE TABLE recipient_entities (
  id BIGSERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  normalized_name TEXT NOT NULL,
  tax_id TEXT,
  entity_type TEXT,
  country TEXT,
  source_id BIGINT REFERENCES data_sources(id),
  source_record_id TEXT
);
CREATE INDEX recipient_entities_name_idx ON recipient_entities USING gin (to_tsvector('simple', name));

CREATE TABLE geographies (
  id BIGSERIAL PRIMARY KEY,
  code TEXT NOT NULL,
  name TEXT NOT NULL,
  level TEXT NOT NULL,
  parent_id BIGINT REFERENCES geographies(id),
  population INTEGER,
  population_year INTEGER,
  source_id BIGINT REFERENCES data_sources(id)
);

CREATE TABLE budget_records (
  id BIGSERIAL PRIMARY KEY,
  fiscal_year INTEGER NOT NULL,
  period TEXT NOT NULL,
  entity_id BIGINT NOT NULL REFERENCES public_entities(id),
  budget_side TEXT NOT NULL CHECK (budget_side IN ('expense','revenue')),
  organic_code TEXT,
  economic_code TEXT,
  economic_level TEXT,
  functional_code TEXT,
  program_code TEXT,
  funding_source_code TEXT,
  geography_id BIGINT REFERENCES geographies(id),
  initial_amount NUMERIC(18,2),
  modifications_amount NUMERIC(18,2),
  final_amount NUMERIC(18,2),
  data_status TEXT CHECK (data_status IN ('project','provisional','advance','definitive')),
  source_id BIGINT NOT NULL REFERENCES data_sources(id),
  source_record_id TEXT NOT NULL,
  ingestion_run_id BIGINT NOT NULL REFERENCES ingestion_runs(id),
  UNIQUE (fiscal_year, period, entity_id, budget_side, organic_code, economic_code, functional_code, program_code, source_record_id)
);

CREATE TABLE budget_execution (
  budget_record_id BIGINT PRIMARY KEY REFERENCES budget_records(id) ON DELETE CASCADE,
  authorized_amount NUMERIC(18,2),
  committed_amount NUMERIC(18,2),
  recognized_amount NUMERIC(18,2),
  paid_amount NUMERIC(18,2),
  raw_payload JSONB
);
CREATE UNIQUE INDEX budget_records_source_record_idx ON budget_records(source_id, source_record_id);

CREATE TABLE contracts (
  id BIGSERIAL PRIMARY KEY,
  procurement_id TEXT NOT NULL,
  title TEXT,
  contracting_authority_id BIGINT REFERENCES public_entities(id),
  contract_type TEXT,
  procedure_type TEXT,
  status TEXT,
  estimated_value NUMERIC(18,2),
  base_tender_budget NUMERIC(18,2),
  publication_date DATE,
  award_date DATE,
  formalization_date DATE,
  is_minor BOOLEAN NOT NULL DEFAULT FALSE,
  source_id BIGINT NOT NULL REFERENCES data_sources(id),
  source_url TEXT,
  source_record_id TEXT NOT NULL,
  ingestion_run_id BIGINT NOT NULL REFERENCES ingestion_runs(id),
  UNIQUE (source_id, source_record_id)
);
CREATE TABLE contract_lots (id BIGSERIAL PRIMARY KEY, contract_id BIGINT NOT NULL REFERENCES contracts(id) ON DELETE CASCADE, lot_number TEXT, title TEXT, budget NUMERIC(18,2), estimated_value NUMERIC(18,2));
CREATE TABLE contract_awards (id BIGSERIAL PRIMARY KEY, contract_id BIGINT NOT NULL REFERENCES contracts(id) ON DELETE CASCADE, lot_id BIGINT REFERENCES contract_lots(id), winner_entity_id BIGINT REFERENCES recipient_entities(id), award_amount NUMERIC(18,2), award_amount_with_tax NUMERIC(18,2), number_of_tenders INTEGER, award_date DATE);
CREATE TABLE contract_events (id BIGSERIAL PRIMARY KEY, contract_id BIGINT NOT NULL REFERENCES contracts(id) ON DELETE CASCADE, event_type TEXT NOT NULL, event_date DATE, source_record_id TEXT, payload JSONB NOT NULL DEFAULT '{}');

CREATE TABLE grant_calls (id BIGSERIAL PRIMARY KEY, bdns_code TEXT NOT NULL UNIQUE, title TEXT, granting_entity_id BIGINT REFERENCES public_entities(id), registration_date DATE, publication_date DATE, budget NUMERIC(18,2), purpose TEXT, source_id BIGINT NOT NULL REFERENCES data_sources(id), source_url TEXT, source_record_id TEXT, ingestion_run_id BIGINT REFERENCES ingestion_runs(id));
CREATE TABLE grant_awards (id BIGSERIAL PRIMARY KEY, grant_call_id BIGINT REFERENCES grant_calls(id), beneficiary_id BIGINT REFERENCES recipient_entities(id), amount NUMERIC(18,2), award_date DATE, instrument TEXT, purpose TEXT, source_id BIGINT NOT NULL REFERENCES data_sources(id), source_record_id TEXT NOT NULL, ingestion_run_id BIGINT REFERENCES ingestion_runs(id));
