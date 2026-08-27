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


@pytest.mark.parametrize("path", ["/api/overview", "/api/budgets", "/api/contracts?pageSize=2", "/api/grants?pageSize=2", "/api/coverage", "/api/policies"])
def test_public_dataset_endpoints_return_json(path):
    status, payload = get_json(path)
    assert status == 200
    assert isinstance(payload, dict)
    assert "data" in payload or "execution" in payload or "dataStatus" in payload


def test_empty_search_is_a_stable_empty_result():
    status, payload = get_json("/api/search?q=")
    assert status == 200
    assert payload == {"data": []}


def test_unknown_route_is_not_found():
    with pytest.raises(HTTPError) as error:
        urlopen(f"{BASE_URL}/api/does-not-exist", timeout=2)
    assert error.value.code == 404
