import { readFile } from 'node:fs/promises';

const files = {
  main: await readFile('src/main.jsx', 'utf8'),
  national: await readFile('src/NationalPagePaged.jsx', 'utf8'),
  styles: await readFile('src/styles.css', 'utf8'),
  outcomes: await readFile('src/outcomes.css', 'utf8'),
};

const checks = [
  ['main table has an accessible caption', files.main.includes('<caption className="sr-only">')],
  ['national table has an accessible caption', files.national.includes('<caption className="sr-only">')],
  ['main table headers expose their scope', files.main.includes('<th scope="col">')],
  ['national table headers expose their scope', files.national.includes('<th scope="col">')],
  ['focus-visible styles exist', files.styles.includes(':focus-visible')],
  ['reduced-motion preference is respected', files.styles.includes('prefers-reduced-motion')],
  ['dialogs expose their role and modal state', files.main.includes('role="dialog"') && files.main.includes('aria-modal="true"')],
  ['loading/results states are announced', files.main.includes('role="status"') && files.national.includes('aria-live="polite"')],
  ['responsive layout breakpoints exist', files.styles.includes('@media(max-width:800px)') && files.outcomes.includes('@media(max-width:600px)')],
];

const failed = checks.filter(([, passed]) => !passed).map(([label]) => label);
if (failed.length) throw new Error(`Accessibility contract failed: ${failed.join(', ')}`);
console.log(`Accessibility contract passed: ${checks.length} checks`);
