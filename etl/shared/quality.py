from __future__ import annotations

from datetime import date, datetime
from typing import Any, Iterable

from etl.shared.normalize import parse_euro, valid_spanish_tax_id


def _valid_date(value: Any) -> bool:
    if value in (None, ""):
        return True
    text = str(value).strip().replace("Z", "+00:00")
    try:
        datetime.fromisoformat(text)
        return True
    except ValueError:
        try:
            date.fromisoformat(text[:10])
            return True
        except ValueError:
            return False


def record_quality_flags(record: dict[str, Any], id_field: str, date_fields: Iterable[str] = (), amount_fields: Iterable[str] = (), exercise_fields: Iterable[str] = (), tax_id_field: str | None = None) -> list[str]:
    flags: list[str] = []
    if not record.get(id_field):
        flags.append("missing_id")
    for field in date_fields:
        value = record.get(field)
        if value not in (None, "") and not _valid_date(value):
            flags.append(f"invalid_date:{field}")
    for field in amount_fields:
        value = record.get(field)
        if value in (None, ""):
            continue
        amount = parse_euro(value)
        if amount is None:
            flags.append(f"unparseable_amount:{field}")
        elif amount < 0:
            flags.append(f"negative_amount:{field}")
    for field in exercise_fields:
        value = record.get(field)
        if value not in (None, ""):
            try:
                if not 2000 <= int(value) <= 2100:
                    flags.append(f"invalid_exercise:{field}")
            except (TypeError, ValueError):
                flags.append(f"invalid_exercise:{field}")
    if tax_id_field:
        valid = valid_spanish_tax_id(record.get(tax_id_field))
        if valid is False:
            flags.append(f"invalid_tax_id:{tax_id_field}")
    return flags
