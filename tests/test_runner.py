import json
import subprocess
import sys


def test_available_loader_runner_dry_run_reports_local_inputs():
    result = subprocess.run([sys.executable, "-m", "etl.run_available", "--dry-run"], check=True, capture_output=True, text=True)
    payload = json.loads(result.stdout)
    assert {row["dataset"] for row in payload["jobs"]} == {"placsp", "bdns-concesiones"}
    assert all(row["status"] in {"ready", "skipped"} for row in payload["jobs"])
    assert payload["run_started_at"] and payload["finished_at"]
    assert all("started_at" in row and "finished_at" in row and row["duration_ms"] >= 0 for row in payload["jobs"])
