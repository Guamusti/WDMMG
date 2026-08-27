from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation
from typing import Any


def normalize_text(value: Any) -> str | None:
    if value is None:
        return None
    cleaned = " ".join(str(value).replace("\u00a0", " ").split())
    return cleaned or None


def normalize_entity_name(value: Any) -> str | None:
    text = normalize_text(value)
    return text.lower() if text else None


def normalize_tax_id(value: Any) -> str | None:
    text = normalize_text(value)
    if not text:
        return None
    return re.sub(r"[ .-]", "", text).upper()


def parse_euro(value: Any) -> Decimal | None:
    if value is None or value == "":
        return None
    text = str(value).strip().replace("\u00a0", "").replace("€", "").replace(" ", "")
    if "," in text and "." in text:
        text = text.replace(".", "").replace(",", ".")
    elif "," in text:
        text = text.replace(",", ".")
    try:
        return Decimal(text)
    except (InvalidOperation, ValueError):
        return None


def normalize_code(value: Any) -> str | None:
    text = normalize_text(value)
    return text.upper() if text else None
