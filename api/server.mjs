import { createServer } from 'node:http';
import { existsSync, readFileSync, statSync } from 'node:fs';
import { join } from 'node:path';
import pg from 'pg';

const { Pool } = pg;
const databaseUrl = process.env.DATABASE_URL || 'postgresql://postgres:postgres@localhost:55432/dinero_publico';
const pool = new Pool({ connectionString: databaseUrl, connectionTimeoutMillis: 700 });

const port = Number(process.env.API_PORT || 8787);
const root = process.cwd();
const fileCache = new Map();
const grantConcessionsCache = new Map();

function readJsonl(path) {
  if (!existsSync(path)) return [];
  const mtimeMs = statSync(path).mtimeMs;
  const cached = fileCache.get(path);
  if (cached?.mtimeMs === mtimeMs) return cached.value;
  const value = readFileSync(path, 'utf8').split(/\r?\n/).filter(Boolean).map(line => JSON.parse(line));
  fileCache.set(path, { mtimeMs, value });
  return value;
}

function readJson(path) {
  if (!existsSync(path)) return null;
  const mtimeMs = statSync(path).mtimeMs;
  const cached = fileCache.get(path);
  if (cached?.mtimeMs === mtimeMs) return cached.value;
  const value = JSON.parse(readFileSync(path, 'utf8'));
  fileCache.set(path, { mtimeMs, value });
  return value;
}

function json(res, status, body) {
  res.writeHead(status, { 'content-type': 'application/json; charset=utf-8', 'access-control-allow-origin': 'http://localhost:5173', 'x-content-type-options': 'nosniff', 'referrer-policy': 'no-referrer', 'cache-control': 'no-store' });
  res.end(JSON.stringify(body));
}

function csv(res, filename, rows) {
  const columns = rows.length ? Object.keys(rows[0]) : [];
  const quote = value => `"${String(value ?? '').replaceAll('"', '""')}"`;
  const body = [columns.map(quote).join(','), ...rows.map(row => columns.map(column => quote(row[column])).join(','))].join('\r\n');
  res.writeHead(200, { 'content-type': 'text/csv; charset=utf-8', 'content-disposition': `attachment; filename="${filename}"`, 'access-control-allow-origin': 'http://localhost:5173', 'x-content-type-options': 'nosniff' });
  res.end(`\uFEFF${body}`);
}

function getContracts() {
  return readJsonl(join(root, 'data', 'processed', 'placsp', 'contracts.jsonl'));
}

function getGrants() {
  return readJsonl(join(root, 'data', 'processed', 'bdns', 'records.jsonl'));
}

function companiesFromJsonl(query = '', limit = 100) {
  const needle = query.toLocaleLowerCase('es');
  const groups = new Map();
  for (const contract of getContracts()) {
    for (const award of contract.awards || []) {
      const name = String(award.winner_name || '').trim();
      if (!name || (needle && !name.toLocaleLowerCase('es').includes(needle))) continue;
      const key = String(award.winner_id || name).trim();
      const current = groups.get(key) || { id: key, name, tax_id: award.winner_id || null, contract_count: 0, authority_count: 0, award_amount: 0, contract_ids: new Set(), authorities: new Set() };
      if (!current.contract_ids.has(contract.source_record_id)) { current.contract_ids.add(contract.source_record_id); current.contract_count += 1; }
      if (contract.contracting_authority) current.authorities.add(contract.contracting_authority);
      current.authority_count = current.authorities.size;
      current.award_amount += Number(award.award_amount || 0);
      groups.set(key, current);
    }
  }
  return [...groups.values()].sort((a, b) => b.award_amount - a.award_amount).slice(0, limit).map(({ contract_ids, authorities, ...company }) => company);
}

async function databaseCompanies(query, limit) {
  const search = `%${query}%`;
  const result = await pool.query(`
    SELECT re.id, re.name, re.tax_id,
      COUNT(DISTINCT ca.contract_id)::int AS contract_count,
      COUNT(DISTINCT c.contracting_authority_id)::int AS authority_count,
      COALESCE(SUM(ca.award_amount), 0) AS award_amount
    FROM recipient_entities re
    JOIN contract_awards ca ON ca.winner_entity_id = re.id
    JOIN contracts c ON c.id = ca.contract_id
    WHERE ($1 = '' OR re.name ILIKE $2 OR re.tax_id ILIKE $2)
    GROUP BY re.id, re.name, re.tax_id
    ORDER BY award_amount DESC NULLS LAST, re.name
    LIMIT $3`, [query, search, limit]);
  return result.rows;
}

async function databaseCompanyInsight(query) {
  const search = `%${query}%`;
  const result = await pool.query(`
    WITH grouped AS (
      SELECT re.id, COALESCE(SUM(ca.award_amount), 0) AS amount
      FROM recipient_entities re JOIN contract_awards ca ON ca.winner_entity_id = re.id
      WHERE ($1 = '' OR re.name ILIKE $2 OR COALESCE(re.tax_id, '') ILIKE $2)
      GROUP BY re.id
    )
    SELECT COUNT(*)::int AS entity_count, COALESCE(SUM(amount), 0) AS total_amount,
      COALESCE((SELECT SUM(amount) FROM (SELECT amount FROM grouped ORDER BY amount DESC LIMIT 5) top_five), 0) AS top5_amount
    FROM grouped`, [query, search]);
  return result.rows[0];
}

