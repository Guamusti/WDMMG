import fullMadridAdmissions from '../../data/processed/admissions/madrid-2025-2026.json';
import ructUniversities from '../../data/processed/ruct/madrid-public-universities.json';

const madridSeedOffers = [
  { id:'ucm-informatica', university:'Universidad Complutense de Madrid', short:'UCM', degree:'Ingeniería Informática', campus:'Campus Moncloa', city:'Madrid', cutoff:10.175, branch:'Ingeniería y Arquitectura', places:null, source:'Comunidad de Madrid · notas 2025–2026' },
  { id:'ucm-software', university:'Universidad Complutense de Madrid', short:'UCM', degree:'Ingeniería del Software', campus:'Campus Moncloa', city:'Madrid', cutoff:10.036, branch:'Ingeniería y Arquitectura', places:null, source:'Comunidad de Madrid · notas 2025–2026' },
  { id:'ucm-computadores', university:'Universidad Complutense de Madrid', short:'UCM', degree:'Ingeniería de Computadores', campus:'Campus Moncloa', city:'Madrid', cutoff:9.311, branch:'Ingeniería y Arquitectura', places:null, source:'Comunidad de Madrid · notas 2025–2026' },
  { id:'ucm-datos', university:'Universidad Complutense de Madrid', short:'UCM', degree:'Ingeniería y Sistemas de Datos', campus:'Campus Moncloa', city:'Madrid', cutoff:11.128, branch:'Ingeniería y Arquitectura', places:null, source:'Comunidad de Madrid · notas 2025–2026' },
  { id:'ucm-mat-info', university:'Universidad Complutense de Madrid', short:'UCM', degree:'Matemáticas e Informática', campus:'Campus Moncloa', city:'Madrid', cutoff:11.507, branch:'Ciencias', places:null, source:'Comunidad de Madrid · notas 2025–2026' },
  { id:'ucm-double', university:'Universidad Complutense de Madrid', short:'UCM', degree:'Ingeniería Informática + ADE', campus:'Campus Moncloa', city:'Madrid', cutoff:11.589, branch:'Ingeniería y Arquitectura', places:null, source:'Comunidad de Madrid · notas 2025–2026', double:true },
  { id:'urjc-info-mostoles', university:'Universidad Rey Juan Carlos', short:'URJC', degree:'Ingeniería Informática', campus:'Móstoles', city:'Móstoles', cutoff:10.503, branch:'Ingeniería y Arquitectura', places:null, source:'URJC · notas de corte 2025–2026' },
  { id:'urjc-info-vicalvaro', university:'Universidad Rey Juan Carlos', short:'URJC', degree:'Ingeniería Informática', campus:'Vicálvaro', city:'Madrid', cutoff:10.036, branch:'Ingeniería y Arquitectura', places:null, source:'URJC · notas de corte 2025–2026' },
  { id:'urjc-software', university:'Universidad Rey Juan Carlos', short:'URJC', degree:'Ingeniería del Software', campus:'Móstoles', city:'Móstoles', cutoff:9.986, branch:'Ingeniería y Arquitectura', places:null, source:'URJC · notas de corte 2025–2026' },
  { id:'urjc-ia', university:'Universidad Rey Juan Carlos', short:'URJC', degree:'Inteligencia Artificial', campus:'Móstoles', city:'Móstoles', cutoff:10.428, branch:'Ingeniería y Arquitectura', places:null, source:'URJC · notas de corte 2025–2026' },
  { id:'uc3m-info-leganes', university:'Universidad Carlos III de Madrid', short:'UC3M', degree:'Ingeniería Informática', campus:'Leganés', city:'Leganés', cutoff:10.978, branch:'Ingeniería y Arquitectura', places:180, source:'UC3M · autoinforme de grado 2025–2026' },
  { id:'uc3m-info-colme', university:'Universidad Carlos III de Madrid', short:'UC3M', degree:'Ingeniería Informática', campus:'Colmenarejo', city:'Colmenarejo', cutoff:10.364, branch:'Ingeniería y Arquitectura', places:25, source:'UC3M · autoinforme de grado 2025–2026' },
  { id:'upm-info', university:'Universidad Politécnica de Madrid', short:'UPM', degree:'Ingeniería Informática', campus:'Campus Sur', city:'Madrid', cutoff:10.175, branch:'Ingeniería y Arquitectura', places:null, source:'Comunidad de Madrid · notas 2025–2026' },
  { id:'upm-software-pars', university:'Universidad Politécnica de Madrid', short:'UPM', degree:'Ingeniería del Software (PARS)', campus:'Campus Montegancedo', city:'Boadilla del Monte', cutoff:11.533, branch:'Ingeniería y Arquitectura', places:null, source:'Comunidad de Madrid · notas 2025–2026' },
  { id:'upm-org', university:'Universidad Politécnica de Madrid', short:'UPM', degree:'Ingeniería de Organización', campus:'Campus Sur', city:'Madrid', cutoff:12.636, branch:'Ingeniería y Arquitectura', places:null, source:'Comunidad de Madrid · notas 2025–2026' },
  { id:'upm-data', university:'Universidad Politécnica de Madrid', short:'UPM', degree:'Ingeniería y Sistemas de Datos', campus:'Campus Sur', city:'Madrid', cutoff:11.128, branch:'Ingeniería y Arquitectura', places:null, source:'Comunidad de Madrid · notas 2025–2026' },
  { id:'uah-info', university:'Universidad de Alcalá', short:'UAH', degree:'Ingeniería Informática', campus:'Campus Científico-Tecnológico', city:'Alcalá de Henares', cutoff:10.700, branch:'Ingeniería y Arquitectura', places:null, source:'Comunidad de Madrid · notas 2025–2026' },
  { id:'uah-info-ade', university:'Universidad de Alcalá', short:'UAH', degree:'Ingeniería Informática + ADE', campus:'Campus Científico-Tecnológico', city:'Alcalá de Henares', cutoff:10.436, branch:'Ingeniería y Arquitectura', places:null, source:'Comunidad de Madrid · notas 2025–2026', double:true },
  { id:'uah-telematica', university:'Universidad de Alcalá', short:'UAH', degree:'Ingeniería Telemática', campus:'Campus Científico-Tecnológico', city:'Alcalá de Henares', cutoff:7.575, branch:'Ingeniería y Arquitectura', places:null, source:'Comunidad de Madrid · notas 2025–2026' },
  { id:'uah-sistemas', university:'Universidad de Alcalá', short:'UAH', degree:'Ingeniería en Sistemas de Información', campus:'Campus Científico-Tecnológico', city:'Alcalá de Henares', cutoff:8.139, branch:'Ingeniería y Arquitectura', places:null, source:'Comunidad de Madrid · notas 2025–2026' },
  { id:'uah-industriales', university:'Universidad de Alcalá', short:'UAH', degree:'Ingeniería en Tecnologías Industriales', campus:'Campus Científico-Tecnológico', city:'Alcalá de Henares', cutoff:11.000, branch:'Ingeniería y Arquitectura', places:null, source:'Comunidad de Madrid · notas 2025–2026' },
  { id:'uam-info-mat', university:'Universidad Autónoma de Madrid', short:'UAM', degree:'Ingeniería Informática + Matemáticas', campus:'Cantoblanco', city:'Madrid', cutoff:13.136, branch:'Ciencias', places:null, source:'Comunidad de Madrid · notas 2025–2026', double:true },
  { id:'uam-filo-politica', university:'Universidad Autónoma de Madrid', short:'UAM', degree:'Filosofía, Política y Economía', campus:'Cantoblanco', city:'Madrid', cutoff:11.820, branch:'Ciencias Sociales y Jurídicas', places:null, source:'Comunidad de Madrid · notas 2025–2026' },
  { id:'uam-maestros', university:'Universidad Autónoma de Madrid', short:'UAM', degree:'Maestro Infantil + Maestro Primaria', campus:'Cantoblanco', city:'Madrid', cutoff:10.278, branch:'Ciencias Sociales y Jurídicas', places:null, source:'Comunidad de Madrid · notas 2025–2026', double:true },
  { id:'uc3m-ade', university:'Universidad Carlos III de Madrid', short:'UC3M', degree:'Administración de Empresas', campus:'Getafe', city:'Getafe', cutoff:11.516, branch:'Ciencias Sociales y Jurídicas', places:null, source:'Comunidad de Madrid · notas 2025–2026' },
  { id:'uc3m-datos', university:'Universidad Carlos III de Madrid', short:'UC3M', degree:'Ciencia e Ingeniería de Datos', campus:'Leganés', city:'Leganés', cutoff:11.556, branch:'Ingeniería y Arquitectura', places:null, source:'Comunidad de Madrid · notas 2025–2026' },
  { id:'uc3m-ia', university:'Universidad Carlos III de Madrid', short:'UC3M', degree:'Inteligencia Artificial', campus:'Leganés', city:'Leganés', cutoff:11.775, branch:'Ingeniería y Arquitectura', places:null, source:'Comunidad de Madrid · notas 2025–2026' },
  { id:'uc3m-ia-colme', university:'Universidad Carlos III de Madrid', short:'UC3M', degree:'Inteligencia Artificial', campus:'Colmenarejo', city:'Colmenarejo', cutoff:10.448, branch:'Ingeniería y Arquitectura', places:null, source:'Comunidad de Madrid · notas 2025–2026' },
  { id:'uc3m-matematica', university:'Universidad Carlos III de Madrid', short:'UC3M', degree:'Matemática Aplicada', campus:'Leganés', city:'Leganés', cutoff:12.024, branch:'Ciencias', places:null, source:'Comunidad de Madrid · notas 2025–2026' },
  { id:'uc3m-aero', university:'Universidad Carlos III de Madrid', short:'UC3M', degree:'Ingeniería Aeroespacial', campus:'Leganés', city:'Leganés', cutoff:13.300, branch:'Ingeniería y Arquitectura', places:null, source:'Comunidad de Madrid · notas 2025–2026' },
  { id:'uc3m-empresa-tec', university:'Universidad Carlos III de Madrid', short:'UC3M', degree:'Empresa y Tecnología', campus:'Getafe', city:'Getafe', cutoff:12.213, branch:'Ciencias Sociales y Jurídicas', places:null, source:'Comunidad de Madrid · notas 2025–2026' },
  { id:'urjc-videojuegos', university:'Universidad Rey Juan Carlos', short:'URJC', degree:'Diseño y Desarrollo de Videojuegos + Ingeniería de Computadores', campus:'Móstoles', city:'Móstoles', cutoff:11.102, branch:'Ingeniería y Arquitectura', places:null, source:'Comunidad de Madrid · notas 2025–2026', double:true },
  { id:'urjc-derecho-relaciones', university:'Universidad Rey Juan Carlos', short:'URJC', degree:'Derecho + Relaciones Internacionales', campus:'Fuenlabrada', city:'Fuenlabrada', cutoff:13.161, branch:'Ciencias Sociales y Jurídicas', places:null, source:'Comunidad de Madrid · notas 2025–2026', double:true },
  { id:'urjc-economia-mates', university:'Universidad Rey Juan Carlos', short:'URJC', degree:'Economía + Matemáticas', campus:'Móstoles', city:'Móstoles', cutoff:12.489, branch:'Ciencias Sociales y Jurídicas', places:null, source:'Comunidad de Madrid · notas 2025–2026', double:true },
  { id:'urjc-crimi-derecho', university:'Universidad Rey Juan Carlos', short:'URJC', degree:'Criminología + Derecho', campus:'Vicálvaro', city:'Madrid', cutoff:12.433, branch:'Ciencias Sociales y Jurídicas', places:null, source:'Comunidad de Madrid · notas 2025–2026', double:true },
  { id:'upm-datos-ai-monte', university:'Universidad Politécnica de Madrid', short:'UPM', degree:'Ciencia de Datos e Inteligencia Artificial', campus:'Montegancedo', city:'Boadilla del Monte', cutoff:11.899, branch:'Ingeniería y Arquitectura', places:null, source:'Comunidad de Madrid · notas 2025–2026' },
  { id:'upm-datos-ai-sur', university:'Universidad Politécnica de Madrid', short:'UPM', degree:'Ciencia de Datos e Inteligencia Artificial', campus:'Campus Sur', city:'Madrid', cutoff:12.139, branch:'Ingeniería y Arquitectura', places:null, source:'Comunidad de Madrid · notas 2025–2026' },
  { id:'upm-industriales', university:'Universidad Politécnica de Madrid', short:'UPM', degree:'Ingeniería en Tecnologías Industriales', campus:'Campus Sur', city:'Madrid', cutoff:12.114, branch:'Ingeniería y Arquitectura', places:null, source:'Comunidad de Madrid · notas 2025–2026' },
  { id:'upm-aero', university:'Universidad Politécnica de Madrid', short:'UPM', degree:'Ingeniería Aeroespacial', campus:'Campus Sur', city:'Madrid', cutoff:12.484, branch:'Ingeniería y Arquitectura', places:null, source:'Comunidad de Madrid · notas 2025–2026' }
];

