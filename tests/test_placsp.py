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