async function databaseCompanyById(id) {
  const summary = await pool.query(`
    SELECT re.id, re.name, re.tax_id,
      COUNT(DISTINCT ca.contract_id)::int AS contract_count,
      COUNT(DISTINCT c.contracting_authority_id)::int AS authority_count,
      COALESCE(SUM(ca.award_amount), 0) AS award_amount
    FROM recipient_entities re
    JOIN contract_awards ca ON ca.winner_entity_id = re.id
    JOIN contracts c ON c.id = ca.contract_id
    WHERE re.id::text = $1 OR COALESCE(re.tax_id, '') = $1
    GROUP BY re.id, re.name, re.tax_id
    LIMIT 1`, [id]);
  if (!summary.rows[0]) return null;
  const contracts = await pool.query(`
    SELECT c.procurement_id, c.title, c.source_url, c.publication_date,
      ca.award_amount, ca.award_amount_with_tax, ca.number_of_tenders,
      pe.name AS contracting_authority
    FROM recipient_entities re
    JOIN contract_awards ca ON ca.winner_entity_id = re.id
    JOIN contracts c ON c.id = ca.contract_id
    LEFT JOIN public_entities pe ON pe.id = c.contracting_authority_id
    WHERE re.id::text = $1 OR COALESCE(re.tax_id, '') = $1
    ORDER BY ca.award_amount DESC NULLS LAST, c.publication_date DESC NULLS LAST`, [id]);
  const authorities = [...new Set(contracts.rows.map(row => row.contracting_authority).filter(Boolean))];
  return { ...summary.rows[0], authorities, contracts: contracts.rows };
}

function companyFromJsonl(id) {
  const contracts = [];
  let company = null;
  for (const contract of getContracts()) {
    for (const award of contract.awards || []) {
      const key = String(award.winner_id || award.winner_name || '').trim();
      if (key !== id) continue;
      company ||= { id: key, name: award.winner_name || key, tax_id: award.winner_id || null, contract_count: 0, authority_count: 0, award_amount: 0, contracts, authorities: new Set() };
      if (contract.contracting_authority) company.authorities.add(contract.contracting_authority);
      company.authority_count = company.authorities.size;
      if (!contracts.some(item => item.procurement_id === contract.procurement_id)) { company.contract_count += 1; contracts.push({ procurement_id: contract.procurement_id, title: contract.title, source_url: contract.source_url, contracting_authority: contract.contracting_authority, award_amount: award.award_amount, award_amount_with_tax: award.award_amount_with_tax, number_of_tenders: award.number_of_tenders }); }
      company.award_amount += Number(award.award_amount || 0);
    }
  }
  if (company) company.authorities = [...company.authorities];
  return company;
}

async function databaseContracts(query, page, pageSize) {
  const offset = (page - 1) * pageSize;
  const search = `%${query}%`;
  const result = await pool.query(`
    SELECT c.procurement_id, c.title, pe.name AS contracting_authority, re.name AS winner_name, re.tax_id AS winner_tax_id,
      c.estimated_value, c.base_tender_budget, c.status, c.source_url, c.source_record_id,
      ca.award_amount, ca.award_amount_with_tax
    FROM contracts c
    LEFT JOIN public_entities pe ON pe.id = c.contracting_authority_id
    LEFT JOIN LATERAL (SELECT ca.* FROM contract_awards ca WHERE ca.contract_id = c.id ORDER BY ca.award_amount DESC NULLS LAST, ca.id LIMIT 1) ca ON TRUE
    LEFT JOIN recipient_entities re ON re.id = ca.winner_entity_id
    WHERE ($1 = '' OR c.title ILIKE $2 OR c.procurement_id ILIKE $2 OR pe.name ILIKE $2 OR re.name ILIKE $2)
    ORDER BY c.publication_date DESC NULLS LAST, c.id DESC LIMIT $3 OFFSET $4`, [query, search, pageSize, offset]);
  return result.rows;
}

async function databaseContractById(id) {
  const result = await pool.query(`
    SELECT c.procurement_id, c.title, c.contract_type, c.procedure_type, c.status,
      c.estimated_value, c.base_tender_budget, c.publication_date, c.award_date,
      c.source_url, c.source_record_id, pe.name AS contracting_authority,
      re.name AS winner_name, re.tax_id AS winner_tax_id, ca.award_amount, ca.award_amount_with_tax,
      COALESCE(json_agg(json_build_object('lot_number', cl.lot_number, 'title', cl.title, 'budget', cl.budget)) FILTER (WHERE cl.id IS NOT NULL), '[]') AS lots,
      (SELECT COALESCE(json_agg(json_build_object('event_type', ce.event_type, 'event_date', ce.event_date, 'source_record_id', ce.source_record_id, 'payload', ce.payload) ORDER BY ce.event_date NULLS LAST, ce.id), '[]') FROM contract_events ce WHERE ce.contract_id = c.id) AS events
    FROM contracts c LEFT JOIN public_entities pe ON pe.id = c.contracting_authority_id LEFT JOIN contract_awards ca ON ca.contract_id = c.id LEFT JOIN recipient_entities re ON re.id = ca.winner_entity_id LEFT JOIN contract_lots cl ON cl.contract_id = c.id
    WHERE c.procurement_id = $1 OR c.source_record_id = $1
    GROUP BY c.id, pe.name, re.name, re.tax_id, ca.award_amount, ca.award_amount_with_tax LIMIT 1`, [id]);
  return result.rows[0] || null;
}

