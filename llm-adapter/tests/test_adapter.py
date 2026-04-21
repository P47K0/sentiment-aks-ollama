import pytest
from app import analyze_sentiment
import requests

def test_analyze_sentiment_no_text(client):
    response = client.post('/sentiment', json={})
    assert response.status_code == 400
    assert response.json == {"error": "No text provided"}

def test_analyze_sentiment_empty_text(client):
    response = client.post('/sentiment', json={"text": ""})
    assert response.status_code == 400
    assert response.json == {"error": "No text provided"}

def test_analyze_sentiment_missing_prompt_template(monkeypatch, client):
    monkeypatch.setenv("PROMPT_TEMPLATE", "")
    response = client.post('/sentiment', json={"text": "Hello"})
    assert response.status_code == 500
    assert response.json == {"error": "Prompt configuration missing"}

def test_analyze_sentiment_valid_text(monkeypatch, client):
    monkeypatch.setenv("PROMPT_TEMPLATE", "Analyze the sentiment of this text: {text}")
    response = client.post('/sentiment', json={"text": "Hello"})
    assert response.status_code == 200
    # Assuming a valid JSON response from Ollama
    assert isinstance(response.json, dict)

def test_analyze_sentiment_ollama_timeout(monkeypatch, client):
    monkeypatch.setenv("PROMPT_TEMPLATE", "Analyze the sentiment of this text: {text}")
    with pytest.raises(requests.exceptions.Timeout):
        analyze_sentiment({"text": "Hello"})

def test_analyze_sentiment_ollama_request_exception(monkeypatch, client):
    monkeypatch.setenv("PROMPT_TEMPLATE", "Analyze the sentiment of this text: {text}")
    with pytest.raises(requests.exceptions.RequestException):
        analyze_sentiment({"text": "Hello"})

def test_analyze_sentiment_unexpected_error(monkeypatch, client):
    monkeypatch.setenv("PROMPT_TEMPLATE", "Analyze the sentiment of this text: {text}")
    with pytest.raises(Exception):
        analyze_sentiment({"text": "Hello"})
