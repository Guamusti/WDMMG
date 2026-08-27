"""Download the official University of León 2025/2026 cutoff PDF."""
from pathlib import Path
from urllib.request import urlopen
import ssl
import certifi

URL = "https://www.unileon.es/files/2025-11/notas_de_corte_2025nw.pdf"
TARGET = Path("data/raw/admissions/castilla-leon/2025-2026/notas-de-corte-unileon-2025-2026.pdf")
TARGET.parent.mkdir(parents=True, exist_ok=True)
with urlopen(URL, context=ssl.create_default_context(cafile=certifi.where())) as response:
    TARGET.write_bytes(response.read())
print(f"Saved {TARGET} ({TARGET.stat().st_size} bytes)")
