from providers.http import get_json


def get_marine_forecast(lat: float, lon: float):

    url = (
        "https://marine-api.open-meteo.com/v1/marine"
        f"?latitude={lat}"
        f"&longitude={lon}"
        "&hourly=wave_height,wave_direction,wave_period"
        "&timezone=auto"
    )

    return get_json(url)
