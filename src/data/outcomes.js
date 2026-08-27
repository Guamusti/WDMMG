const SIIU = 'https://estadisticas.universidades.gob.es/jaxiPx/Datos.htm';

export const outcomeSources = {
  performance: `${SIIU}?file=Rendimiento_Exito_Eval_Grado_Univ.px&path=%2FUniversitaria%2FIndicadores%2F2024%2F1_Grado%2Fl0%2F`,
  dropout: `${SIIU}?file=Abandono_Grado_Univ.px&path=%2FUniversitaria%2FIndicadores%2F2023%2F1_Grado%2Fl0%2F`,
  graduation: `${SIIU}?file=Graduacion_Grado_Univ.px&path=%2FUniversitaria%2FIndicadores%2F2023%2F1_Grado%2Fl0%2F`,
  employment: 'https://estadisticas.universidades.gob.es/jaxiPx/Tabla.htm?L=0&file=Base_cotizacion_Sexo_Campo_Grado_Total.px&path=%2FUniversitaria%2FInsercion_laboral%2F2024%2FGRADO%2FCAP6_BMC%2F%2Fl0%2F&type=pcaxis',
  transcript: `${SIIU}?file=Nota_Expediente_Grado_Tot.px&path=%2FUniversitaria%2FIndicadores%2F2024%2F1_Grado%2Fl0%2F`
};

// Contexto universitario publicado por SIIU. No se presenta como dato específico de carrera.
export const universityOutcomeMetrics = {
  UAH: { performance: 82.75, dropout: 11.47, graduation: 56.65 },
  UAM: { performance: 88.94, dropout: 10.78, graduation: 68.59 },
  UC3M: { performance: 89.10, dropout: 11.26, graduation: 64.51 },
  UCM: { performance: 83.57, dropout: 13.64, graduation: 57.03 },
  UPM: { performance: 67.23, dropout: 16.19, graduation: null },
  URJC: { performance: 80.08, dropout: 13.40, graduation: null }
};
