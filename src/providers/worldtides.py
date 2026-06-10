import os
import requests


def get_tides(
    lat: float,
    lon: float
):

    api_key = os.environ["WORLDTIDES_API_KEY"]

    url = (
        "https://www.worldtides.info/api/v3"
        f"?heights"
        f"&lat={lat}"
        f"&lon={lon}"
        f"&key={api_key}"
    )

    response = requests.get(
        url,
        timeout=10
    )

    response.raise_for_status()

    return response.json()