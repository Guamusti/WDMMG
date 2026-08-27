-- Índices incrementales para las consultas públicas del MVP.
-- Se pueden aplicar varias veces sin cambiar los datos.
CREATE INDEX IF NOT EXISTS public_entities_name_idx ON public_entities (name);
CREATE INDEX IF NOT EXISTS public_entities_parent_idx ON public_entities (parent_id);
CREATE INDEX IF NOT EXISTS recipient_entities_name_idx ON recipient_entities (normalized_name);
CREATE INDEX IF NOT EXISTS recipient_entities_tax_id_idx ON recipient_entities (tax_id) WHERE tax_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS contracts_authority_idx ON contracts (contracting_authority_id, id DESC);
CREATE INDEX IF NOT EXISTS contracts_publication_idx ON contracts (publication_date DESC, id DESC);
CREATE INDEX IF NOT EXISTS contract_awards_winner_idx ON contract_awards (winner_entity_id, contract_id);
CREATE INDEX IF NOT EXISTS contract_awards_contract_idx ON contract_awards (contract_id, award_amount DESC NULLS LAST);
CREATE INDEX IF NOT EXISTS contract_events_contract_date_idx ON contract_events (contract_id, event_date DESC NULLS LAST);
CREATE INDEX IF NOT EXISTS grant_calls_title_idx ON grant_calls (title);
CREATE INDEX IF NOT EXISTS grant_awards_call_idx ON grant_awards (grant_call_id, award_date DESC NULLS LAST);
CREATE INDEX IF NOT EXISTS budget_records_lookup_idx ON budget_records (fiscal_year DESC, period DESC, economic_level, id);
