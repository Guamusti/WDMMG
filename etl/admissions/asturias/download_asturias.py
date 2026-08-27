"""Download the University of Oviedo 2025-2026 first-call table."""
from pathlib import Path
from urllib.request import urlopen
import ssl
import certifi

URL = "https://torres.epv.uniovi.es/centon/notas-acceso-oviedo-25.html"
TARGET = Path("data/raw/admissions/asturias/2025-2026/notas-acceso-oviedo-julio-2025.html")
TARGET.parent.mkdir(parents=True, exist_ok=True)
with urlopen(URL, context=ssl.create_default_context(cafile=certifi.where())) as response:
    TARGET.write_bytes(response.read())
print(f"Saved {TARGET} ({TARGET.stat().st_size} bytes)")
