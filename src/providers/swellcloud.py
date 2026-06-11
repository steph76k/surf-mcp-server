import os
import requests

from datetime import datetime
from datetime import timedelta
from datetime import timezone


def get_swellcloud_forecast(
    lat: float,
    lon: float
):

    api_key = os.environ["SWELLCLOUD_API_KEY"]

    start = datetime.now(timezone.utc)
    end = start + timedelta(days=1)

    params = {
        "lat": lat,
        "lon": lon,
        "model": "gfs",
        "units": "uk",
        "vars": (
            "hs,tp,dp,"
            "ss_hs,ss_dp,"
            "ww_hs,ww_dp,"
            "wndspd,wnddir"
        ),
        "start": start.strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        ),
        "end": end.strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
    }

    response = requests.get(
        "https://api.swellcloud.net/v1/point",
        params=params,
        headers={
            "X-API-Key": api_key
        },
        timeout=30
    )

    response.raise_for_status()

    return response.json()