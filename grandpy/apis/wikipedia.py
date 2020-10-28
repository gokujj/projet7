import requests


class WikipediaError(Exception):
    pass


class WikipediaNothingFound(WikipediaError):
    pass


class WikipediaInvalidGPSCoordinates(WikipediaError):
    pass


class WikipediaClient:
    """Represents a client to search the API
     REST from Wikipedia.
    """

    def __init__(self, lang="fr"):
        if lang not in ("fr", "en", "de"):
            raise ValueError("The lang arg must be in ('fr', 'en', 'de')")
        self._url = f"https://{lang}.wikipedia.org/w/api.php"

    def geosearch(self, latitude, longitude):
        """Search wikipedia pages by GPS coordinates."""
        # Validating arguments
        if abs(latitude) > 90:
            raise WikipediaInvalidGPSCoordinates(
                "Latitude must stay between -90 and 90."
            )
        if abs(longitude) > 180:
            raise WikipediaInvalidGPSCoordinates(
                "Longitude must stay between -180 and 180."
            )
        # Wikipedia API call
        try:
            response = requests.get(
                self._url,
                params={
                    "format": "json",
                    "action": "query",
                    "list": "geosearch",
                    "gsradius": 10000,
                    "gscoord": f"{latitude}|{longitude}",
                },
            )
            response.raise_for_status()
        except requests.HTTPError:
            raise WikipediaError(
                "A HTTP status difference from 200 was received."
            )
        except requests.ConnectionError:
            raise WikipediaError(
                "A Connection error occured when contacting the wikipedia API."
            )
        # Processing of data received from Wikipedia API.
        # If the Wikipedia API did not find anything, the pages list is empty
        data = response.json()
        pages = [WikipediaPage() for page in data["query"]["geosearch"]]
        return pages


class WikipediaPage:
    """Represents a wikipedia page from which you can consult
    the title, the summary, the url.
    """

    pass
