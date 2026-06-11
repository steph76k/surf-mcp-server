import socket

import requests
import urllib3.util.connection as urllib3_connection


DEFAULT_TIMEOUT = (2, 8)
DEFAULT_HEADERS = {
    "Accept": "application/json",
    "User-Agent": "surf-mcp-server/0.1.0",
}


def prefer_ipv4() -> None:
    urllib3_connection.allowed_gai_family = lambda: socket.AF_INET


def get_json(url: str, *, params: dict | None = None) -> dict:
    prefer_ipv4()

    try:
        response = requests.get(
            url,
            params=params,
            headers=DEFAULT_HEADERS,
            timeout=DEFAULT_TIMEOUT,
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        raise RuntimeError(
            f"HTTP request failed for {url}: {exc}"
        ) from exc
