from pathlib import Path
import sys
from app.utils import setup_logger
from flask import Blueprint, Flask, redirect, request, session, url_for
from oic import rndstr
from oic.oic import Client
from oic.utils.authn.client import CLIENT_AUTHN_METHOD
from oic.oic.message import AuthorizationResponse, RegistrationResponse

from app.assistants.blueprint import (
    api_assistants_blueprint,
    ui_assistants_blueprint,
)
from app.notes.blueprint import api_notes_blueprint, ui_notes_blueprint
from app.plugins.blueprint import api_plugins_blueprint, ui_plugins_blueprint
from app.references.blueprint import (
    api_references_blueprint,
    ui_references_blueprint,
)
from app.config import settings

logger = setup_logger(__name__)

root_folder = Path(__file__).resolve().parent
logger.debug("Adding %s to PYTHON_PATH", root_folder)
sys.path.append(str(root_folder))

flask_app = Flask(__name__, static_folder="static")
flask_app.secret_key = settings.SECRET_KEY

api_blueprint = Blueprint("api", __name__)
api_blueprint.register_blueprint(api_assistants_blueprint, url_prefix="/assistants")
api_blueprint.register_blueprint(api_notes_blueprint, url_prefix="/notes")
api_blueprint.register_blueprint(api_plugins_blueprint, url_prefix="/plugins")
api_blueprint.register_blueprint(api_references_blueprint, url_prefix="/references")

ui_blueprint = Blueprint("ui", __name__)
ui_blueprint.register_blueprint(ui_assistants_blueprint, url_prefix="/assistants")
ui_blueprint.register_blueprint(ui_notes_blueprint, url_prefix="/notes")
ui_blueprint.register_blueprint(ui_plugins_blueprint, url_prefix="/plugins")
ui_blueprint.register_blueprint(ui_references_blueprint, url_prefix="/references")

client = Client(
    client_id=settings.OIDC_CLIENT_ID, client_authn_method=CLIENT_AUTHN_METHOD
)
provider_config = client.provider_config(settings.OIDC_DISCOVERY_URI)
info = {
    "client_id": settings.OIDC_CLIENT_ID,
    "client_secret": settings.OIDC_CLIENT_SECRET,
    "redirect_uris": settings.OIDC_REDIRECT_URIS.split(","),
}
client_registration_response = RegistrationResponse(**info)
client.store_registration_info(client_registration_response)


@ui_blueprint.before_request
def require_login():
    logger.debug("sub %s", session.get("oidc_sub"))


@ui_blueprint.context_processor
def inject_oidc():
    return dict(email=session.get("oidc_email"))


@ui_blueprint.route("/oidc/login")
def oidc_login():
    logger.debug("Received authorization request.")

    nonce = rndstr()
    state = rndstr()
    logger.debug("Generated nonce '%s' and state '%s'.", nonce, state)

    authorization_request = client.construct_AuthorizationRequest(
        request_args={
            "client_id": client.client_id,
            "response_type": "code",
            "scope": ["email", "openid"],
            "nonce": nonce,
            "redirect_uri": client.registration_response["redirect_uris"][0],
            "state": state,
        },
    )
    logger.debug("Authorization request %s", authorization_request)

    authorization_url = authorization_request.request(client.authorization_endpoint)
    logger.debug("Redirecting to authorization URL '%s'.", authorization_url)

    return redirect(authorization_url)


@ui_blueprint.route("/oidc/callback")
def oidc_callback():
    query_string = request.query_string.decode()
    logger.debug("query_string %s", query_string)

    authorization_response = client.parse_response(
        AuthorizationResponse, info=query_string, sformat="urlencoded"
    )
    logger.debug(authorization_response)

    state = authorization_response.get("state")
    code = authorization_response.get("code")
    if code is None:
        return "No code provided", 400

    token_response = client.do_access_token_request(
        request_args={"code": code},
        scope=["email", "openid"],
        state=state,
    )
    if access_token := token_response.get("access_token"):
        user_info_response = client.do_user_info_request(token=access_token)
        user_info = user_info_response.to_dict()
        email = user_info.get("email")
        sub = user_info.get("sub")

        session["oidc_email"] = email
        session["oidc_sub"] = sub
        session["oidc_access_token"] = access_token

        response = redirect(url_for("ui.notes_ui.index"))
        return response
    else:
        return "Token exchange failed", 400


flask_app.register_blueprint(api_blueprint, url_prefix="/api/v1")
flask_app.register_blueprint(ui_blueprint, url_prefix="/ui")
