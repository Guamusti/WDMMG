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

      {view === 'methodology' ? <Methodology /> : view === 'contracts' ? <Contracts rows={contracts} loading={contractsLoading} /> : view === 'grants' ? <Grants /> : <>
        <section className="insight-panel">
          <div><span className="eyebrow insight-kicker">LA LECTURA RÁPIDA · AGE · {overview?.period || 'MAYO 2026'}</span><p className="insight-label">De cada 1 € de crédito definitivo</p><strong className="insight-value">{imported ? `${decimal(execution.recognized, execution.finalCredit)} €` : '—'}</strong><p className="insight-caption">ya figura como obligación reconocida</p></div>
          <div className="insight-grid"><div className="insight-card"><span>Y de cada 1 € reconocido</span><b>{imported ? `${decimal(execution.paid, execution.recognized)} €` : '—'}</b><small>ya se ha pagado</small></div><div className="insight-card"><span>Lectura contable</span><b>{imported ? `${percent(execution.recognized, execution.finalCredit)}%` : '—'}</b><small>ejecución reconocida sobre crédito</small></div></div>
          <p className="insight-source">Ratio calculado con magnitudes IGAE separadas; no equivale a “impuestos destinados” a una política concreta.</p>
        </section>
        <section className="stats">
          <Stat label="Crédito definitivo AGE" value={imported ? `${millions(execution.finalCredit)} M€` : 'Cargando…'} note={imported ? `${overview.period} · ${overview.unit}` : 'Conector IGAE'} />
          <Stat label="Obligaciones reconocidas" value={imported ? `${millions(execution.recognized)} M€` : 'Cargando…'} note={imported ? `${percent(execution.recognized, execution.finalCredit)}% del crédito` : 'Separado del pago'} />
          <Stat label="Pagos realizados" value={imported ? `${millions(execution.paid)} M€` : 'Cargando…'} note={imported ? `${percent(execution.paid, execution.recognized)}% de las obligaciones` : 'Dato IGAE'} />
          <Stat label="Contratos" value={overview?.contracts?.records ? overview.contracts.records.toLocaleString('es-ES') : '—'} note="Registros PLACSP cargados" />
        </section>
        <section className="notice"><ShieldCheck size={17}/><span><strong>Fuente conectada.</strong> Ejecución AGE IGAE · {imported ? `${overview.period} · estado provisional · unidad ${overview.unit}` : 'cargando datos'}. Contratos y subvenciones todavía no se agregan.</span><a href={overview?.sourceUrl || sources.hacienda} target="_blank">Ver fuente original <ExternalLink size={13}/></a></section>
        <section className="section-head"><div><span className="eyebrow">01 · PRESUPUESTO</span><h2>¿En qué se gasta?</h2></div><button className="filter"><SlidersHorizontal size={16}/> Filtrar</button></section>
        <section className="explorer-grid">
          <div className="treemap" aria-label="Clasificación funcional del gasto">
            {budgetLoading ? <div className="drilldown-empty">Cargando capítulos IGAE…</div> : chapters.length ? chapters.map((row, i) => <button key={row.id || row.economic_code} className={`tile tile-${i} ${selectedChapter?.economic_code === row.economic_code ? 'selected' : ''}`} style={{ background: tileColors[i % tileColors.length] }} onClick={() => { setActiveCategory(row.economic_code); setSelectedChapter(row); }}><span>{row.economic_code}</span><b>{selectedChapter?.economic_code === row.economic_code ? 'Abierto →' : `${percent(row.final_amount, budgetTotal)}%`}</b></button>) : <div className="drilldown-empty">No hay capítulos importados.</div>}
          </div>
          <aside className="side-card"><div className="eyebrow">ADMINISTRACIÓN PILOTO</div><h3>Administración General del Estado</h3><p>La primera rebanada conecta presupuesto, ejecución, contratación y subvenciones con identificadores de fuente independientes.</p><button className="text-link" onClick={() => setView('contracts')}>Ver contrataciones <ArrowUpRight size={15}/></button><div className="source-line"><Database size={15}/> Datos estructurados en preparación</div></aside>
        </section>
        {selectedChapter && <section className="drilldown-panel"><div><span className="eyebrow">DESGLOSE · {selectedChapter.economic_code}</span><h3>{selectedChapter.economic_code}</h3><p>{millions(selectedChapter.final_amount)} M€ de crédito definitivo · {percent(selectedChapter.final_amount, budgetTotal)}% del total de capítulos.</p></div>{selectedSubrows.length ? <div className="drilldown-tiles">{selectedSubrows.map((row, i) => <div className="drilldown-tile" key={row.id || row.economic_code} style={{ borderTopColor: tileColors[i % tileColors.length] }}><span>{row.economic_code}</span><b>{millions(row.final_amount)} M€</b><small>{percent(row.final_amount, selectedChapter.final_amount)}% del capítulo</small></div>)}</div> : <div className="drilldown-empty"><strong>El siguiente nivel todavía no está disponible.</strong><span>La descarga IGAE conectada permite ver capítulos, pero no aporta aquí una relación padre-hijo para subcategorías como pensiones o IMV. Las vistas administrativas de inversión se mantienen separadas hasta poder enlazarlas correctamente.</span></div>}</section>}
        <p className="footnote">Distribución por capítulos económicos del extracto IGAE conectado · importes en miles de euros.</p>
        <section className="section-head compact"><div><span className="eyebrow">02 · ÚLTIMOS REGISTROS</span><h2>Contratación pública</h2></div><button className="text-link" onClick={() => setView('contracts')}>Ver todo <ChevronRight size={15}/></button></section>
        <Contracts rows={contracts} loading={contractsLoading} compact />
      </>}
    </main>
    <footer><span>DINERO PÚBLICO · MVP</span><span>Datos oficiales, conceptos separados, fuentes visibles.</span></footer>
  </div>
}