async function databaseGrants(query, page, pageSize) {
  const offset = (page - 1) * pageSize;
  const search = `%${query}%`;
  const result = await pool.query(`
    SELECT gc.bdns_code, gc.title, gc.registration_date, gc.publication_date, gc.budget,
      gc.purpose, gc.source_url, pe.name AS granting_entity
    FROM grant_calls gc LEFT JOIN public_entities pe ON pe.id = gc.granting_entity_id
    WHERE ($1 = '' OR gc.title ILIKE $2 OR gc.bdns_code ILIKE $2 OR gc.purpose ILIKE $2 OR pe.name ILIKE $2)
    ORDER BY gc.registration_date DESC NULLS LAST, gc.id DESC LIMIT $3 OFFSET $4`, [query, search, pageSize, offset]);
  return result.rows;
}

async function databaseGrantByCode(code) {
  const result = await pool.query(`
    SELECT gc.bdns_code, gc.title, gc.registration_date, gc.publication_date, gc.budget,
      gc.purpose, gc.source_url, gc.source_record_id, pe.name AS granting_entity
    FROM grant_calls gc LEFT JOIN public_entities pe ON pe.id = gc.granting_entity_id
    WHERE gc.bdns_code = $1 LIMIT 1`, [code]);
  return result.rows[0] || null;
}

function grantFromJsonl(code) {
  const row = getGrants().find(grant => String(grant.bdns_code || grant.source_record_id) === code);
  if (!row) return null;
  return { bdns_code: row.bdns_code, title: row.title, registration_date: row.registration_date, publication_date: row.publication_date, budget: row.raw_record?.convocatoria?.financiacion?.[0]?.importe || null, purpose: row.purpose, source_url: row.source_url, source_record_id: row.source_record_id, granting_entity: row.granting_body };
}

async function officialGrantConcessions(code, page = 0, pageSize = 100) {
  const cacheKey = `${code}:${page}:${pageSize}`;
  const cached = grantConcessionsCache.get(cacheKey);
  if (cached && cached.expiresAt > Date.now()) return cached.value;
  const endpoint = `https://www.infosubvenciones.es/bdnstrans/api/concesiones/busqueda?numeroConvocatoria=${encodeURIComponent(code)}&pageSize=${pageSize}&page=${page}`;
  const response = await fetch(endpoint, { headers: { Accept: 'application/json' }, signal: AbortSignal.timeout(8000) });
  if (!response.ok) throw new Error(`BDNS respondió ${response.status}`);
  const payload = await response.json();
  const data = (payload.content || []).map(row => ({ id: row.codConcesion || row.id, beneficiary: row.beneficiario || null, amount: row.importe ?? null, date: row.fechaConcesion || null, instrument: row.instrumento || null, callCode: row.numeroConvocatoria || code }));
  const value = { data, meta: { total: Number(payload.totalElements || data.length), page, pageSize, dataStatus: 'official_live', sourceUrl: endpoint, warning: payload.advertencia || null } };
  grantConcessionsCache.set(cacheKey, { value, expiresAt: Date.now() + 300000 });
  return value;
}

async function databaseSearch(query) {
  const search = `%${query}%`;
  const [contracts, grants, budgets, companies] = await Promise.all([
    pool.query(`SELECT 'contract' AS type, c.procurement_id AS id, c.title, pe.name AS subtitle, CONCAT('/?vista=contracts&contrato=', c.procurement_id) AS "sourceUrl" FROM contracts c LEFT JOIN public_entities pe ON pe.id = c.contracting_authority_id WHERE c.title ILIKE $1 OR c.procurement_id ILIKE $1 OR pe.name ILIKE $1 ORDER BY c.id DESC LIMIT 8`, [search]),
    pool.query(`SELECT 'grant' AS type, gc.bdns_code AS id, gc.title, gc.purpose AS subtitle, gc.source_url AS "sourceUrl" FROM grant_calls gc WHERE gc.title ILIKE $1 OR gc.bdns_code ILIKE $1 OR gc.purpose ILIKE $1 ORDER BY gc.id DESC LIMIT 8`, [search]),
    pool.query(`SELECT 'budget' AS type, br.economic_code AS id, br.economic_code AS title, br.economic_level AS subtitle, ds.source_url AS "sourceUrl" FROM budget_records br JOIN data_sources ds ON ds.id = br.source_id WHERE br.economic_code ILIKE $1 ORDER BY br.id DESC LIMIT 8`, [search]),
    pool.query(`SELECT 'company' AS type, re.id::text AS id, re.name AS title, CONCAT(COUNT(DISTINCT ca.contract_id)::int, ' contratos · ', COALESCE(re.tax_id, 'identificador no publicado')) AS subtitle, CONCAT('/?vista=companies&empresa=', re.id::text) AS "sourceUrl" FROM recipient_entities re JOIN contract_awards ca ON ca.winner_entity_id = re.id WHERE re.name ILIKE $1 OR COALESCE(re.tax_id, '') ILIKE $1 GROUP BY re.id, re.name, re.tax_id ORDER BY COUNT(DISTINCT ca.contract_id) DESC, re.name LIMIT 8`, [search])
  ]);
  return [...contracts.rows, ...grants.rows, ...budgets.rows, ...companies.rows].slice(0, 20);
}

