import pytest
import requests

from grandpy.apis import googlemaps


GOOGLE_GEOCODING_SUCCESS_RESPONSE = {
    'results': [
        {
            'formatted_address': 'Champ de Mars, 5 Avenue Anatole France, 75007 Paris, France',
            'geometry': {
                'location': {'lat': 48.85837009999999, 'lng': 2.2944813},
            },
        }
    ],
    'status': 'OK',
}

GOOGLE_GEOCODING_NOTHING_FOUND_RESPONSE = {
    'results': [],
    'status': 'ZERO_RESULTS',
}


@pytest.fixture
def client():
    """Fixture creating a GoogleGeocodingClient client for each test."""
    client = googlemaps.GoogleGeocodingClient()
    yield client


@pytest.fixture
def mock_get(monkeypatch):
    """Fixture replacing requests.get function with an imitation."""

    class MockRequestsResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return GOOGLE_GEOCODING_SUCCESS_RESPONSE

    def mock_requests_get(url, params):
        mock_requests_get.called_with_parameters = {
            "url": url,
            "params": params,
        }
        return MockRequestsResponse()

    monkeypatch.setattr('requests.get', mock_requests_get)
    yield mock_requests_get


@pytest.fixture
def mock_get_with_http_error(monkeypatch):
    """Fixture replacing requests.get function with an imitation
     raising a request.HTTPError via raise_for_status."""

    class MockRequestsResponse:
        def raise_for_status(self):
            raise requests.HTTPError(
                "Exception raised by mock_get_with_http_error"
            )

        def json(self):
            return GOOGLE_GEOCODING_SUCCESS_RESPONSE

    def mock_requests_get(url, params):
        mock_requests_get.called_with_parameters = {
            "url": url,
            "params": params,
        }
        return MockRequestsResponse()

    monkeypatch.setattr('requests.get', mock_requests_get)
    yield mock_requests_get


@pytest.fixture
def mock_get_with_connection_error(monkeypatch):
    """Fixture replacing requests.get function with an imitation
     raising a requests.ConnectionError."""

    def mock_requests_get(url, params):
        raise requests.ConnectionError(
            "Exception raised by mock_get_with_http_error"
        )

    monkeypatch.setattr('requests.get', mock_requests_get)
    yield mock_requests_get


@pytest.fixture
def mock_get_with_no_result(monkeypatch):
    """Fixture replacing requests.get function with an imitation
     simulating an unsuccessful call to the API."""

    class MockRequestsResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return GOOGLE_GEOCODING_NOTHING_FOUND_RESPONSE

    def mock_requests_get(url, params):
        mock_requests_get.called_with_parameters = {
            "url": url,
            "params": params,
        }
        return MockRequestsResponse()

    monkeypatch.setattr('requests.get', mock_requests_get)
    yield mock_requests_get


class TestGoogleGeocodingClient:
    def test_google_geocoding_client_class_exists(self):
        assert hasattr(googlemaps, "GoogleGeocodingClient")

    def test_search_method_exists(self, client, mock_get):
        client.search("tour eiffel")

    def test_search_method_returns_a_dictionnary(self, client, mock_get):
        result = client.search("tour eiffel")
        assert isinstance(result, dict)

    def test_search_method_returns_a_dict_with_address_latitude_longitude_fields(
        self, client, mock_get
    ):
        result = client.search("tour eiffel")
        assert "address" in result
        assert "latitude" in result
        assert "longitude" in result

    def test_search_method_calls_requests_get(self, client, mock_get):
        result = client.search("tour eiffel")
        assert hasattr(mock_get, "called_with_parameters")

    def test_search_method_calls_requests_get_with_correct_arguments(
        self, client, mock_get
    ):
        result = client.search("tour eiffel")
        assert (
            mock_get.called_with_parameters['url']
            == "https://maps.googleapis.com/maps/api/geocode/json"
        )
        assert "address" in mock_get.called_with_parameters['params']
        assert "key" in mock_get.called_with_parameters["params"]

    def test_search_method_sends_address_argument_to_requests_get(
        self, client, mock_get
    ):
        result = client.search("tour eiffel")
        assert (
            mock_get.called_with_parameters["params"]["address"]
            == "tour eiffel"
        )

    def test_search_method_returns_dict_with_correct_address_latitude_longitude(
        self, client, mock_get
    ):
        result = client.search("tour eiffel")
        assert (
            result["address"]
            == GOOGLE_GEOCODING_SUCCESS_RESPONSE["results"][0][
                "formatted_address"
            ]
        )
        assert (
            result["latitude"]
            == GOOGLE_GEOCODING_SUCCESS_RESPONSE["results"][0]["geometry"][
                "location"
            ]["lat"]
        )
        assert (
            result["longitude"]
            == GOOGLE_GEOCODING_SUCCESS_RESPONSE["results"][0]["geometry"][
                "location"
            ]["lng"]
        )

    def test_search_method_raises_custom_exception_in_case_of_http_error(
        self, client, mock_get_with_http_error
    ):
        with pytest.raises(googlemaps.GoogleGeocodingError):
            result = client.search("tour eiffel")

    def test_search_method_raises_custom_exception_in_case_of_connection_error(
        self, client, mock_get_with_connection_error
    ):
        with pytest.raises(googlemaps.GoogleGeocodingError):
            result = client.search("tour eiffel")

    def test_search_method_raises_custom_exception_if_nothing_found(
        self, client, mock_get_with_no_result
    ):
        with pytest.raises(googlemaps.GoogleGeocodingNothingFoundError):
            result = client.search("tour eiffel")

    def test_search_method_raises_custom_exception_if_address_is_empty(
        self, client, mock_get
    ):
        with pytest.raises(googlemaps.GoogleGeocodingError):
            client.search("")
            client.search("   ")
