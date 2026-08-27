import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const dataPath = resolve(root, 'data/processed/admissions/madrid-2025-2026.json');
const sourceUrl = 'https://www.comunidad.madrid/docs/assets/2026/02/25/notas_de_corte_2025-26_publicacion_para_web.pdf?VersionId=TQubbLf9LLERJuuTNTnhd4CGSZZjgmUx';

const shortByCode = { '010':'UCM', '023':'UAM', '025':'UPM', '029':'UAH', '036':'UC3M', '056':'URJC' };
const cities = ['Alcalá de Henares','Aranjuez','Alcorcón','Boadilla del Monte','Colmenarejo','Fuenlabrada','Getafe','Guadalajara','Leganés','Madrid','Móstoles'];
function normalize(row, index) {
  const degree = String(row.degree_name_source || '').replaceAll('�', '').replace(/\s+/g, ' ').trim();
  const city = cities.find(name => degree.endsWith(`(${name})`)) || 'Madrid';
  return { id: `madrid-${row.university_ruct_code || 'unknown'}-${index + 1}`, university: row.university_name_source, short: shortByCode[row.university_ruct_code], universityRuctCode: row.university_ruct_code, degree, campus: city, city, double: /\s-\s/.test(degree), branch: String(row.branch_name_source || '').replaceAll('�', '').trim() || 'Rama pendiente de RUCT', cutoff: row.cutoff_score, scaleMax: row.score_scale_max, ects: row.ects_source, durationYears: row.duration_years_source, academicYear: row.academic_year, sourcePage: row.source_page, source: 'Comunidad de Madrid · notas 2025–2026', sourceUrl };
}

const server = createServer(async (request, response) => {
  response.setHeader('Access-Control-Allow-Origin', '*');
  response.setHeader('Content-Type', 'application/json; charset=utf-8');
  if (request.url === '/api/health') { response.end(JSON.stringify({ status: 'ok', service: 'atlas-api' })); return; }
  if (!request.url?.startsWith('/api/offers')) { response.statusCode = 404; response.end(JSON.stringify({ error: 'not_found' })); return; }
  try {
    const rows = JSON.parse(await readFile(dataPath, 'utf8')).map(normalize);
    const url = new URL(request.url, 'http://localhost');
    const q = (url.searchParams.get('q') || '').toLocaleLowerCase();
    const university = url.searchParams.get('university');
    const branch = url.searchParams.get('branch');
    const page = Math.max(1, Number(url.searchParams.get('page') || 1));
    const limit = Math.min(1000, Math.max(1, Number(url.searchParams.get('limit') || 25)));
    const filtered = rows.filter(row => (!q || `${row.degree} ${row.university}`.toLocaleLowerCase().includes(q)) && (!university || row.universityRuctCode === university) && (!branch || row.branch === branch));
    const start = (page - 1) * limit;
    response.end(JSON.stringify({ data: filtered.slice(start, start + limit), page, limit, total: filtered.length, source: sourceUrl }));
  } catch (error) { response.statusCode = 500; response.end(JSON.stringify({ error: 'data_unavailable', detail: error.message })); }
});

const port = Number(process.env.ATLAS_API_PORT || 8787);
server.listen(port, '127.0.0.1', () => console.log(`Atlas API listening on http://127.0.0.1:${port}`));
