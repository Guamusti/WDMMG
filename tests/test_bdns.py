import json

from etl.bdns.concessions import ingest_many, parse_page
import etl.bdns.concessions as concessions_module
from etl.bdns.client import BDNS20Client
from etl.bdns.load_concessions import parse_date
from etl.shared.normalize import normalize_tax_id, parse_euro, valid_spanish_tax_id
from pathlib import Path
from decimal import Decimal


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


def test_concession_loader_accepts_official_date_formats():
    assert str(parse_date("2026-08-27")) == "2026-08-27"
    assert str(parse_date("27/08/2026")) == "2026-08-27"
    assert parse_date("not-a-date") is None


def test_bdns20_client_uses_disk_cache_without_second_request(tmp_path):
    class FakeResponse:
        status_code = 200
        headers = {"content-type": "application/json"}
        content = b'{"content": []}'

        def raise_for_status(self):
            return None

    class FakeSession:
        calls = 0

        def get(self, url, timeout, headers):
            self.calls += 1
            return FakeResponse()

    session = FakeSession()
    client = BDNS20Client(tmp_path / "cache", min_interval=0, session=session)
    client.fetch("https://official.example/bdns20", tmp_path / "one.payload")
    cached = client.fetch("https://official.example/bdns20", tmp_path / "two.payload")
    assert session.calls == 1
    assert cached["cache_hit"] is True
    assert Path(tmp_path / "two.payload").read_bytes() == FakeResponse.content


def test_concession_ingest_many_keeps_calls_in_one_auditable_output(tmp_path, monkeypatch):
    class FakeClient:
        def __init__(self, *_args, **_kwargs):
            pass

        def fetch(self, url, destination, cache_ttl=300):
            destination.write_text(json.dumps({"content": []}), encoding="utf-8")
            return {"retrieved_at": "2026-08-27T10:00:00Z", "sha256": "empty"}

    monkeypatch.setattr(concessions_module, "BDNS20Client", FakeClient)
    result = ingest_many(["925963", "926814"], tmp_path / "raw", tmp_path / "out.jsonl", page_size=10, max_pages=2, min_interval=0)
    assert [call["bdns_code"] for call in result["calls"]] == ["925963", "926814"]
    assert result["pages"] == 2
    assert result["records_created"] == 0


def test_normalization_handles_spanish_tax_ids_and_euro_formats():
    assert normalize_tax_id(" b-123 456 78 ") == "B12345678"
    assert parse_euro("1.234,56") == Decimal("1234.56")
    assert parse_euro("1234.56") == Decimal("1234.56")
    assert valid_spanish_tax_id("B99286320") is True
    assert valid_spanish_tax_id("***6433**") is None
