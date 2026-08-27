from __future__ import annotations

import argparse
import hashlib
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

from etl.shared.io import download, write_jsonl
from etl.shared.quality import record_quality_flags


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


def direct_text(node: ET.Element, name: str) -> str | None:
    wanted = name.lower()
    child = next((item for item in node if local_name(item.tag) == wanted), None)
    if child is None:
        return None
    return (child.text or '').strip() or text_of(child, name)


def parse_lots(entry: ET.Element) -> list[dict]:
    lots = []
    for lot in entry.iter():
        if local_name(lot.tag) != 'procurementprojectlot':
            continue
        project = next((child for child in lot if local_name(child.tag) == 'procurementproject'), None)
        if project is None:
            continue
        budget = next((child for child in project.iter() if local_name(child.tag) == 'budgetamount'), None)
        lots.append({
            'lot_number': direct_text(lot, 'id'),
            'title': direct_text(project, 'name'),
            'budget': text_of(budget, 'taxexclusiveamount') if budget is not None else None,
            'estimated_value': text_of(budget, 'taxexclusiveamount') if budget is not None else None,
        })
    return lots


def parse_awards(entry: ET.Element, contract_id: str | None = None) -> list[dict]:
    awards = []
    contract_id = contract_id or text_of(entry, "contractFolderID", "contractFolderId") or "unknown-contract"
    for index, result in enumerate(entry.iter()):
        if local_name(result.tag) != 'tenderresult':
            continue
        source_id = f"{contract_id}:award:{index}"
        winner = next((child for child in result if local_name(child.tag) == 'winningparty'), None)
        awarded_project = next((child for child in result if local_name(child.tag) == 'awardedtenderedproject'), None)
        monetary_total = next((child for child in awarded_project if local_name(child.tag) == 'legalmonetarytotal'), None) if awarded_project is not None else None
        awards.append({
            'award_id': source_id,
            'result_code': text_of(result, 'resultCode'),
            'lot_number': text_of(result, 'lotID', 'lotId', 'procurementProjectLotID'),
            'award_date': text_of(result, 'awardDate'),
            'number_of_tenders': text_of(result, 'receivedTenderQuantity'),
            'sme_awarded': text_of(result, 'smeAwardedIndicator'),
            'winner_id': text_of(winner, 'id') if winner is not None else None,
            'winner_name': text_of(winner, 'name') if winner is not None else None,
            'award_amount': text_of(monetary_total, 'taxExclusiveAmount') if monetary_total is not None else None,
            'award_amount_with_tax': text_of(monetary_total, 'payableAmount') if monetary_total is not None else None,
        })
    return awards


def parse_events(entry: ET.Element) -> list[dict]:
    events = []
    for modification in entry.iter():
        if local_name(modification.tag) != 'contractmodification':
            continue
        events.append({
            'event_type': 'contract_modification',
            'event_id': text_of(modification, 'id'),
            'contract_id': text_of(modification, 'contractId'),
            'event_date': text_of(modification, 'issueDate', 'modificationDate'),
            'note': text_of(modification, 'note'),
            'duration_change': text_of(modification, 'contractModificationDurationMeasure'),
            'final_duration': text_of(modification, 'finalDurationMeasure'),
        })
    return events


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
        record = {
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
            "lots": parse_lots(entry),
            "awards": parse_awards(entry, identifier),
            "events": parse_events(entry),
        }
        record['quality_flags'] = record_quality_flags(record, 'source_record_id', ('updated_at', 'publication_date'), ('estimated_value', 'base_tender_budget'), ('fiscal_year',))
        for award in record['awards']:
            award['quality_flags'] = record_quality_flags(award, 'award_id', ('award_date',), ('award_amount', 'award_amount_with_tax'))
        records.append(record)
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
