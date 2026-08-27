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


def valid_spanish_tax_id(value: Any) -> bool | None:
    """Valida el formato y dígito de control de NIF/CIF completos.

    Devuelve None para valores ausentes, anonimizados o que no permiten una
    comprobación honesta (por ejemplo, identificadores parcialmente ocultos).
    """
    tax_id = normalize_tax_id(value)
    if not tax_id or '*' in tax_id or len(tax_id) != 9:
        return None
    if tax_id[0].isdigit():
        if not tax_id[:8].isdigit() or not tax_id[8].isalnum():
            return False
        control = "TRWAGMYFPDXBNJZSQVHLCKE"
        return tax_id[8] == control[int(tax_id[:8]) % 23]
    if tax_id[0] not in "ABCDEFGHJNPQRSUVW" or not tax_id[1:8].isdigit() or not tax_id[8].isalnum():
        return False
    total = 0
    for index, digit in enumerate(tax_id[1:8]):
        number = int(digit)
        total += sum(int(char) for char in str(number * (2 if index % 2 == 0 else 1)))
    control_digit = str((10 - total % 10) % 10)
    control_letter = "JABCDEFGHI"[int(control_digit)]
    return tax_id[8] == control_letter if tax_id[0] in "PQRSNW" else tax_id[8] == control_digit


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
