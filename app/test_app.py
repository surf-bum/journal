import pytest
from playwright.sync_api import Page
import requests

from app.notes.tables import NoteSerializer
from app.utils import setup_logger

logger = setup_logger(__name__)


@pytest.fixture()
def note():
    response = requests.post("http://127.0.0.1:15000/api/v1/notes/", json={})
    assert response.status_code == 201
    yield NoteSerializer(response.json)


def test_edit_note(page: Page):
    pass
    # page.goto("http://127.0.0.1:15000/ui/notes/")

    # random_suffix = str(uuid.uuid4())
    # title = f"Test note {random_suffix}"
    # note = NoteSerializer(id=uuid.uuid4(), title=title)
    # note = await NoteManager.create_note(note)

    # page.get_by_role("button", name="Create note").click()
    # page.wait_for_selector("text='Create a new note'")
    # assert page.is_visible("text='Create a new note'")
    # random_suffix = str(uuid.uuid4())
    # title = f"Foo-{random_suffix}"
    # page.locator('input[name="title"]').type(title)
    # page.get_by_label("Create a new note").get_by_role(
    #     "button", name="Create note"
    # ).click()
    # created_successfully_alert_text = f"Note '{title}' created successfully!"
    # selector = f"text='{created_successfully_alert_text}'"
    # page.wait_for_selector(selector)
    # assert page.is_visible(selector)

    # page.get_by_role("heading", name=title).click(force=True)
    # selector = f"text='{title}'"
    # page.wait_for_selector(selector)
    # assert page.is_visible(selector)

    # # create cell
    # page.get_by_role("button", name="Create cell").click()
    # page.wait_for_selector("text='Create a new cell'")
    # assert page.is_visible("text='Create a new cell'")
    # title = f"Foo-Cell-{random_suffix}"
    # page.locator('input[name="title"]').type(title)
    # content = f"Bar-Cell-{random_suffix}"
    # page.locator('textarea[name="content"]').type(content)
    # page.locator('button[form="createCellForm"][type="submit"]').click()

    # # read cell title, content
    # selector = f"text='{title}'"
    # page.wait_for_selector(selector)
    # assert page.is_visible(selector)
    # selector = f"text='{content}'"
    # page.wait_for_selector(selector)
    # assert page.is_visible(selector)

    # # edit cell
    # page.locator('button[aria-label="Edit cell"]').click()
    # edited_content = "Edited content."
    # edit_content_textarea = page.locator('textarea[data-test-id="cellEditFormContentTextArea"]')
    # edit_content_textarea.fill("")
    # edit_content_textarea.type(edited_content)
    # page.get_by_role("button", name="Save changes").click()

    # selector = f"text='{edited_content}'"
    # page.wait_for_selector(selector)
    # assert page.is_visible(selector)
