-- Vistas analíticas no materializadas: siempre reflejan la última carga.
-- Las magnitudes se mantienen separadas para impedir dobles conteos.
CREATE OR REPLACE VIEW public_budget_chain AS
SELECT br.fiscal_year, br.period, br.entity_id, br.economic_code, br.economic_level,
       br.final_amount AS final_credit, be.committed_amount, be.recognized_amount, be.paid_amount,
       br.data_status, br.source_id, br.source_record_id
FROM budget_records br
LEFT JOIN budget_execution be ON be.budget_record_id = br.id;

CREATE OR REPLACE VIEW public_authority_contract_totals AS
SELECT pe.id AS authority_id, pe.name AS authority_name,
       COUNT(DISTINCT c.id)::int AS contract_count,
       COUNT(DISTINCT ca.winner_entity_id)::int AS contractor_count,
       COALESCE(SUM(ca.award_amount), 0) AS awarded_amount
FROM public_entities pe
JOIN contracts c ON c.contracting_authority_id = pe.id
LEFT JOIN contract_awards ca ON ca.contract_id = c.id
GROUP BY pe.id, pe.name;

CREATE OR REPLACE VIEW public_recipient_contract_totals AS
SELECT re.id AS recipient_id, re.name AS recipient_name, re.tax_id,
       COUNT(DISTINCT ca.contract_id)::int AS contract_count,
       COUNT(DISTINCT c.contracting_authority_id)::int AS authority_count,
       COALESCE(SUM(ca.award_amount), 0) AS awarded_amount
FROM recipient_entities re
JOIN contract_awards ca ON ca.winner_entity_id = re.id
JOIN contracts c ON c.id = ca.contract_id
GROUP BY re.id, re.name, re.tax_id;
