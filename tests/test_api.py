from unittest.mock import Mock, patch

import pytest

from pawzok import PawzokAssertionError, assert_api


@patch("pawzok.api.requests.request")
def test_assert_api_matches_expected_response(mock_request):
    response = Mock()
    response.status_code = 200
    response.json.return_value = {"id": 123, "status": "READY"}
    mock_request.return_value = response

    result = assert_api(
        method="GET",
        url="https://example.test/orders/123",
        expected_status=200,
        expected={"status": "READY"},
    )

    assert result.actual_status == 200
    assert result.actual["status"] == "READY"


@patch("pawzok.api.requests.request")
def test_assert_api_reports_body_difference(mock_request):
    response = Mock()
    response.status_code = 200
    response.json.return_value = {"id": 123, "status": "PROCESSING"}
    mock_request.return_value = response

    with pytest.raises(PawzokAssertionError) as error:
        assert_api(
            method="GET",
            url="https://example.test/orders/123",
            expected_status=200,
            expected={"status": "READY"},
        )

    assert "status: expected 'READY', got 'PROCESSING'" in str(error.value)


@patch("pawzok.api.requests.request")
def test_assert_api_reports_status_difference(mock_request):
    response = Mock()
    response.status_code = 404
    response.json.return_value = {"error": "not found"}
    mock_request.return_value = response

    with pytest.raises(PawzokAssertionError) as error:
        assert_api(
            method="GET",
            url="https://example.test/orders/123",
            expected_status=200,
        )

    assert "status code: expected 200, got 404" in str(error.value)
