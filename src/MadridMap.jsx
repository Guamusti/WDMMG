import { CircleMarker, MapContainer, TileLayer, Tooltip } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

export function MadridMap({ universities, onUniversitySelect }) {
  return <MapContainer center={[40.43, -3.66]} zoom={10} scrollWheelZoom={false} className="leaflet-map" aria-label="Mapa de universidades de la Comunidad de Madrid">
    <TileLayer attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>' url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
    {universities.map(university => <CircleMarker key={university.short} center={university.position} radius={7} pathOptions={{ color: university.color, fillColor: university.color, fillOpacity: .9 }} eventHandlers={{ click: () => onUniversitySelect(university.short) }}>
      <Tooltip direction="top"><strong>{university.short}</strong><br />{university.name}<br /><span>{university.city}</span></Tooltip>
    </CircleMarker>)}
  </MapContainer>;
}
