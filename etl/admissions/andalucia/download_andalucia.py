"""Download the official Distrito Único Andaluz 2025 cutoff response."""
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import ssl
import certifi

URL = "https://www.juntadeandalucia.es/economiaconocimientoempresasyuniversidad/sguit/g_not_cor_anteriores.php"
TARGET = Path("data/raw/admissions/andalucia/2025-2026/notas-de-corte-general-2025-2026.html")
TARGET.parent.mkdir(parents=True, exist_ok=True)
request = Request(URL, data=urlencode({"univpet": "", "titulpet": "", "anio": "2025", "familia": ""}).encode(), headers={"Content-Type": "application/x-www-form-urlencoded"})
with urlopen(request, context=ssl.create_default_context(cafile=certifi.where())) as response:
    TARGET.write_bytes(response.read())
print(f"Saved {TARGET} ({TARGET.stat().st_size} bytes)")
