CREATE TABLE IF NOT EXISTS public_entity_aliases (
  id BIGSERIAL PRIMARY KEY,
  entity_id BIGINT NOT NULL REFERENCES public_entities(id) ON DELETE CASCADE,
  alias TEXT NOT NULL,
  normalized_alias TEXT NOT NULL,
  source_id BIGINT REFERENCES data_sources(id),
  source_record_id TEXT
);

CREATE TABLE IF NOT EXISTS recipient_aliases (
  id BIGSERIAL PRIMARY KEY,
  entity_id BIGINT NOT NULL REFERENCES recipient_entities(id) ON DELETE CASCADE,
  alias TEXT NOT NULL,
  normalized_alias TEXT NOT NULL,
  source_id BIGINT REFERENCES data_sources(id),
  source_record_id TEXT
);

CREATE TABLE IF NOT EXISTS entity_merge_candidates (
  id BIGSERIAL PRIMARY KEY,
  entity_type TEXT NOT NULL CHECK (entity_type IN ('public','recipient')),
  left_entity_id BIGINT NOT NULL,
  right_entity_id BIGINT NOT NULL,
  matching_method TEXT NOT NULL CHECK (matching_method IN ('tax_id','official_id','deterministic','probabilistic')),
  confidence NUMERIC(5,4),
  review_status TEXT NOT NULL DEFAULT 'pending' CHECK (review_status IN ('pending','accepted','rejected')),
  evidence JSONB NOT NULL DEFAULT '{}',
  reviewed_at TIMESTAMPTZ,
  CHECK (left_entity_id <> right_entity_id)
);

CREATE INDEX IF NOT EXISTS transfers_source_idx ON transfers(source_entity_id);
CREATE INDEX IF NOT EXISTS transfers_destination_idx ON transfers(destination_entity_id);
CREATE INDEX IF NOT EXISTS public_entity_aliases_normalized_idx ON public_entity_aliases(normalized_alias);
CREATE INDEX IF NOT EXISTS recipient_aliases_normalized_idx ON recipient_aliases(normalized_alias);
