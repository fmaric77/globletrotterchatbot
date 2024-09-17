import requests
from langchain.tools import tool
import logging
from wikipediatools import fetch_wikipedia_summary

@tool
def get_best_travel_package(location: str) -> str:
    """Get the best travel package for the user's desired location using Wikipedia."""
    summary = fetch_wikipedia_summary(location)
    if summary == "Page not found.":
        return f"No travel package information available for {location}. It seems there is no dedicated page for {location} on Wikipedia."
    elif summary:
        return f"Best travel package for {location}:\n{summary}"
    else:
        return f"No travel package information available for {location} or API error. Please try again later."

@tool
def get_tourism_info(country: str) -> str:
    """Get tourism information for the specified country using Wikipedia, specifically focusing on tourism statistics tables."""
    tourism_page = f"Tourism_in_{country}"
    summary = fetch_wikipedia_summary(tourism_page)
    if summary == "Page not found.":
        return f"No tourism information available for {country}. It seems there is no dedicated page for tourism in {country} on Wikipedia."
    elif summary:
        return f"Tourism information for {country}:\n{summary}"
    else:
        return f"No tourism information available for {country} or API error. Please try again later."

