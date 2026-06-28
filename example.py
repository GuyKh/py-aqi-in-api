import asyncio

from aqi_in_api import AQIClient


async def main() -> None:
    client = AQIClient()

    ip_details = await client.get_ip_details()
    print(f"Location: {ip_details.city}, {ip_details.country}")

    nearest = await client.get_nearest_location(lat=ip_details.lat, long=ip_details.lon)
    station = nearest[0]
    print(f"Nearest station: {station.station} ({station.location_slug})")

    location = await client.get_location_by_slug(slug=station.location_slug)
    print(f"Location AQI: {location[0].iaqi}")

    history = await client.get_last_24_hour_history(
        slug=station.location_slug,
        sensorname="pm25",
        slug_type="locationId",
    )
    print(f"24h PM2.5 avg: {history.avgValue}")

    await client.close()


asyncio.run(main())
