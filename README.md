# Surf MCP Server

Ein kleiner MCP Server fuer Surfspot-Daten und einfache Spot-Suche. Die Spots liegen als JSON-Dateien im Ordner `data/` und koennen ueber MCP Tools abgefragt werden.

Der Server ist bewusst simpel gehalten, damit er auf verschiedenen Systemen und mit unterschiedlichen Python-Versionen leicht getestet werden kann.

## Voraussetzungen

- Python `>=3.10`
- Zugriff auf dieses Repo
- Installation der Python-Abhaengigkeiten aus `pyproject.toml`

Abhaengigkeiten:

- `mcp[cli]`
- `requests`

## Setup

Vom Repo-Root aus:

```bash
cd surf-mcp-server
python -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e .
```

Alternativ, falls du mit `uv` arbeitest:

```bash
cd surf-mcp-server
uv sync
```

Wichtig: Den Server aus dem Repo-Root starten, weil die Spot-Dateien relativ ueber `data/` geladen werden.

## Server starten

```bash
python src/server.py
```

Der Server startet aktuell mit `streamable-http`:

```python
mcp.run(transport="streamable-http")
```

Wenn du ihn auf einem anderen System testest, reicht normalerweise:

1. Repo kopieren oder klonen
2. Python-Umgebung erstellen
3. Dependencies installieren
4. `python src/server.py` aus dem Repo-Root ausfuehren

## Projektstruktur

```text
surf-mcp-server/
├── src/
│   ├── server.py     # MCP Tools und Server-Start
│   ├── spots.py      # Laden der Spot-Dateien
│   ├── forecast.py   # Forecast-Orchestrierung
│   └── providers/    # Forecast- und Tide-Provider
├── data/             # Surfspot JSON-Dateien
├── tests/            # Unit Tests
├── charts/           # Helm Chart
├── Dockerfile
├── .dockerignore
├── LICENSE
├── pyproject.toml
├── uv.lock
└── README.md
```

## Verfuegbare MCP Tools

### `list_regions()`

Gibt alle verfuegbaren Regionen zurueck.

Beispiel-Resultat:

```json
["Airport Reefs", "Lakey", "Uluwatu", "Ungasan", "West Sumbawa"]
```

### `list_spots(region: string | null = null)`

Listet Spots. Optional kann nach Region gefiltert werden.

Beispiel:

```json
{
  "region": "Uluwatu"
}
```

Resultat enthaelt:

```json
{
  "id": "uluwatu_the_peak",
  "name": "Uluwatu - The Peak",
  "country": "Indonesia",
  "island": "Bali",
  "region": "Uluwatu"
}
```

### `get_spot_info(spot_id: string)`

Gibt alle Details fuer einen Spot zurueck.

Beispiel:

```json
{
  "spot_id": "lakey_peak"
}
```

### `find_spots(...)`

Findet Spots anhand mehrerer Kriterien.

Parameter:

- `skill`: z.B. `intermediate`, `advanced`, `expert`
- `country`: z.B. `Indonesia`
- `island`: z.B. `Bali` oder `Sumbawa`
- `region`: z.B. `Uluwatu`, `Lakey`, `West Sumbawa`
- `tide`: z.B. `low`, `mid`, `high`
- `wind`: z.B. `SE`, `N`, `NW`
- `swell_direction`: z.B. `S`, `SW`, `W`
- `swell_height_ft`: z.B. `4`

Beispiel:

```json
{
  "skill": "intermediate",
  "island": "Bali",
  "region": "Uluwatu",
  "tide": "mid",
  "wind": "SE",
  "swell_direction": "SW",
  "swell_height_ft": 4
}
```

### `count_spots()`

Gibt die Anzahl der Spot-Dateien zurueck.

### `search_spots(query: string)`

Sucht Spots nach Name.

Beispiel:

```json
{
  "query": "uluwatu"
}
```

### `get_forecast(spot_id: string)`

Gibt aktuell einen Mock Forecast zurueck.

Beispiel-Resultat:

```json
{
  "wave_height_ft": 6,
  "period_s": 14,
  "wind_kts": 8
}
```

## Spot JSON Schema

Jeder Spot ist eine eigene JSON-Datei in `data/`. Der Dateiname sollte zur `spot_id` passen.

Beispiel:

```json
{
  "spot_id": "uluwatu_the_peak",
  "name": "Uluwatu - The Peak",
  "country": "Indonesia",
  "island": "Bali",
  "region": "Uluwatu",
  "coordinates": {
    "lat": -8.816633,
    "lon": 115.08625
  },
  "conditions": {
    "swell": {
      "directions": ["S", "SW"],
      "min_ft": 1,
      "max_ft": 6
    },
    "wind": {
      "offshore": ["SE"]
    },
    "tide": ["mid", "high"]
  },
  "wave": {
    "direction": "left",
    "type": "reef"
  },
  "ratings": {
    "crowd": 10,
    "localism": 9,
    "risk": 6,
    "fun": 9
  },
  "surfer_level": ["intermediate", "advanced"],
  "notes": "At high tide, aim south of the cave when coming in.",
  "description": "Short description of the spot.",
  "hazards": [
    "sharp coral reef",
    "strong currents"
  ]
}
```

## Wichtige Daten-Konventionen

### `surfer_level`

`surfer_level` ist immer ein Array, damit die Suche einzelne Levels sauber matchen kann:

```json
{
  "surfer_level": ["intermediate", "advanced"]
}
```

Nicht mehr verwenden:

```json
{
  "surfer_level": "intermediate / advanced"
}
```

Empfohlene Werte:

- `beginner`
- `intermediate`
- `advanced`
- `expert`

### Location Felder

`country`, `island` und `region` sind getrennte Felder:

```json
{
  "country": "Indonesia",
  "island": "Bali",
  "region": "Uluwatu"
}
```

Nicht mehr verwenden:

```json
{
  "region": "Bali - Uluwatu Area"
}
```

## Aktuelle Regionen

- `Airport Reefs`
- `Lakey`
- `Uluwatu`
- `Ungasan`
- `West Sumbawa`

## Neue Spots hinzufuegen

1. Neue Datei in `data/` erstellen, z.B. `my_spot.json`
2. `spot_id` passend zum Dateinamen setzen, z.B. `my_spot`
3. Schema wie oben verwenden
4. JSON validieren:

```bash
jq empty data/my_spot.json
```

Alle Spot-Dateien validieren:

```bash
for f in data/*.json; do jq empty "$f" || exit 1; done
```

## Hinweise

- `get_forecast` ist aktuell noch Mock-Datenlogik.
- Spot-Daten werden bei jedem Tool-Aufruf direkt aus `data/*.json` gelesen.
- `src/providers/open_meteo.py`, `src/providers/worldtides.py` und `src/providers/stormglass.py` sind als Provider-Struktur vorbereitet. Open-Meteo liefert aktuell noch normalisierte Platzhalterdaten.
- Das Helm Chart nutzt standardmaessig die im Docker Image enthaltenen Spot-Daten. Ein externer ConfigMap-Mount fuer `/app/data` kann ueber `spotData.configMap.enabled=true` aktiviert werden.
