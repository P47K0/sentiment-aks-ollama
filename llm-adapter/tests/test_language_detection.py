import pytest
from unittest.mock import patch, Mock
import requests
import os

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

def test_detect_language_missing_prompt_template(monkeypatch, client):
    monkeypatch.setenv("LANGUAGE_PROMPT_TEMPLATE", "")
    response = client.post('/sentiment', json={"text": "Hello"})
    assert response.status_code == 500
    assert response.json == {"error": "Prompt configuration missing"}


@patch("app.requests.post")
def test_detect_language_valid_text(mock_post, monkeypatch, client):
    monkeypatch.setenv("LANGUAGE_PROMPT_TEMPLATE", "Detect the language of this text: {text}")
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"response": '{"language": "en"}'}
    mock_post.return_value = mock_response

    response = client.post('/detect-language', json={"text": "Hello"})
    assert response.status_code == 200
    assert response.json == {'language': 'en'}

@patch("app.requests.post")
def test_detect_language_ollama_timeout(mock_post,monkeypatch, client):
    monkeypatch.setenv("LANGUAGE_PROMPT_TEMPLATE", "Detect the language of this text: {text}")
    mock_post.side_effect = requests.Timeout

    response = client.post('/detect-language', json={"text": "Hello"})
    assert response.status_code == 504
    assert response.json == {"error": "Ollama request timed out"}

@patch("app.requests.post")
def test_detect_language_ollama_request_exception(mock_post,monkeypatch, client):
    monkeypatch.setenv("LANGUAGE_PROMPT_TEMPLATE", "Detect the language of this text: {text}")
    mock_post.side_effect = requests.RequestException("Request failed")

    response = client.post('/detect-language', json={"text": "Hello"})
    assert response.status_code == 502
    assert response.json == {"error": "Failed to communicate with Ollama", "details": "Request failed"}

@patch("app.requests.post")
def test_detect_language_ollama_general_exception(mock_post, monkeypatch, client):
    monkeypatch.setenv("LANGUAGE_PROMPT_TEMPLATE", "Detect the language of this text: {text}")
    mock_post.side_effect = Exception("General error")

    response = client.post('/detect-language', json={"text": "Hello"})
    assert response.status_code == 500
    assert response.json == {"error": "Internal error in adapter", "details": "General error"}
