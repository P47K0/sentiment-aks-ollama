import pytest
import app
from unittest.mock import patch
from app import analyze_sentiment
import requests

class MockResponseValidText:
    status_code = 200

    def raise_for_status(self):
        pass

    def json(self):
        return {
            "response": "positive"
        }

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
    monkeypatch.setattr(app.requests, "post", lambda *args, **kwargs: MockResponseValidText())
    monkeypatch.setenv("PROMPT_TEMPLATE", "Analyze the sentiment of this text: {text}")
    response = client.post('/sentiment', json={"text": "Hello"})
    assert response.status_code == 200
    # Assuming a valid JSON response from Ollama
    assert isinstance(response.json, dict)

def test_analyze_sentiment_ollama_timeout(monkeypatch, client):
    expected_response = {"error": "Ollama request timed out", "details": "504"}
    monkeypatch.setenv("PROMPT_TEMPLATE", "Analyze the sentiment of this text: {text}")
    with patch('app.requests.post') as mock_post:                                                                                       
        mock_post.side_effect = requests.exceptions.Timeout()                                                    
                                                                                                                                    
        response = client.post('/sentiment', json={"text": "Hello"})                                                                   
        assert response.status_code == 504                                                                                          
        assert response.json.get("error") == expected_response["error"]

def test_analyze_sentiment_ollama_request_exception(monkeypatch, client):
    expected_response = {"error": "Failed to communicate with Ollama", "details": "502"}
    monkeypatch.setenv("PROMPT_TEMPLATE", "Analyze the sentiment of this text: {text}")
    with patch('app.requests.post') as mock_post:                                                                                       
        mock_post.side_effect = requests.exceptions.RequestException()                                     
                                                                                                                                    
        response = client.post('/sentiment', json={"text": "Hello"})                                                                   
        assert response.status_code == 502                                                                                          
        assert response.json.get("error") == expected_response["error"]

def test_analyze_sentiment_ollama_general_exception(monkeypatch, client):
    expected_response = {"error": "Internal error in adapter", "details": "500"}
    monkeypatch.setenv("PROMPT_TEMPLATE", "Analyze the sentiment of this text: {text}")
    with patch('app.requests.post') as mock_post:                                                                                       
        mock_post.side_effect = Exception()                                     
                                                                                                                                    
        response = client.post('/sentiment', json={"text": "Hello"})                                                                   
        assert response.status_code == 500                                                                                          
        assert response.json.get("error") == expected_response["error"]