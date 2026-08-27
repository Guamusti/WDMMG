from pathlib import Path

from etl.placsp.ingest import parse_atom


def test_parse_atom_keeps_provenance_and_core_fields(tmp_path: Path):
    atom = '''<?xml version="1.0" encoding="utf-8"?>
    <feed xmlns="http://www.w3.org/2005/Atom" xmlns:cbc="urn:example">
      <entry>
        <id>urn:example:PROC-1</id>
        <title>Servicio de prueba estructural</title>
        <updated>2026-08-27T10:00:00Z</updated>
        <link href="https://example.invalid/licitacion/PROC-1" />
        <cbc:contractFolderID>PROC-1</cbc:contractFolderID>
        <cbc:contractTypeCode>2</cbc:contractTypeCode>
      <cbc:totalAmount>100.00</cbc:totalAmount>
      <cac:ProcurementProjectLot xmlns:cac="urn:example">
        <cbc:ID>1</cbc:ID>
        <cac:ProcurementProject><cbc:Name>Lote de prueba</cbc:Name><cac:BudgetAmount><cbc:TaxExclusiveAmount>50.00</cbc:TaxExclusiveAmount></cac:BudgetAmount></cac:ProcurementProject>
      </cac:ProcurementProjectLot>
      <cac:TenderResult xmlns:cac="urn:example" xmlns:cbc="urn:example">
        <cbc:ResultCode>9</cbc:ResultCode><cbc:AwardDate>2026-08-27</cbc:AwardDate><cbc:ReceivedTenderQuantity>3</cbc:ReceivedTenderQuantity>
        <cac:WinningParty><cac:PartyIdentification><cbc:ID schemeName="NIF">B12345678</cbc:ID></cac:PartyIdentification><cac:PartyName><cbc:Name>Empresa adjudicataria</cbc:Name></cac:PartyName></cac:WinningParty>
        <cac:AwardedTenderedProject><cac:LegalMonetaryTotal><cbc:TaxExclusiveAmount>80.00</cbc:TaxExclusiveAmount><cbc:PayableAmount>96.80</cbc:PayableAmount></cac:LegalMonetaryTotal></cac:AwardedTenderedProject>
      </cac:TenderResult>
      <cac:ContractModification xmlns:cac="urn:example" xmlns:cbc="urn:example"><cbc:ID>MOD-1</cbc:ID><cbc:ContractID>PROC-1</cbc:ContractID><cbc:Note>Prórroga de prueba</cbc:Note><cbc:ContractModificationDurationMeasure unitCode="ANN">1</cbc:ContractModificationDurationMeasure></cac:ContractModification>
      </entry>
    </feed>'''
    path = tmp_path / "sample.atom"
    path.write_text(atom, encoding="utf-8")

    rows = parse_atom(path, "https://official.example/feed.atom", "test-run")

    assert len(rows) == 1
    assert rows[0]["procurement_id"] == "PROC-1"
    assert rows[0]["title"] == "Servicio de prueba estructural"
    assert rows[0]["source_feed_url"] == "https://official.example/feed.atom"
    assert rows[0]["ingestion_run_id"] == "test-run"
    assert rows[0]["base_tender_budget"] == "100.00"
    assert rows[0]["lots"][0]["title"] == "Lote de prueba"
    assert rows[0]["lots"][0]["budget"] == "50.00"
    assert rows[0]["awards"][0]["winner_id"] == "B12345678"
    assert rows[0]["awards"][0]["winner_name"] == "Empresa adjudicataria"
    assert rows[0]["awards"][0]["award_amount"] == "80.00"
    assert rows[0]["events"][0]["event_type"] == "contract_modification"
    assert rows[0]["events"][0]["event_id"] == "MOD-1"
