from spots import get_spot
from providers.open_meteo import get_marine_forecast
from providers.worldtides import get_tides
from providers.swellcloud import get_swellcloud_forecast
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


def lookup_forecast(
    spot_id: str,
    provider: str = "swellcloud"
):

    spot = get_spot(spot_id)

    lat = spot["coordinates"]["lat"]
    lon = spot["coordinates"]["lon"]

    if provider == "open_meteo":

        raw = get_marine_forecast(
            lat,
            lon
        )

        return normalize_open_meteo(raw)

    if provider == "swellcloud":

        raw = get_swellcloud_forecast(
            lat,
            lon
        )

        return normalize_swellcloud(raw)

    raise ValueError(
        f"Unknown provider: {provider}"
    )

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


def normalize_tides(data: dict) -> dict:

    heights_result = []

    heights = data["heights"]

    min_height = min(
        h["height"]
        for h in heights
    )

    max_height = max(
        h["height"]
        for h in heights
    )

    for h in heights:

        tide_height_m = h["height"]

        heights_result.append(
            {
                "time": h["date"],
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

    extremes_result = []

    for e in data.get("extremes", []):

        extremes_result.append(
            {
                "time": e["date"],
                "type": e["type"].lower(),
                "height_ft": round(
                    e["height"] * 3.28084,
                    1
                )
            }
        )

    return {
        "timezone": data.get("timezone"),
        "datum": data.get("responseDatum"),
        "extremes": extremes_result,
        "heights": heights_result
    }

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

def parse_time(ts: str):

    if ts.endswith("Z"):
        ts = ts.replace(
            "Z",
            "+00:00"
        )


    dt = datetime.fromisoformat(ts)

    if dt.tzinfo is None:
        dt = dt.replace(
            tzinfo=timezone.utc
        )

    return dt

def lookup_conditions(
    spot_id: str,
    provider: str = "swellcloud"
):

    spot = get_spot(
        spot_id
    )

    forecast = lookup_forecast(
        spot_id,
        provider
    )

    tides = lookup_tides(
        spot_id
    )

    tide_heights = tides["heights"]

    conditions = []

    for forecast_item in forecast:

        forecast_time = parse_time(
            forecast_item["time"]
        )

        closest_tide = min(
            tide_heights,
            key=lambda tide: abs(
                parse_time(
                    tide["time"]
                ) - forecast_time
            )
        )

        conditions.append(
            {
                "time":
                    forecast_item["time"],

                "wave_height_ft":
                    forecast_item["wave_height_ft"],

                "wave_period_s":
                    forecast_item["wave_period_s"],

                "swell_direction":
                    forecast_item["swell_direction"],

                "swell_direction_deg":
                    forecast_item["swell_direction_deg"],

                "wind_speed_mph":
                    forecast_item.get("wind_speed_mph"),

                "wind_direction":
                    forecast_item.get("wind_direction"),

                "wind_direction_deg":
                    forecast_item.get("wind_direction_deg"),

                "secondary_swell_ft":
                    forecast_item.get("secondary_swell_ft"),

                "secondary_swell_direction_deg":
                    forecast_item.get(
                        "secondary_swell_direction_deg"
                    ),

                "wind_wave_ft":
                    forecast_item.get("wind_wave_ft"),

                "wind_wave_direction_deg":
                    forecast_item.get(
                        "wind_wave_direction_deg"
                    ),

                "tide_height_ft":
                    closest_tide["tide_height_ft"],

                "tide_state":
                    closest_tide["tide_state"]
            }
        )

    return {
        "spot": {
            "spot_id":
                spot["spot_id"],

            "name":
                spot["name"],

            "country":
                spot["country"],

            "island":
                spot["island"],

            "region":
                spot["region"],

            "coordinates":
                spot["coordinates"],

            "preferred_conditions":
                spot["preferred_conditions"],

            "wave":
                spot["wave"],

            "ratings":
                spot["ratings"],

            "surfer_level":
                spot["surfer_level"],

            "notes":
                spot["notes"],

            "description":
                spot["description"],

            "hazards":
                spot["hazards"]
        },

        "timezone":
            tides["timezone"],

        "datum":
            tides["datum"],

        "tide_extremes":
            tides["extremes"],

        "forecast_conditions":
            conditions
    }

def normalize_swellcloud(data):

    result = []

    for item in data["data"]:

        result.append(
            {
                "time": item["time"],

                "wave_height_ft": item["hs"],
                "wave_period_s": item["tp"],

                "swell_direction_deg": item["dp"],
                "swell_direction": degrees_to_direction(
                    item["dp"]
                ),

                "wind_speed_mph": item["wndspd"],
                "wind_direction_deg": item["wnddir"],
                "wind_direction": degrees_to_direction(
                    item["wnddir"]
                ),

                "secondary_swell_ft": item["ss_hs"],
                "secondary_swell_direction_deg": item["ss_dp"],

                "wind_wave_ft": item["ww_hs"],
                "wind_wave_direction_deg": item["ww_dp"]
            }
        )

    return result