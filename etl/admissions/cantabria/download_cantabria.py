"""Download the official University of Cantabria cutoff PDF."""
from pathlib import Path
from urllib.request import urlopen
import ssl
import certifi

URL = "https://web.unican.es/estudiantesuc/Documents/Estad%C3%ADsticas/Grado/Estad%C3%ADsticas%20de%20Ordenaci%C3%B3n%20Acad%C3%A9mica/7%20Notas%20de%20corte.pdf"
TARGET = Path("data/raw/admissions/cantabria/2025-2026/notas-de-corte-unican-2025-2026.pdf")
TARGET.parent.mkdir(parents=True, exist_ok=True)
with urlopen(URL, context=ssl.create_default_context(cafile=certifi.where())) as response:
    TARGET.write_bytes(response.read())
print(f"Saved {TARGET} ({TARGET.stat().st_size} bytes)")
