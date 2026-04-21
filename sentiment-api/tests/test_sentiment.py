import pytest
from unittest.mock import patch

def test_sentiment_success(client):
    text = "This is a positive sentence."
    expected_response = {"sentiment": "positive"}

    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = expected_response

        response = client.post('/sentiment', json={"text": text})
        assert response.status_code == 200
        assert response.json == expected_response

def test_sentiment_invalid_payload(client):
    invalid_text = ""
    expected_response = {"error": "No text provided"}

    response = client.post('/sentiment', json={"text": invalid_text})
    assert response.status_code == 400
    assert response.json == expected_response

def test_sentiment_upstream_failure(client):
    text = "This is a positive sentence."
    expected_response = {"error": "Failed to get sentiment", "details": "Adapter service is down"}

    with patch('requests.post') as mock_post:
        mock_post.side_effect = requests.exceptions.RequestException("Adapter service is down")

        response = client.post('/sentiment', json={"text": text})
        assert response.status_code == 500
        assert response.json == expected_response
