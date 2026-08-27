import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { ArrowUpRight, ChevronRight, Database, ExternalLink, Search, ShieldCheck, SlidersHorizontal } from 'lucide-react';
import './styles.css';
import './overrides.css';

const sources = {
  hacienda: 'https://www.hacienda.gob.es/es-ES/CDI/Paginas/centraldeinformacion.aspx',
  igae: 'https://www.igae.pap.hacienda.gob.es/sitios/igae/es-ES/Contabilidad/ContabilidadPublica/CPE/EjecucionPresupuestaria/Paginas/imextractoejecucion.aspx',
  placsp: 'https://contrataciondelestado.es/datosabiertos/DGPE_PLACSP_OpenPLACSP_v.2.2.pdf',
  bdns: 'https://www.oficinavirtual.pap.hacienda.gob.es/sitios/oficinavirtual/en-GB/CatalogoSistemasInformacion/TESEOnet/Paginas/Documentación.aspx',
  ine: 'https://www.ine.es/dyngs/DAB/index.htm?cid=1099'
};

const tileColors = ['#de6c4c', '#1c7770', '#dcae42', '#8f9f58', '#466b8a', '#b06b86', '#6d7a9d', '#9b715c', '#547d73'];

function Money({ children }) { return <span className="money">{children}</span>; }

