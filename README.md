# Dinero Público

MVP del explorador visual del gasto público español. La primera iteración valida una navegación vertical sobre la AGE: presupuesto → ejecución → contratación → empresa/subvención, con conceptos contables separados y procedencia visible.

## Arranque

```bash
npm install
npm run dev
```

> Estado actual: interfaz funcional de exploración y documentación de fuentes. Las cifras económicas permanecen desactivadas hasta completar la ingesta validada; los porcentajes del treemap están marcados como referencia visual de interacción.

## Principios

- Presupuesto, ejecución, contratos y subvenciones son perspectivas distintas.
- Toda cifra deberá conservar fuente, registro original, versión e ingesta.
- No se infieren relaciones entre partidas y contratos sin evidencia.
- Las anomalías se marcan para revisión; no se borran automáticamente.

Consulta [docs/DATA_SOURCES.md](docs/DATA_SOURCES.md) para la investigación inicial y [docs/DATA_MODEL.md](docs/DATA_MODEL.md) para el modelo normalizado.
## Mantenimiento rápido

En Windows, ejecuta `iniciar.bat`: sincroniza la rama `master`, instala dependencias si hacen falta, levanta API y frontend y abre `http://localhost:5173/`. La guía completa está en [`docs/MAINTENANCE.md`](docs/MAINTENANCE.md).
