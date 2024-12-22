import requests
import time

# Map weather codes to descriptions
WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Drizzle: Light",
    53: "Drizzle: Moderate",
    55: "Drizzle: Dense",
    61: "Rain: Slight",
    63: "Rain: Moderate",
    65: "Rain: Heavy",
    80: "Rain showers: Slight",
    81: "Rain showers: Moderate",
    82: "Rain showers: Violent",
    95: "Thunderstorm: Slight",
    96: "Thunderstorm: Moderate",
    99: "Thunderstorm: Severe",
    # Add more codes if needed
}


def fetch_weather(location):
    """
    Fetch weather data for a given location using Open Meteo API.
    """
    # Geocoding to get latitude and longitude
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={location}"
    geo_response = requests.get(geo_url)
    if geo_response.status_code != 200 or not geo_response.json().get("results"):
        return {"error": f"Location '{location}' not found."}

    geo_data = geo_response.json()["results"][0]
    latitude, longitude = geo_data["latitude"], geo_data["longitude"]
    location_name = geo_data["name"]

    # Fetch weather data
    weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true"
    weather_response = requests.get(weather_url)

    if weather_response.status_code != 200:
        return {"error": "Failed to fetch weather data."}

    weather_data = weather_response.json()["current_weather"]
    weather_code = weather_data["weathercode"]
    weather_description = WEATHER_CODES.get(weather_code, "Unknown")

    return {
        "location": location_name,
        "latitude": latitude,
        "longitude": longitude,
        "temperature": weather_data["temperature"],
        "wind_speed": weather_data["windspeed"],
        "description": weather_description
    }


def preprocess_weather_data(location):
    """
    Preprocess weather data for embedding.
    """
    # Fetch real-time weather data
    weather_data = fetch_weather(location)
    if "error" in weather_data:
        return None

    # Generate logical supply chain impacts based on weather conditions
    supply_chain_impact = []

    # Temperature impacts
    if weather_data["temperature"] > 35:
        supply_chain_impact.append("High temperatures may damage perishable goods and disrupt storage facilities.")
    elif weather_data["temperature"] < 0:
        supply_chain_impact.append("Freezing temperatures may delay transportation and damage certain goods.")

    # Wind speed impacts
    if weather_data["wind_speed"] > 50:
        supply_chain_impact.append("High wind speeds may delay air and sea freight operations.")
    elif weather_data["wind_speed"] > 20:
        supply_chain_impact.append("Moderate wind speeds may cause minor delays in truck and rail logistics.")

    # Weather description impacts
    weather_description = weather_data["description"].lower()
    if "rain" in weather_description or "drizzle" in weather_description:
        supply_chain_impact.append("Rain may cause delays in road transportation and increase the risk of accidents.")
    elif "snow" in weather_description:
        supply_chain_impact.append("Snow may block roads, delay flights, and disrupt logistics.")
    elif "storm" in weather_description or "thunderstorm" in weather_description:
        supply_chain_impact.append("Storms may disrupt port operations, flights, and ground transportation.")

    # Default impact if no conditions are severe
    if not supply_chain_impact:
        supply_chain_impact.append("Weather conditions are unlikely to cause significant disruptions.")

    # Combine the data for embedding
    return {
        "text": f"""
        Location: {weather_data['location']}
        Temperature: {weather_data['temperature']}°C
        Wind Speed: {weather_data['wind_speed']} km/h
        Condition: {weather_data['description']}
        Supply Chain Impact: {" ".join(supply_chain_impact)}
        """,
        "metadata": {
            "location": weather_data["location"],
            "latitude": weather_data["latitude"],
            "longitude": weather_data["longitude"],
        },
    }
