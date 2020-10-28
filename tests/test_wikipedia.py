import pytest
import requests

from grandpy.apis import wikipedia

TEST_PAGE_IDS = [6422233, 5105544]

WIKIPEDIA_GEOSEARCH_SUCCESS_RESPONSE = {
    'query': {
        'geosearch': [
            {
                'dist': 129.9,
                'lat': 37.78785,
                'lon': -122.40065,
                'ns': 0,
                'pageid': TEST_PAGE_IDS[0],
                'primary': '',
                'title': 'Academy of Art University',
            },
            {
                'dist': 140.9,
                'lat': 37.788139,
                'lon': -122.399056,
                'ns': 0,
                'pageid': TEST_PAGE_IDS[1],
                'primary': '',
                'title': '101 Second Street',
            },
        ]
    }
}

WIKIPEDIA_GEOSEARCH_NOTHING_FOUND_RESPONSE = {
    'query': {'geosearch': []},
}


WIKIPEDIA_PAGE_SUCCESS_RESPONSE = {
    'query': {
        'pages': {
            '6422233': {
                'extract': 'L’Academy of Art University '
                '(autrefois Academy of Art '
                'College), est une université '
                'appartenant au Stephens '
                'Institute, fondée à San Francisco '
                'en Californie en 1929 par le '
                'peintre Richard S. Stephens.'
                'Avec plus de 18 000 étudiants, '
                "l'Academy of Art de San Francisco "
                "est la plus grande école d'art et "
                'des États-Unis,.\n',
                'fullurl': 'https://fr.wikipedia.org/wiki/Academy_of_Art_University',
                'title': 'Academy of Art University',
            }
        }
    },
}

WIKIPEDIA_PAGE_NOT_FOUND_RESPONSE = {
    'query': {
        'pages': {
            f'{TEST_PAGE_IDS[0]}': {'missing': '', 'pageid': TEST_PAGE_IDS[0]}
        }
    },
}


@pytest.fixture
def client():
    client = wikipedia.WikipediaClient()
    yield client


@pytest.fixture
def page():
    page = wikipedia.WikipediaPage(TEST_PAGE_IDS[0])
    yield page


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
            "url": url,
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
            return {}

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


@pytest.fixture
def mock_get_page(monkeypatch):
    """Fixture replacing the requests.get function with an imitation simulating
     a successful search of the Wikipedia Extracts API.
    """

    class MockRequestsResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return WIKIPEDIA_PAGE_SUCCESS_RESPONSE

    def mock_requests_get(url, params):
        mock_requests_get.called_with_parameters = {
            "url": url,
            "params": params,
        }
        return MockRequestsResponse()

    monkeypatch.setattr('requests.get', mock_requests_get)
    yield mock_requests_get


@pytest.fixture
def mock_get_page_not_found(monkeypatch):
    """Fixture replacing the requests.get function with an imitation simulating
     a search of the Wikipedia Extracts API with no results.
    """

    class MockRequestsResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return WIKIPEDIA_PAGE_NOT_FOUND_RESPONSE

    def mock_requests_get(url, params):
        mock_requests_get.called_with_parameters = {
            "url": url,
            "params": params,
        }
        return MockRequestsResponse()

    monkeypatch.setattr('requests.get', mock_requests_get)
    yield mock_requests_get


class TestWikipediaClient:
    def test_geosearch_returns_a_list(self, client, mock_get_geosearch):
        result = client.geosearch(latitude=0, longitude=0)
        assert isinstance(result, list)

    def test_geosearch_calls_wikipedia_api(self, client, mock_get_geosearch):
        result = client.geosearch(latitude=0, longitude=0)
        # vérifie que le mock a été appelé
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

    def test_geosearch_raises_custom_exception_if_nothing_found(
        self, client, mock_get_geosearch_with_no_result
    ):
        with pytest.raises(wikipedia.WikipediaNothingFound):
            results = client.geosearch(latitude=0, longitude=0)


class TestWikipediaPage:
    def test_wikipedia_page_can_be_instantiated_with_a_page_id(self):
        page = wikipedia.WikipediaPage(TEST_PAGE_IDS[0])

    def test_get_data_calls_wikipedia_api(self, page, mock_get_page):
        page.get_data()
        arguments = mock_get_page.called_with_parameters
        assert "https://fr.wikipedia.org/w/api.php" in arguments["url"]
        assert "json" == arguments["params"]["format"]
        assert "query" == arguments["params"]["action"]
        assert "extracts|info" == arguments["params"]["prop"]
        assert "url" == arguments["params"]["inprop"]
        assert 1200 == arguments["params"]["exchars"]
        assert True == arguments["params"]["explaintext"]
        assert TEST_PAGE_IDS[0] == arguments["params"]["pageids"]

    def test_get_data_raises_custom_exception_if_http_error(
        self, page, mock_get_geosearch_with_http_error
    ):
        with pytest.raises(wikipedia.WikipediaError):
            page.get_data()

    def test_get_data_raises_custom_exception_if_connection_error(
        self, page, mock_get_geosearch_with_connection_error
    ):
        with pytest.raises(wikipedia.WikipediaError):
            page.get_data()

    def test_get_data_raises_custom_exception_if_nothing_found(
        self, page, mock_get_page_not_found
    ):
        with pytest.raises(wikipedia.WikipediaNothingFound):
            page.get_data()

    def test_page_has_not_none_title_summary_and_url(
        self, page, mock_get_page
    ):
        page.get_data()
        assert page.title is not None
        assert page.summary is not None
        assert page.url is not None

    def test_page_has_not_none_title_summary_and_url_without_get_data(
        self, page, mock_get_page
    ):
        assert page.title is not None
        assert page.summary is not None
        assert page.url is not None

    def test_page_as_dict_method_returns_a_dict_with_title_summary_url(
        self, page, mock_get_page
    ):
        dict_data = page.as_dict()
        assert isinstance(dict_data, dict)
        assert dict_data["title"] == page.title
        assert dict_data["url"] == page.url
        assert dict_data["summary"] == page.summary
