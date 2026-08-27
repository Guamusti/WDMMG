"""Download the UIB cutoff index and per-degree historical pages."""
from __future__ import annotations
import json
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import urlopen
import re
import ssl
import certifi

INDEX_URL = "https://estudis.uib.es/es/estudis-de-grau/com-hi-pots-accedir/admissio/notes-de-tall"
ROOT = Path("data/raw/admissions/illes-balears/2025-2026")
CONTEXT = ssl.create_default_context(cafile=certifi.where())


def fetch(url: str) -> bytes:
    with urlopen(url, context=CONTEXT) as response:
        return response.read()


ROOT.mkdir(parents=True, exist_ok=True)
index = fetch(INDEX_URL)
(ROOT / "index.html").write_bytes(index)
text = index.decode("utf-8", errors="replace")
urls = sorted({urljoin(INDEX_URL, match) for match in re.findall(r'href="([^"]*notesTallPla[^"]+)"', text, flags=re.I)})
pages = ROOT / "pages"
pages.mkdir(exist_ok=True)
manifest = []
for number, url in enumerate(urls, 1):
    content = fetch(url)
    target = pages / f"{number:03d}.html"
    target.write_bytes(content)
    manifest.append({"url": url, "file": str(target).replace("\\", "/")})
(ROOT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"Saved {len(manifest)} UIB degree pages")
