from flask import Flask, request, jsonify
from werkzeug.exceptions import BadRequest
import requests
import os
import logging
import json

from azure.identity import DefaultAzureCredential
from azure.appconfiguration import AzureAppConfigurationClient
from azure.core.exceptions import ResourceNotFoundError

app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

ADAPTER_URL = os.environ.get("ADAPTER_URL", "http://llm-adapter:5000")
APP_CONFIG_ENDPOINT = os.environ.get("APP_CONFIG_ENDPOINT")
APP_CONFIG_LABEL = os.environ.get("APP_CONFIG_LABEL")

FEATURE_LANGUAGE_DETECTION = "language-detection-simple"
FEATURE_SUMMARIZATION = "summarization"


if not APP_CONFIG_ENDPOINT:
    raise RuntimeError("APP_CONFIG_ENDPOINT is not set")

credential = DefaultAzureCredential()
app_config_client = AzureAppConfigurationClient(
    base_url=APP_CONFIG_ENDPOINT,
    credential=credential,
)

def get_feature_flag(feature_name: str, label: str | None = None) -> dict | None:
    key = f".appconfig.featureflag/{feature_name}"

    try:
        setting = app_config_client.get_configuration_setting(
            key=key,
            label=label,
        )
        logger.info("Loaded feature flag key=%s label=%s", key, label)
        return json.loads(setting.value)
    except ResourceNotFoundError:
        logger.warning("Feature flag key not found: %s label=%s", key, label)
        return None
    except Exception as ex:
        logger.error("Failed to load feature flag %s: %s", feature_name, ex)
        return None

def is_feature_enabled(feature_name: str, label: str | None = None) -> bool:
    flag = get_feature_flag(feature_name, label)

    if not flag:
        return False

    enabled = bool(flag.get("enabled", False))
    logger.info("Feature '%s' enabled = %s", feature_name, enabled)
    return enabled

def get_api_user():
    return request.headers.get("X-Api-User", "anonymous")


def is_feature_enabled(feature_name: str) -> bool:
    try:
        enabled = feature_manager.is_enabled(feature_name)
        logger.info(f"Feature '{feature_name}' enabled = {enabled}")
        return enabled
    except Exception as ex:
        logger.error(f"Feature check failed for '{feature_name}': {ex}")
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