const shortByUniversity = {
  'Universidad de Alcalá': 'UAH',
  'Universidad Autónoma de Madrid': 'UAM',
  'Universidad Carlos III de Madrid': 'UC3M',
  'Universidad Complutense de Madrid': 'UCM',
  'Universidad Politécnica de Madrid': 'UPM',
  'Universidad Rey Juan Carlos': 'URJC'
};
const universityByRuctCode = Object.fromEntries(ructUniversities.map(item => [item.ruct_code, item.name]));
const cleanPdf = value => String(value || '').replaceAll('�', '').replace(/\s+/g, ' ').trim();
const cityNames = ['Alcalá de Henares', 'Aranjuez', 'Alcorcón', 'Boadilla del Monte', 'Colmenarejo', 'Fuenlabrada', 'Getafe', 'Guadalajara', 'Leganés', 'Madrid', 'Móstoles'];
const fullOffers = fullMadridAdmissions.map((row, index) => {
  const universityName = universityByRuctCode[row.university_ruct_code] || cleanPdf(row.university_name_source);
  const rawDegree = cleanPdf(row.degree_name_source);
  const city = cityNames.find(name => rawDegree.endsWith(`(${name})`)) || (universityName === 'Universidad Carlos III de Madrid' ? 'Leganés' : universityName === 'Universidad Rey Juan Carlos' ? 'Móstoles' : universityName === 'Universidad de Alcalá' ? 'Alcalá de Henares' : 'Madrid');
  const campus = rawDegree.match(/\(([^()]+)\)$/)?.[1] || city;
  return { id:`madrid-${shortByUniversity[universityName] || 'oferta'}-${index + 1}`, university:universityName, short:shortByUniversity[universityName], ructCode:row.university_ruct_code, degree:rawDegree, campus, city, cutoff:row.cutoff_score, branch:cleanPdf(row.branch_name_source) || 'Rama pendiente de RUCT', places:null, double:/\s-\s/.test(rawDegree), durationYears:row.duration_years_source, ects:row.ects_source, source:'Comunidad de Madrid · notas 2025–2026', sourcePage:row.source_page };
});

