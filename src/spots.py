import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data"

def list_spots():
    return [
        f.stem
        for f in DATA_DIR.glob("*.json")
    ]

def get_spot(spot_id: str):
    with open(DATA_DIR / f"{spot_id}.json") as f:
        return json.load(f)
        
def get_all_spots():
    spots = []

    for file in DATA_DIR.glob("*.json"):
        with open(file) as f:
            spots.append(json.load(f))

    return spots
