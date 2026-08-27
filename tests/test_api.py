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


def test_index_exposes_share_metadata_in_spanish():
    with open("index.html", encoding="utf-8") as handle:
        body = handle.read()
    assert 'lang="es"' in body
    assert 'property="og:title"' in body
    assert 'name="twitter:card"' in body
    assert 'name="robots" content="index,follow"' in body
    with open("src/main.jsx", encoding="utf-8") as handle:
        app = handle.read()
    assert "function PageMetadata" in app
    assert "function ShareMetadata" in app
    assert "function ContractEventTimeline" in app
    assert "setInterval(sync, 500)" in app
    assert "document.title = title" in app


def test_windows_launcher_syncs_and_waits_for_frontend():
    with open("iniciar.bat", encoding="utf-8") as handle:
        launcher = handle.read()
    assert "git pull --ff-only" in launcher
    assert "Invoke-WebRequest" in launcher
    assert "http://127.0.0.1:5173/" in launcher


def test_public_discovery_assets_are_present():
    with open("public/robots.txt", encoding="utf-8") as handle:
        assert "Allow: /" in handle.read()
    with open("public/site.webmanifest", encoding="utf-8") as handle:
        manifest = json.load(handle)
    assert manifest["lang"] == "es"
    assert manifest["start_url"] == "/"


def test_api_sets_basic_security_headers():
    try:
        with urlopen(f"{BASE_URL}/api/health", timeout=2) as response:
            assert response.headers["X-Content-Type-Options"] == "nosniff"
            assert response.headers["Referrer-Policy"] == "no-referrer"
            assert response.headers["Cache-Control"] == "no-store"
    except (URLError, TimeoutError) as error:
        pytest.skip(f"API local no disponible: {error}")


def test_frontend_and_api_smoke_flow():
    try:
        with urlopen("http://localhost:5173/", timeout=2) as response:
            html = response.read().decode("utf-8")
            assert response.status == 200
            assert 'id="root"' in html
            assert "/src/main.jsx" in html
        status, payload = get_json("/api/overview")
        assert status == 200
        assert "dataStatus" in payload
    except (URLError, TimeoutError) as error:
        pytest.skip(f"Frontend/API local no disponible: {error}")


@pytest.mark.parametrize("path", ["/api/overview", "/api/history", "/api/quality", "/api/budgets", "/api/contracts?pageSize=2", "/api/companies?limit=2", "/api/grants?pageSize=2", "/api/coverage", "/api/policies"])
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


def test_quality_report_keeps_audit_counts():
    status, payload = get_json("/api/quality")
    assert status == 200
    assert {"placsp", "igae", "bdns", "ign-geography"}.issubset({row["id"] for row in payload["data"]})
    assert all(row["records"] >= 0 and row["duplicates"] >= 0 for row in payload["data"])


def test_population_endpoint_returns_official_municipal_result():
    try:
        with urlopen(f"{BASE_URL}/api/population?q=Sevilla&limit=3", timeout=12) as response:
            payload = json.loads(response.read().decode("utf-8"))
            assert response.status == 200
            assert payload["meta"]["dataStatus"] == "official_live"
            assert payload["meta"]["searchField"] == "municipality"
            assert payload["data"]
            assert {"municipality", "province", "population"}.issubset(payload["data"][0])
    except (URLError, TimeoutError) as error:
        pytest.skip(f"INE no disponible: {error}")


def test_contract_rows_expose_adjudicatario_when_available():
    status, payload = get_json("/api/contracts?pageSize=2")
    assert status == 200
    ids = [row["procurement_id"] for row in payload["data"]]
    assert len(ids) == len(set(ids))
    assert isinstance(payload["data"], list)
    for row in payload["data"]:
        assert "winner_name" in row


def test_community_geography_returns_simplified_official_boundaries():
    status, payload = get_json("/api/geography/communities")
    assert status == 200
    assert payload["meta"]["dataStatus"] in {"official_live_simplified", "official_snapshot_simplified"}
    assert payload["meta"]["source"].startswith("IGN")
    assert payload["data"]
    assert {"id", "names", "coordinates"}.issubset(payload["data"][0])


def test_publication_datasets_are_not_presented_as_budget_payments():
    status, contracts = get_json("/api/contracts?pageSize=20")
    assert status == 200
    status, grants = get_json("/api/grants?pageSize=20")
    assert status == 200
    financial_execution_fields = {"paid_amount", "committed_amount", "recognized_amount", "final_credit"}
    assert not financial_execution_fields.intersection(*(row.keys() for row in contracts["data"]))
    assert not financial_execution_fields.intersection(*(row.keys() for row in grants["data"]))


def test_policy_export_contains_parent_and_child_rows():
    with urlopen(f"{BASE_URL}/api/export.csv?entity=policies", timeout=5) as response:
        body = response.read().decode("utf-8-sig")
        assert response.status == 200
        assert "partida" in body and "nivel" in body
        assert "Pensiones" in body
        assert '"partida"' in body


def test_companies_csv_export_is_available():
    try:
        with urlopen(f"{BASE_URL}/api/export.csv?entity=companies", timeout=4) as response:
            body = response.read(300).decode("utf-8-sig")
            assert response.status == 200
            assert "name" in body
    except (URLError, TimeoutError) as error:
        pytest.skip(f"API local no disponible: {error}")


def test_company_insights_report_concentration_denominator():
    status, payload = get_json("/api/companies/insights")
    assert status == 200
    assert payload["data"]["entity_count"] >= 1
    assert float(payload["data"]["top5_amount"]) <= float(payload["data"]["total_amount"])


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


def test_search_contract_results_link_to_internal_profiles():
    status, payload = get_json("/api/search?q=ayuntamiento")
    assert status == 200
    contract_rows = [row for row in payload["data"] if row["type"] == "contract"]
    if contract_rows:
        assert "vista=contracts" in contract_rows[0]["sourceUrl"]


def test_coverage_exposes_partial_and_blocked_sources():
    status, payload = get_json("/api/coverage")
    assert status == 200
    assert payload["meta"]["checkedAt"]
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


def test_contract_detail_exposes_verified_money_trail_fields():
    status, contracts = get_json("/api/contracts?pageSize=1")
    assert status == 200 and contracts["data"]
    status, payload = get_json(f"/api/contracts/{contracts['data'][0]['procurement_id']}")
    assert status == 200
    assert "contracting_authority" in payload["data"]
    assert "winner_name" in payload["data"]
    assert isinstance(payload["data"].get("events", []), list)


def test_grant_detail_exposes_official_call():
    status, grants = get_json("/api/grants?pageSize=1")
    assert status == 200 and grants["data"]
    code = grants["data"][0]["bdns_code"]
    status, payload = get_json(f"/api/grants/{code}")
    assert status == 200
    assert payload["data"]["bdns_code"] == code
    assert payload["data"]["source_url"]


def test_grant_concessions_expose_pagination_metadata():
    try:
        status, payload = get_json("/api/grants/925963/concesiones?page=0&pageSize=10")
        assert status == 200
        assert payload["meta"]["dataStatus"] == "official_live"
        assert payload["meta"]["page"] == 0
        assert payload["meta"]["pageSize"] == 10
        assert isinstance(payload["data"], list)
    except (URLError, TimeoutError) as error:
        pytest.skip(f"BDNS no disponible: {error}")


def test_unknown_route_is_not_found():
    with pytest.raises(HTTPError) as error:
        urlopen(f"{BASE_URL}/api/does-not-exist", timeout=2)
    assert error.value.code == 404
