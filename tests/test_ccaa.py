from pathlib import Path

from openpyxl import Workbook

from etl.territorial.ccaa_execution import normalize_workbook


def test_normalize_workbook_keeps_latest_cumulative_month_and_provenance(tmp_path: Path):
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Andalucía"
    sheet.append(["ANDALUCÍA. SERIE DE INGRESOS Y GASTOS."])
    sheet.append(["Derechos/Obligaciones reconocidas. Datos acumulados."])
    sheet.append(["Periodo", "INGRESOS CORRIENTES", "INGRESOS CAPITAL", "INGRESOS NO FINANCIEROS", "GASTOS CORRIENTES", "GASTOS DE CAPITAL", "GASTOS NO FINANCIEROS"])
    sheet.append(["Abril", 10, 1, 11, 12, 2, 14])
    sheet.append(["Mayo", 20, 2, 22, 24, 3, 27])
    source = tmp_path / "ccaa.xlsx"
    workbook.save(source)

    records = normalize_workbook(source, retrieved_at="2026-08-27T00:00:00+00:00")

    assert len(records) == 1
    assert records[0]["territory"] == "Andalucía"
    assert records[0]["period"] == "2026-05"
    assert records[0]["recognized_expense_non_financial"] == 27
    assert records[0]["data_status"] == "advance"
    assert len(records[0]["raw_workbook_sha256"]) == 64
