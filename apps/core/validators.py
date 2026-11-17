import re
from typing import Tuple

def validate_and_clean_phone(phone_raw: str) -> Tuple[bool, str, str]:
    """
    Validates and normalizes phone number.
    Accepts:
    +7 999 123-45-67, 89991234567, 79991234567, 9991234567, +375..., etc.
    Returns:
    (is_valid, normalized_phone, error_message)
    """
    if not phone_raw or not isinstance(phone_raw, str):
        return False, "", "Укажите номер телефона"

    phone_trimmed = phone_raw.strip()
    if not phone_trimmed:
        return False, "", "Укажите номер телефона"

    # Check for invalid letters or non-phone characters
    # If the input has Cyrillic or Latin letters, reject immediately
    if re.search(r'[a-zA-Zа-яА-ЯёЁ]', phone_trimmed):
        return False, "", "Номер телефона не должен содержать буквы"

    # Extract digits only
    digits = re.sub(r'\D', '', phone_trimmed)

    if not digits:
        return False, "", "Номер телефона должен содержать цифры"

    # Russian standard: 10 digits (e.g. 9991234567) or 11 digits (8999... or 7999...)
    if len(digits) == 10:
        normalized = f"+7{digits}"
    elif len(digits) == 11 and digits.startswith(('7', '8')):
        normalized = f"+7{digits[1:]}"
    elif 10 <= len(digits) <= 15:
        # International numbers
        normalized = f"+{digits}"
    else:
        return False, "", "Некорректная длина номера (требуется 10-11 цифр)"

    return True, normalized, ""
