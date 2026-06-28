import asyncio

from aqi_in_api import create_aqi_client


async def main() -> None:
    client = create_aqi_client()

    ip_details = await client.get_ip_details()
    print(ip_details)

    nearest_location = await client.get_nearest_location(
        lat=ip_details.lat,
        long=ip_details.lon,
    )
    print(nearest_location)

    station = nearest_location[0].location_slug

    location_details = await client.get_location_by_slug(slug=station)
    print(location_details)

    history = await client.get_last_24_hour_history(
        slug=station,
        sensorname="pm25",
        slug_type="locationId",
    )
    print(history)

    history_30_days = await client.get_last_30_days_history(
        slug=station,
        sensorname="pm25",
        slug_type="locationId",
    )
    print(history_30_days)


asyncio.run(main())
