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

    Use this tool when the user wants to browse
    surf destinations by geographic area.

    Examples:

    - What surf regions are available?
    - Show me all Bali regions.
    - Which regions do you know in Sumbawa?

    Returns region names only.
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
    List available surf spots.

    Optionally filter by region.

    Use this tool when the user wants to:

    - browse surf spots
    - discover spots in a region
    - see available spot names
    - explore the surf database

    Examples:

    - Show all spots in Lakey.
    - List surf spots in Bali.
    - What spots do you know?

    Returns summary information including:

    - spot name
    - location
    - surfer level
    - wave type
    - fun rating
    - risk rating
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
            "region": spot["region"],
            "wave_type": spot["wave"]["type"],
            "surfer_level": spot["surfer_level"],
            "fun": spot["ratings"]["fun"],
            "risk": spot["ratings"]["risk"]
        }
        for spot in spots
    ]

@mcp.tool()
def get_spot_info(spot_id: str) -> dict:
    """
    Get detailed information about a surf spot.

    Use this tool when the user asks about a specific spot.

    Provides:

    - location
    - surfer level
    - wave type
    - wave direction
    - hazards
    - local notes
    - crowd rating
    - localism rating
    - risk rating
    - preferred swell directions
    - preferred wind directions
    - preferred tides

    Examples:

    - Tell me about Lakey Peak.
    - Is Airport Right suitable for intermediates?
    - What hazards exist at Nungas?

    This tool does not include live forecast data.
    Use get_conditions for current surf conditions.
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
    Find surf spots matching specific criteria.

    Supports filtering by:

    - surfer skill level
    - country
    - island
    - region
    - preferred tide
    - preferred wind direction
    - preferred swell direction
    - swell size range

    Use this tool when the user is searching for
    possible surf spots rather than asking about
    one specific location.

    Examples:

    - Find intermediate spots in Bali.
    - Show reef breaks that work on SW swell.
    - Find spots for high tide.
    - Find spots for 4 ft surf.

    Returns matching spots only.
    Use get_conditions afterwards to evaluate
    current surf conditions.
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
                for t in spot["preferred_conditions"]["tide"]
            ]

            if tide.lower() not in tides:
                continue

        # Wind
        if wind:
            offshore = [
                w.upper()
                for w in spot["preferred_conditions"]["wind"]["offshore"]
            ]

            if wind.upper() not in offshore:
                continue

        # Swell Direction
        if swell_direction:
            swell_dirs = [
                d.upper()
                for d in spot["preferred_conditions"]["swell"]["directions"]
            ]

            if swell_direction.upper() not in swell_dirs:
                continue

        # Swell Height
        if swell_height_ft is not None:

            swell = spot["preferred_conditions"]["swell"]

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
    Return the number of surf spots currently available
    in the surf database.

    Useful for diagnostics and database validation.
    """

    return len(get_all_spots())

@mcp.tool()
def search_spots(query: str) -> list:
    """
    Search surf spots by name.

    Use this tool when the user mentions a spot name
    or partial spot name.

    Examples:

    - Lakey
    - Airport
    - Uluwatu

    Returns matching surf spots.
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
def get_forecast(
    spot_id: str,
    provider: str = "swellcloud"
) -> dict:
    """
    Get marine forecast for a surf spot.

    Provides forecast-only information:

    - wave height
    - wave period
    - swell direction
    - wind speed
    - wind direction
    - secondary swell
    - wind waves

    Supported providers:

    - swellcloud
    - open_meteo

    Use this tool when the user asks:

    - How big will it be?
    - What is the swell forecast?
    - What is the wind forecast?

    This tool does not include spot suitability analysis.
    Use get_conditions for complete surf evaluation.
    """

    return lookup_forecast(
    spot_id,
    provider
)

@mcp.tool()
def get_tides(
    spot_id: str
) -> list:
    """
    Get tide forecast for a surf spot.

    Provides:

    - tide heights
    - tide states
    - tide extremes
    - local timezone

    Use this tool when tide information is important.

    Examples:

    - When is high tide?
    - What tide will Lakey have tomorrow?
    - Is the spot suitable at low tide?

    This tool only returns tide information.
    """

    return lookup_tides(
        spot_id
    )

@mcp.tool()
def get_conditions(
    spot_id: str
) -> list:
    """
    PRIMARY SURF ANALYSIS TOOL.

    Use this tool whenever surf recommendations
    or surf spot comparisons are required.

    This tool already combines:

    - forecast
    - tides
    - spot information
    - preferred conditions
    - hazards
    - surfer level

    In most cases you do NOT need to call:

    - get_forecast()
    - get_tides()
    - get_spot_info()

    before using this tool.

    Use get_conditions() as the default tool for
    surf forecasting and spot recommendations.
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

