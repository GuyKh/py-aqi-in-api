from datetime import UTC, datetime, timedelta

import jwt

from aqi_in_api._token import JWT_SECRET, TOKEN_EXPIRY_SECONDS, generate_token


class TestGenerateToken:
    def test_returns_valid_jwt(self) -> None:
        token = generate_token()
        assert token.count(".") == 2

    def test_contains_correct_payload(self) -> None:
        token = generate_token()
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        assert payload["userID"] == 1
        assert "iat" in payload
        assert "exp" in payload

    def test_has_7_day_expiry(self) -> None:
        token = generate_token()
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        actual_duration = datetime.fromtimestamp(payload["exp"], tz=UTC) - datetime.fromtimestamp(
            payload["iat"], tz=UTC
        )
        assert actual_duration == timedelta(seconds=TOKEN_EXPIRY_SECONDS)
