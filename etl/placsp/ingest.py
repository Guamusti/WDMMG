from __future__ import annotations

import argparse
import hashlib
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

from etl.shared.io import download, write_jsonl


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].lower()


def text_of(node: ET.Element, *names: str) -> str | None:
    # El orden de `names` expresa prioridad: CODICE debe ganar al id ATOM
    # cuando ambos identificadores están presentes en una entry.
    for name in names:
        wanted = name.lower()
        for child in node.iter():
            if local_name(child.tag) == wanted and child.text and child.text.strip():
                return child.text.strip()
    return None


def parse_atom(path: Path, source_url: str, run_id: str) -> list[dict]:
    root = ET.parse(path).getroot()
    records = []
    for entry in root.iter():
        if local_name(entry.tag) != "entry":
            continue
        identifier = text_of(entry, "contractFolderID", "contractFolderId", "id")
        title = text_of(entry, "title")
        link = next((child.attrib.get("href") for child in entry if local_name(child.tag) == "link" and child.attrib.get("href")), None)
        record_id = identifier or link or hashlib.sha256(ET.tostring(entry)).hexdigest()
        records.append({
            "procurement_id": record_id,
            "title": title,
            "contracting_authority": text_of(entry, "name", "contractingPartyName", "buyerProfileURI"),
            "contract_type": text_of(entry, "contractTypeCode", "typeCode"),
            "procedure_type": text_of(entry, "procedureCode"),
            "status": text_of(entry, "tenderStatusCode", "contractFolderStatusCode"),
            "updated_at": text_of(entry, "updated"),
            "cpv_code": text_of(entry, "cpvCode", "mainCpvCode"),
            "estimated_value": text_of(entry, "totalEstimatedAmount", "estimatedOverallContractAmount"),
            "base_tender_budget": text_of(entry, "totalAmount", "budgetAmount"),
            "currency": text_of(entry, "currencyID", "currencyCode"),
            "publication_date": text_of(entry, "issueDate", "publicationDate"),
            "source_url": link or source_url,
            "source_record_id": record_id,
            "source_feed_url": source_url,
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "ingestion_run_id": run_id,
            "raw_payload_sha256": hashlib.sha256(ET.tostring(entry)).hexdigest(),
        })
    return records


def main() -> None:
    parser = argparse.ArgumentParser(description="Importa un feed ATOM/XML oficial de PLACSP.")
    parser.add_argument("--feed-url", required=True, help="URL del feed OpenPLACSP o de una sindicacion oficial")
    parser.add_argument("--raw-dir", default="data/raw/placsp")
    parser.add_argument("--out", default="data/processed/placsp/contracts.jsonl")
    args = parser.parse_args()
    run_id = datetime.now(timezone.utc).strftime("placsp-%Y%m%dT%H%M%SZ")
    raw_path = Path(args.raw_dir) / f"{run_id}.atom"
    metadata = download(args.feed_url, raw_path)
    records = parse_atom(raw_path, args.feed_url, run_id)
    write_jsonl(records, Path(args.out))
    print({"run_id": run_id, "records_downloaded": 1, "records_created": len(records), "raw": metadata})


if __name__ == "__main__":
    main()
