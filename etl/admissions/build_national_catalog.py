"""Build the explicitly scoped national admissions catalog."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MADRID = ROOT / "data/processed/admissions/madrid-2025-2026.json"
GALICIA = ROOT / "data/processed/admissions/galicia-2025-2026.json"
ARAGON = ROOT / "data/processed/admissions/aragon-2025-2026.json"
CATALUNA = ROOT / "data/processed/admissions/cataluna-2025-2026.json"
ANDALUCIA = ROOT / "data/processed/admissions/andalucia-2025-2026.json"
CASTILLA_LEON = ROOT / "data/processed/admissions/castilla-leon-2025-2026.json"
SALAMANCA = ROOT / "data/processed/admissions/salamanca-2025-2026.json"
CANTABRIA = ROOT / "data/processed/admissions/cantabria-2025-2026.json"
NAVARRA = ROOT / "data/processed/admissions/navarra-2025-2026.json"
ASTURIAS = ROOT / "data/processed/admissions/asturias-2025-2026.json"
ILLES_BALEARS = ROOT / "data/processed/admissions/illes-balears-2025-2026.json"
CANARIAS_ULPGC = ROOT / "data/processed/admissions/canarias-ulpgc-2025-2026.json"
CANARIAS_ULL = ROOT / "data/processed/admissions/canarias-ull-2025-2026.json"
LA_RIOJA = ROOT / "data/processed/admissions/la-rioja-2025-2026.json"
PAIS_VASCO = ROOT / "data/processed/admissions/pais-vasco-2025-2026.json"
RUCT_MATCHES = ROOT / "data/processed/ruct/madrid-degree-matches.json"
OUTPUT = ROOT / "data/processed/admissions/national-2025-2026.json"
REPORT = ROOT / "data/processed/admissions/national-2025-2026-quality.json"


def load(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def build() -> tuple[list[dict], dict]:
    rows: list[dict] = []
    ruct_matches = {row["admission_id"]: row for row in load(RUCT_MATCHES)} if RUCT_MATCHES.exists() else {}
    for index, source in enumerate(load(MADRID), 1):
        ruct = ruct_matches.get(f"madrid:{index}", {})
        centers = ruct.get("ruct_centers") or []
        rows.append({
            "id": f"madrid:{index}",
            "community": "Comunidad de Madrid",
            "university": source["university_name_source"],
            "university_ruct_code": source["university_ruct_code"],
            "campus": None,
            "degree": source["degree_name_source"],
            "branch": source.get("branch_name_source") or ruct.get("ruct_branch") or None,
            "field": ruct.get("ruct_field") or None,
            "ruct_degree_code": ruct.get("ruct_degree_code") or None,
            "ruct_centers": centers,
            "academic_year": source["academic_year"],
            "admission_round": source["admission_round"],
            "admission_group": source["admission_group"],
            "cutoff_score": source["cutoff_score"],
            "source_page": source["source_page"],
            "source_file": source["source_file"],
            "source_url": "https://www.comunidad.madrid/docs/assets/2026/02/25/notas_de_corte_2025-26_publicacion_para_web.pdf?VersionId=TQubbLf9LLERJuuTNTnhd4CGSZZjgmUx",
        })
    for path in (GALICIA, ARAGON, CATALUNA, ANDALUCIA, CASTILLA_LEON, SALAMANCA, CANTABRIA, NAVARRA, ASTURIAS, ILLES_BALEARS, CANARIAS_ULPGC, CANARIAS_ULL, LA_RIOJA, PAIS_VASCO):
        for source in load(path):
            rows.append({
            "id": f"{source['community'].lower()}:{len(rows) + 1}",
                "community": source["community"],
                "university": source["university"],
                "university_ruct_code": None,
                "campus": source.get("campus"),
                "center": source.get("center"),
                "source_row": source.get("source_row"),
                "degree": source["degree"],
                "branch": source.get("branch"),
                "field": None,
                "ruct_degree_code": None,
                "ruct_centers": [],
                "academic_year": source["academic_year"],
                "admission_round": source["admission_round"],
                "admission_group": source["admission_group"],
                "cutoff_score": source["cutoff_score"],
                "places": source.get("places"),
                "source_group": source.get("source_group"),
                "waitlist_position": source.get("waitlist_position"),
                "source_process": source.get("source_process"),
                "source_date": source.get("source_date"),
                "source_page": source["source_page"],
                "source_file": str(path.relative_to(ROOT)),
                "source_url": source["source_url"],
            })
    keys = [(r["community"], r["university"], r["campus"], r.get("center"), r.get("source_row"), r.get("source_process"), r.get("source_date"), r["degree"], r["academic_year"], r["admission_round"], r["admission_group"], r["cutoff_score"], r["source_page"], r["source_url"]) for r in rows]
    report = {
        "records": len(rows),
        "communities": sorted({r["community"] for r in rows}),
        "by_community": {community: sum(r["community"] == community for r in rows) for community in sorted({r["community"] for r in rows})},
        "duplicates": len(keys) - len(set(keys)),
        "comparability": {
            "same_academic_year": len({r["academic_year"] for r in rows}) == 1,
            "same_scale_0_14": all(0 <= r["cutoff_score"] <= 14 for r in rows),
            "round_and_group_present": all(r["admission_round"] and r["admission_group"] for r in rows),
            "branch_coverage": sum(bool(r["branch"]) for r in rows),
            "field_coverage": sum(bool(r["field"]) for r in rows),
        },
    }
    return rows, report


if __name__ == "__main__":
    rows, report = build()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))
