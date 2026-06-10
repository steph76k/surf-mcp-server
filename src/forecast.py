from spots import get_spot
from providers.open_meteo import get_marine_forecast
from providers.worldtides import get_tides
from datetime import datetime, timezone

def degrees_to_direction(deg: float) -> str:

    directions = [
        "N",
        "NNE",
        "NE",
        "ENE",
        "E",
        "ESE",
        "SE",
        "SSE",
        "S",
        "SSW",
        "SW",
        "WSW",
        "W",
        "WNW",
        "NW",
        "NNW",
    ]

    return directions[
        round(deg / 22.5) % 16
    ]

def normalize_open_meteo(
    data: dict,
    interval_hours: int = 3
) -> list:

    result = []

    times = data["hourly"]["time"]
    heights = data["hourly"]["wave_height"]
    periods = data["hourly"]["wave_period"]
    directions = data["hourly"]["wave_direction"]

    for i in range(
        0,
        min(24, len(times)),
        interval_hours
    ):

        result.append(
            {
                "time": times[i],
                "wave_height_ft": round(
                    heights[i] * 3.28084,
                    1
                ),
                "wave_period_s": round(
                    periods[i],
                    1
                ),
                "swell_direction": degrees_to_direction(
                    directions[i]
                ),
                "swell_direction_deg": directions[i]
            }
        )

    return result


def lookup_forecast(spot_id: str):

    spot = get_spot(spot_id)

    lat = spot["coordinates"]["lat"]
    lon = spot["coordinates"]["lon"]

    raw = get_marine_forecast(lat, lon)

    return normalize_open_meteo(raw)

def classify_tide(
    height: float,
    min_height: float,
    max_height: float
) -> str:

    tide_range = max_height - min_height

    if tide_range == 0:
        return "mid"

    normalized = (
        height - min_height
    ) / tide_range

    if normalized < 0.33:
        return "low"

    if normalized < 0.66:
        return "mid"

    return "high"


def normalize_tides(data: dict) -> list:

    result = []

    heights = data["heights"]

    min_height = min(
        h["height"]
        for h in heights
    )

    max_height = max(
        h["height"]
        for h in heights
    )

    # WorldTides liefert 30-Minuten-Werte
    # Alle 6 Werte = alle 3 Stunden

    for i in range(0, len(heights), 6):

        tide_height_m = heights[i]["height"]

        result.append(
            {
                "time": heights[i]["date"],
                "tide_height_ft": round(
                    tide_height_m * 3.28084,
                    1
                ),
                "tide_state": classify_tide(
                    tide_height_m,
                    min_height,
                    max_height
                )
            }
        )

    return result

def lookup_tides(
    spot_id: str
):

    spot = get_spot(spot_id)

    lat = spot["coordinates"]["lat"]
    lon = spot["coordinates"]["lon"]

    raw = get_tides(
        lat,
        lon
    )

    return normalize_tides(raw)

def parse_time(ts):

    if "+" in ts:
        return datetime.strptime(
            ts,
            "%Y-%m-%dT%H:%M%z"
        )

    return datetime.strptime(
        ts,
        "%Y-%m-%dT%H:%M"
    ).replace(
        tzinfo=timezone.utc
    )

def lookup_conditions(
    spot_id: str
):

    forecast = lookup_forecast(spot_id)
    tides = lookup_tides(spot_id)

    result = []

    for forecast_item in forecast:

        forecast_time = parse_time(
            forecast_item["time"]
        )

        closest_tide = min(
            tides,
            key=lambda tide: abs(
                parse_time(
                    tide["time"]
                ) - forecast_time
            )
        )

        result.append(
            {
                **forecast_item,
                "tide_height_ft": closest_tide["tide_height_ft"],
                "tide_state": closest_tide["tide_state"]
            }
        )

    return result