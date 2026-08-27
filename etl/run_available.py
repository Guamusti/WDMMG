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
import time
from datetime import datetime, timezone
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Actualiza datasets normalizados disponibles en local.")
    parser.add_argument("--database-url", default=os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:55432/dinero_publico"))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    jobs = [
        ("igae-ejecucion", Path("data/processed/igae/execution-2026-05.jsonl"), "etl.budgets.load_postgres"),
        ("placsp", Path("data/processed/placsp/contracts.jsonl"), "etl.placsp.load_postgres"),
        ("bdns-concesiones", Path("data/processed/bdns/concessions.jsonl"), "etl.bdns.load_concessions"),
    ]
    run_started_at = datetime.now(timezone.utc).isoformat()
    results = []
    for name, input_path, module in jobs:
        started_at = datetime.now(timezone.utc).isoformat()
        started_clock = time.perf_counter()
        if not input_path.exists():
            results.append({"dataset": name, "status": "skipped", "reason": "input_missing", "input": str(input_path), "started_at": started_at, "finished_at": datetime.now(timezone.utc).isoformat(), "duration_ms": 0})
            continue
        if args.dry_run:
            results.append({"dataset": name, "status": "ready", "input": str(input_path), "started_at": started_at, "finished_at": datetime.now(timezone.utc).isoformat(), "duration_ms": round((time.perf_counter() - started_clock) * 1000)})
            continue
        completed = subprocess.run([sys.executable, "-m", module, "--input", str(input_path), "--database-url", args.database_url], check=False, text=True, capture_output=True)
        results.append({"dataset": name, "status": "success" if completed.returncode == 0 else "failed", "input": str(input_path), "output": completed.stdout.strip(), "error": completed.stderr.strip(), "started_at": started_at, "finished_at": datetime.now(timezone.utc).isoformat(), "duration_ms": round((time.perf_counter() - started_clock) * 1000)})
    print(json.dumps({"run_started_at": run_started_at, "finished_at": datetime.now(timezone.utc).isoformat(), "jobs": results}, ensure_ascii=False))
    return 0 if all(item["status"] in {"success", "ready", "skipped"} for item in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