@mcp.prompt()
def spot_comparison() -> str:
    return """
    You are an expert surf forecaster.

    Compare multiple surf spots using:

    - swell height
    - swell period
    - swell direction
    - tide
    - wind
    - hazards
    - surfer level

    Explain tradeoffs clearly.

    Response format:

    Spot Comparison

    Spot A:
    - strengths
    - weaknesses

    Spot B:
    - strengths
    - weaknesses

    Recommendation:
    - best overall choice
    - best choice for progression
    - safest choice

    Never assume conditions.
    Use available forecast and spot data.
    """

@mcp.prompt()
def trip_planner() -> str:
    return """
    You are a surf travel planner.

    Help surfers plan trips based on:

    - season
    - swell patterns
    - wind patterns
    - surfer level
    - crowd levels
    - accessibility
    - local conditions

    Consider:

    - airports
    - accommodation
    - transport
    - surf consistency
    - hazards

    Response format:

    Recommended Region

    Best Spots

    Best Time To Visit

    Advantages

    Disadvantages

    Travel Notes
    """

@mcp.prompt()
def beginner_advisor() -> str:
    return """
    You are a surf instructor.

    Prioritize safety.

    Avoid recommending spots that exceed
    the surfer's skill level.

    Consider:

    - wave height
    - period
    - reef hazards
    - currents
    - localism
    - crowd

    Response format:

    Recommended Spot

    Why It Is Suitable

    Risks

    Skills To Practice

    Spots To Avoid
    """

@mcp.prompt()
def surf_report() -> str:
    return """
    You are a professional surf forecaster.

    Create a concise surf report.

    Include:

    - swell height
    - swell period
    - swell direction
    - wind
    - tide

    Explain how these factors affect the spot.

    Response format:

    Surf Report

    Conditions

    Best Surf Window

    Recommended Skill Level

    Hazards

    Overall Rating (1-10)
    """

@mcp.resource("surf://guides/surf_levels")
def surf_levels() -> str:
    return """
# Surf Skill Levels

## Beginner

Suitable Conditions:

- whitewater
- small waves
- sandy bottom
- low current
- low crowd pressure

Typical Wave Size:

- 1-3 ft

Avoid:

- reef breaks
- heavy currents
- shallow waves
- advanced lineups

---

## Intermediate

Suitable Conditions:

- reef or beach breaks
- predictable takeoffs
- moderate currents

Typical Wave Size:

- 3-6 ft

Skills Expected:

- duck diving
- lineup positioning
- basic wave selection
- safe board control

---

## Advanced

Suitable Conditions:

- powerful reef breaks
- fast takeoffs
- hollow sections
- crowded lineups

Typical Wave Size:

- 6-10 ft+

Skills Expected:

- confident duck diving
- barrel riding
- critical takeoffs
- advanced ocean awareness

---

## Expert

Suitable Conditions:

- heavy reefs
- large surf
- strong currents
- complex lineups

Typical Wave Size:

- 10 ft+

Skills Expected:

- complete lineup awareness
- rescue capability
- advanced wave reading
- high-risk decision making

---

General Rule

Never recommend a surf spot significantly above the surfer's skill level.

Safety is more important than wave quality.
"""


@mcp.resource("surf://guides/surf_etiquette")
def surf_etiquette() -> str:
    return """
# Surf Etiquette

## Right of Way

The surfer closest to the breaking part of the wave has priority.

Do not drop in on another surfer.

---

## Respect the Lineup

Wait your turn.

Do not paddle around everyone to gain priority.

---

## Communicate

If unsure, communicate clearly.

A simple call can avoid collisions.

---

## Don't Snake

Do not paddle around another surfer who already has priority.

This is considered poor etiquette.

---

## Respect Locals

Many surf spots have local surfers who surf there every day.

Be respectful and observe how the lineup works.

---

## Control Your Board

Never let your board become a hazard.

Protect other surfers first.

---

## Reef Break Awareness

Do not sit directly in the takeoff zone if you are not catching waves.

Avoid blocking surfers riding toward you.

---

## Crowded Lineups

Take fewer waves.

Share waves fairly.

Be patient.

---

## If You Make a Mistake

Apologize immediately.

Most conflicts can be avoided through respect and communication.

---

Golden Rule

The best surfer in the water is usually the one showing the most respect.
"""


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
