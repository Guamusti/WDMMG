"""Apply campus disambiguations already audited against cached RUCT detail pages."""
from __future__ import annotations

import html
import json
import re
import sys
from io import StringIO
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from etl.ruct.match_madrid_degrees import clean_text

ROOT = Path(__file__).resolve().parents[2]
MATCHES = ROOT / "data/processed/ruct/madrid-degree-matches.json"
REPORT = ROOT / "data/processed/ruct/madrid-degree-matches-quality.json"
RAW = ROOT / "data/raw/ruct/madrid-degrees"
DISAMBIGUATIONS = {
    "madrid:348": {"campus": "aranjuez", "ruct_degree_code": "2503228"},
    "madrid:350": {"campus": "fuenlabrada", "ruct_degree_code": "1500491"},
}


def detail(code: str) -> dict:
    text = (RAW / f"degree-{code}.html").read_text(encoding="utf-8")

    def span(identifier: str) -> str | None:
        match = re.search(rf'id="{identifier}"[^>]*>(.*?)</span>', text, re.S)
        return clean_text(html.unescape(match.group(1))) if match else None

    centers = []
    block = re.search(r'<table[^>]+id="centro"[^>]*>(.*?)</table>', text, re.S)
    if block:
        tables = pd.read_html(StringIO(block.group(0)))
        if tables:
            for _, row in tables[0].iterrows():
                centers.append({"code": re.sub(r"\D", "", str(row.iloc[1])), "name": clean_text(row.iloc[2])})
    title_match = re.search(r'id="estudio_descripcionNombre"[^>]*>(.*?)</span>', text, re.S)
    return {
        "name": clean_text(title_match.group(1)) if title_match else None,
        "branch": span("estudio_descripcionRama"),
        "field": span("estudio_descripcionAmbito"),
        "ects": span("estudio_creditos_ecs"),
        "centers": centers,
    }


def main() -> None:
    rows = json.loads(MATCHES.read_text(encoding="utf-8"))
    changed = 0
    for row in rows:
        choice = DISAMBIGUATIONS.get(row["admission_id"])
        if not choice:
            continue
        if row["status"] == "matched" and row["match_method"] == "normalized_exact_campus_unique":
            continue
        if row["status"] != "pending" or row["match_method"] != "ambiguous_normalized_exact":
            raise ValueError(f"Unexpected current state for {row['admission_id']}")
        info = detail(choice["ruct_degree_code"])
        if not any(choice["campus"] in center["name"].lower() for center in info["centers"]):
            raise ValueError(f"Campus evidence missing for {row['admission_id']}")
        row.update({
            "status": "matched",
            "match_method": "normalized_exact_campus_unique",
            "pending_reason": None,
            "ruct_degree_code": choice["ruct_degree_code"],
            "ruct_degree_name": info["name"],
            "ruct_source_url": f"https://www.educacion.gob.es/ruct/estudio.action?codigoCiclo=SC&codigoTipo=G&CodigoEstudio={choice['ruct_degree_code']}&actual=estudios",
            "ruct_branch": info["branch"],
            "ruct_field": info["field"],
            "ruct_ects": info["ects"],
            "ruct_centers": info["centers"],
        })
        changed += 1
    MATCHES.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    report["ruct_details_downloaded"] = len(list(RAW.glob("degree-*.html")))
    report["counts"] = {
        "matched_unique": sum(row["match_method"] == "normalized_exact_unique" for row in rows),
        "matched_campus_unique": sum(row["match_method"] == "normalized_exact_campus_unique" for row in rows),
        "pending_no_match": sum(row["match_method"] == "no_normalized_exact_match" for row in rows),
        "pending_ambiguous": sum(row["match_method"] == "ambiguous_normalized_exact" for row in rows),
    }
    report["pending_by_reason"] = {reason: sum(row.get("pending_reason") == reason for row in rows if row["status"] == "pending") for reason in sorted({row.get("pending_reason") for row in rows if row["status"] == "pending"})}
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"changed": changed, "matched": sum(row["status"] == "matched" for row in rows), "pending": sum(row["status"] != "matched" for row in rows)}))


if __name__ == "__main__":
    main()
