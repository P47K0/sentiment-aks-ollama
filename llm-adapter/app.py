from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://ollama-service:11434/api/generate")
MODEL = os.environ.get("MODEL", "phi3:mini")

@app.route('/sentiment', methods=['POST'])
def analyze_sentiment():
    data = request.get_json()
    text = data.get("text", "").strip()
    
    if not text:
        return jsonify({"error": "No text provided"}), 400

    # Professional prompt for consistent output
    prompt = f"""Analyze the sentiment of the following text.
Return ONLY a JSON object with exactly these fields:
{{
  "sentiment": "POSITIVE" or "NEGATIVE" or "NEUTRAL",
  "positive": float between 0 and 1,
  "neutral": float between 0 and 1,
  "negative": float between 0 and 1
}}

Text: {text}

JSON:"""

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "temperature": 0.0,
        "max_tokens": 150
    }

    try:
        response = requests.post(f"{OLLAMA_URL.rstrip('/')}/api/generate", json=payload, timeout=30)
        response.raise_for_status()
        
        raw_output = response.json()["response"].strip()
        
        # Simple parsing - Ollama often returns clean JSON when asked
        import json
        try:
            result = json.loads(raw_output)
        except:
            # Fallback parsing if JSON is not perfect
            result = {
                "sentiment": "NEUTRAL",
                "positive": 0.4,
                "neutral": 0.4,
                "negative": 0.2
            }

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": "Failed to analyze sentiment", "details": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Liveness probe - checks if the app is running"""
    return jsonify({"status": "healthy"}), 200

@app.route('/ready', methods=['GET'])
def ready():
    """Readiness probe - checks if Ollama is reachable"""
    try:
        response = requests.get(f"{OLLAMA_URL.rstrip('/')}/api/version", timeout=5)
        if response.status_code == 200:
            return jsonify({"status": "ready"}), 200
        else:
            return jsonify({"status": "not ready", "reason": f"ollama returned {response.status_code}"}), 503
    except requests.exceptions.RequestException as e:
        return jsonify({"status": "not ready", "reason": f"connection error: {str(e)}"}), 503
    except Exception as e:
        return jsonify({"status": "not ready", "reason": f"unknown error: {str(e)}"}), 503
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)