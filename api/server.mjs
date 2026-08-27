import { createServer } from 'node:http';
import { existsSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import pg from 'pg';

const { Pool } = pg;
const databaseUrl = process.env.DATABASE_URL || 'postgresql://postgres:postgres@localhost:55432/dinero_publico';
const pool = new Pool({ connectionString: databaseUrl, connectionTimeoutMillis: 700 });

const port = Number(process.env.API_PORT || 8787);
const root = process.cwd();

function readJsonl(path) {
  if (!existsSync(path)) return [];
  return readFileSync(path, 'utf8').split(/\r?\n/).filter(Boolean).map(line => JSON.parse(line));
}

function readJson(path) {
  if (!existsSync(path)) return null;
  return JSON.parse(readFileSync(path, 'utf8'));
}

function json(res, status, body) {
  res.writeHead(status, { 'content-type': 'application/json; charset=utf-8', 'access-control-allow-origin': '*' });
  res.end(JSON.stringify(body));
}

function csv(res, filename, rows) {
  const columns = rows.length ? Object.keys(rows[0]) : [];
  const quote = value => `"${String(value ?? '').replaceAll('"', '""')}"`;
  const body = [columns.map(quote).join(','), ...rows.map(row => columns.map(column => quote(row[column])).join(','))].join('\r\n');
  res.writeHead(200, { 'content-type': 'text/csv; charset=utf-8', 'content-disposition': `attachment; filename="${filename}"`, 'access-control-allow-origin': '*' });
  res.end(`\uFEFF${body}`);
}

function getContracts() {
  return readJsonl(join(root, 'data', 'processed', 'placsp', 'contracts.jsonl'));
}

async function databaseContracts(query, page, pageSize) {
  const offset = (page - 1) * pageSize;
  const search = `%${query}%`;
  const result = await pool.query(`
    SELECT c.procurement_id, c.title, pe.name AS contracting_authority, c.estimated_value, c.base_tender_budget, c.status, c.source_url, c.source_record_id
    FROM contracts c LEFT JOIN public_entities pe ON pe.id = c.contracting_authority_id
    WHERE ($1 = '' OR c.title ILIKE $2 OR c.procurement_id ILIKE $2 OR pe.name ILIKE $2)
    ORDER BY c.publication_date DESC NULLS LAST, c.id DESC LIMIT $3 OFFSET $4`, [query, search, pageSize, offset]);
  return result.rows;
}

async function databaseContractById(id) {
  const result = await pool.query(`
    SELECT c.procurement_id, c.title, c.contract_type, c.procedure_type, c.status,
      c.estimated_value, c.base_tender_budget, c.publication_date, c.award_date,
      c.source_url, c.source_record_id, pe.name AS contracting_authority,
      COALESCE(json_agg(json_build_object('lot_number', cl.lot_number, 'title', cl.title, 'budget', cl.budget)) FILTER (WHERE cl.id IS NOT NULL), '[]') AS lots
    FROM contracts c LEFT JOIN public_entities pe ON pe.id = c.contracting_authority_id LEFT JOIN contract_lots cl ON cl.contract_id = c.id
    WHERE c.procurement_id = $1 OR c.source_record_id = $1
    GROUP BY c.id, pe.name LIMIT 1`, [id]);
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

async function databaseSearch(query) {
  const search = `%${query}%`;
  const [contracts, grants, budgets] = await Promise.all([
    pool.query(`SELECT 'contract' AS type, c.procurement_id AS id, c.title, pe.name AS subtitle, c.source_url AS "sourceUrl" FROM contracts c LEFT JOIN public_entities pe ON pe.id = c.contracting_authority_id WHERE c.title ILIKE $1 OR c.procurement_id ILIKE $1 OR pe.name ILIKE $1 ORDER BY c.id DESC LIMIT 8`, [search]),
    pool.query(`SELECT 'grant' AS type, gc.bdns_code AS id, gc.title, gc.purpose AS subtitle, gc.source_url AS "sourceUrl" FROM grant_calls gc WHERE gc.title ILIKE $1 OR gc.bdns_code ILIKE $1 OR gc.purpose ILIKE $1 ORDER BY gc.id DESC LIMIT 8`, [search]),
    pool.query(`SELECT 'budget' AS type, br.economic_code AS id, br.economic_code AS title, br.economic_level AS subtitle, ds.source_url AS "sourceUrl" FROM budget_records br JOIN data_sources ds ON ds.id = br.source_id WHERE br.economic_code ILIKE $1 ORDER BY br.id DESC LIMIT 8`, [search])
  ]);
  return [...contracts.rows, ...grants.rows, ...budgets.rows].slice(0, 20);
}

async function databaseCoverage() {
  const result = await pool.query(`
    SELECT ds.id, ds.name, ds.institution, ds.source_url, ds.format, ds.coverage_description,
      ds.last_checked_at, ds.last_imported_at,
      (SELECT COUNT(*) FROM budget_records br WHERE br.source_id = ds.id) AS budget_records,
      (SELECT COUNT(*) FROM contracts c WHERE c.source_id = ds.id) AS contract_records,
      (SELECT COUNT(*) FROM grant_calls gc WHERE gc.source_id = ds.id) AS grant_records
    FROM data_sources ds WHERE ds.is_official = TRUE ORDER BY ds.id`);
  return result.rows;
}

function getExecution() {
  return readJsonl(join(root, 'data', 'processed', 'igae', 'execution-2026-05.jsonl'));
}

function getTerritorialExecution() {
  return readJsonl(join(root, 'data', 'processed', 'ccaa', 'execution-2026-05.jsonl'));
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
  if (url.pathname === '/api/export.csv') {
    const entity = url.searchParams.get('entity') || 'contracts';
    const query = (url.searchParams.get('q') || '').trim();
    try {
      if (entity === 'contracts') return csv(res, 'contratos-placsp.csv', await databaseContracts(query, 1, 10000));
      if (entity === 'grants') return csv(res, 'convocatorias-bdns.csv', await databaseGrants(query, 1, 10000));
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
    catch (error) { const contracts = getContracts().filter(row => JSON.stringify(row).toLocaleLowerCase('es').includes(query)).slice(0, 20); return json(res, 200, { data: contracts.map(row => ({ type: 'contract', id: row.source_record_id, title: row.title, sourceUrl: row.source_url })), meta: { backend: 'jsonl-fallback', warning: error.message } }); }
  }
  if (url.pathname === '/api/coverage') {
    try { return json(res, 200, { data: await databaseCoverage(), meta: { backend: 'postgresql' } }); }
    catch (error) { return json(res, 200, { data: [], meta: { backend: 'unavailable', warning: error.message } }); }
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