const canonicalName = value => cleanPdf(value).toLowerCase().replace(/\([^)]*\)/g, '').replace(/\s+/g, ' ').replace(/\s[-+]\s/g, '+').trim();
const offerKey = offer => [offer.short, canonicalName(offer.degree), cleanPdf(offer.city).toLowerCase(), Number(offer.cutoff).toFixed(3)].join('|');
const mergedOffers = new Map();
// La selección inicial conserva sus URLs públicas; el extracto oficial aporta el resto.
[...madridSeedOffers, ...fullOffers].forEach(offer => { if (!mergedOffers.has(offerKey(offer))) mergedOffers.set(offerKey(offer), offer); });
export const madridOffers = [...mergedOffers.values()];
const ructByShort = Object.fromEntries(ructUniversities.map(item => [item.short, item.ruct_code]));

export const madridUniversities = [
  { short:'UCM', ructCode:ructByShort.UCM, name:'Universidad Complutense de Madrid', city:'Madrid', position:[40.448, -3.726], color:'#e35d48' },
  { short:'UPM', ructCode:ructByShort.UPM, name:'Universidad Politécnica de Madrid', city:'Madrid', position:[40.389, -3.628], color:'#ef9b44' },
  { short:'UC3M', ructCode:ructByShort.UC3M, name:'Universidad Carlos III de Madrid', city:'Leganés', position:[40.334, -3.764], color:'#e35d48' },
  { short:'URJC', ructCode:ructByShort.URJC, name:'Universidad Rey Juan Carlos', city:'Móstoles', position:[40.334, -3.881], color:'#ef9b44' },
  { short:'UAH', ructCode:ructByShort.UAH, name:'Universidad de Alcalá', city:'Alcalá de Henares', position:[40.482, -3.364], color:'#8a9c68' },
  { short:'UAM', ructCode:ructByShort.UAM, name:'Universidad Autónoma de Madrid', city:'Cantoblanco', position:[40.545, -3.696], color:'#8a9c68' }
];
