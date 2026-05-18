from flask import Flask, request, jsonify
from werkzeug.exceptions import BadRequest
import requests
import os

from azure.identity import DefaultAzureCredential
from azure.appconfiguration.provider import load
from featuremanagement import FeatureManager

app = Flask(__name__)

ADAPTER_URL = os.environ.get("ADAPTER_URL", "http://llm-adapter:5000")
APP_CONFIG_ENDPOINT = os.environ.get("APP_CONFIG_ENDPOINT")
APP_CONFIG_LABEL = os.environ.get("APP_CONFIG_LABEL")

FEATURE_LANGUAGE_DETECTION = "language-detection"
FEATURE_SUMMARIZATION = "summarization"


def build_feature_manager():
    if not APP_CONFIG_ENDPOINT:
        raise RuntimeError("APP_CONFIG_ENDPOINT is not set")

    config = load(
        endpoint=APP_CONFIG_ENDPOINT,
        credential=DefaultAzureCredential(),
        feature_flags_enabled=True,
    )

    fm = FeatureManager(config)

    try:
        print("Loaded feature flags:", list(fm.list_feature_flag_names()))
    except Exception as ex:
        print("Could not list feature flags:", str(ex))

    return fm


feature_manager = build_feature_manager()


def get_api_user():
    return request.headers.get("X-Api-User", "anonymous")


def is_feature_enabled(feature_name: str) -> bool:
    try:
        enabled = feature_manager.is_enabled(feature_name)
        print(f"Feature '{feature_name}' enabled = {enabled}")
        return enabled
    except Exception as ex:
        print(f"Feature check failed for '{feature_name}': {ex}")
        return False


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
        response = requests.post(f"{ADAPTER_URL}/sentiment", json={"text": text}, timeout=30)
        response.raise_for_status()
        result = response.json()

        if not isinstance(result, dict) or "sentiment" not in result:
            return jsonify({"error": "Unexpected upstream response format"}), 500

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": "Failed to get sentiment", "details": str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"}), 200


@app.route('/ready', methods=['GET'])
def ready():
    try:
        response = requests.get(f"{ADAPTER_URL}/health", timeout=2)
        if response.status_code == 200:
            return jsonify({"status": "ready"}), 200
        return jsonify({"status": "not ready"}), 503
    except Exception:
        return jsonify({"status": "not ready"}), 503


@app.route('/detect-language', methods=['POST'])
def detect_language():
    if not is_feature_enabled(FEATURE_LANGUAGE_DETECTION):
        return jsonify({"error": "Language detection is disabled"}), 403

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
        response = requests.post(f"{ADAPTER_URL}/detect-language", json={"text": text}, timeout=30)
        response.raise_for_status()
        result = response.json()

        if not isinstance(result, dict) or "language" not in result:
            return jsonify({"error": "Unexpected upstream response format"}), 500

        return jsonify(result)

    except requests.Timeout:
        return jsonify({"error": "Ollama timeout"}), 504
    except requests.RequestException as e:
        return jsonify({"error": "Failed to detect language", "details": str(e)}), 500
    except Exception as e:
        return jsonify({"error": "Failed to detect language", "details": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)