import { readFile } from 'node:fs/promises';

const frontendPort = (await readFile('.atlas-frontend-port', 'utf8')).trim();
const { port: apiPort } = JSON.parse((await readFile('public/api-port.json', 'utf8')).replace(/^\uFEFF/, ''));
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
if (proxiedMadrid.total < 459 || !proxiedMadrid.data[0]?.sourceUrl) throw new Error('Vite API proxy: catalog contract missing');
await expectOk(`${api}/api/health`, 'health');

const madrid = await (await expectOk(`${api}/api/offers?limit=1`, 'Madrid offers')).json();
if (madrid.total < 459 || !madrid.data[0]?.sourceUrl) throw new Error('Madrid offers: incomplete source contract');

const nationalResponse = await expectOk(`${api}/api/national-offers?limit=1&admissionRound=ordinary&admissionGroup=group_1`, 'national offers');
const national = await nationalResponse.json();
if (!national.total || !national.data[0]?.admissionRound || !national.data[0]?.admissionGroup) throw new Error('National offers: admission dimensions missing');

const etag = nationalResponse.headers.get('etag');
if (!etag || !nationalResponse.headers.get('cache-control')) throw new Error('National offers: HTTP cache headers missing');
const cached = await fetch(`${api}/api/national-offers?limit=1`, { headers: { 'If-None-Match': etag } });
if (cached.status !== 304) throw new Error(`National offers: expected 304, got ${cached.status}`);

await expectOk(`${api}/api/coverage`, 'coverage');
console.log(`Smoke check passed: frontend ${frontendPort}, API ${apiPort}, Madrid ${madrid.total}, national filtered ${national.total}`);
