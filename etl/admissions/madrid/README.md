# Ingestor de notas de Madrid

```bash
pip install -r etl/requirements.txt
python etl/admissions/madrid/download_madrid.py
python etl/admissions/madrid/parse_madrid.py
```

La fuente es la publicación oficial de notas de acceso 2025–2026 de la Comunidad de Madrid. El parser conserva página y fila original para revisión. No hace matching automático contra RUCT: esa unión se hará en una etapa posterior mediante códigos oficiales.
