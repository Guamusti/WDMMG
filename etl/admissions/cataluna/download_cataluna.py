"""Download the official Catalonia first-assignment cutoff PDF."""
from pathlib import Path
import ssl
from urllib.request import urlopen

import certifi

URL = "https://universitats.gencat.cat/web/.content/02_preinscripcio/enllac-documents/notes-de-tall/Notes-tall-1a-assignacio_juny_2025_v3.pdf"
TARGET = Path("data/raw/admissions/cataluna/2025-2026/notes-tall-1a-assignacio-juny-2025.pdf")
TARGET.parent.mkdir(parents=True, exist_ok=True)
with urlopen(URL, context=ssl.create_default_context(cafile=certifi.where())) as response:
    TARGET.write_bytes(response.read())
print(f"Saved {TARGET} ({TARGET.stat().st_size} bytes)")
