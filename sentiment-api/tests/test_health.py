import pytest

from flask import Flask, jsonify

@pytest.mark.parametrize("endpoint", ["/health"])
def test_health_endpoint(client, endpoint):
    response = client.get(endpoint)
    assert response.status_code == 200
    assert response.json == {"status": "healthy"}
