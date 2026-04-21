import pytest
from unittest.mock import patch                                                                                                     
import requests                                                                                                                     
                                                                                                                                    
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
                                                                                                                                    
def test_sentiment_malformed_json(client):                                                                                          
    malformed_json = '{"text": "This is a positive sentence."'                                                                      
    expected_response = {"error": "Malformed JSON"}                                                                                 
                                                                                                                                    
    response = client.post('/sentiment', data=malformed_json, content_type='application/json')                                      
    assert response.status_code == 400                                                                                              
    assert response.json == expected_response                                                                                       
                                                                                                                                    
def test_sentiment_missing_required_field(client):                                                                                  
    missing_field_json = '{"not_text": "This is a positive sentence."}'                                                             
    expected_response = {"error": "No text provided"}                                                                               
                                                                                                                                    
    response = client.post('/sentiment', json=missing_field_json)                                                                   
    assert response.status_code == 400                                                                                              
    assert response.json == expected_response                                                                                       
                                                                                                                                    
def test_sentiment_wrong_http_method(client):                                                                                       
    text = "This is a positive sentence."                                                                                           
    expected_response = {"error": "Method Not Allowed"}                                                                             
                                                                                                                                    
    response = client.get('/sentiment', json={"text": text})                                                                        
    assert response.status_code == 405                                                                                              
    assert response.json == expected_response                                                                                       
                                                                                                                                    
def test_sentiment_unexpected_upstream_format(client):                                                                              
    text = "This is a positive sentence."                                                                                           
    unexpected_response = {"unexpected_key": "value"}                                                                               
                                                                                                                                    
    with patch('requests.post') as mock_post:                                                                                       
        mock_post.return_value.status_code = 200                                                                                    
        mock_post.return_value.json.return_value = unexpected_response                                                              
                                                                                                                                    
        response = client.post('/sentiment', json={"text": text})                                                                   
        assert response.status_code == 500                                                                                          
        assert response.json == {"error": "Unexpected upstream response format"}                                                    
                                                                                                                                    
def test_sentiment_upstream_failure(client):                                                                                        
    text = "This is a positive sentence."                                                                                           
    expected_response = {"error": "Failed to get sentiment", "details": "Adapter service is down"}                                  
                                                                                                                                    
    with patch('requests.post') as mock_post:                                                                                       
        mock_post.side_effect = requests.exceptions.RequestException("Adapter service is down")                                     
                                                                                                                                    
        response = client.post('/sentiment', json={"text": text})                                                                   
        assert response.status_code == 500                                                                                          
        assert response.json == expected_response                                                                                   
                                                                                                                                    
def test_sentiment_timeout(client):                                                                                                 
    text = "This is a positive sentence."                                                                                           
    expected_response = {"error": "Failed to get sentiment", "details": "Request timed out"}                                        
                                                                                                                                    
    with patch('requests.post') as mock_post:                                                                                       
        mock_post.side_effect = requests.exceptions.Timeout("Request timed out")                                                    
                                                                                                                                    
        response = client.post('/sentiment', json={"text": text})                                                                   
        assert response.status_code == 500                                                                                          
        assert response.json == expected_response
