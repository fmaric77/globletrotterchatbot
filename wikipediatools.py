import requests
from langchain.tools import tool
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

WIKIPEDIA_API_URL = "https://en.wikipedia.org/api/rest_v1/page/summary"

def fetch_wikipedia_summary(page_title):
    """Fetch summary information from Wikipedia for a given page title."""
    url = f"{WIKIPEDIA_API_URL}/{page_title}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get('extract', 'No summary available.')
    except requests.RequestException as e:
        logging.error(f"Error fetching Wikipedia summary for {page_title}: {e}")
        return None

@tool
def get_city_highlights(city: str) -> str:
    """Get historical and cultural highlights of a past Olympic host city."""
    summary = fetch_wikipedia_summary(city)
    if summary:
        return f"Historical and cultural highlights of {city}:\n{summary}"
    else:
        return f"City not found or API error. It looks like there was an error retrieving information for {city}. Please try again later."

@tool
def get_sport_clubs_info(city: str) -> str:
    """Get the most popular sport clubs in the city and their recent success."""
    page_title = f"{city}_sports"
    summary = fetch_wikipedia_summary(page_title)
    if summary:
        return f"Most popular sport clubs in {city} and their recent success:\n{summary}"
    else:
        return f"No information available for sport clubs in {city} or API error. Please try again later."