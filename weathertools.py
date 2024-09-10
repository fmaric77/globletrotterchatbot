import requests
from langchain.tools import tool

# Directly use the API key
WEATHER_API_KEY = '78cf93102503bb0c15fdd28d60188084'

# Function to get current weather information
def fetch_current_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        weather = {
            "city": city,
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
def fetch_weather_forecast(city):
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={WEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        forecast = []
        for entry in data['list']:
            forecast.append({
                "datetime": entry['dt_txt'],
                "temperature": entry['main']['temp'],
                "description": entry['weather'][0]['description'],
                "humidity": entry['main']['humidity'],
                "wind_speed": entry['wind']['speed']
            })
        return forecast
    else:
        print(f"Error fetching weather forecast: {response.status_code} - {response.text}")
        return None

# Function to get latitude and longitude of a city
def get_city_coordinates(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        coordinates = {
            "latitude": data['coord']['lat'],
            "longitude": data['coord']['lon']
        }
        return coordinates
    else:
        print(f"Error fetching city coordinates: {response.status_code} - {response.text}")
        return None

# Function to fetch historical weather data
def fetch_historical_weather(latitude, longitude, start_date, end_date):
    url = f"https://archive-api.open-meteo.com/v1/era5?latitude={latitude}&longitude={longitude}&start_date={start_date}&end_date={end_date}&hourly=temperature_2m"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        historical_weather = []
        for time, temp in zip(data['hourly']['time'], data['hourly']['temperature_2m']):
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
def get_current_weather(city: str) -> str:
    """Get the current weather for a specified city."""
    weather_info = fetch_current_weather(city)
    if weather_info:
        return f"Current weather in {city}: {weather_info['temperature']}°C, {weather_info['description']}, Humidity: {weather_info['humidity']}%, Wind Speed: {weather_info['wind_speed']} m/s"
    else:
        return f"City not found or API error. It looks like there was an error retrieving the current weather for {city}. The API may not have been able to find the city or there was an issue with the connection. I apologize that I'm unable to provide the current weather for {city} at this time. Please let me know if you have any other questions!"

@tool
def get_weather_forecast(city: str) -> str:
    """Get the weather forecast for the next 5 days for a specified city."""
    forecast_info = fetch_weather_forecast(city)
    if forecast_info:
        forecast_str = f"Weather forecast for {city}:\n"
        for entry in forecast_info:
            forecast_str += f"{entry['datetime']}: {entry['temperature']}°C, {entry['description']}, Humidity: {entry['humidity']}%, Wind Speed: {entry['wind_speed']} m/s\n"
        return forecast_str
    else:
        return f"City not found or API error. It looks like there was an error retrieving the weather forecast for {city}. The API may not have been able to find the city or there was an issue with the connection. I apologize that I'm unable to provide the weather forecast for {city} at this time. Please let me know if you have any other questions!"

@tool
def get_historical_weather(city: str, start_date: str, end_date: str) -> str:
    """Get the historical weather data for a specified city and date range."""
    coordinates = get_city_coordinates(city)
    if coordinates:
        latitude = coordinates['latitude']
        longitude = coordinates['longitude']
        historical_weather_info = fetch_historical_weather(latitude, longitude, start_date, end_date)
        if historical_weather_info:
            total_temp = 0
            count = 0
            historical_weather_str = f"Historical weather data for {city} from {start_date} to {end_date}:\n"
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
        return f"City not found or API error. It looks like there was an error retrieving the coordinates for {city}. The API may not have been able to find the city or there was an issue with the connection. I apologize that I'm unable to provide the historical weather data for {city} at this time. Please let me know if you have any other questions!"