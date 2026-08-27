"""Download the official University of Salamanca second cutoff list."""
from pathlib import Path
from urllib.request import urlopen
import ssl
import certifi

URL = "https://comunicacion.usal.es/sites/comunicacion.usal.es/files/180725_2___Listado_Notas_de_corte_2025_2026..pdf"
TARGET = Path("data/raw/admissions/castilla-leon/2025-2026/notas-de-corte-usal-2025-2026.pdf")
TARGET.parent.mkdir(parents=True, exist_ok=True)
with urlopen(URL, context=ssl.create_default_context(cafile=certifi.where())) as response:
    TARGET.write_bytes(response.read())
print(f"Saved {TARGET} ({TARGET.stat().st_size} bytes)")
