CREATE TABLE IF NOT EXISTS source_files (
  id BIGSERIAL PRIMARY KEY,
  source_id BIGINT NOT NULL REFERENCES data_sources(id),
  source_url TEXT NOT NULL,
  retrieved_at TIMESTAMPTZ NOT NULL,
  sha256 TEXT NOT NULL,
  dataset_version TEXT,
  storage_key TEXT NOT NULL,
  content_type TEXT,
  byte_size BIGINT,
  UNIQUE (source_id, sha256)
);

CREATE INDEX IF NOT EXISTS source_files_source_idx ON source_files(source_id, retrieved_at DESC);
