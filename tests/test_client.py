from __future__ import annotations

from datetime import UTC, datetime, timedelta

import jwt
import pytest

from aqi_in_api import AQIClient, AQIException, ClientConfig, create_aqi_client

IP_DETAILS_MOCK = {
    "city": "Delhi",
    "country": "India",
    "countryCode": "IN",
    "lat": 28.61,
    "lon": 77.23,
    "offset": 19800,
    "query": "1.2.3.4",
    "regionName": "Delhi",
    "status": "success",
    "timezone": "Asia/Kolkata",
    "zip": "",
}


class TestCreateAQIClient:
    def test_create_without_config(self) -> None:
        client = create_aqi_client()
        assert isinstance(client, AQIClient)

    def test_create_with_config(self) -> None:
        config = ClientConfig(token="test-token")
        client = create_aqi_client(config)
        assert isinstance(client, AQIClient)


class TestAQIClient:
    async def test_uses_default_base_url(self, httpx_mock) -> None:
        httpx_mock.add_response(json={"status": "success", "data": IP_DETAILS_MOCK})
        client = AQIClient()
        result = await client.get_ip_details()
        assert result.city == "Delhi"
        request = httpx_mock.get_requests()[0]
        assert str(request.url).startswith("https://apiserver.aqi.in")

    async def test_uses_custom_base_url(self, httpx_mock) -> None:
        httpx_mock.add_response(json={"status": "success", "data": IP_DETAILS_MOCK})
        client = AQIClient(ClientConfig(base_url="https://custom.api.com"))
        await client.get_ip_details()
        request = httpx_mock.get_requests()[0]
        assert str(request.url).startswith("https://custom.api.com")

    async def test_uses_custom_token(self, httpx_mock) -> None:
        httpx_mock.add_response(json={"status": "success", "data": IP_DETAILS_MOCK})
        client = AQIClient(ClientConfig(token="my-token"))
        await client.get_ip_details()
        request = httpx_mock.get_requests()[0]
        assert request.headers.get("authorization") == "bearer my-token"

    async def test_auto_generates_jwt_token(self, httpx_mock) -> None:
        httpx_mock.add_response(json={"status": "success", "data": IP_DETAILS_MOCK})
        client = AQIClient()
        await client.get_ip_details()
        request = httpx_mock.get_requests()[0]
        auth = request.headers.get("authorization", "")
        assert auth.startswith("bearer ")
        token = auth.removeprefix("bearer ")
        payload = jwt.decode(token, "masai", algorithms=["HS256"])
        assert payload["userID"] == 1
        assert payload["exp"] is not None

    async def test_token_expiry_is_7_days(self, httpx_mock) -> None:
        httpx_mock.add_response(json={"status": "success", "data": IP_DETAILS_MOCK})
        client = AQIClient()
        await client.get_ip_details()
        request = httpx_mock.get_requests()[0]
        token = request.headers.get("authorization", "").removeprefix("bearer ")
        payload = jwt.decode(token, "masai", algorithms=["HS256"])
        expected_duration = timedelta(days=7)
        actual_duration = datetime.fromtimestamp(payload["exp"], tz=UTC) - datetime.fromtimestamp(
            payload["iat"], tz=UTC
        )
        assert actual_duration == expected_duration

    async def test_raises_on_http_error(self, httpx_mock) -> None:
        httpx_mock.add_response(status_code=404, text="Not Found")
        client = AQIClient()
        with pytest.raises(AQIException) as exc:
            await client.get_ip_details()
        assert exc.value.status_code == 404

    async def test_raises_on_failed_status(self, httpx_mock) -> None:
        httpx_mock.add_response(
            json={"status": "failed", "message": "Invalid request", "status_code": 400}
        )
        client = AQIClient()
        with pytest.raises(AQIException) as exc:
            await client.get_ip_details()
        assert exc.value.status_code == 400
        assert "Invalid request" in str(exc.value)

    async def test_close(self) -> None:
        client = AQIClient()
        await client.close()
