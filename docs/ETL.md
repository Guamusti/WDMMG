# ETL

Pipeline objetivo:

```text
download → raw → parse → validate → normalize → match → upsert → quality report
```

Los archivos originales deben conservarse en `data/raw/<dataset>/<region>/<academic-year>/`. Las anomalías se marcan, no se borran automáticamente.

Validaciones mínimas:

- nota entre 0 y escala máxima;
- curso académico con formato `YYYY-YYYY`;
- universidad y título con código oficial cuando la fuente lo proporcione;
- ausencia de duplicados de oferta/curso/grupo;
- URL de origen y fecha de recuperación en cada registro.
