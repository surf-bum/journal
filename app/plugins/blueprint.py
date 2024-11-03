from datetime import datetime
import uuid

from  slugify import slugify
from app import storage
from app.plugins.manager import PluginManager
from app.utils import setup_logger
from app.plugins.tables import PluginSerializer

from flask import (
    Blueprint,
    render_template,
    flash,
    redirect,
    send_file,
    url_for,
    request,
)

logger = setup_logger(__name__)

api_plugins_blueprint = Blueprint("plugins_api", __name__)
ui_plugins_blueprint = Blueprint("plugins_ui", __name__)


@ui_plugins_blueprint.route("/create", methods=["POST"])
async def create_plugin():
    name = request.form["name"]

    if name:
        slugified_name = slugify(name)
        path = f"plugins/{uuid.uuid4()}/{slugified_name}/index.html"
        storage.store_file("", path)
        new_plugin = PluginSerializer(
            id=uuid.uuid4(),
            created_at=datetime.now(),
            name=name,
            path=path,
            provider="s3",
            updated_at=datetime.now(),
        )
        new_plugin = await PluginManager.create_plugin(new_plugin)
        flash(f"Plugin '{new_plugin.name}' uploaded successfully!")
    else:
        flash("Please provide name!")

    return redirect(url_for("ui.plugins_ui.list_plugins"))


@ui_plugins_blueprint.route("/<uuid:plugin_id>")
async def get_plugin(plugin_id):
    plugin = await PluginManager.get_plugin(plugin_id)
    return render_template("plugins/detail.html", plugin=plugin)

@ui_plugins_blueprint.route("/<string:plugin>/load")
async def load_plugin(plugin: str):
    return send_file(f"static/plugins/{plugin}/index.html")

@ui_plugins_blueprint.route("/partials/<string:cellId>/iframe")
async def partial_plugin_iframe(cellId: str):
    plugin = request.args.get("plugin")
    logger.debug("Loading iframe for plugin '%s' in partial request.", plugin)
    return render_template("plugins/partials/iframe.html", cell_id=cellId, plugin=plugin)

@ui_plugins_blueprint.route("/<string:plugin>/<path>")
async def load_plugin_path(plugin: str, path: str):
    return send_file(f"static/plugins/{plugin}/{path}")

@ui_plugins_blueprint.route("/")
async def list_plugins():
    plugins = await PluginManager.get_plugins()
    return render_template("plugins/list.html", plugins=plugins)


@api_plugins_blueprint.route("/<uuid:plugin_id>", methods=["DELETE"])
async def delete_plugin(plugin_id):
    plugin = await PluginManager.get_plugin(plugin_id) 
    if not plugin:
        return {"error": {"message": "Detail not found."}}, 404
    
    storage.delete_file(plugin.path)

    await PluginManager.delete_plugin(plugin.id)

    return "", 204


@api_plugins_blueprint.route("/<uuid:plugin_id>/content", methods=["GET"])
async def get_plugin_content(plugin_id):
    plugin = await PluginManager.get_plugin(plugin_id)
    if not plugin:
        return {"error": {"message": "Detail not found."}}, 404

    content = storage.retrieve_file(plugin.path)
    content = content.read().decode()

    return {"content": content or ""}


@api_plugins_blueprint.route("/<uuid:plugin_id>/content", methods=["PATCH"])
async def update_plugin_content(plugin_id):
    payload = request.get_json()
    content = payload.get("content", "")

    plugin = await PluginManager.get_plugin(plugin_id)
    if not plugin:
        return {"error": {"message": "Detail not found."}}

    content = storage.store_file(content, plugin.path)

    return "", 204
