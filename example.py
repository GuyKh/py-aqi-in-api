import asyncio

from aqi_in_api import AQIClient


async def main() -> None:
    client = AQIClient()

    ip_details = await client.get_ip_details()
    print("IP Details:", ip_details)

    nearest_location = await client.get_nearest_location(
        lat=ip_details.lat,
        long=ip_details.lon,
    )
    print("Nearest location:", nearest_location)

    station = nearest_location[0].location_slug

    location_details = await client.get_location_by_slug(slug=station)
    print("Location details:", location_details)

    history = await client.get_last_24_hour_history(
        slug=station,
        sensorname="pm25",
        slug_type="locationId",
    )
    print("24h history:", history)

    history_30_days = await client.get_last_30_days_history(
        slug=station,
        sensorname="pm25",
        slug_type="locationId",
    )
    print("30 days history:", history_30_days)

    await client.close()


asyncio.run(main())
