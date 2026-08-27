"""Download the official University of Zaragoza ordinary cutoff PDF."""
from pathlib import Path
import ssl
from urllib.request import urlopen

import certifi

URL = "https://academico.unizar.es/sites/academico/files/archivos/acceso/admisgrado/corte/grados2526j.pdf"
TARGET = Path("data/raw/admissions/aragon/2025-2026/grados2526j.pdf")
TARGET.parent.mkdir(parents=True, exist_ok=True)
with urlopen(URL, context=ssl.create_default_context(cafile=certifi.where())) as response:
    TARGET.write_bytes(response.read())
print(f"Saved {TARGET} ({TARGET.stat().st_size} bytes)")
