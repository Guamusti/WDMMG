import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

import pytest


BASE_URL = os.environ.get("DINERO_PUBLICO_API", "http://localhost:8787")


def get_json(path):
    try:
        with urlopen(f"{BASE_URL}{path}", timeout=2) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except (URLError, TimeoutError) as error:
        pytest.skip(f"API local no disponible: {error}")


def test_health_reports_service_and_contract_count():
    status, payload = get_json("/api/health")
    assert status == 200
    assert payload["ok"] is True
    assert payload["service"] == "dinero-publico-api"
    assert isinstance(payload["data"]["contracts"], int)


@pytest.mark.parametrize("path", ["/api/overview", "/api/history", "/api/budgets", "/api/contracts?pageSize=2", "/api/companies?limit=2", "/api/grants?pageSize=2", "/api/coverage", "/api/policies"])
def test_public_dataset_endpoints_return_json(path):
    status, payload = get_json(path)
    assert status == 200
    assert isinstance(payload, dict)
    assert "data" in payload or "execution" in payload or "dataStatus" in payload


def test_history_returns_compatible_igae_cuts():
    status, payload = get_json("/api/history")
    assert status == 200
    assert len(payload["data"]) >= 2
    assert [row["period"] for row in payload["data"]] == ["2026-04", "2026-05"]
    assert all(row["unit"] == "miles de euros" for row in payload["data"])


def test_contract_rows_expose_adjudicatario_when_available():
    status, payload = get_json("/api/contracts?pageSize=2")
    assert status == 200
    assert isinstance(payload["data"], list)
    for row in payload["data"]:
        assert "winner_name" in row


def test_companies_csv_export_is_available():
    try:
        with urlopen(f"{BASE_URL}/api/export.csv?entity=companies", timeout=4) as response:
            body = response.read(300).decode("utf-8-sig")
            assert response.status == 200
            assert "name" in body
    except (URLError, TimeoutError) as error:
        pytest.skip(f"API local no disponible: {error}")


def test_empty_search_is_a_stable_empty_result():
    status, payload = get_json("/api/search?q=")
    assert status == 200
    assert payload == {"data": []}


def test_search_can_return_company_profiles():
    status, payload = get_json("/api/search?q=empresa")
    assert status == 200
    assert isinstance(payload["data"], list)
    for row in payload["data"]:
        assert row["type"] in {"contract", "grant", "budget", "company"}
    company_rows = [row for row in payload["data"] if row["type"] == "company"]
    if company_rows:
        assert "vista=companies" in company_rows[0]["sourceUrl"]


def test_coverage_exposes_partial_and_blocked_sources():
    status, payload = get_json("/api/coverage")
    assert status == 200
    sources = {source["id"]: source for source in payload["data"]}
    assert sources["ccaa-execution-2026-05"]["data_status"] == "partial"
    assert sources["local-budgets-2026"]["data_status"] == "blocked_reader"


def test_company_detail_exposes_linked_contracts():
    status, companies = get_json("/api/companies?limit=1")
    assert status == 200 and companies["data"]
    status, payload = get_json(f"/api/companies/{companies['data'][0]['id']}")
    assert status == 200
    assert payload["data"]["contract_count"] >= 1
    assert isinstance(payload["data"]["contracts"], list)
    assert isinstance(payload["data"]["authorities"], list)


def test_grant_detail_exposes_official_call():
    status, grants = get_json("/api/grants?pageSize=1")
    assert status == 200 and grants["data"]
    code = grants["data"][0]["bdns_code"]
    status, payload = get_json(f"/api/grants/{code}")
    assert status == 200
    assert payload["data"]["bdns_code"] == code
    assert payload["data"]["source_url"]


def test_unknown_route_is_not_found():
    with pytest.raises(HTTPError) as error:
        urlopen(f"{BASE_URL}/api/does-not-exist", timeout=2)
    assert error.value.code == 404