async function databaseCoverage() {
  const result = await pool.query(`
    SELECT ds.id, ds.name, ds.institution, ds.source_url, ds.format, ds.coverage_description,
      COALESCE(ds.last_checked_at, (SELECT MAX(ir.finished_at) FROM ingestion_runs ir WHERE ir.source_id = ds.id)) AS last_checked_at,
      COALESCE(ds.last_imported_at, (SELECT MAX(ir.finished_at) FROM ingestion_runs ir WHERE ir.source_id = ds.id AND ir.status = 'success')) AS last_imported_at,
      (SELECT COUNT(*) FROM budget_records br WHERE br.source_id = ds.id) AS budget_records,
      (SELECT COUNT(*) FROM contracts c WHERE c.source_id = ds.id) AS contract_records,
      (SELECT COUNT(*) FROM grant_calls gc WHERE gc.source_id = ds.id) AS grant_records
    FROM data_sources ds WHERE ds.is_official = TRUE ORDER BY ds.id`);
  const ccaaRows = getTerritorialExecution();
  return [
    ...result.rows,
    {
      id: 'ccaa-execution-2026-05',
      name: 'Ejecución presupuestaria de CCAA',
      institution: 'Ministerio de Hacienda / CIMCANET',
      source_url: 'https://serviciostelematicosext.hacienda.gob.es/SGCIEF/Cimcanet/aspx/consulta/consulta.aspx',
      format: 'XLSX',
      coverage_description: '17 comunidades y total CCAA; mayo de 2026; avance no financiero acumulado. No se suma a la AGE.',
      last_checked_at: null,
      last_imported_at: null,
      budget_records: ccaaRows.length,
      contract_records: 0,
      grant_records: 0,
      data_status: ccaaRows.length ? 'partial' : 'awaiting_validated_ingestion'
    },
    {
      id: 'local-budgets-2026',
      name: 'Presupuestos de entidades locales',
      institution: 'Ministerio de Hacienda / CONPREL',
      source_url: 'https://serviciostelematicosext.hacienda.gob.es/SGFAL/CONPREL?acc=null&cd_camp=null',
      format: 'Access dentro de ZIP',
      coverage_description: 'Fuente oficial localizada y descargada; pendiente de extraer tablas con un lector Access compatible.',
      last_checked_at: null,
      last_imported_at: null,
      budget_records: 0,
      contract_records: 0,
      grant_records: 0,
      data_status: 'blocked_reader'
    }
  ];
}

function getExecution() {
  return readJsonl(join(root, 'data', 'processed', 'igae', 'execution-2026-05.jsonl'));
}

function getExecutionHistory() {
  const files = ['execution-2026-04.jsonl', 'execution-2026-05.jsonl'];
  return files.map(file => {
    const rows = readJsonl(join(root, 'data', 'processed', 'igae', file)).filter(row => row.classification_level === 'chapter' && /^[1-9]\.\s/.test(row.classification_label));
    if (!rows.length) return null;
    const sum = key => rows.reduce((total, row) => total + (Number(row[key]) || 0), 0);
    return { fiscalYear: rows[0].fiscal_year, period: rows[0].period, unit: rows[0].unit, finalCredit: sum('final_credit'), committed: sum('committed_amount'), recognized: sum('recognized_amount'), paid: sum('paid_amount'), sourceUrl: rows[0].source_url, dataStatus: rows[0].data_status, records: rows.length };
  }).filter(Boolean);
}

function getTerritorialExecution() {
  return readJsonl(join(root, 'data', 'processed', 'ccaa', 'execution-2026-05.jsonl'));
}

function qualityReport() {
  const contracts = getContracts();
  const contractIds = contracts.map(row => row.procurement_id || row.source_record_id).filter(Boolean);
  const execution = getExecution();
  const grants = getGrants();
  const awards = contracts.flatMap(row => row.awards || []);
  const policies = readJson(join(root, 'data', 'processed', 'igae', 'functional-policies-2024.json'))?.policies || [];
  const geography = readJson(join(root, 'data', 'processed', 'geo', 'community-boundaries.json'))?.data || [];
  const duplicateCount = values => values.length - new Set(values).size;
  return [
    { id: 'placsp', name: 'Contratos PLACSP', records: contracts.length, missingIds: contracts.length - contractIds.length, duplicates: duplicateCount(contractIds), anomalies: contracts.filter(row => !row.source_url).length, sourceUrl: 'https://contrataciondelestado.es/' },
    { id: 'placsp-awards', name: 'Adjudicaciones PLACSP', records: awards.length, missingIds: awards.filter(row => !row.award_id).length, duplicates: duplicateCount(awards.map(row => row.award_id).filter(Boolean)), anomalies: awards.filter(row => row.award_amount == null && row.winner_name).length, sourceUrl: 'https://contrataciondelestado.es/' },
    { id: 'igae', name: 'Ejecución AGE · mayo 2026', records: execution.length, missingIds: execution.filter(row => !row.source_record_id).length, duplicates: duplicateCount(execution.map(row => row.source_record_id).filter(Boolean)), anomalies: execution.filter(row => (row.quality_flags || []).length).length, sourceUrl: execution[0]?.source_url || null },
    { id: 'igae-policies', name: 'Partidas funcionales IGAE · 2024', records: policies.length, missingIds: policies.filter(row => !row.code).length, duplicates: duplicateCount(policies.map(row => row.code).filter(Boolean)), anomalies: policies.filter(row => Number(row.amount) < 0).length, sourceUrl: 'https://www.igae.pap.hacienda.gob.es/' },
    { id: 'bdns', name: 'Convocatorias BDNS', records: grants.length, missingIds: grants.filter(row => !(row.bdns_code || row.source_record_id)).length, duplicates: duplicateCount(grants.map(row => row.bdns_code || row.source_record_id).filter(Boolean)), anomalies: grants.filter(row => !row.source_url).length, sourceUrl: grants[0]?.source_url || null },
    { id: 'ign-geography', name: 'Límites CCAA · IGN', records: geography.length, missingIds: geography.filter(row => !row.id).length, duplicates: duplicateCount(geography.map(row => row.id).filter(Boolean)), anomalies: geography.filter(row => !Array.isArray(row.coordinates) || row.coordinates.length < 2).length, sourceUrl: 'https://api-features.ign.es/collections/administrativeboundary?f=json' }
  ];
}

