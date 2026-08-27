const SIIU = 'https://estadisticas.universidades.gob.es/jaxiPx/Datos.htm';
import informaticaEmployment from '../../data/processed/outcomes/informatica-2017-2018.json';
import madridUniversityContext from '../../data/processed/outcomes/madrid-university-context-2022-2023.json';
import madridUniversityEnrolment from '../../data/processed/outcomes/madrid-university-enrolment-2023-2024.json';
import madridUniversityGraduates from '../../data/processed/outcomes/madrid-university-graduates-2023-2024.json';
import fieldEmployment from '../../data/processed/outcomes/field-employment-2018-2019-four-years.json';

export const outcomeSources = {
  performance: `${SIIU}?file=Rendimiento_Exito_Eval_Grado_Univ.px&path=%2FUniversitaria%2FIndicadores%2F2024%2F1_Grado%2Fl0%2F`,
  dropout: `${SIIU}?file=Abandono_Grado_Univ.px&path=%2FUniversitaria%2FIndicadores%2F2023%2F1_Grado%2Fl0%2F`,
  graduation: `${SIIU}?file=Graduacion_Grado_Univ.px&path=%2FUniversitaria%2FIndicadores%2F2023%2F1_Grado%2Fl0%2F`,
  employment: 'https://estadisticas.universidades.gob.es/jaxiPx/Tabla.htm?L=0&file=Base_cotizacion_Sexo_Campo_Grado_Total.px&path=%2FUniversitaria%2FInsercion_laboral%2F2024%2FGRADO%2FCAP6_BMC%2F%2Fl0%2F&type=pcaxis',
  transcript: `${SIIU}?file=Nota_Expediente_Grado_Tot.px&path=%2FUniversitaria%2FIndicadores%2F2024%2F1_Grado%2Fl0%2F`,
  admissionMean: `${SIIU}?file=3_6_NI_Nota_media_Sex_Rama_Univ.px&path=%2FUniversitaria%2FAlumnado%2FEEU_2023%2FGradoCiclo%2FNuevoIngreso%2Fl0%2F`,
  newAdmissionCount: madridUniversityContext.new_admission_source_url
};

// Contexto universitario publicado por SIIU. No se presenta como dato específico de carrera.
export const universityOutcomeMetrics = madridUniversityContext.universities;
export const newAdmissionSource = madridUniversityContext.new_admission_source_url;
export const universityEnrolmentMetrics = madridUniversityEnrolment.universities;
export const enrolmentSource = madridUniversityEnrolment.source_url;
export const universityGraduateMetrics = madridUniversityGraduates.universities;
export const graduatesSource = madridUniversityGraduates.source_url;

// Referencia laboral por ámbito de estudio. No se atribuye como dato propio
// de una titulación: QEDU/SIIU puede ofrecer el ámbito cuando falta el cruce
// específico. La base de cotización no equivale a salario neto, medio o mediano.
const employmentMeta = {
  cohort: fieldEmployment.cohort,
  granularity: fieldEmployment.granularity,
  source: fieldEmployment.source,
  sourceUrl: fieldEmployment.source_url,
  officialDatasetUrl: informaticaEmployment.officialDatasetUrl,
  limitations: fieldEmployment.limitations
};
export const employmentByField = Object.fromEntries(Object.entries(fieldEmployment.fields).map(([key, metrics]) => [key, { ...metrics, ...employmentMeta }]));

export function employmentForOffer(offer) {
  const degree = String(offer?.degree || '').toLocaleLowerCase();
  // A field aggregate must never be presented as the result of a double degree
  // or a combined/international title. Keep the offer without a field match.
  if (/\s*[-–]\s+|\s+[-–]\s*|\s+\+\s+|\s+\/\s+/.test(degree)) return null;
  if (/informática|software|computadores|ciencia de datos|inteligencia artificial/.test(degree)) return employmentByField.informatica;
  if (/medicina/.test(degree)) return employmentByField.medicina;
  if (/enfermería/.test(degree)) return employmentByField.enfermeria;
  if (/periodismo/.test(degree)) return employmentByField.periodismo;
  if (/sociología/.test(degree)) return employmentByField.sociologia;
  if (/economía/.test(degree)) return employmentByField.economia;
  if (/derecho/.test(degree)) return employmentByField.derecho;
  if (/administración y dirección de empresas|\bade\b/.test(degree)) return employmentByField.ade;
  return null;
}
