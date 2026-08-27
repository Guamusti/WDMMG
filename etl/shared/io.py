from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def download(url: str, destination: Path, timeout: int = 60, retries: int = 3) -> dict[str, Any]:
    """Download an official payload and keep a deterministic local raw copy."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    last_error = None
    for attempt in range(retries):
        try:
            response = requests.get(
                url,
                timeout=timeout,
                headers={"User-Agent": "dinero-publico/0.1 (open-data research)"},
            )
            response.raise_for_status()
            destination.write_bytes(response.content)
            return {
                "url": url,
                "path": str(destination),
                "retrieved_at": utc_now(),
                "status_code": response.status_code,
                "content_type": response.headers.get("content-type"),
                "bytes": len(response.content),
                "sha256": hashlib.sha256(response.content).hexdigest(),
            }
        except requests.RequestException as error:
            last_error = error
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
    raise RuntimeError(f"No se pudo descargar {url}: {last_error}") from last_error


def write_jsonl(records: list[dict[str, Any]], destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