async function officialPopulation(query, limit = 12, level = 'municipality') {
  const safeQuery = query.replaceAll("'", "''").trim();
  const base = 'https://ine.es/servergis/rest/services/Hosted/Censo_2024___N%C3%BAmero_de_personas/FeatureServer/1/query';
  const field = level === 'province' ? 'NPRO' : 'NMUN';
  const params = new URLSearchParams({ where: `${field} LIKE '%${safeQuery}%'`, outFields: 'cumun,nmun,npro,nca,n_personas', returnGeometry: 'false', resultRecordCount: String(level === 'province' ? 2000 : limit), f: 'json' });
  const endpoint = `${base}?${params}`;
  const response = await fetch(endpoint, { headers: { Accept: 'application/json' }, signal: AbortSignal.timeout(8000) });
  if (!response.ok) throw new Error(`INE respondió ${response.status}`);
  const payload = await response.json();
  if (payload.error) throw new Error(payload.error.message || 'INE rechazó la consulta');
  const municipalities = (payload.features || []).map(feature => feature.attributes).map(row => ({ code: row.cumun, municipality: row.nmun, province: row.npro, community: row.nca, population: Number(row.n_personas) || 0 }));
  if (level !== 'province') return { data: municipalities, meta: { dataStatus: 'official_live', sourceUrl: endpoint, referenceDate: '2024-01-01', source: 'INE Censo Anual de Población 2024', searchField: 'municipality' } };
  const grouped = new Map();
  for (const row of municipalities) {
    const current = grouped.get(row.province) || { code: row.province, province: row.province, population: 0, municipality_count: 0 };
    current.population += row.population;
    current.municipality_count += 1;
    grouped.set(row.province, current);
  }
  return { data: [...grouped.values()].sort((a, b) => b.population - a.population), meta: { dataStatus: 'official_live_aggregate', sourceUrl: endpoint, referenceDate: '2024-01-01', source: 'INE Censo Anual de Población 2024', searchField: 'province', aggregation: 'suma de municipios devueltos por el INE' } };
}

let communityMapCache = null;
function simplifyLine(points, tolerance = 0.04) {
  if (!Array.isArray(points) || points.length < 3) return points || [];
  const square = tolerance * tolerance;
  const distance = (point, start, end) => {
    let x = start[0], y = start[1], dx = end[0] - x, dy = end[1] - y;
    if (dx || dy) { const t = ((point[0] - x) * dx + (point[1] - y) * dy) / (dx * dx + dy * dy); if (t > 1) { x = end[0]; y = end[1]; } else if (t > 0) { x += dx * t; y += dy * t; } }
    dx = point[0] - x; dy = point[1] - y; return dx * dx + dy * dy;
  };
  const reduce = (start, end) => { let index = -1, max = square; for (let i = start + 1; i < end; i += 1) { const value = distance(points[i], points[start], points[end]); if (value > max) { index = i; max = value; } } if (index < 0) return [points[start], points[end]]; const left = reduce(start, index); const right = reduce(index, end); return left.slice(0, -1).concat(right); };
  return reduce(0, points.length - 1);
}

async function officialCommunityMap() {
  if (communityMapCache) return communityMapCache;
  const snapshot = readJson(join(root, 'data', 'processed', 'geo', 'community-boundaries.json'));
  if (snapshot?.data?.length) {
    communityMapCache = { data: snapshot.data, meta: { dataStatus: 'official_snapshot_simplified', sourceUrl: snapshot.sourceUrl, source: `${snapshot.source} · snapshot versionado`, retrievedAt: snapshot.retrievedAt, geometry: 'límites entre comunidades autónomas simplificados en servidor', featureCount: snapshot.data.length } };
    return communityMapCache;
  }
  const sourceUrl = 'https://api-features.ign.es/collections/administrativeboundary/items?f=json&limit=50&filter-lang=cql-text&filter=nationallevelname%20%3D%20%27Comunidad%20aut%C3%B3noma%27';
  const response = await fetch(sourceUrl, { headers: { Accept: 'application/geo+json' }, signal: AbortSignal.timeout(20000) });
  if (!response.ok) throw new Error(`IGN respondió ${response.status}`);
  const payload = await response.json();
  const data = (payload.features || []).filter(feature => feature.geometry?.type === 'LineString').map(feature => ({ id: String(feature.id), names: String(feature.properties?.name_boundary || '').split('#').filter(Boolean), coordinates: simplifyLine(feature.geometry.coordinates) }));
  communityMapCache = { data, meta: { dataStatus: data.length ? 'official_live_simplified' : 'unavailable', sourceUrl, source: 'IGN OGC API Features · Unidades administrativas', geometry: 'límites entre comunidades autónomas simplificados en servidor', featureCount: data.length } };
  return communityMapCache;
}

