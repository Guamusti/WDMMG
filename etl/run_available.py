"""Ejecuta de forma explícita los loaders cuyos aterrizajes ya existen.

No descarga fuentes por sorpresa: la descarga/ingesta sigue siendo una decisión
del operador y cada loader conserva su propia provenance.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Actualiza datasets normalizados disponibles en local.")
    parser.add_argument("--database-url", default=os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:55432/dinero_publico"))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    jobs = [
        ("placsp", Path("data/processed/placsp/contracts.jsonl"), "etl.placsp.load_postgres"),
        ("bdns-concesiones", Path("data/processed/bdns/concessions.jsonl"), "etl.bdns.load_concessions"),
    ]
    results = []
    for name, input_path, module in jobs:
        if not input_path.exists():
            results.append({"dataset": name, "status": "skipped", "reason": "input_missing", "input": str(input_path)})
            continue
        if args.dry_run:
            results.append({"dataset": name, "status": "ready", "input": str(input_path)})
            continue
        completed = subprocess.run([sys.executable, "-m", module, "--input", str(input_path), "--database-url", args.database_url], check=False, text=True, capture_output=True)
        results.append({"dataset": name, "status": "success" if completed.returncode == 0 else "failed", "input": str(input_path), "output": completed.stdout.strip(), "error": completed.stderr.strip()})
    print(json.dumps({"jobs": results}, ensure_ascii=False))
    return 0 if all(item["status"] in {"success", "ready", "skipped"} for item in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
