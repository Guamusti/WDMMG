from pathlib import Path

from etl.shared.io import write_jsonl


def test_write_jsonl_is_utf8_and_line_delimited(tmp_path: Path):
    output = tmp_path / "rows.jsonl"
    write_jsonl([{"title": "Ayuda pública", "amount": "10.00"}], output)
    assert output.read_text(encoding="utf-8") == '{"title": "Ayuda pública", "amount": "10.00"}\n'
