# Ingestor de notas de Madrid

```bash
pip install -r etl/requirements.txt
python etl/admissions/madrid/download_madrid.py
python etl/admissions/madrid/parse_madrid.py
```

La fuente es la publicación oficial de notas de acceso 2025–2026 de la Comunidad de Madrid. El parser conserva universidad, página y fila original para revisión, y soporta las tablas con dos y cinco grupos de acceso. El extracto actual contiene 426 filas numéricas de las seis universidades públicas. No hace matching automático contra RUCT: esa unión se hará en una etapa posterior mediante códigos oficiales.

Después de parsear, se puede ejecutar `python etl/shared/quality_report.py` para generar `data/quality/madrid-2025-2026.json`. El informe valida rango de nota, duplicados, año, nombre de titulación y universidad; el estado `pass` no implica que el matching RUCT esté terminado.
