# providers/swellcloud.py

import os
from datetime import datetime, timedelta, timezone

from providers.http import get_json


def get_swellcloud_forecast(lat: float, lon: float):

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
        "start": start.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "end": end.strftime("%Y-%m-%dT%H:%M:%SZ")
    }

    return get_json(
        "https://api.swellcloud.net/v1/point",
        params=params,
        headers={
            "X-API-Key": api_key
        }
    )