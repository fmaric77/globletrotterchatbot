import requests
from langchain.tools import tool

# Function to fetch historical and cultural information from Wikipedia
def fetch_wikipedia_summary(city):
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{city}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get('extract', 'No summary available.')
    else:
        print(f"Error fetching Wikipedia summary: {response.status_code} - {response.text}")
        return None

# Wrap the Wikipedia function as a tool
@tool
def get_city_highlights(city: str) -> str:
    """Get historical and cultural highlights of a past Olympic host city."""
    summary = fetch_wikipedia_summary(city)
    if summary:
        return f"Historical and cultural highlights of {city}:\n{summary}"
    else:
        return f"City not found or API error. It looks like there was an error retrieving information for {city}. Please try again later."
    


# Function to fetch information about popular sport clubs in a city from Wikipedia
def fetch_sport_clubs_info(city):
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{city}_sports"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get('extract', 'No information available.')
    else:
        print(f"Error fetching Wikipedia summary: {response.status_code} - {response.text}")
        return None

# Wrap the sport clubs function as a tool
@tool
def get_sport_clubs_info(city: str) -> str:
    """Get the most popular sport clubs in the city and their recent success."""
    summary = fetch_sport_clubs_info(city)
    if summary:
        return f"Most popular sport clubs in {city} and their recent success:\n{summary}"
    else:
        return f"No information available for sport clubs in {city} or API error. Please try again later."