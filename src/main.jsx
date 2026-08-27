import React, { useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { ArrowUpRight, ChevronRight, Database, ExternalLink, Search, ShieldCheck, SlidersHorizontal } from 'lucide-react';
import './styles.css';

const sources = {
  hacienda: 'https://www.hacienda.gob.es/es-ES/CDI/Paginas/centraldeinformacion.aspx',
  igae: 'https://www.igae.pap.hacienda.gob.es/sitios/igae/es-ES/Contabilidad/ContabilidadPublica/CPE/EjecucionPresupuestaria/Paginas/imextractoejecucion.aspx',
  placsp: 'https://contrataciondelestado.es/datosabiertos/DGPE_PLACSP_OpenPLACSP_v.2.2.pdf',
  bdns: 'https://www.oficinavirtual.pap.hacienda.gob.es/sitios/oficinavirtual/en-GB/CatalogoSistemasInformacion/TESEOnet/Paginas/Documentación.aspx',
  ine: 'https://www.ine.es/dyngs/DAB/index.htm?cid=1099'
};

const budget = [
  { name: 'Protección social', value: 39, color: '#de6c4c' },
  { name: 'Servicios públicos generales', value: 18, color: '#1c7770' },
  { name: 'Asuntos económicos', value: 16, color: '#dcae42' },
  { name: 'Sanidad', value: 11, color: '#8f9f58' },
  { name: 'Educación', value: 9, color: '#466b8a' },
  { name: 'Defensa y seguridad', value: 7, color: '#b06b86' }
];

const contracts = [
  { title: 'Servicios de apoyo a la gestión y mantenimiento', authority: 'Administración General del Estado', winner: 'Indra Sistemas, S.A.', amount: '—', status: 'Adjudicación' },
  { title: 'Suministro de equipamiento tecnológico', authority: 'Ministerio de Transformación Digital', winner: 'Telefónica Soluciones', amount: '—', status: 'Formalizado' },
  { title: 'Servicios de consultoría y asistencia técnica', authority: 'Ministerio de Hacienda', winner: 'Accenture, S.L.', amount: '—', status: 'Licitación' }
];

function Money({ children }) { return <span className="money">{children}</span>; }

function App() {
  const [query, setQuery] = useState('');
  const [view, setView] = useState('overview');
  const [activeCategory, setActiveCategory] = useState(null);
  const filteredContracts = useMemo(() => contracts.filter(c => `${c.title} ${c.authority} ${c.winner}`.toLowerCase().includes(query.toLowerCase())), [query]);

  return <div className="app">
    <header className="topbar">
      <button className="brand" onClick={() => setView('overview')}><span className="brand-mark">€</span><span>DINERO<br/><i>PÚBLICO</i></span></button>
      <nav><button className={view === 'overview' ? 'active' : ''} onClick={() => setView('overview')}>Explorar</button><button onClick={() => setView('contracts')}>Contratos</button><button onClick={() => setView('methodology')}>Metodología</button></nav>
      <div className="year">2026 <span>⌄</span></div>
    </header>

    <main>
      <section className="hero">
        <div className="eyebrow">EXPLORADOR DEL SECTOR PÚBLICO ESPAÑOL <span className="live-dot" /> MVP · AGE</div>
        <h1>¿Dónde va<br/><em>el dinero público?</em></h1>
        <p className="intro">Empieza por una administración, un programa o una empresa. Sigue el rastro y consulta siempre la fuente original.</p>
        <div className="searchbox"><Search size={20}/><input value={query} onChange={e => setQuery(e.target.value)} placeholder="Buscar organismo, empresa, contrato…"/><kbd>⌘ K</kbd></div>
      </section>

      {view === 'methodology' ? <Methodology /> : view === 'contracts' ? <Contracts rows={filteredContracts} /> : <>
        <section className="stats">
          <Stat label="Presupuesto AGE" value="Dato pendiente" note="Conector IGAE preparado" />
          <Stat label="Ejecución" value="Dato pendiente" note="Separaremos obligación y pago" />
          <Stat label="Contratos" value="Muestra técnica" note="Feed PLACSP / ATOM" />
          <Stat label="Subvenciones" value="Muestra técnica" note="BDNS / servicios web" />
        </section>
        <section className="notice"><ShieldCheck size={17}/><span><strong>Transparencia de datos.</strong> Esta primera iteración muestra la arquitectura y el flujo de exploración. Las cifras económicas no se presentan hasta completar la ingesta validada.</span><a href={sources.hacienda} target="_blank">Ver fuente central <ExternalLink size={13}/></a></section>
        <section className="section-head"><div><span className="eyebrow">01 · PRESUPUESTO</span><h2>¿En qué se gasta?</h2></div><button className="filter"><SlidersHorizontal size={16}/> Filtrar</button></section>
        <section className="explorer-grid">
          <div className="treemap" aria-label="Clasificación funcional del gasto">
            {budget.map((item, i) => <button key={item.name} className={`tile tile-${i} ${activeCategory === item.name ? 'selected' : ''}`} style={{ background: item.color }} onClick={() => setActiveCategory(item.name)}><span>{item.name}</span><b>{activeCategory === item.name ? 'Explorar →' : `${item.value}%*`}</b></button>)}
          </div>
          <aside className="side-card"><div className="eyebrow">ADMINISTRACIÓN PILOTO</div><h3>Administración General del Estado</h3><p>La primera rebanada conecta presupuesto, ejecución, contratación y subvenciones con identificadores de fuente independientes.</p><button className="text-link" onClick={() => setView('contracts')}>Ver contrataciones <ArrowUpRight size={15}/></button><div className="source-line"><Database size={15}/> Datos estructurados en preparación</div></aside>
        </section>
        <p className="footnote">* Distribución visual de referencia para validar la interacción. No es una cifra publicada y no se agrega al resto de magnitudes.</p>
        <section className="section-head compact"><div><span className="eyebrow">02 · ÚLTIMOS REGISTROS</span><h2>Contratación pública</h2></div><button className="text-link" onClick={() => setView('contracts')}>Ver todo <ChevronRight size={15}/></button></section>
        <Contracts rows={filteredContracts} compact />
      </>}
    </main>
    <footer><span>DINERO PÚBLICO · MVP</span><span>Datos oficiales, conceptos separados, fuentes visibles.</span></footer>
  </div>
}

function Stat({ label, value, note }) { return <div className="stat"><span className="eyebrow">{label}</span><strong>{value}</strong><small>{note}</small></div> }
function Contracts({ rows, compact }) { return <section className={`contracts ${compact ? 'compact-table' : ''}`}><div className="table-head"><span>Expediente / objeto</span><span>Órgano contratante</span><span>Adjudicatario</span><span>Importe</span><span>Estado</span></div>{rows.map((row, i) => <div className="contract-row" key={i}><div><b>{row.title}</b><small>Registro de integración · PLACSP</small></div><span>{row.authority}</span><span>{row.winner}</span><Money>{row.amount}</Money><span className="pill">{row.status}</span></div>)}</section> }
function Methodology() { return <section className="methodology"><span className="eyebrow">METODOLOGÍA</span><h2>Una cifra, una definición, una fuente.</h2><p>El producto separa presupuesto, ejecución, contratos y subvenciones. No suma magnitudes que puedan solaparse y no infiere relaciones entre una partida y una adjudicación sin evidencia.</p><div className="source-list">{[['Hacienda / IGAE','Ejecución AGE mensual y presupuestos',sources.igae],['PLACSP','Feeds abiertos ATOM/XML de licitaciones',sources.placsp],['BDNS','Servicios web y especificaciones BDNS20',sources.bdns],['INE','API JSON y población municipal oficial',sources.ine]].map(([n,d,u]) => <a href={u} target="_blank" className="source-item" key={n}><span><b>{n}</b><small>{d}</small></span><ExternalLink size={16}/></a>)}</div></section> }

createRoot(document.getElementById('root')).render(<App />);
