from __future__ import annotations

import hashlib
import json
import shutil
import time
from pathlib import Path
from typing import Any

import requests

from etl.shared.io import utc_now


class BDNS20Client:
    """Cliente conservador para servicios BDNS/BDNS20.

    Mantiene una copia de respuesta por URL y respeta un intervalo mínimo
    entre peticiones. La caché es un artefacto raw, no una fuente de datos:
    conserva URL, fecha, tipo, tamaño y hash para poder auditar cada lectura.
    """

    def __init__(self, cache_dir: Path | None = None, min_interval: float = 0.5, timeout: int = 60, session: requests.Session | None = None):
        self.cache_dir = cache_dir
        self.min_interval = max(0.0, min_interval)
        self.timeout = timeout
        self.session = session or requests.Session()
        self._last_request = 0.0

    def _cache_path(self, url: str) -> Path | None:
        if self.cache_dir is None:
            return None
        return self.cache_dir / f"{hashlib.sha256(url.encode('utf-8')).hexdigest()}.payload"

    def fetch(self, url: str, destination: Path, cache_ttl: int = 300) -> dict[str, Any]:
        destination.parent.mkdir(parents=True, exist_ok=True)
        cached = self._cache_path(url)
        if cached and cached.exists() and time.time() - cached.stat().st_mtime <= max(0, cache_ttl):
            shutil.copyfile(cached, destination)
            content = destination.read_bytes()
            return self._metadata(url, destination, content, cache_hit=True)

        wait = self.min_interval - (time.monotonic() - self._last_request)
        if wait > 0:
            time.sleep(wait)
        response = self.session.get(url, timeout=self.timeout, headers={"User-Agent": "dinero-publico/0.1 (open-data research)"})
        self._last_request = time.monotonic()
        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After", "")
            raise RuntimeError(f"BDNS ha limitado la petición (HTTP 429; Retry-After={retry_after or 'no indicado'})")
        response.raise_for_status()
        content = response.content
        destination.write_bytes(content)
        if cached:
            cached.parent.mkdir(parents=True, exist_ok=True)
            cached.write_bytes(content)
        return self._metadata(url, destination, content, response=response, cache_hit=False)

    @staticmethod
    def _metadata(url: str, destination: Path, content: bytes, response: requests.Response | None = None, cache_hit: bool = False) -> dict[str, Any]:
        return {
            "url": url,
            "path": str(destination),
            "retrieved_at": utc_now(),
            "status_code": response.status_code if response is not None else 200,
            "content_type": response.headers.get("content-type") if response is not None else None,
            "bytes": len(content),
            "sha256": hashlib.sha256(content).hexdigest(),
            "cache_hit": cache_hit,
        }


def parse_json_payload(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        items = payload
    elif isinstance(payload, dict) and isinstance(payload.get("content"), list):
        items = payload["content"]
    else:
        items = [payload]
    return [item for item in items if isinstance(item, dict)]
