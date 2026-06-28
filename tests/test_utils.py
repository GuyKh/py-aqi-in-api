from aqi_in_api._utils import build_url, get_slug_depth


class TestBuildUrl:
    def test_creates_url_with_base_and_endpoint(self) -> None:
        url = build_url("https://api.example.com", "/test")
        assert url.startswith("https://api.example.com/test?")

    def test_adds_source_param(self) -> None:
        url = build_url("https://api.example.com", "/test")
        assert "source=web" in url

    def test_adds_provided_params(self) -> None:
        url = build_url("https://api.example.com", "/test", {"foo": "bar", "num": 123})
        assert "foo=bar" in url
        assert "num=123" in url

    def test_ignores_none_params(self) -> None:
        params = {"defined": "value", "notDefined": None}
        url = build_url("https://api.example.com", "/test", params)
        assert "defined=value" in url
        assert "notDefined" not in url


class TestGetSlugDepth:
    def test_returns_1_for_country(self) -> None:
        assert get_slug_depth("india") == 1

    def test_returns_2_for_state(self) -> None:
        assert get_slug_depth("india/delhi") == 2

    def test_returns_3_for_city(self) -> None:
        assert get_slug_depth("india/delhi/new-delhi") == 3

    def test_returns_4_for_station(self) -> None:
        assert get_slug_depth("india/delhi/new-delhi/janpath") == 4
