import os

import requests


def get_tides(lat: float, lon: float):

    api_key = os.environ["WORLDTIDES_API_KEY"]

    params = {
        "heights": "",
        "extremes": "",
        "datum": "CD",
        "localtime": "",
        "timezone": "",
        "step":3600,
        "days": 1,
        "lat": lat,
        "lon": lon,
        "key": api_key,
    }

    response = requests.get(
        "https://www.worldtides.info/api/v3",
        params=params,
        timeout=10,
    )

    response.raise_for_status()

    return response.json()
