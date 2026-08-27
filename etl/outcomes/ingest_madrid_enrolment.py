"""Download and normalize Madrid's open-data enrolment totals.

The source labels courses by their final year: 2024 is 2023-2024.
The resulting JSON is an institutional context metric, never a degree metric.
"""

from __future__ import annotations

import csv
import io
import json
import urllib.request
from datetime import date
from pathlib import Path

SOURCE_URL = (
    "https://datos.comunidad.madrid/dataset/"
    "a36fddce-c572-4312-ad02-3656cfcd470b/resource/"
    "e5a161fd-b5f3-4116-9318-42a974c15703/download/"
    "estudiantes-matriculados-en-estudios-de-grado-presenciales-por-universidad.csv"
)
OUTPUT = Path(__file__).parents[2] / "data/processed/outcomes/madrid-university-enrolment-2023-2024.json"
ALIASES = {
    "universidad de alcalá": "UAH",
    "universidad autónoma de madrid": "UAM",
    "universidad carlos iii de madrid": "UC3M",
    "universidad complutense de madrid": "UCM",
    "universidad politécnica de madrid": "UPM",
    "universidad rey juan carlos": "URJC",
}


def main() -> None:
    with urllib.request.urlopen(SOURCE_URL, timeout=30) as response:
        raw = response.read().decode("cp1252")
    rows = csv.DictReader(io.StringIO(raw), delimiter=";")
    values: dict[str, int] = {}
    for row in rows:
        if row.get("Año") != "2024":
            continue
        concept = row.get("Concepto", "").lower().strip()
        for label, short in ALIASES.items():
            if label in concept:
                values[short] = int(row["Valor"])
                break
    missing = sorted(set(ALIASES.values()) - set(values))
    if missing:
        raise RuntimeError(f"Missing Madrid universities: {', '.join(missing)}")
    payload = {
        "academic_year": "2023-2024",
        "granularity": "Universidad · grados presenciales",
        "source_url": SOURCE_URL,
        "retrieved_at": date.today().isoformat(),
        "definition": "Estudiantes matriculados en estudios de Grado presenciales en cada universidad; el año 2024 representa el curso 2023-2024.",
        "limitations": "Es un total institucional de grados presenciales, no el número de matriculados de una oferta o titulación concreta. No incluye grados no presenciales.",
        "universities": values,
    }
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
