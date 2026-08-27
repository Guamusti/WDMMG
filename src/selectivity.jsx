import React, { useMemo, useState } from 'react';

const parse = value => {
  const number = Number(String(value).replace(',', '.'));
  return Number.isFinite(number) && number >= 0 && number <= 10 ? number : null;
};

const format = value => value == null ? '—' : value.toFixed(3).replace('.', ',');

export function SelectivityCalculator({ onClose }) {
  const [bachillerato, setBachillerato] = useState('');
  const [mandatory, setMandatory] = useState(['', '', '', '']);
  const [optional, setOptional] = useState([{ name: 'Materia 1', grade: '', weight: '0.2' }, { name: 'Materia 2', grade: '', weight: '0.2' }]);
  const result = useMemo(() => {
    const bach = parse(bachillerato);
    const exams = mandatory.map(parse);
    if (bach == null || exams.some(value => value == null)) return { status: 'incomplete' };
    const phase = exams.reduce((sum, value) => sum + value, 0) / exams.length;
    const access = 0.6 * bach + 0.4 * phase;
    const additions = optional.map(item => { const grade = parse(item.grade); const weight = Number(item.weight); return grade != null && grade >= 5 && weight > 0 ? grade * weight : 0; }).sort((a, b) => b - a).slice(0, 2);
    return { phase, access, admission: access >= 5 && phase >= 4 ? Math.min(14, access + additions.reduce((sum, value) => sum + value, 0)) : null };
  }, [bachillerato, mandatory, optional]);
  const updateMandatory = (index, value) => setMandatory(values => values.map((item, position) => position === index ? value : item));
  const updateOptional = (index, key, value) => setOptional(values => values.map((item, position) => position === index ? { ...item, [key]: value } : item));
  return <div className="modal-backdrop" onClick={onClose}><div className="calculator-modal" role="dialog" aria-modal="true" aria-labelledby="calculator-title" onClick={event => event.stopPropagation()}><div className="modal-head"><div><div className="eyebrow">HERRAMIENTA DE ACCESO</div><h2 id="calculator-title">Calculadora de nota PAU</h2><p className="muted">Estima tu nota de admisión sobre 14.</p></div><button onClick={onClose} aria-label="Cerrar calculadora">×</button></div><div className="calculator-grid"><section><label>Nota media de Bachillerato<input inputMode="decimal" value={bachillerato} onChange={event => setBachillerato(event.target.value)} placeholder="8,50"/></label><h3>Fase obligatoria</h3><p className="calculator-help">Introduce las cuatro materias de la PAU en Madrid.</p>{['Lengua Castellana y Literatura','Historia de España / Filosofía','Lengua Extranjera','Materia de modalidad'].map((label, index) => <label key={label}>{label}<input inputMode="decimal" value={mandatory[index]} onChange={event => updateMandatory(index, event.target.value)} placeholder="0–10"/></label>)}<h3>Fase de admisión</h3><p className="calculator-help">Añade hasta dos materias superadas y su ponderación para el grado.</p>{optional.map((item, index) => <div className="optional-row" key={item.name}><label>{item.name}<input inputMode="decimal" value={item.grade} onChange={event => updateOptional(index, 'grade', event.target.value)} placeholder="0–10"/></label><label>Ponderación<select value={item.weight} onChange={event => updateOptional(index, 'weight', event.target.value)}><option value="0">No pondera</option><option value="0.1">0,1</option><option value="0.2">0,2</option></select></label></div>)}</section><aside className="calculator-result"><span className="eyebrow">TU RESULTADO</span><div><small>Nota de acceso · sobre 10</small><strong>{format(result.access)}</strong></div><div><small>Nota de admisión · sobre 14</small><strong>{format(result.admission)}</strong></div>{result.status === 'incomplete' ? <p>Completa Bachillerato y las cuatro materias obligatorias.</p> : result.admission == null ? <p>La fase obligatoria necesita al menos un 4 y la nota de acceso un 5 para añadir ponderaciones.</p> : <p>Se han sumado las dos mejores aportaciones ponderadas de las materias con nota igual o superior a 5.</p>}</aside></div><div className="calculator-note">Fórmula: 0,6 × Bachillerato + 0,4 × fase obligatoria + a × M1 + b × M2. Es una estimación: las ponderaciones dependen del grado y de la universidad.</div><a className="source-link" href="https://www.educacionfpydeportes.gob.es/ca/prensa/actualidad/2024/06/20240611-pau.html" target="_blank" rel="noreferrer">Consultar explicación oficial de la PAU ↗</a></div></div>;
}
