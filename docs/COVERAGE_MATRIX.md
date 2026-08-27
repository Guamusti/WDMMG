# Matriz de cobertura efectiva

Fecha de revisión: 27/08/2026. “Disponible” significa que existe una publicación oficial localizada; “cargado” significa que hay registros en el MVP.

| Ámbito / dataset | Fuente oficial | Periodicidad publicada | Estado actual | Qué puede mostrar el MVP |
|---|---|---:|---|---|
| AGE — ejecución y presupuesto | IGAE | Mensual | **Cargado**: 91 filas por corte; abril y mayo de 2026 disponibles para evolución | Crédito, obligaciones, pagos y periodo |
| AGE — gasto por finalidad | Cuenta General del Estado 2024 | Anual | **Cargado**: 28 políticas | Rueda, partidas principales y “Resto” desglosado |
| Contratos del sector público | PLACSP, sindicaciones abiertas | Continua / incremental | **Cargado**: 382 contratos canónicos | Expediente, órgano, lotes, importes y fuente |
| Convocatorias de ayudas | BDNS / SNPSAP | Continua | **Cargado**: 1 convocatoria de muestra | Convocatoria independiente del presupuesto |
| Comunidades autónomas | Central de Información de Hacienda | Variable | **Cargado parcialmente**: 17 CCAA + total, mayo 2026 | Gasto no financiero acumulado; no se suma a AGE |
| Entidades locales | Portal de Hacienda / CONPREL | Trimestral / anual según conjunto | **Descarga validada, parser bloqueado** | ZIP Access 2026 localizado; falta lector Access compatible para identificar tablas y claves |
| Entidades públicas y jerarquía | Inventario de entes públicos | Según publicación | **Localizado, no cargado** | Pendiente de IDs estables y relaciones |
| Población y geografía | INE | Anual | **Localizado, no cargado** | Pendiente de códigos territoriales compatibles |

## Reglas para ampliar cobertura

1. Cada ámbito debe conservar su fuente, fecha, periodo, unidad y estado de validación.
2. No se agregan AGE, CCAA y entidades locales hasta resolver transferencias internas y el riesgo de doble conteo.
3. El gasto por habitante solo aparece cuando población, territorio y ejercicio sean compatibles.
4. Una ausencia de datos se muestra como “no cargado” o “no disponible”; nunca se representa como cero.

La matriz se actualizará junto con cada nueva ingesta y se reflejará en `/api/coverage` y en la página pública de cobertura.
