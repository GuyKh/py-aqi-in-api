from urllib.parse import urlencode, urljoin

from aqi_in_api.models import SlugType


def build_url(
    base_url: str,
    endpoint: str,
    params: dict[str, str | int | None] | None = None,
) -> str:
    """Build a URL from base, endpoint, and query parameters.

    Always appends ?source=web to match the TS SDK behavior.
    """
    url = urljoin(base_url.rstrip("/") + "/", endpoint.lstrip("/"))
    query_params: dict[str, str] = {"source": "web"}

    if params:
        for key, value in params.items():
            if value is not None:
                query_params[key] = str(value)

    return f"{url}?{urlencode(query_params)}"


def get_slug_depth(slug: str) -> SlugType:
    """Determine the slug depth (1=country, 2=state, 3=city, 4=station)."""
    depth = slug.count("/") + 1
    if depth < 1:
        return 1
    if depth > 4:
        return 4
    return depth  # type: ignore[return-value]
