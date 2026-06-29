from __future__ import annotations

import dataclasses
import typing
from dataclasses import dataclass
from typing import Any, TypeVar

import httpx

from aqi_in_api._constants import DEFAULT_BASE_URL, DEFAULT_USER_AGENT, ENDPOINTS
from aqi_in_api._exceptions import AQIException
from aqi_in_api._token import generate_token
from aqi_in_api._utils import build_url, get_slug_depth
from aqi_in_api.models import (
    HistoryData,
    HistoryDataWithWHO,
    IPDetails,
    LocationDetails,
    LocationType,
    RankingEntry,
    RankType,
    SearchResults,
    SearchType,
    SensorName,
    SlugType,
    Station,
)

T = TypeVar("T")


@dataclass(frozen=True)
class ClientConfig:
    token: str | None = None
    base_url: str = DEFAULT_BASE_URL
    user_agent: str = DEFAULT_USER_AGENT


def _from_dict(model_cls: type[T], data: dict[str, Any]) -> T:
    """Convert a nested dict into a frozen dataclass instance, skipping unknown fields."""
    if not dataclasses.is_dataclass(model_cls) or not isinstance(data, dict):
        return data  # type: ignore[return-value]
    kwargs: dict[str, Any] = {}
    for field in dataclasses.fields(model_cls):
        if field.name not in data:
            continue
        kwargs[field.name] = _convert_value(field.type, data[field.name])
    return model_cls(**kwargs)


def _convert_value(field_type: object, value: Any) -> Any:
    if value is None:
        return None
    origin = typing.get_origin(field_type)
    args = typing.get_args(field_type)
    if origin is typing.Union:
        non_none = [a for a in args if a is not type(None)]
        if non_none:
            return _convert_value(non_none[0], value)
        return None
    if origin is list and args and isinstance(value, list):
        return [_convert_value(args[0], item) for item in value]
    if origin is tuple and args and isinstance(value, (list, tuple)):
        return tuple(_convert_value(args[i], v) for i, v in enumerate(value[: len(args)]))
    try:
        if isinstance(value, dict) and dataclasses.is_dataclass(field_type):
            return _from_dict(field_type, value)  # type: ignore[arg-type]
    except TypeError:
        pass
    return value


def _to_model(model_cls: type[T], data: Any) -> Any:
    if isinstance(data, list):
        return [_from_dict(model_cls, item) for item in data]
    return _from_dict(model_cls, data)


class AQIClient:
    def __init__(self, config: ClientConfig | None = None) -> None:
        config = config or ClientConfig()
        self._base_url = config.base_url
        self._custom_token = config.token
        self._user_agent = config.user_agent
        self._cached_token: str | None = None
        self._http = httpx.AsyncClient(timeout=30.0)

    async def _get_token(self) -> str:
        if self._custom_token is not None:
            return self._custom_token
        if self._cached_token is None:
            self._cached_token = generate_token()
        return self._cached_token

    async def _request(
        self,
        endpoint: str,
        params: dict[str, str | int | float | None] | None = None,
    ) -> Any:
        url = build_url(self._base_url, endpoint, params)
        token = await self._get_token()

        response = await self._http.get(
            url,
            headers={
                "User-Agent": self._user_agent,
                "authorization": f"bearer {token}",
            },
        )

        if not response.is_success:
            raise AQIException(
                f"Request failed: {response.status_code} {response.reason_phrase}",
                response.status_code,
                response.text,
            )

        body: dict[str, Any] = response.json()

        if body.get("status") in ("failed",):
            raise AQIException(
                body.get("message") or body.get("error") or "Unknown error",
                body.get("status_code", 400),
            )

        return body["data"]

    async def get_ip_details(self) -> IPDetails:
        data = await self._request(ENDPOINTS["IP_DETAILS"])
        return _from_dict(IPDetails, data)

    async def get_nearest_location(
        self,
        *,
        lat: float,
        long: float,
        type: LocationType | None = None,
    ) -> list[Station]:
        data = await self._request(
            ENDPOINTS["NEAREST_LOCATION"],
            {"lat": lat, "long": long, "type": "2" if type == "city" else "1"},
        )
        return _to_model(Station, data)  # type: ignore[no-any-return]

    async def get_location_by_slug(
        self,
        *,
        slug: str,
        type: SlugType | None = None,
    ) -> list[LocationDetails]:
        data = await self._request(
            ENDPOINTS["LOCATION_BY_SLUG"],
            {
                "slug": slug,
                "type": type if type is not None else get_slug_depth(slug),
            },
        )
        return _to_model(LocationDetails, data)  # type: ignore[no-any-return]

    async def search(self, *, search_string: str) -> SearchResults:
        data = await self._request(ENDPOINTS["SEARCH"], {"searchString": search_string})
        return _from_dict(SearchResults, data)

    async def get_last_12_hour_history(
        self,
        *,
        slug: str,
        sensorname: SensorName,
        slug_type: SearchType,
    ) -> HistoryData:
        data = await self._request(
            ENDPOINTS["HISTORY_12H"],
            {"slug": slug, "sensorname": sensorname, "slugType": slug_type},
        )
        return _from_dict(HistoryData, data)

    async def get_last_24_hour_history(
        self,
        *,
        slug: str,
        sensorname: SensorName,
        slug_type: SearchType,
    ) -> HistoryDataWithWHO:
        data = await self._request(
            ENDPOINTS["HISTORY_24H"],
            {"slug": slug, "sensorname": sensorname, "slugType": slug_type},
        )
        return _from_dict(HistoryDataWithWHO, data)

    async def get_last_7_days_history(
        self,
        *,
        slug: str,
        sensorname: SensorName,
        slug_type: SearchType,
    ) -> HistoryDataWithWHO:
        data = await self._request(
            ENDPOINTS["HISTORY_7D"],
            {"slug": slug, "sensorname": sensorname, "slugType": slug_type},
        )
        return _from_dict(HistoryDataWithWHO, data)

    async def get_last_30_days_history(
        self,
        *,
        slug: str,
        sensorname: SensorName,
        slug_type: SearchType,
    ) -> HistoryDataWithWHO:
        data = await self._request(
            ENDPOINTS["HISTORY_30D"],
            {"slug": slug, "sensorname": sensorname, "slugType": slug_type},
        )
        return _from_dict(HistoryDataWithWHO, data)

    async def get_rankings(
        self,
        *,
        sensorname: SensorName,
        type: RankType,
        limit: int = 10,
    ) -> list[RankingEntry]:
        data = await self._request(
            ENDPOINTS["RANKINGS"],
            {
                "sensorname": sensorname,
                "type": "1" if type == "country" else "2",
                "limit": limit,
            },
        )
        return _to_model(RankingEntry, data)  # type: ignore[no-any-return]

    async def close(self) -> None:
        await self._http.aclose()


def create_aqi_client(config: ClientConfig | None = None) -> AQIClient:
    return AQIClient(config)
