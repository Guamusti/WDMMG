"""Download the official CIUG cutoff publication for 2025."""
from pathlib import Path
import ssl
from urllib.request import urlopen
import certifi

URL = "https://ciug.gal/PDF/2025/ACCESO/notas_de_corte_2025.pdf"
TARGET = Path("data/raw/admissions/galicia/2025-2026/notas-de-corte-galicia-2025-2026.pdf")

TARGET.parent.mkdir(parents=True, exist_ok=True)
with urlopen(URL, context=ssl.create_default_context(cafile=certifi.where())) as response:
    TARGET.write_bytes(response.read())
print(f"Saved {TARGET} ({TARGET.stat().st_size} bytes)")