function App() {
  const [query, setQuery] = useState('');
  const [view, setView] = useState('overview');
  const [activeCategory, setActiveCategory] = useState(null);
  const [overview, setOverview] = useState(null);
  const [contracts, setContracts] = useState([]);
  const [contractsLoading, setContractsLoading] = useState(true);
  const [budgetRows, setBudgetRows] = useState([]);
  const [budgetLoading, setBudgetLoading] = useState(true);
  const [selectedChapter, setSelectedChapter] = useState(null);
  const [searchResults, setSearchResults] = useState([]);
  useEffect(() => { fetch('http://localhost:8787/api/overview').then(response => response.ok ? response.json() : null).then(setOverview).catch(() => setOverview(null)); }, []);
  useEffect(() => { fetch('http://localhost:8787/api/budgets').then(response => response.ok ? response.json() : { data: [] }).then(payload => setBudgetRows(payload.data || [])).catch(() => setBudgetRows([])).finally(() => setBudgetLoading(false)); }, []);
  useEffect(() => { if (!query.trim()) { setSearchResults([]); return; } const timer = setTimeout(() => fetch(`http://localhost:8787/api/search?q=${encodeURIComponent(query)}`).then(response => response.ok ? response.json() : { data: [] }).then(payload => setSearchResults(payload.data || [])).catch(() => setSearchResults([])), 220); return () => clearTimeout(timer); }, [query]);
  useEffect(() => { setContractsLoading(true); fetch(`http://localhost:8787/api/contracts?pageSize=20${query ? `&q=${encodeURIComponent(query)}` : ''}`).then(response => response.ok ? response.json() : { data: [] }).then(payload => setContracts(payload.data || [])).catch(() => setContracts([])).finally(() => setContractsLoading(false)); }, [query]);
  const imported = overview?.dataStatus === 'imported';
  const execution = overview?.execution;
  const chapters = budgetRows.filter(row => row.economic_level === 'chapter' && /^[1-9]\.\s/.test(row.economic_code || '') && Number(row.final_amount) > 0);
  const budgetTotal = chapters.reduce((sum, row) => sum + Number(row.final_amount || 0), 0);
  // GTOS 002 is a separate administrative view, not a child hierarchy of chapters.
  // Until a parent key is modeled, do not present those rows as nested chapter data.
  const selectedSubrows = [];

  return <div className="app">
    <header className="topbar">
      <button className="brand" onClick={() => setView('overview')}><span className="brand-mark">€</span><span>DINERO<br/><i>PÚBLICO</i></span></button>
      <nav><button className={view === 'overview' ? 'active' : ''} onClick={() => setView('overview')}>Explorar</button><button className={view === 'contracts' ? 'active' : ''} onClick={() => setView('contracts')}>Contratos</button><button className={view === 'grants' ? 'active' : ''} onClick={() => setView('grants')}>Subvenciones</button><button className={view === 'methodology' ? 'active' : ''} onClick={() => setView('methodology')}>Metodología</button></nav>
      <div className="year">2026 <span>⌄</span></div>
    </header>

    <main>
      <section className="hero">
        <div className="eyebrow">EXPLORADOR DEL SECTOR PÚBLICO ESPAÑOL <span className="live-dot" /> MVP · AGE</div>
        <h1>¿Dónde va<br/><em>el dinero público?</em></h1>
        <p className="intro">Empieza por una administración, un programa o una empresa. Sigue el rastro y consulta siempre la fuente original.</p>
        <div className="searchbox"><Search size={20}/><input value={query} onChange={e => setQuery(e.target.value)} placeholder="Buscar organismo, empresa, contrato…"/><kbd>⌘ K</kbd></div>
        {query.trim() && <div className="search-results" aria-live="polite">{searchResults.length ? searchResults.map(row => <a href={row.sourceUrl || '#'} target="_blank" key={`${row.type}-${row.id}`}><span className={`result-type ${row.type}`}>{resultType(row.type)}</span><span><b>{row.title || row.id}</b><small>{row.subtitle || row.id}</small></span><ExternalLink size={14}/></a>) : <div className="search-empty">Buscando en contratos, convocatorias y presupuesto…</div>}</div>}
      </section>

      {view === 'methodology' ? <Methodology /> : view === 'contracts' ? <Contracts rows={contracts} loading={contractsLoading} query={query} /> : view === 'grants' ? <Grants /> : <>
        <section className="insight-panel">
          <div><span className="eyebrow insight-kicker">EN DOS CIFRAS · ADMINISTRACIÓN DEL ESTADO · {overview?.period ? periodLabel(overview.period) : 'MAYO 2026'}</span><p className="insight-label">De cada 1 € que el Estado tenía previsto gastar</p><strong className="insight-value">{imported ? `${decimal(execution.paid, execution.finalCredit)} €` : '—'}</strong><p className="insight-caption">ya se ha pagado</p></div>
          <div className="insight-grid"><div className="insight-card"><span>Ya están comprometidos</span><b>{imported ? `${decimal(execution.committed, execution.finalCredit)} €` : '—'}</b><small>por cada euro previsto</small></div><div className="insight-card"><span>Ya constan como gasto</span><b>{imported ? `${decimal(execution.recognized, execution.finalCredit)} €` : '—'}</b><small>por cada euro previsto</small></div></div>
          <p className="insight-source">Cálculo con datos oficiales de ejecución. “Previsto”, “comprometido” y “pagado” son conceptos distintos.</p>
        </section>
        <section className="stats">
          <Stat label="Presupuesto previsto" value={imported ? `${millions(execution.finalCredit)} M€` : 'Cargando…'} note={imported ? `${periodLabel(overview.period)} · fuente oficial` : 'Conectando con Hacienda'} />
          <Stat label="Gasto registrado" value={imported ? `${millions(execution.recognized)} M€` : 'Cargando…'} note={imported ? `${percent(execution.recognized, execution.finalCredit)}% del presupuesto` : 'Aún cargando'} />
          <Stat label="Dinero pagado" value={imported ? `${millions(execution.paid)} M€` : 'Cargando…'} note={imported ? `${percent(execution.paid, execution.finalCredit)}% del presupuesto` : 'Aún cargando'} />
          <Stat label="Contratos publicados" value={overview?.contracts?.records ? overview.contracts.records.toLocaleString('es-ES') : '—'} note="Registros oficiales cargados" />
        </section>
        <section className="notice"><ShieldCheck size={17}/><span><strong>Datos oficiales.</strong> La información llega hasta {imported ? periodLabel(overview.period).toLowerCase() : 'el último mes disponible'}. Presupuesto, contratos y ayudas aparecen por separado.</span><a href={overview?.sourceUrl || sources.hacienda} target="_blank">Comprobar fuente <ExternalLink size={13}/></a></section>
        <section className="section-head"><div><span className="eyebrow">01 · EL REPARTO</span><h2>¿A qué se dedica el dinero?</h2><p className="section-subtitle">Toca un bloque para ver cuánto representa y qué información hay disponible.</p></div><button className="filter"><SlidersHorizontal size={16}/> Filtrar</button></section>
        <section className="explorer-grid">
          <div className="treemap" aria-label="Clasificación funcional del gasto">
            {budgetLoading ? <div className="drilldown-empty">Cargando reparto…</div> : chapters.length ? chapters.map((row, i) => <button key={row.id || row.economic_code} className={`tile tile-${i} ${selectedChapter?.economic_code === row.economic_code ? 'selected' : ''}`} style={{ background: tileColors[i % tileColors.length] }} onClick={() => { setActiveCategory(row.economic_code); setSelectedChapter(row); }}><span>{friendlyChapter(row.economic_code)}<small>{row.economic_code}</small></span><b>{selectedChapter?.economic_code === row.economic_code ? 'Ver detalle →' : `${percent(row.final_amount, budgetTotal)}%`}</b></button>) : <div className="drilldown-empty">No hay capítulos importados.</div>}
          </div>
          <aside className="side-card"><div className="eyebrow">DÓNDE ESTAMOS MIRANDO</div><h3>El Estado</h3><p>Empezamos por la Administración General del Estado. Aquí puedes pasar del reparto general a contratos y ayudas concretas.</p><button className="text-link" onClick={() => setView('contracts')}>Ver contratos <ArrowUpRight size={15}/></button><div className="source-line"><Database size={15}/> Datos oficiales conectados</div></aside>
        </section>
        {selectedChapter && <section className="drilldown-panel"><div><span className="eyebrow">HAS ELEGIDO</span><h3>{friendlyChapter(selectedChapter.economic_code)}</h3><p>{millions(selectedChapter.final_amount)} M€ reservados · {percent(selectedChapter.final_amount, budgetTotal)}% del total.</p></div>{selectedSubrows.length ? <div className="drilldown-tiles">{selectedSubrows.map((row, i) => <div className="drilldown-tile" key={row.id || row.economic_code} style={{ borderTopColor: tileColors[i % tileColors.length] }}><span>{row.economic_code}</span><b>{millions(row.final_amount)} M€</b><small>{percent(row.final_amount, selectedChapter.final_amount)}% del capítulo</small></div>)}</div> : <div className="drilldown-empty"><strong>Aún no podemos abrir este bloque en más partes.</strong><span>La fuente conectada publica el total del capítulo, pero no su reparto interno. Cuando exista ese detalle oficial, aparecerá aquí; no rellenamos el hueco con estimaciones.</span></div>}</section>}
        <p className="footnote">Distribución por capítulos económicos del extracto IGAE conectado · importes en miles de euros.</p>
        <section className="section-head compact"><div><span className="eyebrow">02 · ÚLTIMOS REGISTROS</span><h2>Contratación pública</h2></div><button className="text-link" onClick={() => setView('contracts')}>Ver todo <ChevronRight size={15}/></button></section>
        <Contracts rows={contracts} loading={contractsLoading} compact query={query} />
      </>}
    </main>
    <footer><span>DINERO PÚBLICO · MVP</span><span>Datos oficiales, conceptos separados, fuentes visibles.</span></footer>
  </div>
}

