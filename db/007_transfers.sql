CREATE TABLE IF NOT EXISTS transfers (
  id BIGSERIAL PRIMARY KEY,
  fiscal_year INTEGER NOT NULL,
  period TEXT NOT NULL,
  source_entity_id BIGINT REFERENCES public_entities(id),
  destination_entity_id BIGINT REFERENCES public_entities(id),
  geography_id BIGINT REFERENCES geographies(id),
  transfer_type TEXT NOT NULL CHECK (transfer_type IN ('internal','external','unknown')),
  gross_spending NUMERIC(18,2),
  consolidated_spending NUMERIC(18,2),
  source_id BIGINT NOT NULL REFERENCES data_sources(id),
  source_record_id TEXT NOT NULL,
  ingestion_run_id BIGINT REFERENCES ingestion_runs(id),
  UNIQUE (fiscal_year, period, source_id, source_record_id)
);

CREATE INDEX IF NOT EXISTS transfers_source_idx ON transfers(source_entity_id);
CREATE INDEX IF NOT EXISTS transfers_destination_idx ON transfers(destination_entity_id);
