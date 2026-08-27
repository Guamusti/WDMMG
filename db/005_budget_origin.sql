ALTER TABLE budget_records
  ADD COLUMN IF NOT EXISTS budget_origin_year INTEGER,
  ADD COLUMN IF NOT EXISTS is_extended_budget BOOLEAN;

COMMENT ON COLUMN budget_records.budget_origin_year IS 'Año de origen del presupuesto cuando la fuente identifica una prórroga.';
COMMENT ON COLUMN budget_records.is_extended_budget IS 'TRUE solo cuando la fuente identifica explícitamente un presupuesto prorrogado.';
