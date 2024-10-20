import socket
import time
import uuid

import pytest
from playwright.sync_api import Page

from utils import setup_logger

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


@pytest.fixture(scope="module")
def app():
    from app.serve import flask_app

    flask_app.config["TESTING"] = True
    
    yield flask_app


@pytest.fixture(scope="module")
def client(app):
    return app.test_client()


def wait_for_port(port, timeout=3):
    start_time = time.time()
    while time.time() - start_time < timeout:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            result = sock.connect_ex(("127.0.0.1", port))
            if result == 0:
                return
        print("ping")
        time.sleep(0.1)
    raise RuntimeError(f"Port {port} not open after {timeout} seconds")


@pytest.fixture(autouse=True, scope="module")
def server(app):
    import threading

    thread = threading.Thread(
        daemon=True, target=lambda: app.run(port=15000, use_reloader=False)
    )
    thread.start()

    wait_for_port(15000)
    yield


def test_create_and_read_note(page: Page):
    # create
    page.goto("http://127.0.0.1:15000/ui/notes")

    page.get_by_role("button", name="Create note").click()
    page.wait_for_selector("text='Create a new note'")
    assert page.is_visible("text='Create a new note'")

    random_suffix = str(uuid.uuid4())
    title = f"Foo-{random_suffix}"
    page.locator('input[name="title"]').type(title)
    content = f"# Bar-{random_suffix}"
    page.locator('textarea[name="content"]').type(content)
    page.get_by_label("Create a new note").get_by_role(
        "button", name="Create note"
    ).click()

    created_successfully_alert_text = f"Note '{title}' created successfully!"
    selector = f"text='{created_successfully_alert_text}'"
    page.wait_for_selector(selector)
    assert page.is_visible(selector)

    # read
    page.get_by_role("heading", name=title).click(force=True)
    selector = f"text='{title}'"
    page.wait_for_selector(selector)
    assert page.is_visible(selector)

    # edit
    page.get_by_role("button", name="Edit").click()
    edited_content = "Edited content."
    edit_content_textarea = page.locator('textarea[id="noteContentTextArea"]')
    edit_content_textarea.fill("")
    edit_content_textarea.type(edited_content)
    page.get_by_role("button", name="Save changes").click()

    selector = f"text='{edited_content}'"
    page.wait_for_selector(selector)
    assert page.is_visible(selector)
