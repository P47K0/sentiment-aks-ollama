from flask import Flask, request, jsonify
import requests
import os
import json
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


app = Flask(__name__)

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://ollama-service:11434/api/generate")
MODEL = os.environ.get("MODEL", "phi3:mini")

def get_prompt_template():
    return os.environ.get("PROMPT_TEMPLATE", "")

def get_language_prompt_template():
    return os.getenv("LANGUAGE_PROMPT_TEMPLATE", "")

@app.route('/sentiment', methods=['POST'])
def analyze_sentiment():
    data = request.get_json()
    text = data.get("text", "").strip()
    
    prompt_template = get_prompt_template()

    if not text:
        return jsonify({"error": "No text provided"}), 400

    if not prompt_template:
        logger.error("PROMPT_TEMPLATE not found in environment")
        return jsonify({"error": "Prompt configuration missing"}), 500

    prompt = prompt_template.format(text=text)

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "temperature": 0.0,
        "max_tokens": 150
    }

    try:
        response = requests.post(f"{OLLAMA_URL.rstrip('/')}/api/generate", json=payload, timeout=60)
        response.raise_for_status()
        
        raw_output = response.json().get("response", "").strip()
        logger.info(f"Raw Ollama response: {raw_output[:500]}...")   # Log first 500 chars

        # Try to parse JSON
        try:
            if '{' in raw_output and '}' in raw_output:
                # Extract JSON part if there's extra text
                json_start = raw_output.find('{')
                json_end = raw_output.rfind('}') + 1
                json_part = raw_output[json_start:json_end]
                result = json.loads(json_part)
            else:
                result = json.loads(raw_output)
            
            logger.info(f"Successfully parsed result: {result}")
            return jsonify(result)

        except json.JSONDecodeError as je:
            logger.error(f"JSON decode error: {je}")
            logger.error(f"Failed to parse raw output: {raw_output}")
            # Fallback with more balanced defaults
            result = {
                "sentiment": "NEUTRAL",
                "positive": 0.35,
                "neutral": 0.35,
                "negative": 0.3
            }
            return jsonify(result)

    except requests.exceptions.Timeout:
        logger.error("Request to Ollama timed out")
        return jsonify({"error": "Ollama request timed out"}), 504
    except requests.exceptions.RequestException as e:
        logger.error(f"Request exception: {e}")
        return jsonify({"error": "Failed to communicate with Ollama", "details": str(e)}), 502
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({"error": "Internal error in adapter", "details": str(e)}), 500


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


@app.route('/detect-language', methods=['POST'])
def detect_language():
    data = request.get_json()
    text = data.get("text", "").strip()

    prompt_template = get_language_prompt_template()

    if not text:
        return jsonify({"error": "No text provided"}), 400

    if not prompt_template:
        logger.error("LANGUAGE_PROMPT_TEMPLATE not found in environment")
        return jsonify({"error": "Prompt configuration missing"}), 500

    prompt = prompt_template.format(text=text)

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "temperature": 0.0,
        "format": {
            "type": "object",
            "properties": {
                "language": {"type": "string"}
            },
            "required": ["language"]
        }
    }

    try:
        response = requests.post(f"{OLLAMA_URL.rstrip('/')}/api/generate", json=payload, timeout=60)
        response.raise_for_status()

        raw_output = response.json().get("response", "").strip()
        result = json.loads(raw_output)

        if "language" not in result:
            return jsonify({"error": "Unexpected upstream response format"}), 500

        return jsonify(result)

    except requests.exceptions.Timeout:
        return jsonify({"error": "Ollama request timed out"}), 504
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Failed to communicate with Ollama", "details": str(e)}), 502
    except json.JSONDecodeError as e:
        return jsonify({"error": "Failed to parse Ollama response", "details": str(e)}), 500
    except Exception as e:
        return jsonify({"error": "Internal error in adapter", "details": str(e)}), 500