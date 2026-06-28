from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

SensorName = Literal["pm25", "pm10", "aqi", "AQI-IN", "co", "no2", "o3", "so2"]
SearchType = Literal["locationId", "cityId", "stateId", "countryId"]
LocationType = Literal["station", "city"]
SlugType = Literal[1, 2, 3, 4]
RankType = Literal["city", "country"]


@dataclass(frozen=True)
class IAQI:
    AQI_IN: int | None = None
    aqi: int | None = None
    pm25: int | None = None
    pm10: int | None = None
    co: int | None = None
    no2: int | None = None
    o3: int | None = None
    so2: int | None = None
    noise: int | None = None
    tvoc: int | None = None
    t: float | None = None


@dataclass(frozen=True)
class WeatherCondition:
    text: str
    icon: str
    code: int


@dataclass(frozen=True)
class UVCondition:
    text: str
    color_code: str


@dataclass(frozen=True)
class Weather:
    uid: str
    cloud: int
    condition: WeatherCondition
    feelslike_c: float
    feelslike_f: float
    gust_kph: float
    gust_mph: float
    humidity: int
    is_day: int
    last_updated: str
    last_updated_epoch: int
    precip_in: float
    precip_mm: float
    pressure_in: float
    pressure_mb: float
    temp_c: float
    temp_f: float
    uv: float
    vis_km: float
    vis_miles: float
    wind_degree: int
    wind_dir: str
    wind_kph: float
    wind_mph: float
    uv_condition: UVCondition | None = None


@dataclass(frozen=True)
class WeatherSimple:
    temp_c: float
    temp_f: float


@dataclass(frozen=True, kw_only=True)
class BaseLocation:
    location: str
    locationId: str
    slug: str
    latitude: float
    longitude: float
    flag: str
    searchType: SearchType
    uid: str | None = None


@dataclass(frozen=True)
class Station(BaseLocation):
    station: str
    city: str
    state: str
    country: str
    location_slug: str
    city_slug: str
    state_slug: str
    country_slug: str
    time_zone: str
    coordinates: tuple[float, float]
    background_image: str
    city_lat: float
    city_lon: float
    state_lat: float
    state_lon: float
    country_lat: float
    country_lon: float
    isOnline: bool
    isRankedCity: bool
    iaqi: IAQI
    updated_at: str
    weather: Weather | None = None
    updatedAt: str | None = None
    createdAt: str | None = None
    distance: float | None = None
    source: str | None = None


@dataclass(frozen=True)
class City(BaseLocation):
    city: str
    state: str
    country: str
    weather: WeatherSimple | None = None
    iaqi: IAQI | None = None


@dataclass(frozen=True)
class State(BaseLocation):
    state: str
    country: str


@dataclass(frozen=True)
class Country(BaseLocation):
    pass


@dataclass(frozen=True)
class IPDetails:
    city: str
    country: str
    countryCode: str
    lat: float
    lon: float
    offset: int
    query: str
    regionName: str
    status: str
    timezone: str
    zip: str


@dataclass(frozen=True)
class LocationDetails:
    uid: str
    location: str
    country: str
    time_zone: str
    latitude: float
    longitude: float
    country_slug: str
    background_image: str
    flag: str
    country_lat: float
    country_lon: float
    isOnline: bool
    isRankedCity: bool
    iaqi: IAQI
    updated_at: str
    locationId: str
    searchType: SearchType
    slug: str
    station: str | None = None
    city: str | None = None
    state: str | None = None
    location_slug: str | None = None
    city_slug: str | None = None
    state_slug: str | None = None
    city_lat: float | None = None
    city_lon: float | None = None
    state_lat: float | None = None
    state_lon: float | None = None
    weather: Weather | None = None
    updatedAt: str | None = None


@dataclass(frozen=True)
class HistoryData:
    minValue: float
    maxValue: float
    avgValue: float
    averageArray: list[float]
    timeArray: list[str]


@dataclass(frozen=True)
class WHOGuideData:
    Data: HistoryData


@dataclass(frozen=True)
class HistoryDataWithWHO(HistoryData):
    whoguidedata: WHOGuideData | None = None


@dataclass(frozen=True)
class SearchResults:
    countries: list[Country]
    states: list[State]
    cities: list[City]
    stations: list[Station]


@dataclass(frozen=True)
class RankingEntry:
    location: str
    locationId: str
    flag: str
    slug: str
    latitude: float
    longitude: float
    updated_at: str
    rank: int
    city: str | None = None
    state: str | None = None
    country: str | None = None
    pm25: float | None = None
    pm10: float | None = None
    aqi: float | None = None


@dataclass(frozen=True)
class GetNearestLocationParams:
    lat: float
    long: float
    type: LocationType | None = None


@dataclass(frozen=True)
class GetLocationBySlugParams:
    slug: str
    type: SlugType | None = None


@dataclass(frozen=True)
class SearchParams:
    searchString: str


@dataclass(frozen=True)
class GetHistoryParams:
    slug: str
    sensorname: SensorName
    slugType: SearchType


@dataclass(frozen=True)
class GetRankingParams:
    sensorname: SensorName
    type: RankType
    limit: int = 10
