"""Module responsible for implementing an interface for the Wikipedia API."""
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
        """Initializes a new client for the Wikipedia API."""
        self.lang = lang
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
        pages = [
            WikipediaPage(page["pageid"], self.lang)
            for page in data["query"]["geosearch"]
        ]
        if not pages:
            raise WikipediaNothingFound("No data has been found.")
        return pages


class WikipediaPage:
    """Represents a wikipedia page from which you can consult
    the title, the summary, the url.
    """

    def __init__(self, page_id, lang="fr"):
        """Initializes a new wikipedia page."""
        self.lang = lang
        if lang not in ("fr", "en", "de"):
            raise ValueError("The lang arg must be in ('fr', 'en', 'de')")
        self._url = f"https://{lang}.wikipedia.org/w/api.php"
        self.id = page_id
        self._title = None
        self._summary = None
        self._fullurl = None

    def get_data(self):
        """Downloads page data from wikipedia API."""
        # query parameters
        params = {
            "format": "json",
            "action": "query",
            "prop": "extracts|info",
            "inprop": "url",
            "exchars": 1200,
            "explaintext": True,
            "pageids": self.id,
        }
        try:
            response = requests.get(self._url, params=params)
            response.raise_for_status()
        except requests.HTTPError:
            raise WikipediaError(
                "A HTTP status difference from 200 was received."
            )
        except requests.ConnectionError:
            raise WikipediaError(
                "A Connection error occured when contacting the wikipedia API."
            )
        # Recovery of received data
        data = response.json()
        if "missing" in data["query"]["pages"][str(self.id)]:
            raise WikipediaNothingFound("No data has been found.")
        self._title = data["query"]["pages"][str(self.id)]["title"]
        self._summary = data["query"]["pages"][str(self.id)]["extract"]
        self._fullurl = data["query"]["pages"][str(self.id)]["fullurl"]

    @property
    def title(self):
        """Title of the wikipedia page."""
        if self._title is None:
            self.get_data()
        return self._title

    @property
    def summary(self):
        """Summary of the wikipedia page."""
        if self._summary is None:
            self.get_data()
        return self._summary

    @property
    def url(self):
        """URL of the wikipedia page."""
        if self._url is None:
            self.get_data()
        return self._fullurl

    def as_dict(self):
        """Returns the page data as a dictionary."""
        return {"title": self.title, "url": self.url, "summary": self.summary}
