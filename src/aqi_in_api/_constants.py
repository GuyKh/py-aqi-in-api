DEFAULT_BASE_URL = "https://apiserver.aqi.in"

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/143.0.0.0 Safari/537.36"
)

ENDPOINTS = {
    "NEAREST_LOCATION": "/aqi/v2/getNearestLocation",
    "IP_DETAILS": "/service/get/ip/details",
    "LOCATION_BY_SLUG": "/aqi/v2/getLocationDetailsBySlug",
    "SEARCH": "/aqi/searchLocationCityStateCountry",
    "HISTORY_12H": "/aqi/getLast12HourHistory",
    "HISTORY_24H": "/aqi/v3/getLast24HourHistory",
    "HISTORY_7D": "/aqi/getLast7DaysHistory",
    "HISTORY_30D": "/aqi/getLast30DaysHistory",
    "RANKINGS": "/aqi/getAirQualityRanklistCountryAndCity",
}
