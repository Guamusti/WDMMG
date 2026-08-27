-- Vistas de lectura para reconstruir la búsqueda sin recalcular métricas en cada petición.
CREATE MATERIALIZED VIEW IF NOT EXISTS admission_cutoff_percentiles AS
SELECT
  ac.id,
  ac.degree_offering_id,
  ac.academic_year_id,
  ac.cutoff_score,
  ac.scale_max,
  percent_rank() OVER (PARTITION BY ac.academic_year_id, ac.scale_max ORDER BY ac.cutoff_score) AS percentile
FROM admission_cutoffs ac
WHERE ac.cutoff_score IS NOT NULL AND ac.scale_max IS NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS idx_cutoff_percentiles_id ON admission_cutoff_percentiles(id);

CREATE MATERIALIZED VIEW IF NOT EXISTS madrid_offer_coverage AS
SELECT
  u.short_name,
  u.name AS university_name,
  ay.label AS academic_year,
  count(DISTINCT dof.id) AS offerings,
  count(DISTINCT d.id) AS degrees,
  count(DISTINCT ac.id) AS cutoffs
FROM degree_offerings dof
JOIN universities u ON u.id = dof.university_id
JOIN degrees d ON d.id = dof.degree_id
JOIN academic_years ay ON ay.id = dof.academic_year_id
LEFT JOIN admission_cutoffs ac ON ac.degree_offering_id = dof.id
GROUP BY u.short_name, u.name, ay.label;

CREATE UNIQUE INDEX IF NOT EXISTS idx_madrid_coverage_key ON madrid_offer_coverage(short_name, academic_year);
