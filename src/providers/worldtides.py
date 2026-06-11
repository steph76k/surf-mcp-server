import os

from providers.http import get_json


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

    return get_json(
        "https://www.worldtides.info/api/v3",
        params=params,
    )
