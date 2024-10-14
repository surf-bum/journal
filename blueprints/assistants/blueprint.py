import ollama
import requests

from flask import (
    Blueprint,
    Response,
    render_template,
    request,
)

from config import settings
from utils import get_chromadb_collection, setup_logger

logger = setup_logger(__name__)

api_assistants_blueprint = Blueprint("assistants_api", __name__)
ui_assistants_blueprint = Blueprint("assistants_ui", __name__)

MODEL_REGISTRY = {"gemma2:27b": {"name": "gemma2:27b"}, "llama3.1:8b": {"name": "llama3.1:8b"}}
model = MODEL_REGISTRY.get("gemma2:27b")


@api_assistants_blueprint.route(
    "/fake-uuid/sessions/fake-uuid/completion", methods=["POST"]
)
def prompt_assistant():
    data = request.get_json()
    prompt = data.get("prompt", "Why is the sky blue?")

    r = requests.post(
        f"http://{settings.OLLAMA_HOST}:11434/api/generate",
        json={"model": model.get("name"), "prompt": prompt},
        stream=True,
    )

    if not r.ok:
        return {"error": "Streaming request failed"}, r.status_code

    def generate():
        for chunk in r.iter_content(chunk_size=1024 * 4):
            if chunk:  # Filter out KeepAlive
                yield chunk

    return Response(generate(), mimetype="application/octet-stream")


@api_assistants_blueprint.route("/fake-uuid/sessions/fake-uuid/query", methods=["POST"])
def query_assistant():
    data = request.get_json()
    prompt = data.get("prompt")
    logger.debug("prompt %s", prompt)

    response = ollama.embeddings(prompt=prompt, model="mxbai-embed-large")

    collection = get_chromadb_collection()
    results = collection.query(query_embeddings=[response["embedding"]], n_results=1)
    data = results["documents"][0][0]

    r = requests.post(
        f"http://{settings.OLLAMA_HOST}:11434/api/generate",
        json={
            "model": model.get("name"),
            "prompt": f"Using this data: {data}. Respond to this prompt: {prompt}",
        },
        stream=True,
    )

    if not r.ok:
        return {"error": "Streaming request failed"}, r.status_code

    def generate():
        for chunk in r.iter_content(chunk_size=1024 * 4):
            if chunk:  # Filter out KeepAlive
                yield chunk

    return Response(generate(), mimetype="application/octet-stream")


@ui_assistants_blueprint.route("/", methods=["GET"])
def list_assistants():
    assistants = [model]
    return render_template("assistants/list.html", assistants=assistants)


@ui_assistants_blueprint.route("/<string:assistant>/completion", methods=["GET"])
def view_assistant_completion(assistant: str):
    return render_template("assistants/completion.html")


@ui_assistants_blueprint.route("/<string:assistant>/query", methods=["GET"])
def view_assistant_query(assistant: str):
    return render_template("assistants/query.html")
