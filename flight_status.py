# flight_status.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()
AVIATIONSTACK_URL = "http://api.aviationstack.com/v1/flights"

def get_flight_info(flight_code: str) -> dict | None:
    """
    Fetch live flight data via Aviationstack free-tier.
    Returns dict with keys: status, departure, arrival, airline, flight.
    """
    api_key = os.getenv("AVIATIONSTACK_KEY")
    if not api_key:
        raise RuntimeError("Set AVIATIONSTACK_KEY in .env")

    params = {
        "access_key": api_key,
        "flight_iata": flight_code.upper(),
        "limit": 1
    }
    try:
        r = requests.get(AVIATIONSTACK_URL, params=params, timeout=10)
        r.raise_for_status()
        payload = r.json()
    except Exception as e:
        print(f"[flight_status] API error: {e}")
        return None

    # Aviationstack returns data list under "data"
    items = payload.get("data") or payload.get("results") or []
    if not items:
        return None

    f = items[0]
    return {
        "status": f.get("flight_status"),
        "departure": f.get("departure", {}),
        "arrival": f.get("arrival", {}),
        "airline": f.get("airline", {}),
        "flight": f.get("flight", {}),
        "live": f.get("live", {})
    }

if __name__ == "__main__":
    test = "BA2490"
    info = get_flight_info(test)
    if info:
        lg = info.get("live", {})
        in_air = lg.get("is_ground") is False
        print(f"{info['airline'].get('name')} flight {info['flight'].get('iata')} " +
              ("is in the air." if in_air else "is not in the air."))
    else:
        print("No data.")
