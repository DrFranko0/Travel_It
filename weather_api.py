# weather_api.py

import requests

def get_current_weather(latitude: float, longitude: float) -> dict:
    """
    Fetch current weather (temperature, wind, etc.) from Open-Meteo for the given coordinates.
    Returns a dict with 'temperature' and other fields, or None on error.
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current_weather": True
    }
    try:
        res = requests.get(url, params=params, timeout=5)
        res.raise_for_status()
        data = res.json()
        return data.get("current_weather")
    except Exception as e:
        print(f"Weather API error: {e}")
        return None
