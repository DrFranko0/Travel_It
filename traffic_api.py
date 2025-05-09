# traffic_api.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def get_travel_time(origin_lat: float, origin_lon: float,
                    dest_lat: float, dest_lon: float) -> float | None:
    """
    Use TomTom Routing API (free tier) to get travel time in minutes.
    """
    key = os.getenv("TOMTOM_KEY")
    if not key:
        return None

    url = (
        f"https://api.tomtom.com/routing/1/calculateRoute/"
        f"{origin_lat},{origin_lon}:{dest_lat},{dest_lon}/json"
    )
    params = {
        "key": key,
        "traffic": "true",
        "routeRepresentation": "summaryOnly",
        "computeTravelTimeFor": "all"
    }
    try:
        r = requests.get(url, params=params, timeout=5)
        r.raise_for_status()
        summary = r.json()["routes"][0]["summary"]
        return summary["travelTimeInSeconds"] / 60.0
    except Exception as e:
        print(f"[traffic_api] error: {e}")
        return None
