from mcp.server.fastmcp import FastMCP
from spots import get_spot, get_all_spots
from forecast import lookup_forecast, lookup_tides, lookup_conditions
from typing import Optional


# Host und Port direkt bei der Initialisierung übergeben
mcp = FastMCP(
    "Surf MCP Server",
    host="0.0.0.0",
    port=8000
)

def _matches(value, query: str) -> bool:
    if isinstance(value, list):
        return query.lower() in [item.lower() for item in value]

    return value.lower() == query.lower()

@mcp.tool()
def list_regions() -> list:
    """
    List all available surf regions.
    """

    return sorted(
        list(
            set(
                spot["region"]
                for spot in get_all_spots()
            )
        )
    )

@mcp.tool()
def list_spots(region: Optional[str] = None) -> list:
    """
    List all available surf spots.
    Optionally filter by region.
    """

    spots = get_all_spots()

    if region:
        spots = [
            spot
            for spot in spots
            if _matches(spot["region"], region)
        ]

    return [
        {
            "id": spot["spot_id"],
            "name": spot["name"],
            "country": spot["country"],
            "island": spot["island"],
            "region": spot["region"]
        }
        for spot in spots
    ]

@mcp.tool()
def get_spot_info(spot_id: str) -> dict:
    """
    Get detailed information about a surf spot.
    """

    return get_spot(spot_id)

@mcp.tool()
def find_spots(
    skill: Optional[str] = None,
    country: Optional[str] = None,
    island: Optional[str] = None,
    region: Optional[str] = None,
    tide: Optional[str] = None,
    wind: Optional[str] = None,
    swell_direction: Optional[str] = None,
    swell_height_ft: Optional[float] = None,
) -> list:
    """
    Find surf spots matching one or more criteria.
    """

    result = []

    for spot in get_all_spots():

        # Skill
        if skill:
            if not _matches(spot["surfer_level"], skill):
                continue

        # Country
        if country:
            if not _matches(spot["country"], country):
                continue

        # Island
        if island:
            if not _matches(spot["island"], island):
                continue

        # Region
        if region:
            if not _matches(spot["region"], region):
                continue

        # Tide
        if tide:
            tides = [
                t.lower()
                for t in spot["conditions"]["tide"]
            ]

            if tide.lower() not in tides:
                continue

        # Wind
        if wind:
            offshore = [
                w.upper()
                for w in spot["conditions"]["wind"]["offshore"]
            ]

            if wind.upper() not in offshore:
                continue

        # Swell Direction
        if swell_direction:
            swell_dirs = [
                d.upper()
                for d in spot["conditions"]["swell"]["directions"]
            ]

            if swell_direction.upper() not in swell_dirs:
                continue

        # Swell Height
        if swell_height_ft is not None:

            swell = spot["conditions"]["swell"]

            if (
                swell_height_ft < swell["min_ft"]
                or
                swell_height_ft > swell["max_ft"]
            ):
                continue

        result.append(
            {
                "id": spot["spot_id"],
                "name": spot["name"],
                "country": spot["country"],
                "island": spot["island"],
                "region": spot["region"],
                "skill": spot["surfer_level"]
            }
        )

    return result

@mcp.tool()
def count_spots() -> int:
    """
    Return the number of available surf spots.
    """

    return len(get_all_spots())

@mcp.tool()
def search_spots(query: str) -> list:
    """
    Search spots by name.
    """

    query = query.lower()

    return [
        {
            "id": spot["spot_id"],
            "name": spot["name"]
        }
        for spot in get_all_spots()
        if query in spot["name"].lower()
    ]

@mcp.tool()
def get_forecast(spot_id: str) -> dict:
    """
    Get marine forecast for a surf spot.
    """

    return lookup_forecast(spot_id)

@mcp.tool()
def get_tides(
    spot_id: str
) -> list:
    """
    Get tide forecast for a surf spot.
    """

    return lookup_tides(
        spot_id
    )

@mcp.tool()
def get_conditions(
    spot_id: str
) -> list:
    """
    Get combined surf conditions.
    """

    return lookup_conditions(
        spot_id
    )

@mcp.prompt()
def surf_advisor() -> str:
    return """
    You are an experienced surf guide and surf forecaster.

    Your goal is to help surfers choose the best surf spot based on:

    * surfer skill level
    * swell height
    * swell period
    * swell direction
    * tide state
    * wind direction
    * spot characteristics
    * hazards and local conditions

    Guidelines:

    1. Always consider whether the swell direction matches the preferred swell directions of the spot.

    2. Longer wave periods are generally more powerful and can make a spot more advanced.

    3. Consider the preferred tide conditions of each spot:

    * low
    * mid
    * high

    4. Consider the surfer's skill level:

    * beginner
    * intermediate
    * advanced
    * expert

    5. Avoid recommending dangerous or unsuitable spots when the surfer's skill level is below the spot requirements.

    6. Use spot notes, hazards, and local knowledge whenever available.

    7. When comparing multiple spots, explain the tradeoffs.

    8. Always explain WHY a recommendation is made.

    Response format:

    Recommendation: <best spot>

    Why:

    * reason 1
    * reason 2
    * reason 3

    Alternative Spots:

    * spot A
    * spot B

    Warnings:

    * hazards
    * localism
    * reef exposure
    * tide concerns

    Never recommend a spot blindly. Always justify the recommendation using the available forecast and spot data.

    """


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
