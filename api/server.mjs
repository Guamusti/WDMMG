import { createServer } from 'node:http';
import { existsSync, readFileSync } from 'node:fs';
import { join } from 'node:path';

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

function getExecution() {
  return readJsonl(join(root, 'data', 'processed', 'igae', 'execution-2026-05.jsonl'));
}

function overview() {
  const rows = getExecution().filter(row => row.classification_level === 'chapter');
  if (!rows.length) return { dataStatus: 'awaiting_validated_ingestion', budget: null, execution: null, contracts: null, grants: null };
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

const server = createServer((req, res) => {
  const url = new URL(req.url, `http://${req.headers.host}`);
  if (req.method !== 'GET') return json(res, 405, { error: 'method_not_allowed' });
  if (url.pathname === '/api/health') return json(res, 200, { ok: true, service: 'dinero-publico-api', data: { contracts: getContracts().length } });
  if (url.pathname === '/api/overview') return json(res, 200, overview());
  if (url.pathname === '/api/budgets') return json(res, 200, { data: getExecution(), meta: { total: getExecution().length, dataStatus: getExecution().length ? 'imported' : 'awaiting_validated_ingestion' } });
  if (url.pathname === '/api/contracts') {
    const query = (url.searchParams.get('q') || '').toLocaleLowerCase('es');
    const page = Math.max(1, Number(url.searchParams.get('page') || 1));
    const pageSize = Math.min(100, Math.max(1, Number(url.searchParams.get('pageSize') || 25)));
    const all = getContracts().filter(row => !query || JSON.stringify(row).toLocaleLowerCase('es').includes(query));
    return json(res, 200, { data: all.slice((page - 1) * pageSize, page * pageSize), meta: { page, pageSize, total: all.length, dataStatus: all.length ? 'imported' : 'awaiting_validated_ingestion' } });
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
