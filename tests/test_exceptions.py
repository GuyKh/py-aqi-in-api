from aqi_in_api import AQIException


class TestAQIException:
    def test_creates_with_message_and_status_code(self) -> None:
        exc = AQIException("Test error", 400)
        assert exc.message == "Test error"
        assert exc.status_code == 400
        assert exc.name == "AQIException"

    def test_creates_with_body(self) -> None:
        exc = AQIException("Test error", 500, body='{"error": "internal"}')
        assert exc.body == '{"error": "internal"}'

    def test_is_exception_subclass(self) -> None:
        exc = AQIException("Test", 400)
        assert isinstance(exc, Exception)
