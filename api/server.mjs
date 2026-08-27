import { createServer } from 'node:http';
import { readFile, stat } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const dataPath = resolve(root, 'data/processed/admissions/madrid-2025-2026.json');
const ructMatchesPath = resolve(root, 'data/processed/ruct/madrid-degree-matches.json');
const nationalDataPath = resolve(root, 'data/processed/admissions/national-2025-2026.json');
const nationalQualityPath = resolve(root, 'data/processed/admissions/national-2025-2026-quality.json');
const sourceUrl = 'https://www.comunidad.madrid/docs/assets/2026/02/25/notas_de_corte_2025-26_publicacion_para_web.pdf?VersionId=TQubbLf9LLERJuuTNTnhd4CGSZZjgmUx';

const shortByCode = { '010':'UCM', '023':'UAM', '025':'UPM', '029':'UAH', '036':'UC3M', '056':'URJC' };
const universityByCode = { '010':'Universidad Complutense de Madrid', '023':'Universidad Autónoma de Madrid', '025':'Universidad Politécnica de Madrid', '029':'Universidad de Alcalá', '036':'Universidad Carlos III de Madrid', '056':'Universidad Rey Juan Carlos' };
const jsonCache = new Map();
async function readJsonCached(path) {
  const modified = (await stat(path)).mtimeMs;
  const cached = jsonCache.get(path);
  if (cached?.modified === modified) return cached.value;
  const value = JSON.parse(await readFile(path, 'utf8'));
  jsonCache.set(path, { modified, value });
  return value;
}
function notModified(request, response, modified) {
  const etag = `W/"${Math.trunc(modified)}"`;
  response.setHeader('ETag', etag);
  response.setHeader('Cache-Control', 'public, max-age=0, must-revalidate');
  if (request.headers['if-none-match'] === etag) { response.statusCode = 304; response.end(); return true; }
  return false;
}
const cities = ['Alcalá de Henares','Aranjuez','Alcorcón','Boadilla del Monte','Colmenarejo','Fuenlabrada','Getafe','Guadalajara','Leganés','Madrid','Móstoles'];
function normalize(row, index, ructMatch) {
  const degree = String(row.degree_name_source || '').replaceAll('�', '').replace(/\s+/g, ' ').trim();
  const city = cities.find(name => degree.endsWith(`(${name})`)) || 'Madrid';
  return { id: `madrid-${row.university_ruct_code || 'unknown'}-${index + 1}`, university: universityByCode[row.university_ruct_code] || String(row.university_name_source || '').trim(), short: shortByCode[row.university_ruct_code], universityRuctCode: row.university_ruct_code, degree, campus: city, city, double: /\s-\s/.test(degree), branch: String(row.branch_name_source || '').replaceAll('�', '').trim() || 'Rama pendiente de RUCT', cutoff: row.cutoff_score, scaleMax: row.score_scale_max, ects: row.ects_source, durationYears: row.duration_years_source, academicYear: row.academic_year, admissionRound: row.admission_round, admissionGroup: row.admission_group, ructMatchStatus: ructMatch?.status || 'pending', ructMatchMethod: ructMatch?.match_method || 'not_available', ructDegreeCode: ructMatch?.ruct_degree_code || null, ructDegreeName: ructMatch?.ruct_degree_name || null, ructSourceUrl: ructMatch?.ruct_source_url || null, ructField: ructMatch?.ruct_field || null, ructCenters: ructMatch?.ruct_centers || [], sourcePage: row.source_page, source: 'Comunidad de Madrid · notas 2025–2026', sourceUrl };
}
// Enriquecimiento separado para no mezclar la normalización de admisión con
// la identidad RUCT ni con la clasificación estructural del programa.
const normalizeAdmissionBase = normalize;
normalize = (row, index, ructMatch) => {
  const offer = normalizeAdmissionBase(row, index, ructMatch);
  return { ...offer, ructCenters: offer.ructCenters?.length ? offer.ructCenters : null, programType: ructMatch?.program_type || (offer.double ? 'double_degree' : 'degree'), componentNames: ructMatch?.component_names || [] };
};

