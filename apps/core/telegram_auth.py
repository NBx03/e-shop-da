import hmac
import hashlib
import json
import time
from urllib.parse import parse_qsl, unquote
from typing import Optional, Dict, Any, Tuple
from django.conf import settings

def verify_telegram_init_data(init_data_raw: str, bot_token: Optional[str] = None, max_age_seconds: int = 86400) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
    """
    Validates Telegram Mini App initData per official Telegram specification:
    https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app

    Returns:
        (is_valid, parsed_data_dict, error_message)
    """
    if not init_data_raw:
        return False, None, "Empty initData"

    token = bot_token or getattr(settings, 'BOT_TOKEN', '')
    if not token:
        return False, None, "Bot token is not configured on server"

    try:
        parsed_qsl = dict(parse_qsl(init_data_raw, keep_blank_values=True))
    except Exception as e:
        return False, None, f"Failed to parse query string: {e}"

    received_hash = parsed_qsl.get('hash')
    if not received_hash:
        return False, None, "Hash field is missing in initData"

    # Telegram algorithm:
    # 1. Sort all key=value pairs except 'hash' alphabetically
    # 2. Join with \n
    data_check_list = []
    for k in sorted(parsed_qsl.keys()):
        if k != 'hash':
            data_check_list.append(f"{k}={parsed_qsl[k]}")
    data_check_string = "\n".join(data_check_list)

    # 3. Secret key is HMAC-SHA256 of bot_token with key "WebAppData"
    secret_key = hmac.new(
        key=b"WebAppData",
        msg=token.encode('utf-8'),
        digestmod=hashlib.sha256
    ).digest()

    # 4. Hash is HMAC-SHA256 of data_check_string with secret_key
    calculated_hash = hmac.new(
        key=secret_key,
        msg=data_check_string.encode('utf-8'),
        digestmod=hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(calculated_hash, received_hash):
        return False, None, "Invalid signature hash"

    # Optional: check auth_date expiration
    auth_date = parsed_qsl.get('auth_date')
    if auth_date:
        try:
            auth_timestamp = int(auth_date)
            current_timestamp = int(time.time())
            if current_timestamp - auth_timestamp > max_age_seconds:
                return False, None, "initData has expired"
        except ValueError:
            return False, None, "Invalid auth_date format"

    # Parse user JSON if present
    parsed_result = dict(parsed_qsl)
    if 'user' in parsed_result:
        try:
            parsed_result['user'] = json.loads(parsed_result['user'])
        except Exception:
            pass

    return True, parsed_result, None
