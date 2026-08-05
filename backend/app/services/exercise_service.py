import json
from pathlib import Path

DATA_PATH = Path(__file__).parent.parent / "data" / "exercises.json"


def load_exercises():
    with open(DATA_PATH, "r") as f:
        return json.load(f)