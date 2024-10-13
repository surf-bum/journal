import ollama
import requests

from flask import (
    Blueprint,
    Response,
    render_template,
    request,
)

from utils import get_chromadb_collection, setup_logger

logger = setup_logger(__name__)

api_assistants_blueprint = Blueprint("assistants_api", __name__)
ui_assistants_blueprint = Blueprint("assistants_ui", __name__)


@api_assistants_blueprint.route(
    "/fake-uuid/sessions/fake-uuid/completion", methods=["POST"]
)
def prompt_assistant():
    data = request.get_json()
    prompt = data.get("prompt", "Why is the sky blue?")

    r = requests.post(
        "http://127.0.0.1:11434/api/generate",
        json={"model": "llama3.1", "prompt": prompt},
        stream=True,
    )

    if not r.ok:
        return {"error": "Streaming request failed"}, 500

    def generate():
        for chunk in r.iter_content(chunk_size=1024 * 32):
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
        "http://127.0.0.1:11434/api/generate",
        json={
            "model": "llama3.1",
            "prompt": f"Using this data: {data}. Respond to this prompt: {prompt}",
        },
        stream=True,
    )

    if not r.ok:
        return {"error": "Streaming request failed"}, 500

    def generate():
        for chunk in r.iter_content(chunk_size=1024 * 32):
            if chunk:  # Filter out KeepAlive
                yield chunk

    return Response(generate(), mimetype="application/octet-stream")


@ui_assistants_blueprint.route("/", methods=["GET"])
def list_assistants():
    assistants = [{"name": "llama3.1"}]
    return render_template("assistants/list.html", assistants=assistants)


@ui_assistants_blueprint.route("/<string:assistant>/completion", methods=["GET"])
def view_assistant_completion(assistant: str):
    return render_template("assistants/completion.html")


@ui_assistants_blueprint.route("/<string:assistant>/query", methods=["GET"])
def view_assistant_query(assistant: str):
    return render_template("assistants/query.html")
