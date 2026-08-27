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

function json(res, status, body) {
  res.writeHead(status, { 'content-type': 'application/json; charset=utf-8', 'access-control-allow-origin': '*' });
  res.end(JSON.stringify(body));
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

function getExecution() {
  return readJsonl(join(root, 'data', 'processed', 'igae', 'execution-2026-05.jsonl'));
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
  if (url.pathname === '/api/search') {
    const query = (url.searchParams.get('q') || '').trim().toLocaleLowerCase('es');
    if (!query) return json(res, 200, { data: [] });
    const contracts = getContracts().filter(row => JSON.stringify(row).toLocaleLowerCase('es').includes(query)).slice(0, 20);
    return json(res, 200, { data: contracts.map(row => ({ type: 'contract', id: row.source_record_id, title: row.title, sourceUrl: row.source_url })) });
  }
  return json(res, 404, { error: 'not_found' });
});

server.listen(port, '127.0.0.1', () => console.log(`Dinero Público API: http://localhost:${port}`));
