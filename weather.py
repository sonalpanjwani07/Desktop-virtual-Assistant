import json
import os
import urllib.parse
import urllib.request


def Weather(default_city="Karachi"):
    """Backward-compatible weather helper used by legacy handler."""
    city = default_city
    api_key = os.getenv("OPENWEATHER_API_KEY", "").strip()
    if not api_key:
        return f"Set OPENWEATHER_API_KEY for live weather. Default city is {city}."
    try:
        params = urllib.parse.urlencode({"q": city, "appid": api_key, "units": "metric"})
        url = f"https://api.openweathermap.org/data/2.5/weather?{params}"
        with urllib.request.urlopen(url, timeout=8) as response:
            data = json.loads(response.read().decode("utf-8"))
        desc = data.get("weather", [{}])[0].get("description", "N/A")
        temp = data.get("main", {}).get("temp", "N/A")
        return f"Weather in {city}: {desc}, {temp} C."
    except Exception:
        return f"Unable to fetch weather for {city} right now."