function normalizeNational(row) {
  return { id: row.id, community: row.community, university: row.university, universityRuctCode: row.university_ruct_code, degree: row.degree, branch: row.branch, field: row.field, ructDegreeCode: row.ruct_degree_code, centers: row.ruct_centers || [], center: row.center || null, campus: row.campus, city: row.campus, places: row.places ?? null, sourceGroup: row.source_group ?? null, waitlistPosition: row.waitlist_position ?? null, sourceProcess: row.source_process ?? null, sourceDate: row.source_date ?? null, cutoff: row.cutoff_score, scaleMax: 14, academicYear: row.academic_year, admissionRound: row.admission_round, admissionGroup: row.admission_group, sourcePage: row.source_page, source: `Fuente oficial · ${row.community} · notas ${row.academic_year}`, sourceUrl: row.source_url };
}

const server = createServer(async (request, response) => {
  response.setHeader('Access-Control-Allow-Origin', '*');
  response.setHeader('Content-Type', 'application/json; charset=utf-8');
  if (request.url === '/api/health') { response.end(JSON.stringify({ status: 'ok', service: 'atlas-api' })); return; }
  if (request.url === '/api/coverage') {
    try { const modified = (await stat(nationalQualityPath)).mtimeMs; if (!notModified(request, response, modified)) response.end(JSON.stringify(await readJsonCached(nationalQualityPath))); } catch (error) { response.statusCode = 500; response.end(JSON.stringify({ error: 'coverage_unavailable', detail: error.message })); }
    return;
  }
  if (!request.url?.startsWith('/api/offers') && !request.url?.startsWith('/api/national-offers')) { response.statusCode = 404; response.end(JSON.stringify({ error: 'not_found' })); return; }
  try {
    const url = new URL(request.url, 'http://localhost');
    const national = url.pathname === '/api/national-offers';
    const dataFile = national ? nationalDataPath : dataPath;
    const modifiedFiles = await Promise.all([stat(dataFile), ...(national ? [] : [stat(ructMatchesPath)])]);
    const modified = Math.max(...modifiedFiles.map(file => file.mtimeMs));
    if (notModified(request, response, modified)) return;
    const ructMatches = national ? [] : await readJsonCached(ructMatchesPath);
    const ructByAdmissionId = new Map(ructMatches.map(match => [match.admission_id, match]));
    const rows = (await readJsonCached(dataFile)).map((row, index) => national ? normalizeNational(row) : normalize(row, index, ructByAdmissionId.get(`madrid:${index + 1}`)));
    const q = (url.searchParams.get('q') || '').toLocaleLowerCase();
    const university = url.searchParams.get('university');
    const branch = url.searchParams.get('branch');
    const field = url.searchParams.get('field');
    const community = url.searchParams.get('community');
    const admissionRound = url.searchParams.get('admissionRound');
    const admissionGroup = url.searchParams.get('admissionGroup');
    const page = Math.max(1, Number(url.searchParams.get('page') || 1));
    const limit = Math.min(5000, Math.max(1, Number(url.searchParams.get('limit') || 25)));
    const filtered = rows.filter(row => (!q || `${row.degree} ${row.university} ${row.center || ''}`.toLocaleLowerCase().includes(q)) && (!university || (national ? row.university === university : row.universityRuctCode === university)) && (!branch || row.branch === branch) && (!field || row.field === field) && (!community || row.community === community) && (!admissionRound || row.admissionRound === admissionRound) && (!admissionGroup || row.admissionGroup === admissionGroup));
    const start = (page - 1) * limit;
    response.end(JSON.stringify({ data: filtered.slice(start, start + limit), page, limit, total: filtered.length, source: national ? 'data/processed/admissions/national-2025-2026.json' : sourceUrl }));
  } catch (error) { response.statusCode = 500; response.end(JSON.stringify({ error: 'data_unavailable', detail: error.message })); }
});

const port = Number(process.env.ATLAS_API_PORT || 8787);
server.listen(port, '127.0.0.1', () => console.log(`Atlas API listening on http://127.0.0.1:${port}`));
