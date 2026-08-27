"""Download the official UPNA 2025-2026 cutoff PDF."""
from pathlib import Path
from urllib.request import urlopen
import ssl
import certifi

URL = "https://www2.unavarra.es/gesadj/Estudios/acceso_matricula/notas_corte/2025/NOTASDECORTE2025-10septiembre.pdf"
TARGET = Path("data/raw/admissions/navarra/2025-2026/notas-corte-upna-10-septiembre-2025.pdf")
TARGET.parent.mkdir(parents=True, exist_ok=True)
with urlopen(URL, context=ssl.create_default_context(cafile=certifi.where())) as response:
    TARGET.write_bytes(response.read())
print(f"Saved {TARGET} ({TARGET.stat().st_size} bytes)")
