import socket
import time
import uuid
from dotenv import load_dotenv
from flask.testing import FlaskClient
import pytest

from app.utils import setup_logger

load_dotenv()


logger = setup_logger(__name__)


@pytest.fixture
def browser_context(browser):
    context = browser.new_context()
    yield context
    context.close()


@pytest.fixture
def page(browser_context):
    page = browser_context.new_page()
    yield page
    page.close()


@pytest.fixture(scope="session")
def app():
    from app.serve import flask_app

    flask_app.config["TESTING"] = True

    yield flask_app


@pytest.fixture(scope="session")
def client(app) -> FlaskClient:
    return app.test_client()


def wait_for_port(port, timeout=3):
    start_time = time.time()
    while time.time() - start_time < timeout:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            result = sock.connect_ex(("127.0.0.1", port))
            if result == 0:
                return
        logger.debug("ping")
        time.sleep(0.1)
    raise RuntimeError(f"Port {port} not open after {timeout} seconds")


@pytest.fixture(autouse=True, scope="session")
def server(app):
    import threading

    thread = threading.Thread(
        daemon=True, target=lambda: app.run(port=15000, use_reloader=False)
    )
    thread.start()

    wait_for_port(15000)
    yield


@pytest.fixture()
def random_suffix():
    yield str(uuid.uuid4())
