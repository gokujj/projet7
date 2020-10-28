"""This module defines a class allowing to easily interact with
the Google Maps REST API.
"""
import os

import requests


class GoogleGeocodingError(Exception):
    """Exception thrown if an error occurs in the HTTP call to the API
    Google geocoding.
    """

    pass


class GoogleGeocodingNothingFoundError(GoogleGeocodingError):
    """Exception thrown if the searched location was not found by google."""

    pass


class GoogleGeocodingClient:
    """Represents a client interface for researching
    on the Google Geocoding API.
    """

    def __init__(self):
        self._url = "https://maps.googleapis.com/maps/api/geocode/json"
        self._key = os.getenv("GOOGLE_MAPS_GEOCODING_KEY")

    def search(self, address):
        """Search for an address on the Google Maps Geocoding API."""
        try:
            response = requests.get(
                url=self._url, params={"address": address, "key": self._key}
            )
            # We check that the status is not different from 200
            response.raise_for_status()
        except (requests.HTTPError, requests.ConnectionError):
            raise GoogleGeocodingError(
                "An HTTP error occured in google geocoding API call."
            )
        data = response.json()
        # On vérifie qu'il existe des résultats
        if data['status'] == 'ZERO_RESULTS':
            raise GoogleGeocodingNothingFoundError(
                "No result found for the current address"
            )
        return {
            "address": data["results"][0]["formatted_address"],
            "latitude": data["results"][0]["geometry"]["location"]["lat"],
            "longitude": data["results"][0]["geometry"]["location"]["lng"],
        }
