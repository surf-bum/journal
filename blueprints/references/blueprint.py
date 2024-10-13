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

from config import settings
from utils import setup_logger

logger = setup_logger(__name__)

s3 = boto3.resource("s3")
s3_client = boto3.client("s3")

bucket_name = settings.S3_BUCKET


api_references_blueprint = Blueprint("references_api", __name__)
ui_references_blueprint = Blueprint("references_ui", __name__)


@ui_references_blueprint.route("/")
def index():
    references = []
    try:
        my_bucket = s3.Bucket(bucket_name)
        for file in my_bucket.objects.all():
            references.append({"key": file.key})
    except ClientError as e:
        logger.error(e)
    logger.debug("list references %s", references)
    return render_template("references/list.html", references=references)


@ui_references_blueprint.route("/<string:key>", methods=["GET"])
def download_reference(key: str):
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
def upload_reference():
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
def delete_reference(key: str):
    try:
        s3_client.delete_object(Bucket=bucket_name, Key=key)
        flash(f"Reference with key '{key}' deleted.")
        return redirect(url_for("ui.references_ui.index"))
    except ClientError as e:
        logger.error(e)
        flash(f"Reference with key '{key}' not found.")
        return redirect(url_for("ui.references_ui.index"))
