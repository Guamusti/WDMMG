import { useEffect, useMemo, useState } from 'react';
import { ArrowUpDown, ExternalLink } from 'lucide-react';
import { CircleMarker, MapContainer, TileLayer, Tooltip } from 'react-leaflet';

const ALL = 'Todas las comunidades';
const ALL_UNIVERSITIES = 'Todas las universidades';
const ALL_BRANCHES = 'Todas las ramas';
const ALL_FIELDS = 'Todos los campos RUCT';
const ALL_ROUNDS = 'Todas las convocatorias';
const ALL_GROUPS = 'Todos los cupos';
const roundLabel = value => ({ assignment_1: 'Primera asignación', first_call: 'Primera fase', ordinary: 'Ordinaria', extraordinary: 'Extraordinaria', last_call: 'Última lista', definitive: 'Definitiva' }[value] || value);
const groupLabel = value => value === 'group_1' ? 'Grupo 1 / general' : value === 'n' ? 'Cupo general (N)' : value ? `Cupo ${value.toUpperCase()}` : 'Cupo no publicado';
const coordinates = {
  'Campus de Ourense': [42.336, -7.864], 'Campus de Pontevedra': [42.431, -8.644],
  'Campus de Vigo': [42.240, -8.720], 'Campus de Santiago': [42.878, -8.544],
  'Campus de Lugo': [43.012, -7.556], 'Campus da Coruña': [43.362, -8.411],
  'Campus de Ferrol': [43.489, -8.219], Zaragoza: [41.649, -0.889],
  Huesca: [42.136, -0.408], Teruel: [40.345, -1.106], 'La Almunia': [41.476, -1.375],
};
const number = value => Number(String(value).replace(',', '.'));
const format = value => Number(value).toFixed(3).replace('.', ',');
const percentile = (value, rows) => {
  const valid = rows.filter(row => Number.isFinite(row.cutoff));
  return valid.length ? Math.round(((valid.filter(row => row.cutoff <= value).length - 0.5) / valid.length) * 100) : null;
};
const scopedPercentiles = (row, rows) => ({
  national: percentile(row.cutoff, rows),
  community: percentile(row.cutoff, rows.filter(candidate => candidate.community === row.community)),
  branch: row.branch ? percentile(row.cutoff, rows.filter(candidate => candidate.branch === row.branch)) : null,
  field: row.field ? percentile(row.cutoff, rows.filter(candidate => candidate.field === row.field)) : null,
});

