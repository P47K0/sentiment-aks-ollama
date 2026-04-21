from flask import Flask, request, jsonify
from werkzeug.exceptions import BadRequest
import requests
import os

app = Flask(__name__)

# Point to the new LLM Adapter service instead of Azure
ADAPTER_URL = os.environ.get("ADAPTER_URL", "http://llm-adapter:5000/sentiment")

@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"error": "Method Not Allowed"}), 405

@app.route('/sentiment', methods=['POST'])
def sentiment():
    try:
        data = request.get_json()
    except BadRequest:
        return jsonify({"error": "Malformed JSON"}), 400
    
    try:
        text = data.get("text", "")
    except AttributeError:
        return jsonify({"error": "No text provided"}), 400
    
    if not text:
        return jsonify({"error": "No text provided"}), 400

    try:
        response = requests.post(ADAPTER_URL, json={"text": text}, timeout=30)
        response.raise_for_status()
        result = response.json()

        if not isinstance(result, dict) or "sentiment" not in result:
            return jsonify({"error": "Unexpected upstream response format"}), 500

        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": "Failed to get sentiment", "details": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Liveness probe - checks if the app is running"""
    return jsonify({"status": "healthy"}), 200

@app.route('/ready', methods=['GET'])
def ready():
    """Readiness probe - checks if the app can connect to the adapter"""
    try:
        # Quick check if adapter is reachable
        response = requests.get("http://llm-adapter:5000/health", timeout=2)
        if response.status_code == 200:
            return jsonify({"status": "ready"}), 200
        else:
            return jsonify({"status": "not ready"}), 503
    except:
        return jsonify({"status": "not ready"}), 503


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)