async function databaseOverview() {
  const result = await pool.query(`
    SELECT br.fiscal_year, br.period, br.data_status, ds.source_url,
      SUM(br.final_amount) AS final_credit,
      SUM(be.committed_amount) AS committed,
      SUM(be.recognized_amount) AS recognized,
      SUM(be.paid_amount) AS paid
    FROM budget_records br
    JOIN budget_execution be ON be.budget_record_id = br.id
    JOIN data_sources ds ON ds.id = br.source_id
    WHERE br.economic_level = 'chapter' AND br.economic_code ~ '^[1-9]\\. '
    GROUP BY br.fiscal_year, br.period, br.data_status, ds.source_url
    ORDER BY br.fiscal_year DESC, br.period DESC LIMIT 1`);
  return result.rows[0] || null;
}

function overviewFromJsonl() {
  // GTOS 004 contiene capítulos y filas TOTAL; no sumar ambas cosas.
  const rows = getExecution().filter(row => row.classification_level === 'chapter' && /^[1-9]\.\s/.test(row.classification_label));
  if (!rows.length) return null;
  const sum = key => rows.reduce((total, row) => total + (Number(row[key]) || 0), 0);
  return {
    dataStatus: 'imported',
    fiscalYear: rows[0].fiscal_year,
    period: rows[0].period,
    unit: rows[0].unit,
    execution: { finalCredit: sum('final_credit'), committed: sum('committed_amount'), recognized: sum('recognized_amount'), paid: sum('paid_amount') },
    contracts: { records: getContracts().length },
    sourceUrl: rows[0].source_url,
  };
}

async function overview() {
  try {
    const row = await databaseOverview();
    if (row) return { dataStatus: 'imported', fiscalYear: row.fiscal_year, period: row.period, unit: 'miles de euros', execution: { finalCredit: Number(row.final_credit), committed: Number(row.committed), recognized: Number(row.recognized), paid: Number(row.paid) }, contracts: { records: getContracts().length }, sourceUrl: row.source_url };
  } catch (error) { console.warn(`PostgreSQL no disponible; fallback JSONL: ${error.message}`); }
  return overviewFromJsonl() || { dataStatus: 'awaiting_validated_ingestion', budget: null, execution: null, contracts: null, grants: null };
}

