import json
import os
import requests


URL = "https://raw.githubusercontent.com/Bowserinator/Periodic-Table-JSON/master/PeriodicTableJSON.json"
# Thank you, Bowserinator! https://github.com/Bowserinator
CACHE_DIR = "./cache"
PATH = f"{CACHE_DIR}/table.json"


class Element:
    def __init__(self, number: int, symbol: str, name: str, atomic_mass: float, category: str, **kwargs):
        self.number = number
        self.mass = atomic_mass
        self.name = name
        self.symbol = symbol
        self.category = category


def _():
    o = None
    os.makedirs(CACHE_DIR, exist_ok=True)
    if os.path.exists(PATH):
        with open(PATH, "r") as f:
            o = json.load(f)
    else:
        o = requests.get(URL).json()
        with open(PATH, "w") as f:
            json.dump(o, f)

    return tuple(Element(**e) for e in o["elements"])


elements = {
    e.symbol: e for e in _()
}