function millions(value) { return new Intl.NumberFormat('es-ES', { maximumFractionDigits: 1 }).format(Number(value) / 1000); }
function percent(value, total) { return total ? new Intl.NumberFormat('es-ES', { maximumFractionDigits: 1 }).format((Number(value) / Number(total)) * 100) : '—'; }
function decimal(value, total) { return total ? new Intl.NumberFormat('es-ES', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(Number(value) / Number(total)) : '—'; }
function resultType(type) { return type === 'grant' ? 'BDNS' : type === 'budget' ? 'IGAE' : 'PLACSP'; }
function Stat({ label, value, note }) { return <div className="stat"><span className="eyebrow">{label}</span><strong>{value}</strong><small>{note}</small></div> }
function Contracts({ rows, loading, compact }) { return <section className={`contracts ${compact ? 'compact-table' : ''}`}><div className="table-head"><span>Expediente / objeto</span><span>Órgano contratante</span><span>Adjudicatario</span><span>Importe</span><span>Estado</span></div>{loading ? <div className="empty-row">Consultando PLACSP…</div> : rows.length ? rows.map((row, i) => <div className="contract-row" key={i}><div><b>{row.title || 'Sin título'}</b><small>{row.source_record_id || 'Registro PLACSP'}</small></div><span>{row.contracting_authority || '—'}</span><span>{row.winner_name || '—'}</span><Money>{row.award_amount || '—'}</Money><span className="pill">{row.status || 'Publicado'}</span></div>) : <div className="empty-row">Todavía no hay contratos PLACSP importados. El conector está preparado; no mostramos registros ficticios.</div>}</section> }
function Grants() { const [rows, setRows] = useState([]); const [loading, setLoading] = useState(true); useEffect(() => { fetch('http://localhost:8787/api/grants?pageSize=25').then(response => response.ok ? response.json() : { data: [] }).then(payload => setRows(payload.data || [])).catch(() => setRows([])).finally(() => setLoading(false)); }, []); return <section className="grants-page"><span className="eyebrow">SUBVENCIONES · BDNS</span><h2>Convocatorias publicadas</h2><p className="page-intro">Ayudas y convocatorias como dataset independiente. No se suman a los pagos presupuestarios.</p><div className="grant-list">{loading ? <div className="empty-row">Consultando BDNS…</div> : rows.length ? rows.map(row => <a className="grant-card" href={row.source_url} target="_blank" key={row.bdns_code}><div><span className="eyebrow">BDNS {row.bdns_code}</span><h3>{row.title || 'Convocatoria sin título'}</h3><p>{row.purpose || 'Finalidad no indicada'} · {row.granting_entity || 'Órgano no identificado'}</p></div><ExternalLink size={17}/></a>) : <div className="empty-row">Todavía no hay convocatorias BDNS importadas.</div>}</div></section> }
function Methodology() { return <section className="methodology"><span className="eyebrow">METODOLOGÍA</span><h2>Una cifra, una definición, una fuente.</h2><p>El producto separa presupuesto, ejecución, contratos y subvenciones. No suma magnitudes que puedan solaparse y no infiere relaciones entre una partida y una adjudicación sin evidencia.</p><div className="source-list">{[['Hacienda / IGAE','Ejecución AGE mensual y presupuestos',sources.igae],['PLACSP','Feeds abiertos ATOM/XML de licitaciones',sources.placsp],['BDNS','Servicios web y especificaciones BDNS20',sources.bdns],['INE','API JSON y población municipal oficial',sources.ine]].map(([n,d,u]) => <a href={u} target="_blank" className="source-item" key={n}><span><b>{n}</b><small>{d}</small></span><ExternalLink size={16}/></a>)}</div></section> }

createRoot(document.getElementById('root')).render(<App />);
