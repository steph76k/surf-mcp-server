import requests


def get_marine_forecast(lat: float, lon: float):

    url = (
        "https://marine-api.open-meteo.com/v1/marine"
        f"?latitude={lat}"
        f"&longitude={lon}"
        "&hourly=wave_height,wave_direction,wave_period"
    )

    response = requests.get(url, timeout=10)

    response.raise_for_status()

    return response.json()