const server = createServer(async (req, res) => {
  const url = new URL(req.url, `http://${req.headers.host}`);
  if (req.method !== 'GET') return json(res, 405, { error: 'method_not_allowed' });
  if (url.pathname === '/api/health') return json(res, 200, { ok: true, service: 'dinero-publico-api', data: { contracts: getContracts().length } });
  if (url.pathname === '/api/overview') return json(res, 200, await overview());
  if (url.pathname === '/api/history') {
    const data = getExecutionHistory();
    return json(res, 200, { data, meta: { dataStatus: data.length > 1 ? 'imported' : 'partial', unit: 'miles de euros', source: 'IGAE' } });
  }
  if (url.pathname === '/api/quality') return json(res, 200, { data: qualityReport(), meta: { dataStatus: 'imported', definition: 'Los registros se auditan sin eliminar anomalías; una ausencia no se convierte en cero.' } });
  if (url.pathname === '/api/population') {
    const query = (url.searchParams.get('q') || '').trim();
    const limit = Math.min(50, Math.max(1, Number(url.searchParams.get('limit') || 12)));
    if (!query) return json(res, 200, { data: [], meta: { dataStatus: 'awaiting_query', source: 'INE' } });
    const level = url.searchParams.get('level') === 'province' ? 'province' : 'municipality';
    try { return json(res, 200, await officialPopulation(query, limit, level)); }
    catch (error) { return json(res, 503, { error: 'population_unavailable', detail: error.message, meta: { dataStatus: 'unavailable', source: 'INE' } }); }
  }
  if (url.pathname === '/api/geography/communities') {
    try { return json(res, 200, await officialCommunityMap()); }
    catch (error) { return json(res, 503, { error: 'geography_unavailable', detail: error.message, meta: { dataStatus: 'unavailable', source: 'IGN' } }); }
  }
  if (url.pathname === '/api/budgets') {
    try {
      const result = await pool.query(`SELECT br.*, be.committed_amount, be.recognized_amount, be.paid_amount, be.raw_payload FROM budget_records br LEFT JOIN budget_execution be ON be.budget_record_id = br.id ORDER BY br.fiscal_year DESC, br.period DESC, br.id`);
      return json(res, 200, { data: result.rows, meta: { total: result.rowCount, dataStatus: 'imported', backend: 'postgresql' } });
    } catch (error) { return json(res, 200, { data: getExecution(), meta: { total: getExecution().length, dataStatus: getExecution().length ? 'imported' : 'awaiting_validated_ingestion', backend: 'jsonl-fallback', warning: error.message } }); }
  }
  if (url.pathname === '/api/contracts') {
    const query = (url.searchParams.get('q') || '').toLocaleLowerCase('es');
    const page = Math.max(1, Number(url.searchParams.get('page') || 1));
    const pageSize = Math.min(100, Math.max(1, Number(url.searchParams.get('pageSize') || 25)));
    try {
      const data = await databaseContracts(query, page, pageSize);
      return json(res, 200, { data, meta: { page, pageSize, total: data.length, dataStatus: data.length ? 'imported' : 'awaiting_validated_ingestion', backend: 'postgresql' } });
    } catch (error) {
      const all = getContracts().filter(row => !query || JSON.stringify(row).toLocaleLowerCase('es').includes(query));
      return json(res, 200, { data: all.slice((page - 1) * pageSize, page * pageSize), meta: { page, pageSize, total: all.length, dataStatus: all.length ? 'imported' : 'awaiting_validated_ingestion', backend: 'jsonl-fallback', warning: error.message } });
    }
  }
  if (url.pathname === '/api/companies') {
    const query = (url.searchParams.get('q') || '').trim();
    const limit = Math.min(100, Math.max(1, Number(url.searchParams.get('limit') || 50)));
    try {
      const data = await databaseCompanies(query, limit);
      return json(res, 200, { data: data.length ? data : companiesFromJsonl(query, limit), meta: { total: data.length, dataStatus: data.length ? 'imported' : 'awaiting_validated_ingestion', backend: 'postgresql' } });
    } catch (error) {
      const data = companiesFromJsonl(query, limit);
      return json(res, 200, { data, meta: { total: data.length, dataStatus: data.length ? 'imported' : 'awaiting_validated_ingestion', backend: 'jsonl-fallback', warning: error.message } });
    }
  }
  if (url.pathname === '/api/companies/insights') {
    const query = (url.searchParams.get('q') || '').trim();
    try { return json(res, 200, { data: await databaseCompanyInsight(query), meta: { backend: 'postgresql', dataStatus: 'imported' } }); }
    catch (error) {
      const rows = companiesFromJsonl(query, 100000);
      const total = rows.reduce((sum, row) => sum + Number(row.award_amount || 0), 0);
      const top5 = rows.slice().sort((a, b) => Number(b.award_amount || 0) - Number(a.award_amount || 0)).slice(0, 5).reduce((sum, row) => sum + Number(row.award_amount || 0), 0);
      return json(res, 200, { data: { entity_count: rows.length, total_amount: total, top5_amount: top5 }, meta: { backend: 'jsonl-fallback', dataStatus: rows.length ? 'imported' : 'awaiting_validated_ingestion', warning: error.message } });
    }
  }
  if (url.pathname.startsWith('/api/companies/')) {
    const id = decodeURIComponent(url.pathname.slice('/api/companies/'.length));
    try {
      const data = await databaseCompanyById(id);
      return data ? json(res, 200, { data, meta: { backend: 'postgresql', dataStatus: 'imported' } }) : json(res, 404, { error: 'company_not_found' });
    } catch (error) {
      const data = companyFromJsonl(id);
      return data ? json(res, 200, { data, meta: { backend: 'jsonl-fallback', dataStatus: 'imported', warning: error.message } }) : json(res, 404, { error: 'company_not_found' });
    }
  }
  if (url.pathname.startsWith('/api/contracts/')) {
    const id = decodeURIComponent(url.pathname.slice('/api/contracts/'.length));
    try { const data = await databaseContractById(id); return data ? json(res, 200, { data, meta: { backend: 'postgresql' } }) : json(res, 404, { error: 'contract_not_found' }); }
    catch (error) { return json(res, 503, { error: 'detail_unavailable', detail: error.message }); }
  }
  if (url.pathname === '/api/grants') {
    const query = (url.searchParams.get('q') || '').trim();
    const page = Math.max(1, Number(url.searchParams.get('page') || 1));
    const pageSize = Math.min(100, Math.max(1, Number(url.searchParams.get('pageSize') || 25)));
    try {
      const data = await databaseGrants(query, page, pageSize);
      return json(res, 200, { data, meta: { page, pageSize, total: data.length, dataStatus: data.length ? 'imported' : 'awaiting_validated_ingestion', backend: 'postgresql' } });
    } catch (error) {
      return json(res, 200, { data: [], meta: { page, pageSize, total: 0, dataStatus: 'awaiting_validated_ingestion', backend: 'unavailable', warning: error.message } });
    }
  }
  if (url.pathname.endsWith('/concesiones') && url.pathname.startsWith('/api/grants/')) {
    const code = decodeURIComponent(url.pathname.slice('/api/grants/'.length, -'/concesiones'.length));
    const page = Math.max(0, Number(url.searchParams.get('page') || 0));
    const pageSize = Math.min(100, Math.max(1, Number(url.searchParams.get('pageSize') || 100)));
    try { return json(res, 200, await officialGrantConcessions(code, page, pageSize)); }
    catch (error) { return json(res, 503, { error: 'grant_concessions_unavailable', detail: error.message, meta: { dataStatus: 'unavailable', sourceUrl: 'https://www.infosubvenciones.es/bdnstrans/api/concesiones/busqueda' } }); }
  }
  if (url.pathname.startsWith('/api/grants/')) {
    const code = decodeURIComponent(url.pathname.slice('/api/grants/'.length));
    try {
      const data = await databaseGrantByCode(code);
      const fallback = grantFromJsonl(code);
      const enriched = data && fallback ? { ...fallback, ...data, budget: data.budget || fallback.budget } : data || fallback;
      return enriched ? json(res, 200, { data: enriched, meta: { backend: data ? 'postgresql' : 'jsonl-fallback', dataStatus: 'imported' } }) : json(res, 404, { error: 'grant_not_found' });
    } catch (error) {
      const data = grantFromJsonl(code);
      return data ? json(res, 200, { data, meta: { backend: 'jsonl-fallback', dataStatus: 'imported', warning: error.message } }) : json(res, 404, { error: 'grant_not_found' });
    }
  }
  if (url.pathname === '/api/export.csv') {
    const entity = url.searchParams.get('entity') || 'contracts';
    const query = (url.searchParams.get('q') || '').trim();
    try {
      if (entity === 'policies') {
        const source = readJson(join(root, 'data', 'processed', 'igae', 'functional-policies-2024.json'));
        if (!source?.policies?.length) return csv(res, 'partidas-funcionales-2024.csv', []);
        const featuredCodes = new Set(['21', '45', '31', '32', '25', '22', '95', '94']);
        const featured = source.policies.filter(policy => featuredCodes.has(String(policy.code)));
        const rest = source.policies.filter(policy => !featuredCodes.has(String(policy.code)));
        const restAmount = rest.reduce((sum, policy) => sum + Number(policy.amount || 0), 0);
        const parentRows = [...featured, { code: 'rest', label: 'Resto de políticas', amount: restAmount }];
        const rows = parentRows.flatMap(policy => [{ partida: policy.label, nivel: 'partida', importe_eur: policy.amount, porcentaje_total: source.total ? (policy.amount / source.total) * 100 : null, padre: '' }, ...(policy.code === 'rest' ? rest : (policy.children || [])).map(child => ({ partida: child.label, nivel: 'subpartida', importe_eur: child.amount, porcentaje_total: source.total ? (child.amount / source.total) * 100 : null, padre: policy.label }))]);
        return csv(res, 'partidas-funcionales-2024.csv', rows);
      }
      if (entity === 'contracts') return csv(res, 'contratos-placsp.csv', await databaseContracts(query, 1, 10000));
      if (entity === 'grants') return csv(res, 'convocatorias-bdns.csv', await databaseGrants(query, 1, 10000));
      if (entity === 'companies') return csv(res, 'empresas-adjudicatarias-placsp.csv', await databaseCompanies(query, 10000));
      if (entity === 'budgets') {
        const search = `%${query}%`;
        const result = await pool.query(`SELECT br.fiscal_year, br.period, br.economic_code, br.economic_level, br.final_amount, be.committed_amount, be.recognized_amount, be.paid_amount, ds.source_url FROM budget_records br LEFT JOIN budget_execution be ON be.budget_record_id = br.id JOIN data_sources ds ON ds.id = br.source_id WHERE ($1 = '' OR br.economic_code ILIKE $2) ORDER BY br.fiscal_year DESC, br.period DESC, br.id`, [query, search]);
        return csv(res, 'presupuesto-igae.csv', result.rows);
      }
      return json(res, 400, { error: 'unsupported_export_entity' });
    } catch (error) { return json(res, 503, { error: 'export_unavailable', detail: error.message }); }
  }
  if (url.pathname === '/api/search') {
    const query = (url.searchParams.get('q') || '').trim().toLocaleLowerCase('es');
    if (!query) return json(res, 200, { data: [] });
    try { return json(res, 200, { data: await databaseSearch(query), meta: { backend: 'postgresql' } }); }
    catch (error) {
      const contracts = getContracts().filter(row => JSON.stringify(row).toLocaleLowerCase('es').includes(query)).slice(0, 12);
      const companies = companiesFromJsonl(query, 8).map(row => ({ type: 'company', id: row.id, title: row.name, subtitle: `${row.contract_count} contratos · ${row.tax_id || 'identificador no publicado'}`, sourceUrl: `/?vista=companies&empresa=${encodeURIComponent(row.id)}` }));
      return json(res, 200, { data: [...companies, ...contracts.map(row => ({ type: 'contract', id: row.source_record_id, title: row.title, sourceUrl: `/?vista=contracts&contrato=${encodeURIComponent(row.source_record_id)}` }))].slice(0, 20), meta: { backend: 'jsonl-fallback', warning: error.message } });
    }
  }
  if (url.pathname === '/api/coverage') {
    const checkedAt = new Date().toISOString();
    try { return json(res, 200, { data: await databaseCoverage(), meta: { backend: 'postgresql', checkedAt } }); }
    catch (error) { return json(res, 200, { data: [], meta: { backend: 'unavailable', checkedAt, warning: error.message } }); }
  }
  if (url.pathname === '/api/policies') {
    const policies = readJson(join(root, 'data', 'processed', 'igae', 'functional-policies-2024.json'));
    return policies ? json(res, 200, { data: policies.policies, meta: { fiscalYear: policies.fiscal_year, unit: policies.unit, total: policies.total, sourceUrl: policies.source_url, sourceSection: policies.source_section, dataStatus: policies.data_status, backend: 'file' } }) : json(res, 503, { error: 'policies_unavailable' });
  }
  if (url.pathname === '/api/territories') {
    const data = getTerritorialExecution();
    return json(res, 200, { data, meta: { fiscalYear: 2026, period: '2026-05', unit: 'thousands_eur', total: data.length, dataStatus: data.length ? 'advance' : 'awaiting_validated_ingestion', sourceUrl: 'https://serviciostelematicosext.hacienda.gob.es/SGCIEF/Cimcanet/aspx/consulta/consulta.aspx', backend: 'file' } });
  }
  return json(res, 404, { error: 'not_found' });
});

server.listen(port, '127.0.0.1', () => console.log(`Dinero Público API: http://localhost:${port}`));
