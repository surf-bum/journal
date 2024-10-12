import socket
import time

import pytest
from playwright.sync_api import Page


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
    from app import app

    app.config["TESTING"] = True
    yield app


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


def test_create_note(page: Page):
    page.goto("http://127.0.0.1:15000/ui/notes")

    page.get_by_role("button", name="Create note").click()
    page.wait_for_selector("text='Create a new note'")
    assert page.is_visible("text='Create a new note'")

    page.get_by_placeholder("Title").type("Foo")
    page.get_by_placeholder("Content").type("# Bar")
    page.get_by_label("Create a new note").get_by_role(
        "button", name="Create note"
    ).click()

    page.wait_for_selector("text='Note created successfully!'")
    assert page.is_visible("text='Note created successfully!'")
