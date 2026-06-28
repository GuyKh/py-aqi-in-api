# py-aqi-in-api

Python SDK for the [AQI.in](https://aqi.in) Air Quality API.

Fully typed, async, using modern Python (3.11+), dataclasses, and httpx.

> **Source**: This is a Python port of the [aqi-in-api](https://github.com/neo773/aqi-in-api) TypeScript SDK by [@neo773](https://github.com/neo773).

## Installation

```bash
pip install py-aqi-in-api
```

Requires Python 3.11+.

## Usage

```python
import asyncio

from aqi_in_api import AQIClient


async def main() -> None:
    client = AQIClient()

    ip_details = await client.get_ip_details()
    print(f"Location: {ip_details.city}, {ip_details.country}")

    nearest = await client.get_nearest_location(
        lat=ip_details.lat, long=ip_details.lon,
    )
    station = nearest[0]
    print(f"Nearest station: {station.station} ({station.location_slug})")

    location = await client.get_location_by_slug(slug=station.location_slug)
    print(f"Location AQI: {location[0].iaqi}")

    history = await client.get_last_24_hour_history(
        slug=station.location_slug, sensorname="pm25", slug_type="locationId",
    )
    print(f"24h PM2.5 avg: {history.avgValue}")

    await client.close()


asyncio.run(main())
```

## API

### `create_aqi_client(config?)`

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `token` | `str \| None` | No | JWT authentication token (auto-generated if omitted) |
| `base_url` | `str` | No | API base URL (default: `https://apiserver.aqi.in`) |
| `user_agent` | `str` | No | Custom user agent |

### Methods

All methods take keyword-only arguments. No `*Params` objects needed.

| Method | Keyword Args | Returns | Description |
|--------|-------------|---------|-------------|
| `get_ip_details()` | — | `IPDetails` | Get location from your IP address |
| `get_nearest_location(**kwargs)` | `lat`, `long`, `type?` | `list[Station]` | Get nearest monitoring stations by coordinates |
| `get_location_by_slug(**kwargs)` | `slug`, `type?` | `list[LocationDetails]` | Get location details by slug |
| `search(**kwargs)` | `search_string` | `SearchResults` | Search locations by name |
| `get_last_12_hour_history(**kwargs)` | `slug`, `sensorname`, `slug_type` | `HistoryData` | Get 12-hour sensor history |
| `get_last_24_hour_history(**kwargs)` | `slug`, `sensorname`, `slug_type` | `HistoryDataWithWHO` | Get 24-hour history with WHO guidelines |
| `get_last_7_days_history(**kwargs)` | `slug`, `sensorname`, `slug_type` | `HistoryDataWithWHO` | Get 7-day sensor history |
| `get_last_30_days_history(**kwargs)` | `slug`, `sensorname`, `slug_type` | `HistoryDataWithWHO` | Get 30-day sensor history |
| `get_rankings(**kwargs)` | `sensorname`, `type`, `limit=10` | `list[RankingEntry]` | Get city or country pollution rankings |
| `close()` | — | `None` | Close the underlying HTTP client |

### Types

```python
from aqi_in_api.models import (
    Station, City, State, Country,
    LocationDetails, IPDetails, SearchResults, RankingEntry,
    HistoryData, HistoryDataWithWHO,
    IAQI, Weather, WeatherCondition, WeatherSimple, UVCondition,
    SensorName, SearchType, SlugType, LocationType, RankType,
)
```

## Development

```bash
git clone https://github.com/GuyKh/py-aqi-in-api
cd py-aqi-in-api
uv sync --dev
uv run pytest
uv run ruff check .
```

## License

MIT

## Disclaimer

This is an **unofficial** API client and is not affiliated with, endorsed by, or associated with AQI.in or its parent organization. This package is provided for educational and informational purposes under fair use.
