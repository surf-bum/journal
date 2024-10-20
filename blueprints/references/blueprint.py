import boto3
from botocore.exceptions import ClientError

from flask import (
    Blueprint,
    render_template,
    flash,
    redirect,
    url_for,
    request,
    send_file,
)
import ollama
import urllib

from config import settings
from utils import get_chromadb_collection, setup_logger

logger = setup_logger(__name__)

s3 = boto3.resource("s3")
s3_client = boto3.client("s3")

bucket_name = settings.S3_BUCKET


api_references_blueprint = Blueprint("references_api", __name__)
ui_references_blueprint = Blueprint("references_ui", __name__)


@api_references_blueprint.route("/embed/<string:key>", methods=["POST"])
async def embed_reference_key(key: str):
    key = urllib.parse.unquote_plus(key)

    logger.debug("embed key %s data %s", key)
    reference = s3_client.get_object(Bucket=bucket_name, Key=key)
    file_stream = reference["Body"].read()
    document = file_stream.decode()
    logger.debug("Loaded document %s from storage.", key)

    response = ollama.embeddings(model="mxbai-embed-large", prompt=document)
    logger.debug("Generated embeddings for reference document %s", key)

    collection = get_chromadb_collection()
    embedding = response["embedding"]
    collection.upsert(ids=[key], embeddings=[embedding], documents=[document])

    return response


@api_references_blueprint.route("/unembed/<string:key>", methods=["POST"])
async def unembed_reference_key(key: str):
    key = urllib.parse.unquote_plus(key)

    collection = get_chromadb_collection()
    collection.delete(
        ids=[key],
    )

    return "", 204


@ui_references_blueprint.route("/")
async def index():
    collection = get_chromadb_collection()
    hits = collection.get(include=["metadatas"])
    hits = hits["ids"]
    logger.debug("hits %s", hits)

    references = []
    try:
        my_bucket = s3.Bucket(bucket_name)
        for file in my_bucket.objects.all():
            references.append(
                {
                    "encodedKey": urllib.parse.quote_plus(file.key),
                    "key": file.key,
                    "embedded": True if file.key in hits else False,
                }
            )
    except ClientError as e:
        logger.error(e)

    logger.debug("list references %s", references)

    return render_template("references/list.html", references=references)


@ui_references_blueprint.route("/<string:key>", methods=["GET"])
async def download_reference(key: str):
    key = urllib.parse.unquote_plus(key)

    logger.debug("download reference %s", key)
    try:
        reference = s3_client.get_object(Bucket=bucket_name, Key=key)
        file_stream = reference["Body"]
        return send_file(file_stream, as_attachment=True, download_name=key)
    except ClientError as e:
        logger.error(e)
        flash(f"Reference with key '{key}' not found.")
        return redirect(url_for("ui.references_ui.index"))


@ui_references_blueprint.route("/upload", methods=["POST"])
async def upload_reference():
    key = request.form["key"]

    try:
        file = request.files["file"]
        s3_client.put_object(Bucket=bucket_name, Key=key, Body=file)
        flash(f"Reference with key '{key}' uploaded.")
        return redirect(url_for("ui.references_ui.index"))
    except ClientError as e:
        logger.error(e)
        flash(f"Reference with key '{key}' not found.")
        return redirect(url_for("ui.references_ui.index"))


@ui_references_blueprint.route("/<string:key>/delete", methods=["GET"])
async def delete_reference(key: str):
    key = urllib.parse.unquote_plus(key)

    try:
        s3_client.delete_object(Bucket=bucket_name, Key=key)
        flash(f"Reference with key '{key}' deleted.")
        return redirect(url_for("ui.references_ui.index"))
    except ClientError as e:
        logger.error(e)
        flash(f"Reference with key '{key}' not found.")
        return redirect(url_for("ui.references_ui.index"))
