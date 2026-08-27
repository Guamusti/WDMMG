from etl.bdns.concessions import parse_page


def test_parse_concession_page_keeps_provenance_and_separates_call():
    rows = parse_page({"content": [{
        "codConcesion": "CON-1",
        "beneficiario": "Asociación de prueba",
        "importe": 1250.5,
        "fechaConcesion": "2026-08-27",
        "instrumento": {"nombre": "Subvención"},
    }]}, "925963", "https://official.example/concesiones?page=0", "2026-08-27T10:00:00Z", "run-1", "abc123")
    assert rows[0]["bdns_code"] == "925963"
    assert rows[0]["source_record_id"] == "CON-1"
    assert rows[0]["beneficiary"] == "Asociación de prueba"
    assert rows[0]["instrument"] == "Subvención"
    assert rows[0]["raw_payload_sha256"] == "abc123"