export default function NationalPagePaged({ onBack }) {
  const [rows, setRows] = useState([]);
  const [query, setQuery] = useState('');
  const [community, setCommunity] = useState(ALL);
  const [university, setUniversity] = useState(ALL_UNIVERSITIES);
  const [branch, setBranch] = useState(ALL_BRANCHES);
  const [field, setField] = useState(ALL_FIELDS);
  const [round, setRound] = useState(ALL_ROUNDS);
  const [group, setGroup] = useState(ALL_GROUPS);
  const [mode, setMode] = useState('intersection');
  const [draftScore, setDraftScore] = useState('');
  const [draftTolerance, setDraftTolerance] = useState('0');
  const [applied, setApplied] = useState({ query: '', community: ALL, university: ALL_UNIVERSITIES, branch: ALL_BRANCHES, field: ALL_FIELDS, round: ALL_ROUNDS, group: ALL_GROUPS, mode: 'intersection', score: '', tolerance: '0' });
  const [sort, setSort] = useState('cutoff');
  const [page, setPage] = useState(1);
  const [error, setError] = useState('');

  useEffect(() => {
    fetch('/api/national-offers?limit=5000')
      .then(response => response.ok ? response.json() : Promise.reject(new Error('No se pudo cargar el catálogo nacional')))
      .then(payload => setRows(payload.data || []))
      .catch(reason => setError(reason.message));
  }, []);

  const communities = [ALL, ...new Set(rows.map(row => row.community).filter(Boolean))];
  const universities = [ALL_UNIVERSITIES, ...new Set(rows.map(row => row.university).filter(Boolean))].sort((a, b) => a === ALL_UNIVERSITIES ? -1 : b === ALL_UNIVERSITIES ? 1 : a.localeCompare(b));
  const branches = [ALL_BRANCHES, ...new Set(rows.map(row => row.branch).filter(Boolean))].sort((a, b) => a === ALL_BRANCHES ? -1 : b === ALL_BRANCHES ? 1 : a.localeCompare(b));
  const fields = [ALL_FIELDS, ...new Set(rows.map(row => row.field).filter(Boolean))];
  const rounds = [ALL_ROUNDS, ...new Set(rows.map(row => row.admissionRound).filter(Boolean))];
  const groups = [ALL_GROUPS, ...new Set(rows.map(row => row.admissionGroup).filter(Boolean))];
  const filters = [query, community !== ALL, university !== ALL_UNIVERSITIES, branch !== ALL_BRANCHES, field !== ALL_FIELDS, round !== ALL_ROUNDS, group !== ALL_GROUPS, draftScore.trim()].filter(Boolean).length;
  const filtered = useMemo(() => {
    const value = number(applied.score);
    const textMatches = row => !applied.query || `${row.degree} ${row.university} ${row.campus || ''} ${row.center || ''}`.toLocaleLowerCase().includes(applied.query.toLocaleLowerCase());
    const selectors = [
      applied.community !== ALL ? row => row.community === applied.community : null,
      applied.university !== ALL_UNIVERSITIES ? row => row.university === applied.university : null,
      applied.branch !== ALL_BRANCHES ? row => row.branch === applied.branch : null,
      applied.field !== ALL_FIELDS ? row => row.field === applied.field : null,
      applied.round !== ALL_ROUNDS ? row => row.admissionRound === applied.round : null,
      applied.group !== ALL_GROUPS ? row => row.admissionGroup === applied.group : null,
      applied.score ? row => Number.isFinite(value) && row.cutoff <= value + Number(applied.tolerance) : null,
    ].filter(Boolean);
    return rows
      .filter(row => textMatches(row)
        && (selectors.length === 0 || (applied.mode === 'union' ? selectors.some(selector => selector(row)) : selectors.every(selector => selector(row))))
      )
      .sort((a, b) => sort === 'name' ? a.degree.localeCompare(b.degree) : b.cutoff - a.cutoff);
  }, [rows, applied, sort]);
  const pageCount = Math.max(1, Math.ceil(filtered.length / 50));
  const visible = filtered.slice((page - 1) * 50, page * 50);
  const apply = () => { setApplied({ query, community, university, branch, field, round, group, mode, score: draftScore, tolerance: draftTolerance }); setPage(1); };
  const points = [...new Set(rows.map(row => row.campus).filter(campus => coordinates[campus]))]
    .map(campus => ({ campus, position: coordinates[campus], count: rows.filter(row => row.campus === campus).length }));

  return <div className="app national-page">
    <header className="topbar"><button className="route-back" onClick={onBack}>← Volver al Atlas</button><div className="brand"><span className="brand-mark">A</span><span>ATLAS <i>UNIVERSITARIO</i></span></div><div className="year">ESPAÑA · 2025—26</div></header>
    <main>
      <div className="route-kicker">EXPLORADOR NACIONAL · DATOS PROCESADOS</div>
      <h1 className="route-title">¿Qué puedes estudiar en España?</h1>
      <p className="route-subtitle">{rows.length || '…'} observaciones oficiales en {communities.length > 1 ? communities.length - 1 : '…'} comunidades, con fuente y convocatoria conservadas.</p>
      <div className="national-map-card"><div className="national-map-heading"><div><div className="eyebrow">MAPA NACIONAL</div><strong>Campus con notas procesadas</strong></div><small>Ubicación orientativa · no es el centro RUCT exacto</small></div><MapContainer center={[41.8, -2.5]} zoom={6} scrollWheelZoom={false} className="national-map"><TileLayer attribution="&copy; OpenStreetMap" url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />{points.map(point => <CircleMarker key={point.campus} center={point.position} radius={7} pathOptions={{ color: '#9b4e3e', fillColor: '#d16c52', fillOpacity: .9 }}><Tooltip><strong>{point.campus}</strong><br />{point.count} ofertas</Tooltip></CircleMarker>)}</MapContainer></div>
      <div className="national-controls">
        <label>Buscar carrera o universidad<input value={query} onChange={event => setQuery(event.target.value)} placeholder="Informática, Zaragoza…" /></label>
        <label>Comunidad<select value={community} onChange={event => setCommunity(event.target.value)}>{communities.map(option => <option key={option}>{option}</option>)}</select></label>
        <label>Universidad<select value={university} onChange={event => setUniversity(event.target.value)}>{universities.map(option => <option key={option}>{option}</option>)}</select></label>
        <label>Rama<select value={branch} onChange={event => setBranch(event.target.value)}>{branches.map(option => <option key={option}>{option}</option>)}</select></label>
        <label>Campo RUCT<select value={field} onChange={event => setField(event.target.value)}>{fields.map(option => <option key={option}>{option}</option>)}</select></label>
        <label>Convocatoria<select value={round} onChange={event => setRound(event.target.value)}>{rounds.map(option => <option key={option} value={option}>{option === ALL_ROUNDS ? option : roundLabel(option)}</option>)}</select></label>
        <label>Cupo<select value={group} onChange={event => setGroup(event.target.value)}>{groups.map(option => <option key={option} value={option}>{option === ALL_GROUPS ? option : groupLabel(option)}</option>)}</select></label>
        <label>Combinar<select value={mode} onChange={event => setMode(event.target.value)}><option value="intersection">Todos los filtros</option><option value="union">Cualquier filtro</option></select></label>
        <label>Tu nota<input inputMode="decimal" value={draftScore} onChange={event => setDraftScore(event.target.value)} placeholder="12,40" /></label>
        <label>Tolerancia<select value={draftTolerance} onChange={event => setDraftTolerance(event.target.value)}><option value="0">Sin tolerancia</option><option value="0.1">+0,1</option><option value="0.2">+0,2</option><option value="0.3">+0,3</option><option value="0.5">+0,5</option></select></label>
        <button className="apply-filters" onClick={apply}>Aplicar {filters} {filters === 1 ? 'filtro' : 'filtros'}</button>
        <button className="sort" onClick={() => setSort(sort === 'cutoff' ? 'name' : 'cutoff')}><ArrowUpDown size={15} /> {sort === 'cutoff' ? 'Ordenar por nota' : 'Ordenar por nombre'}</button>
      </div>
      {error ? <div className="national-empty"><strong>{error}</strong><p>Comprueba que has iniciado el proyecto con <code>iniciar.bat</code>.</p></div> : <>
        <div className="national-summary" role="status" aria-live="polite"><strong>{filtered.length}</strong> resultados · página {page} de {pageCount}{applied.score && ` · hasta ${format(number(applied.score) + Number(applied.tolerance))}`}</div>
        <div className="national-table-wrap"><table><thead><tr><th>CARRERA</th><th>UNIVERSIDAD · CENTRO</th><th>COMUNIDAD</th><th>NOTA</th><th>PLAZAS</th><th>CONVOCATORIA · CUPO</th><th>PERCENTILES</th><th>FUENTE</th></tr></thead><tbody>{visible.map(row => { const scores = scopedPercentiles(row, rows); return <tr key={row.id}><td><strong>{row.degree}</strong></td><td>{row.university}<small>{row.center || row.campus || 'Centro no publicado'}</small></td><td>{row.community}</td><td><b>{format(row.cutoff)}</b><small>/ 14</small></td><td>{row.places == null ? '—' : row.places}</td><td><small>{roundLabel(row.admissionRound)}</small><small>{groupLabel(row.admissionGroup)}{row.sourceGroup ? ` · grupo fuente ${row.sourceGroup}` : ''}</small>{row.sourceProcess && <small>{row.sourceProcess}{row.sourceDate ? ` · ${row.sourceDate}` : ''}</small>}{row.waitlistPosition && <small>Lista de espera: {row.waitlistPosition}</small>}</td><td><b>{scores.national === null ? '—' : `${scores.national}º`}</b><small>Nacional · {scores.community === null ? '—' : `${scores.community}º`} comunidad</small><small>{row.branch ? `Rama · ${scores.branch}º` : 'Rama no publicada'}</small><small>{row.field ? `Campo · ${scores.field}º` : 'Campo no publicado'}</small></td><td><a href={row.sourceUrl} target="_blank" rel="noreferrer">Publicación oficial <ExternalLink size={13} /></a></td></tr>; })}</tbody></table></div>
        <div className="national-pagination"><button className="sort" disabled={page === 1} onClick={() => setPage(current => current - 1)}>Anterior</button><span>Página {page} de {pageCount}</span><button className="sort" disabled={page >= pageCount} onClick={() => setPage(current => current + 1)}>Siguiente</button></div>
      </>}
    </main>
  </div>;
}
