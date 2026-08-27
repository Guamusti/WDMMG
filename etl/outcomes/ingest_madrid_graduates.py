"""Download and normalize Madrid's open-data graduate totals."""

from __future__ import annotations

import csv
import io
import json
import urllib.request
from datetime import date
from pathlib import Path

SOURCE_URL = (
    "https://datos.comunidad.madrid/dataset/"
    "3a30d554-bb0f-4a1f-ae08-e63f525543ae/resource/"
    "c9ad6322-aa09-4d97-b6dc-84b2007c4378/download/"
    "estudiantes-egresados-en-estudios-de-grado-por-universidad.csv"
)
OUTPUT = Path(__file__).parents[2] / "data/processed/outcomes/madrid-university-graduates-2023-2024.json"
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
    values: dict[str, int] = {}
    for row in csv.DictReader(io.StringIO(raw), delimiter=";"):
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
        "definition": "Estudiantes egresados de estudios de Grado presenciales en cada universidad; el año 2024 representa el curso 2023-2024.",
        "limitations": "Es un total institucional de grados presenciales, no el número de egresados de una oferta o titulación concreta. No es una tasa de graduación ni incluye grados no presenciales.",
        "universities": values,
    }
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
