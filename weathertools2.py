import requests
from langchain.tools import tool
from datetime import datetime, timedelta
from urllib.parse import quote
from weathertools import get_location_coordinates, fetch_historical_weather, fetch_weather_forecast


@tool
def recommend_best_time_to_visit(location: str) -> str:
    """Recommend the best time of the year to visit a specified location (city or country) based on historical weather data and forecast."""
    coordinates = get_location_coordinates(location)
    if coordinates:
        latitude = coordinates['latitude']
        longitude = coordinates['longitude']
        
        # Fetch historical weather data for the past year
        one_year_ago = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        historical_weather_info = fetch_historical_weather(latitude, longitude, one_year_ago, datetime.now().strftime("%Y-%m-%d"))
        
        # Fetch weather forecast data for the next 16 days
        forecast_info = fetch_weather_forecast(latitude, longitude)
        
        if historical_weather_info and forecast_info:
            monthly_avg_temp = {}
            current_date = datetime.now().date()
            
            for entry in historical_weather_info:
                try:
                    entry_date = datetime.strptime(entry['datetime'], "%Y-%m-%dT%H:%M:%S").date()
                except ValueError:
                    entry_date = datetime.strptime(entry['datetime'], "%Y-%m-%dT%H:%M").date()
                
                month = entry_date.strftime("%Y-%m")
                if month not in monthly_avg_temp:
                    monthly_avg_temp[month] = {"total_temp": 0, "count": 0}
                if entry['temperature'] is not None:  # Check if temperature is not None
                    monthly_avg_temp[month]["total_temp"] += entry['temperature']
                    monthly_avg_temp[month]["count"] += 1
            
            # Calculate average temperature for each month
            for month in monthly_avg_temp:
                monthly_avg_temp[month]["avg_temp"] = monthly_avg_temp[month]["total_temp"] / monthly_avg_temp[month]["count"]
            
            # Get the current month
            current_month = datetime.now().strftime("%Y-%m")
            
            # Predict future monthly averages based on historical data
            future_months = {}
            for i in range(12):
                future_month = (datetime.now() + timedelta(days=30*i)).strftime("%Y-%m")
                past_month = (datetime.now() - timedelta(days=365-30*i)).strftime("%Y-%m")
                if past_month in monthly_avg_temp:
                    future_months[future_month] = monthly_avg_temp[past_month]
            
            if not future_months:
                return f"No future data available to recommend the best time to visit {location}."
            
            best_month = min(future_months, key=lambda m: abs(future_months[m]["avg_temp"] - 20))
            best_temp = future_months[best_month]["avg_temp"]
            
            # Analyze forecast data for short-term recommendation
            future_forecast_info = [f for f in forecast_info if datetime.strptime(f["datetime"], "%Y-%m-%d").date() >= current_date]
            if not future_forecast_info:
                return f"No future forecast data available to recommend the best day to visit {location}."
            
            best_forecast_day = min(future_forecast_info, key=lambda f: abs(f["temperature_max"] - 20))
            best_forecast_date = best_forecast_day["datetime"]
            best_forecast_temp = best_forecast_day["temperature_max"]
            
            return (f"The best time to visit {location} is in {best_month}, with an average temperature of {best_temp:.2f}°C.\n"
                    f"In the short term, the best day to visit is {best_forecast_date}, with a forecasted maximum temperature of {best_forecast_temp:.2f}°C.")
        else:
            return f"Error fetching weather data. Please check the input parameters and try again."
    else:
        return f"Location not found or API error. It looks like there was an error retrieving the coordinates for {location}. The API may not have been able to find the location or there was an issue with the connection. I apologize that I'm unable to provide the best time to visit {location} at this time. Please let me know if you have any other questions!"