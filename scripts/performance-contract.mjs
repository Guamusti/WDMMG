import { readdir, readFile, stat } from 'node:fs/promises';

const assetDirectory = 'dist/assets';
const assets = await readdir(assetDirectory);
const javascript = assets.filter(asset => asset.endsWith('.js'));
const html = await readFile('dist/index.html', 'utf8');
const initialEntry = javascript.find(asset => html.includes(`/assets/${asset}`));
const initialSize = initialEntry ? (await stat(`${assetDirectory}/${initialEntry}`)).size : 0;
const hasHashedAssets = assets.length > 0 && assets.every(asset => /-[A-Za-z0-9_-]+\.(?:js|css)$/.test(asset));
const checks = [
  ['production assets exist', assets.length > 0],
  ['initial entry is below 300 kB', initialSize > 0 && initialSize < 300_000],
  ['assets use content hashes', hasHashedAssets],
  ['map is code-split', javascript.some(asset => asset.startsWith('MadridMap-'))],
  ['national explorer is code-split', javascript.some(asset => asset.startsWith('NationalPagePaged-'))],
];
const failed = checks.filter(([, passed]) => !passed).map(([label]) => label);
if (failed.length) throw new Error(`Performance contract failed: ${failed.join(', ')}`);
console.log(`Performance contract passed: ${checks.length} checks; initial entry ${Math.round(initialSize / 1024)} kB`);
