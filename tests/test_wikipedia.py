import pytest
import requests

from grandpy.apis import wikipedia


WIKIPEDIA_GEOSEARCH_SUCCESS_RESPONSE = {
    'query': {
        'geosearch': [
            {
                'dist': 129.9,
                'lat': 37.78785,
                'lon': -122.40065,
                'ns': 0,
                'pageid': 6422233,
                'primary': '',
                'title': 'Academy of Art University',
            },
            {
                'dist': 140.9,
                'lat': 37.788139,
                'lon': -122.399056,
                'ns': 0,
                'pageid': 5105544,
                'primary': '',
                'title': '101 Second Street',
            },
        ]
    }
}

WIKIPEDIA_GEOSEARCH_NOTHING_FOUND_RESPONSE = {
    'query': {'geosearch': []},
}


@pytest.fixture
def client():
    client = wikipedia.WikipediaClient()
    yield client


@pytest.fixture
def mock_get_geosearch(monkeypatch):
    """Fixture replacing the requests.get function with an imitation simulating
    a successful search of the Wikipedia API.
    """

    class MockRequestsResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return WIKIPEDIA_GEOSEARCH_SUCCESS_RESPONSE

    def mock_requests_get(url, params):
        mock_requests_get.called_with_parameters = {
            "url": url,
            "params": params,
        }
        return MockRequestsResponse()

    monkeypatch.setattr('requests.get', mock_requests_get)
    yield mock_requests_get


@pytest.fixture
def mock_get_geosearch_with_no_result(monkeypatch):
    """Fixture replacing the requests.get function with an imitation simulating
    a search without results with the Wikipedia API.
    """

    class MockRequestsResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return WIKIPEDIA_GEOSEARCH_NOTHING_FOUND_RESPONSE

    def mock_requests_get(url, params):
        mock_requests_get.called_with_parameters = {
            "url": url, check that the mock has been called

            "params": params,
        }
        return MockRequestsResponse()

    monkeypatch.setattr('requests.get', mock_requests_get)
    yield mock_requests_get


@pytest.fixture
def mock_get_geosearch_with_http_error(monkeypatch):
    """Fixture replacing the requests.get function with an imitation simulating
    a search where raise_for_status () throws a requests.HTTPError.
    """

    class MockRequestsResponse:
        def raise_for_status(self):
            raise requests.HTTPError(
                "Exception raised by mock_get_geosearch_with_http_error"
            )

        def json(self):
            return WIKIPEDIA_GEOSEARCH_SUCCESS_RESPONSE

    def mock_requests_get(url, params):
        mock_requests_get.called_with_parameters = {
            "url": url,
            "params": params,
        }
        return MockRequestsResponse()

    monkeypatch.setattr('requests.get', mock_requests_get)
    yield mock_requests_get


@pytest.fixture
def mock_get_geosearch_with_connection_error(monkeypatch):
    """Fixture replacing the requests.get function with an imitation simulating
    a search with the Wikipedia API raising a
    requests.ConnectionError.
    """

    def mock_requests_get(url, params):
        raise requests.ConnectionError(
            "Raise in mock_get_geosearch_with_connection_error."
        )

    monkeypatch.setattr('requests.get', mock_requests_get)
    yield mock_requests_get


class TestWikipediaClient:
    def test_geosearch_returns_a_list(self, client, mock_get_geosearch):
        result = client.geosearch(latitude=0, longitude=0)
        assert isinstance(result, list)

    def test_geosearch_calls_wikipedia_api(self, client, mock_get_geosearch):
        result = client.geosearch(latitude=0, longitude=0)
        # check that the mock has been called
        assert hasattr(mock_get_geosearch, "called_with_parameters")

    def test_geosearch_calls_wikipedia_api_url(
        self, client, mock_get_geosearch
    ):
        result = client.geosearch(latitude=0, longitude=0)
        assert (
            mock_get_geosearch.called_with_parameters["url"]
            == "https://fr.wikipedia.org/w/api.php"
        )

    def test_geosearch_calls_wikipedia_api_with_right_params(
        self, client, mock_get_geosearch
    ):
        result = client.geosearch(latitude=0, longitude=0)
        params = mock_get_geosearch.called_with_parameters["params"]
        assert params["format"] == "json"
        assert params["action"] == "query"
        assert params["list"] == "geosearch"
        assert 0 <= params["gsradius"] <= 10000
        assert params["gscoord"] == f"0|0"

    def test_geosearch_returns_wikipedia_pages_instances(
        self, client, mock_get_geosearch
    ):
        results = client.geosearch(latitude=0, longitude=0)
        assert len(results) == 2
        for result in results:
            assert isinstance(result, wikipedia.WikipediaPage)

    def test_geosearch_raises_custom_exception_if_invalid_gps_coordinates(
        self, client, mock_get_geosearch
    ):
        with pytest.raises(wikipedia.WikipediaInvalidGPSCoordinates):
            client.geosearch(latitude=91, longitude=0)

        with pytest.raises(wikipedia.WikipediaInvalidGPSCoordinates):
            client.geosearch(latitude=-91, longitude=0)

        with pytest.raises(wikipedia.WikipediaInvalidGPSCoordinates):
            client.geosearch(latitude=0, longitude=181)

        with pytest.raises(wikipedia.WikipediaInvalidGPSCoordinates):
            client.geosearch(latitude=0, longitude=-181)

    def test_geosearch_raises_custom_exception_if_http_error(
        self, client, mock_get_geosearch_with_http_error
    ):
        with pytest.raises(wikipedia.WikipediaError):
            client.geosearch(latitude=0, longitude=0)

    def test_geosearch_raises_custom_exception_if_connection_error(
        self, client, mock_get_geosearch_with_connection_error
    ):
        with pytest.raises(wikipedia.WikipediaError):
            client.geosearch(latitude=0, longitude=0)

    def test_geosearch_returns_empty_list_if_nothing_found(
        self, client, mock_get_geosearch_with_no_result
    ):
        results = client.geosearch(latitude=0, longitude=0)
        assert len(results) == 0


class TestWikipediaPage:
    pass
