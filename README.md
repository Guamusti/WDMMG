# Atlas Universitario

Primer MVP vertical del Atlas Universitario de España. Esta versión cubre las ofertas públicas de la Comunidad de Madrid con notas de corte ordinarias del curso 2025–2026 y una experiencia de exploración, mapa, percentiles y comparación.

## Arranque

```bash
npm install
npm run dev
```

En Windows también puedes hacer doble clic en [`iniciar.bat`](./iniciar.bat). El lanzador entra en la carpeta del proyecto, actualiza dependencias con `npm install`, reutiliza una pareja saludable de API y Vite si ya existe, inicia solo lo que falte en segundo plano y abre el navegador en esa instancia. Se puede volver a ejecutar tras cada cambio sin abrir terminales duplicadas: el puerto persistido se valida antes de lanzar otro proceso.

El mapa utiliza Leaflet y teselas de OpenStreetMap con atribución visible.

El launcher inicia también la API local en un puerto libre desde `8787`, escribe ese puerto en `public/api-port.json` y configura el proxy de Vite para que el frontend consuma siempre `/api/*` en el mismo origen. `GET /api/health` comprueba el servicio y `GET /api/offers?q=informática&page=1&limit=25` devuelve ofertas paginadas con fuente y código RUCT de universidad.

El plan de ejecución se mantiene en [`docs/PLAN.md`](./docs/PLAN.md) y se actualiza junto con cada fase del producto.

## Alcance actual

- Buscador sobre carrera, universidad y ciudad.
- Mapa esquemático de campus/universidades madrileñas.
- Explorador ordenable de ofertas y notas de corte.
- Percentil reproducible sobre el conjunto cargado.
- Comparador de hasta cuatro ofertas.
- Calculadora orientativa de posición para una nota.
- Fuente y metodología visibles.

Las métricas no cargadas (alumnado, demanda, abandono, empleo y precios) no se muestran como cifras. Es una decisión de calidad de datos, no una ausencia accidental.

## Próximo paso

Sustituir el catálogo estático por el pipeline descrito en `docs/ETL.md`, añadir el export estructurado completo de Madrid y después incorporar las 16 comunidades restantes.
