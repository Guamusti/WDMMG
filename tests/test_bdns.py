from etl.bdns.concessions import parse_page
from etl.bdns.client import BDNS20Client
from etl.bdns.load_concessions import parse_date
from etl.shared.normalize import normalize_tax_id, parse_euro
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


def test_normalization_handles_spanish_tax_ids_and_euro_formats():
    assert normalize_tax_id(" b-123 456 78 ") == "B12345678"
    assert parse_euro("1.234,56") == Decimal("1234.56")
    assert parse_euro("1234.56") == Decimal("1234.56")
