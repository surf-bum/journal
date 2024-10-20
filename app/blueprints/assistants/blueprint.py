import ollama
import requests

from flask import (
    Blueprint,
    Response,
    render_template,
    request,
)

from app.config import settings
from utils import get_chromadb_collection, setup_logger

logger = setup_logger(__name__)

api_assistants_blueprint = Blueprint("assistants_api", __name__)
ui_assistants_blueprint = Blueprint("assistants_ui", __name__)

MODEL_REGISTRY = {
    "gemma2:27b": {"name": "gemma2:27b"},
    "llama3.1:8b": {"name": "llama3.1:8b"},
}
model = MODEL_REGISTRY.get("gemma2:27b")


@api_assistants_blueprint.route("/fake-uuid/sessions/fake-uuid/chat", methods=["POST"])
async def prompt_assistant():
    data = request.get_json()
    messages = data.get("messages")
    if not messages:
        return {"error": {"message": "Invalid request."}}, 400

    payload = {
        "model": model.get("name"),
        "messages": messages,
    }
    logger.debug(payload)

    r = requests.post(
        f"http://{settings.OLLAMA_HOST}:11434/api/chat",
        json=payload,
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
async def query_assistant():
    data = request.get_json()
    prompt = data.get("prompt")

    response = ollama.embeddings(prompt=prompt, model="mxbai-embed-large")
    logger.debug("Generated prompt embeddings.")

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
async def list_assistants():
    assistants = [model]
    return render_template("assistants/list.html", assistants=assistants)


@ui_assistants_blueprint.route("/<string:assistant>/chat", methods=["GET"])
async def view_assistant_completion(assistant: str):
    return render_template("assistants/chat.html")


@ui_assistants_blueprint.route("/<string:assistant>/query", methods=["GET"])
async def view_assistant_query(assistant: str):
    return render_template("assistants/query.html")
