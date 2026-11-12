import hmac
import hashlib
import time
from urllib.parse import urlencode
from django.test import SimpleTestCase
from apps.core.telegram_auth import verify_telegram_init_data

class TelegramAuthTestCase(SimpleTestCase):
    def setUp(self):
        self.bot_token = "123456789:TEST_BOT_TOKEN_FOR_SIGNATURE_VERIFICATION"

    def _generate_valid_init_data(self, params: dict, token: str) -> str:
        # Build data_check_string
        data_check_list = [f"{k}={params[k]}" for k in sorted(params.keys())]
        data_check_string = "\n".join(data_check_list)

        secret_key = hmac.new(
            key=b"WebAppData",
            msg=token.encode('utf-8'),
            digestmod=hashlib.sha256
        ).digest()

        computed_hash = hmac.new(
            key=secret_key,
            msg=data_check_string.encode('utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()

        full_params = dict(params)
        full_params['hash'] = computed_hash
        return urlencode(full_params)

    def test_valid_signature_accepted(self):
        params = {
            'auth_date': str(int(time.time())),
            'query_id': 'AAHdF6IQAAAAAN0XohDhrOrc',
            'user': '{"id":987654321,"first_name":"Valentin","username":"lead_dev"}',
        }
        init_data_raw = self._generate_valid_init_data(params, self.bot_token)

        is_valid, parsed_data, err = verify_telegram_init_data(init_data_raw, bot_token=self.bot_token)
        self.assertTrue(is_valid)
        self.assertIsNone(err)
        self.assertEqual(parsed_data['user']['id'], 987654321)
        self.assertEqual(parsed_data['user']['first_name'], "Valentin")

    def test_tampered_signature_rejected(self):
        params = {
            'auth_date': str(int(time.time())),
            'query_id': 'AAHdF6IQAAAAAN0XohDhrOrc',
            'user': '{"id":987654321,"first_name":"Valentin"}',
        }
        init_data_raw = self._generate_valid_init_data(params, self.bot_token)
        
        # Tamper with user id in string
        tampered_raw = init_data_raw.replace('987654321', '111111111')

        is_valid, parsed_data, err = verify_telegram_init_data(tampered_raw, bot_token=self.bot_token)
        self.assertFalse(is_valid)
        self.assertIn("Invalid signature", err)

    def test_expired_auth_date_rejected(self):
        expired_timestamp = int(time.time()) - 90000  # > 24 hours ago
        params = {
            'auth_date': str(expired_timestamp),
            'query_id': 'AAHdF6IQAAAAAN0XohDhrOrc',
            'user': '{"id":987654321,"first_name":"Valentin"}',
        }
        init_data_raw = self._generate_valid_init_data(params, self.bot_token)

        is_valid, parsed_data, err = verify_telegram_init_data(
            init_data_raw,
            bot_token=self.bot_token,
            max_age_seconds=86400
        )
        self.assertFalse(is_valid)
        self.assertIn("expired", err)