function millions(value) { return new Intl.NumberFormat('es-ES', { maximumFractionDigits: 1 }).format(Number(value) / 1000); }
function percent(value, total) { return total ? new Intl.NumberFormat('es-ES', { maximumFractionDigits: 1 }).format((Number(value) / Number(total)) * 100) : '—'; }
function decimal(value, total) { return total ? new Intl.NumberFormat('es-ES', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(Number(value) / Number(total)) : '—'; }
function periodLabel(period) { const month = String(period || '').split('-')[1]; const names = { '01': 'ENERO', '02': 'FEBRERO', '03': 'MARZO', '04': 'ABRIL', '05': 'MAYO', '06': 'JUNIO', '07': 'JULIO', '08': 'AGOSTO', '09': 'SEPTIEMBRE', '10': 'OCTUBRE', '11': 'NOVIEMBRE', '12': 'DICIEMBRE' }; return `${names[month] || period} ${String(period || '').split('-')[0] || ''}`.trim(); }
function friendlyChapter(label) { const code = String(label || '').split('.')[0]; return ({ '1': 'Sueldos y personal', '2': 'Servicios y compras', '3': 'Intereses de la deuda', '4': 'Ayudas y transferencias', '5': 'Imprevistos', '6': 'Inversiones', '7': 'Transferencias para invertir', '8': 'Préstamos y activos', '9': 'Deuda pública' })[code] || label; }
function resultType(type) { return type === 'grant' ? 'BDNS' : type === 'budget' ? 'IGAE' : 'PLACSP'; }
function Stat({ label, value, note }) { return <div className="stat"><span className="eyebrow">{label}</span><strong>{value}</strong><small>{note}</small></div> }
function Contracts({ rows, loading, compact, query = '' }) { return <section className={`contracts ${compact ? 'compact-table' : ''}`}><div className="export-bar"><span>{compact ? 'Muestra más reciente' : 'Resultados PLACSP'}</span><a href={`http://localhost:8787/api/export.csv?entity=contracts${query ? `&q=${encodeURIComponent(query)}` : ''}`}>Descargar CSV</a></div><div className="table-head"><span>Expediente / objeto</span><span>Órgano contratante</span><span>Adjudicatario</span><span>Importe</span><span>Estado</span></div>{loading ? <div className="empty-row">Consultando PLACSP…</div> : rows.length ? rows.map((row, i) => <div className="contract-row" key={i}><div><b>{row.title || 'Sin título'}</b><small>{row.source_record_id || 'Registro PLACSP'}</small></div><span>{row.contracting_authority || '—'}</span><span>{row.winner_name || '—'}</span><Money>{row.award_amount || '—'}</Money><span className="pill">{row.status || 'Publicado'}</span></div>) : <div className="empty-row">Todavía no hay contratos PLACSP importados. El conector está preparado; no mostramos registros ficticios.</div>}</section> }
function Grants() { const [rows, setRows] = useState([]); const [loading, setLoading] = useState(true); useEffect(() => { fetch('http://localhost:8787/api/grants?pageSize=25').then(response => response.ok ? response.json() : { data: [] }).then(payload => setRows(payload.data || [])).catch(() => setRows([])).finally(() => setLoading(false)); }, []); return <section className="grants-page"><span className="eyebrow">SUBVENCIONES · BDNS</span><h2>Convocatorias publicadas</h2><p className="page-intro">Ayudas y convocatorias como dataset independiente. No se suman a los pagos presupuestarios.</p><div className="export-bar"><span>{rows.length} convocatorias cargadas</span><a href="http://localhost:8787/api/export.csv?entity=grants">Descargar CSV</a></div><div className="grant-list">{loading ? <div className="empty-row">Consultando BDNS…</div> : rows.length ? rows.map(row => <a className="grant-card" href={row.source_url} target="_blank" key={row.bdns_code}><div><span className="eyebrow">BDNS {row.bdns_code}</span><h3>{row.title || 'Convocatoria sin título'}</h3><p>{row.purpose || 'Finalidad no indicada'} · {row.granting_entity || 'Órgano no identificado'}</p></div><ExternalLink size={17}/></a>) : <div className="empty-row">Todavía no hay convocatorias BDNS importadas.</div>}</div></section> }
function Methodology() { const [coverage, setCoverage] = useState([]); useEffect(() => { fetch('http://localhost:8787/api/coverage').then(response => response.ok ? response.json() : { data: [] }).then(payload => setCoverage(payload.data || [])).catch(() => setCoverage([])); }, []); return <section className="methodology"><span className="eyebrow">METODOLOGÍA Y COBERTURA</span><h2>Una cifra, una definición, una fuente.</h2><p>El producto separa presupuesto, ejecución, contratos y subvenciones. No suma magnitudes que puedan solaparse y no infiere relaciones entre una partida y una adjudicación sin evidencia.</p><div className="coverage-grid">{coverage.map(source => <div className="coverage-card" key={source.id}><span className="eyebrow">{source.institution}</span><h3>{source.name}</h3><p>{source.coverage_description || 'Cobertura documentada en preparación.'}</p><div><b>{Number(source.budget_records) + Number(source.contract_records) + Number(source.grant_records)}</b><small> registros cargados</small></div><a href={source.source_url} target="_blank">Fuente original <ExternalLink size={13}/></a></div>)}</div><div className="source-list">{[['Hacienda / IGAE','Ejecución AGE mensual y presupuestos',sources.igae],['PLACSP','Feeds abiertos ATOM/XML de licitaciones',sources.placsp],['BDNS','Servicios web y especificaciones BDNS20',sources.bdns],['INE','API JSON y población municipal oficial',sources.ine]].map(([n,d,u]) => <a href={u} target="_blank" className="source-item" key={n}><span><b>{n}</b><small>{d}</small></span><ExternalLink size={16}/></a>)}</div></section> }

createRoot(document.getElementById('root')).render(<App />);
