"""Download the official Comunidad de Madrid cutoff publication."""
from pathlib import Path
from urllib.request import urlretrieve

URL = "https://www.comunidad.madrid/docs/assets/2026/02/25/notas_de_corte_2025-26_publicacion_para_web.pdf?VersionId=TQubbLf9LLERJuuTNTnhd4CGSZZjgmUx"
TARGET = Path("data/raw/admissions/madrid/2025-2026/notas-de-corte-madrid-2025-2026.pdf")

TARGET.parent.mkdir(parents=True, exist_ok=True)
urlretrieve(URL, TARGET)
print(f"Saved {TARGET} ({TARGET.stat().st_size} bytes)")
