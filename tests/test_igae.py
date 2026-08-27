from pathlib import Path

import pytest

from etl.budgets.igae_extract import parse_execution_workbook, parse_workbook


def test_igae_rows_keep_period_state_and_dataset_version():
    path = Path("data/raw/igae/igae-20260827T151648Z.xlsx")
    if not path.exists():
        pytest.skip("muestra IGAE no disponible")
    rows = parse_execution_workbook(path, "https://official.example/igae.xlsx", "test-run")
    assert rows
    assert rows[0]["period_state"] == "provisional"
    assert rows[0]["dataset_version"].startswith("igae-")
    assert len(rows[0]["dataset_version"].rsplit("-", 1)[-1]) == 12


def test_igae_raw_rows_read_period_from_workbook_header():
    path = Path("data/raw/igae/igae-20260827T151648Z.xlsx")
    if not path.exists():
        pytest.skip("muestra IGAE no disponible")
    rows = parse_workbook(path, "https://official.example/igae.xlsx", "test-run")
    assert rows and rows[0]["period"] == "2026-04"
    assert rows[0]["fiscal_year"] == 2026


def test_igae_classification_is_split_when_source_publishes_code():
    path = Path("data/raw/igae/igae-20260827T151648Z.xlsx")
    if not path.exists():
        pytest.skip("muestra IGAE no disponible")
    rows = parse_execution_workbook(path, "https://official.example/igae.xlsx", "test-run")
    chapter = next(row for row in rows if row["classification_level"] == "chapter" and row["classification_code"])
    assert chapter["classification_name"]
