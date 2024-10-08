import requests
from langchain.tools import tool
from datetime import datetime, timedelta
from urllib.parse import quote

# Directly use the API key
WEATHER_API_KEY = '78cf93102503bb0c15fdd28d60188084'

# Function to get current weather information
def fetch_current_weather(location):
    location = location.strip()  # Trim any leading/trailing whitespace
    encoded_location = quote(location)
    url = f"http://api.openweathermap.org/data/2.5/weather?q={encoded_location}&appid={WEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        weather = {
            "location": location,
            "temperature": data['main']['temp'],
            "description": data['weather'][0]['description'],
            "humidity": data['main']['humidity'],
            "wind_speed": data['wind']['speed']
        }
        return weather
    else:
        print(f"Error fetching current weather: {response.status_code} - {response.text}")
        return None

# Function to get weather forecast information
def fetch_weather_forecast(latitude, longitude):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&daily=temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=auto"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        forecast = []
        for date, temp_max, temp_min, precipitation in zip(data['daily']['time'], data['daily']['temperature_2m_max'], data['daily']['temperature_2m_min'], data['daily']['precipitation_sum']):
            forecast.append({
                "datetime": date,
                "temperature_max": temp_max,
                "temperature_min": temp_min,
                "precipitation": precipitation
            })
        return forecast
    else:
        print(f"Error fetching weather forecast: {response.status_code} - {response.text}")
        return None

# Function to get latitude and longitude of a location
def get_location_coordinates(location):
    location = location.strip()  # Trim any leading/trailing whitespace
    encoded_location = quote(location)
    url = f"http://api.openweathermap.org/data/2.5/weather?q={encoded_location}&appid={WEATHER_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        coordinates = {
            "latitude": data['coord']['lat'],
            "longitude": data['coord']['lon']
        }
        return coordinates
    else:
        print(f"Error fetching location coordinates: {response.status_code} - {response.text}")
        return None

# Function to fetch historical weather data
def fetch_historical_weather(latitude, longitude, start_date, end_date):
    # Ensure the date range does not exceed one year from the current date
    current_date = datetime.now().date()
    one_year_ago = current_date - timedelta(days=365)
    start_date = max(datetime.strptime(start_date, "%Y-%m-%d").date(), one_year_ago)
    end_date = min(datetime.strptime(end_date, "%Y-%m-%d").date(), current_date)
    
    url = f"https://archive-api.open-meteo.com/v1/era5?latitude={latitude}&longitude={longitude}&start_date={start_date}&end_date={end_date}&hourly=temperature_2m"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        historical_weather = []
        for time, temp in zip(data['hourly']['time'], data['hourly']['temperature_2m']):
            if temp is not None:  # Check if temperature is not None
                historical_weather.append({
                    "datetime": time,
                    "temperature": temp
                })
        return historical_weather
    else:
        print(f"Error fetching historical weather: {response.status_code} - {response.text}")
        return None

# Wrap the weather functions as tools
@tool
def get_current_weather(location: str) -> str:
    """Get the current weather for a specified location (city or country)."""
    weather_info = fetch_current_weather(location)
    if weather_info:
        return f"Current weather in {location}: {weather_info['temperature']}°C, {weather_info['description']}, Humidity: {weather_info['humidity']}%, Wind Speed: {weather_info['wind_speed']} m/s"
    else:
        return f"Location not found or API error. It looks like there was an error retrieving the current weather for {location}. The API may not have been able to find the location or there was an issue with the connection. I apologize that I'm unable to provide the current weather for {location} at this time. Please let me know if you have any other questions!"

@tool
def get_weather_forecast(location: str) -> str:
    """Get the weather forecast for the next 16 days for a specified location (city or country)."""
    coordinates = get_location_coordinates(location)
    if coordinates:
        latitude = coordinates['latitude']
        longitude = coordinates['longitude']
        forecast_info = fetch_weather_forecast(latitude, longitude)
        if forecast_info:
            forecast_str = f"Weather forecast for {location}:\n"
            for entry in forecast_info:
                forecast_str += f"{entry['datetime']}: Max Temp: {entry['temperature_max']}°C, Min Temp: {entry['temperature_min']}°C, Precipitation: {entry['precipitation']} mm\n"
            return forecast_str
        else:
            return f"Error fetching weather forecast data. Please check the input parameters and try again."
    else:
        return f"Location not found or API error. It looks like there was an error retrieving the coordinates for {location}. The API may not have been able to find the location or there was an issue with the connection. I apologize that I'm unable to provide the weather forecast for {location} at this time. Please let me know if you have any other questions!"

@tool
def get_historical_weather(location: str, start_date: str, end_date: str) -> str:
    """Get the historical weather data for a specified location (city or country) and date range."""
    coordinates = get_location_coordinates(location)
    if coordinates:
        latitude = coordinates['latitude']
        longitude = coordinates['longitude']
        historical_weather_info = fetch_historical_weather(latitude, longitude, start_date, end_date)
        if historical_weather_info:
            total_temp = 0
            count = 0
            historical_weather_str = f"Historical weather data for {location} from {start_date} to {end_date}:\n"
            for entry in historical_weather_info:
                historical_weather_str += f"{entry['datetime']}: {entry['temperature']}°C\n"
                total_temp += entry['temperature']
                count += 1
            if count > 0:
                average_temp = total_temp / count
                historical_weather_str += f"\nSummary:\nAverage Temperature: {average_temp:.2f}°C"
            return historical_weather_str
        else:
            return f"Error fetching historical weather data. Please check the input parameters and try again."
    else:
        return f"Location not found or API error. It looks like there was an error retrieving the coordinates for {location}. The API may not have been able to find the location or there was an issue with the connection. I apologize that I'm unable to provide the historical weather data for {location} at this time. Please let me know if you have any other questions!"

