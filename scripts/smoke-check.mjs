import { readFile } from 'node:fs/promises';

const frontendPort = (await readFile('.atlas-frontend-port', 'utf8')).trim();
const { port: apiPort } = JSON.parse((await readFile('public/api-port.json', 'utf8')).replace(/^\uFEFF/, ''));
const expectedMadrid = JSON.parse(await readFile('data/processed/admissions/madrid-2025-2026.json', 'utf8')).length;
const expectedAndalucia = JSON.parse(await readFile('data/processed/admissions/andalucia-2025-2026.json', 'utf8')).length;
const expectedCastillaLeon = JSON.parse(await readFile('data/processed/admissions/castilla-leon-2025-2026.json', 'utf8')).length;
const expectedSalamanca = JSON.parse(await readFile('data/processed/admissions/salamanca-2025-2026.json', 'utf8')).length;
const expectedCantabria = JSON.parse(await readFile('data/processed/admissions/cantabria-2025-2026.json', 'utf8')).length;
const expectedNavarra = JSON.parse(await readFile('data/processed/admissions/navarra-2025-2026.json', 'utf8')).length;
const expectedAsturias = JSON.parse(await readFile('data/processed/admissions/asturias-2025-2026.json', 'utf8')).length;
const frontend = `http://127.0.0.1:${frontendPort}`;
const api = `http://127.0.0.1:${apiPort}`;

async function expectOk(url, label) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`${label}: HTTP ${response.status}`);
  return response;
}

const page = await expectOk(`${frontend}/`, 'frontend');
if (!(await page.text()).includes('/src/main.jsx')) throw new Error('frontend: Vite entrypoint missing');
const proxiedMadrid = await (await expectOk(`${frontend}/api/offers?limit=1`, 'Vite API proxy')).json();
if (proxiedMadrid.total !== expectedMadrid || !proxiedMadrid.data[0]?.sourceUrl) throw new Error('Vite API proxy: catalog contract missing');
const enrichedOffer = await (await expectOk(`${frontend}/api/offers?q=antropología&limit=1`, 'RUCT enrichment')).json();
if (!enrichedOffer.data[0]?.ructDegreeCode || !enrichedOffer.data[0]?.ructSourceUrl || !enrichedOffer.data[0]?.ructCenters?.length) throw new Error('RUCT enrichment: detail fields missing');
const pendingOffer = await (await expectOk(`${frontend}/api/offers?q=administraci%C3%B3n&university=010&limit=1000`, 'RUCT pending status')).json();
if (!pendingOffer.data.some(row => row.ructMatchStatus === 'pending')) throw new Error('RUCT pending status: missing explicit status');
const programmeCatalog = await (await expectOk(`${frontend}/api/offers?q=inform%C3%A1tica&limit=1000`, 'programme classification')).json();
if (!programmeCatalog.data.some(row => row.programType === 'double_degree' && row.componentNames?.length >= 2)) throw new Error('Programme classification: double-degree components missing');
await expectOk(`${api}/api/health`, 'health');

const madrid = await (await expectOk(`${api}/api/offers?limit=1`, 'Madrid offers')).json();
if (madrid.total !== expectedMadrid || !madrid.data[0]?.sourceUrl) throw new Error('Madrid offers: incomplete source contract');

const nationalResponse = await expectOk(`${api}/api/national-offers?limit=1&admissionRound=ordinary&admissionGroup=group_1`, 'national offers');
const national = await nationalResponse.json();
if (!national.total || !national.data[0]?.admissionRound || !national.data[0]?.admissionGroup) throw new Error('National offers: admission dimensions missing');
const andalucia = await (await expectOk(`${api}/api/national-offers?community=Andaluc%C3%ADa&limit=1`, 'Andalucía offers')).json();
if (andalucia.total !== expectedAndalucia || !andalucia.data[0]?.branch || !andalucia.data[0]?.center) throw new Error('Andalucía offers: branch/center contract missing');
const castillaLeon = await (await expectOk(`${api}/api/national-offers?community=Castilla%20y%20Le%C3%B3n&limit=1`, 'Castilla y León offers')).json();
if (castillaLeon.total !== expectedCastillaLeon + expectedSalamanca || !castillaLeon.data[0]?.cutoff) throw new Error('Castilla y León offers: source contract missing');
const salamanca = await (await expectOk(`${api}/api/national-offers?community=Castilla%20y%20Le%C3%B3n&university=Universidad%20de%20Salamanca&limit=1`, 'Salamanca offers')).json();
if (salamanca.total !== expectedSalamanca || !salamanca.data[0]?.cutoff) throw new Error('Salamanca offers: source contract missing');
const cantabria = await (await expectOk(`${api}/api/national-offers?community=Cantabria&limit=1`, 'Cantabria offers')).json();
if (cantabria.total !== expectedCantabria || cantabria.data[0]?.admissionRound !== 'last_call') throw new Error('Cantabria offers: round/source contract missing');
const navarra = await (await expectOk(`${api}/api/national-offers?community=Navarra&limit=1`, 'Navarra offers')).json();
if (navarra.total !== expectedNavarra || !navarra.data[0]?.sourceUrl || !['last_call', 'extraordinary'].includes(navarra.data[0]?.admissionRound)) throw new Error('Navarra offers: round/source contract missing');
const asturias = await (await expectOk(`${api}/api/national-offers?community=Asturias&limit=1`, 'Asturias offers')).json();
if (asturias.total !== expectedAsturias || asturias.data[0]?.admissionRound !== 'first_call' || !asturias.data[0]?.places) throw new Error('Asturias offers: round/places contract missing');

const etag = nationalResponse.headers.get('etag');
if (!etag || !nationalResponse.headers.get('cache-control')) throw new Error('National offers: HTTP cache headers missing');
const cached = await fetch(`${api}/api/national-offers?limit=1`, { headers: { 'If-None-Match': etag } });
if (cached.status !== 304) throw new Error(`National offers: expected 304, got ${cached.status}`);

await expectOk(`${api}/api/coverage`, 'coverage');
console.log(`Smoke check passed: frontend ${frontendPort}, API ${apiPort}, Madrid ${madrid.total}, national filtered ${national.total}`);
