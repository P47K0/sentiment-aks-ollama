import pytest
from unittest.mock import patch, Mock

from app import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_detect_language_no_text(client):
    response = client.post('/detect-language', json={})
    assert response.status_code == 400
    assert response.json == {"error": "No text provided"}

def test_detect_language_empty_text(client):
    response = client.post('/detect-language', json={"text": ""})
    assert response.status_code == 400
    assert response.json == {"error": "No text provided"}

@patch('requests.post')
def test_detect_language_valid_text(mock_post, client):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"language": "en"}
    mock_post.return_value = mock_response

    response = client.post('/detect-language', json={"text": "Hello"})
    assert response.status_code == 200
    assert response.json == {"language": "en"}

@patch('requests.post')
def test_detect_language_ollama_timeout(mock_post, client):
    mock_post.side_effect = requests.Timeout

    response = client.post('/detect-language', json={"text": "Hello"})
    assert response.status_code == 504
    assert response.json == {"error": "Ollama timeout"}

@patch('requests.post')
def test_detect_language_ollama_request_exception(mock_post, client):
    mock_post.side_effect = requests.RequestException("Request failed")

    response = client.post('/detect-language', json={"text": "Hello"})
    assert response.status_code == 500
    assert response.json == {"error": "Failed to detect language", "details": "Request failed"}

@patch('requests.post')
def test_detect_language_ollama_general_exception(mock_post, client):
    mock_post.side_effect = Exception("General error")

    response = client.post('/detect-language', json={"text": "Hello"})
    assert response.status_code == 500
    assert response.json == {"error": "Failed to detect language", "details": "General error"}

def test_detect_language_feature_flag_disabled(client):
    with patch.dict(os.environ, {"LANGUAGE_DETECTION_ENABLED": "false"}):
        response = client.post('/detect-language', json={"text": "Hello"})
        assert response.status_code == 403
        assert response.json == {"error": "Language detection is disabled"}
