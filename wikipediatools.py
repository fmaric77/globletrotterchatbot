import requests
from langchain.tools import tool
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

WIKIPEDIA_API_URL = "https://en.wikipedia.org/api/rest_v1/page/summary"
WIKIPEDIA_SPORTS_URL = "https://en.wikipedia.org/wiki/Sport_in"

def fetch_wikipedia_summary(page_title):
    """Fetch summary information from Wikipedia for a given page title."""
    url = f"{WIKIPEDIA_API_URL}/{page_title}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get('extract', 'No summary available.')
    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 404:
            logging.error(f"Page not found for {page_title}: {http_err}")
            return "Page not found."
        else:
            logging.error(f"HTTP error occurred for {page_title}: {http_err}")
            return "HTTP error occurred."
    except requests.RequestException as e:
        logging.error(f"Error fetching Wikipedia summary for {page_title}: {e}")
        return "An error occurred while fetching data."

@tool
def get_city_highlights(city: str) -> str:
    """Get historical and cultural highlights of a past Olympic host city."""
    summary = fetch_wikipedia_summary(city)
    if summary:
        return f"Historical and cultural highlights of {city}:\n{summary}"
    else:
        return f"City not found or API error. It looks like there was an error retrieving information for {city}. Please try again later."

@tool
def get_sport_clubs_info(city: str, country: str) -> str:
    """Get the most popular sport clubs in the country of the specified city and their recent success."""
    page_title = f"Sport_in_{country}"
    summary = fetch_wikipedia_summary(page_title)
    if summary == "Page not found.":
        return f"No specific sports information available for the country of {city}. It seems there is no dedicated page for sports in the country of {city} on Wikipedia."
    elif summary:
        return f"Most popular sport clubs in the country of {city} and their recent success:\n{summary}"
    else:
        return f"No information available for sport clubs in the country of {city} or API error. Please try again later."