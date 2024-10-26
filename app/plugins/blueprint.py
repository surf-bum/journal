from datetime import datetime
import uuid
from app import storage
from app.plugins.manager import PluginManager
from app.utils import setup_logger
from app.plugins.tables import PluginSerializer

from flask import (
    Blueprint,
    render_template,
    flash,
    redirect,
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
        path = f"plugins/{uuid.uuid4()}/{name}.html"
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


@ui_plugins_blueprint.route("/")
async def list_plugins():
    plugins = await PluginManager.get_plugins()
    return render_template("plugins/list.html", plugins=plugins)
