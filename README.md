# Atlas Universitario

Primer MVP vertical del Atlas Universitario de España. Esta versión cubre las ofertas públicas de la Comunidad de Madrid con notas de corte ordinarias del curso 2025–2026 y una experiencia de exploración, mapa, percentiles y comparación.

## Arranque

```bash
npm install
npm run dev
```

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
