import pytest
import requests

from playwright.sync_api import Page

from app.notes.serializers import Note


@pytest.fixture()
def note(random_suffix):
    response = requests.post("http://127.0.0.1:15000/api/v1/notes/", json={"title": f"Test note {random_suffix}"})
    assert response.status_code == 201
    note = Note(**response.json())
    yield note

class TestNotesAPI:
    def test_delete_note(self, note):
        response = requests.delete("http://127.0.0.1:15000/api/v1/notes/fake-uuid")
        assert response.status_code == 404

        response = requests.get(f"http://127.0.0.1:15000/api/v1/notes/{note.id}")
        assert response.status_code == 200

        response = requests.delete(f"http://127.0.0.1:15000/api/v1/notes/{note.id}")
        assert response.status_code == 204

        response = requests.get(f"http://127.0.0.1:15000/api/v1/notes/{note.id}")
        assert response.status_code == 404

    def test_patch_note(self, note, random_suffix):
        response = requests.patch(f"http://127.0.0.1:15000/api/v1/notes/{note.id}", json={})
        assert response.status_code == 400

        title = f"Test note {random_suffix} patched"
        response = requests.patch(f"http://127.0.0.1:15000/api/v1/notes/{note.id}", json={"title": title})
        assert response.status_code == 200
        assert response.json()["title"] == title

    def test_post_note(self, random_suffix):
        response = requests.post("http://127.0.0.1:15000/api/v1/notes/", json={})
        assert response.status_code == 400

        title = f"Test note {random_suffix}"
        response = requests.post("http://127.0.0.1:15000/api/v1/notes/", json={"title": title})
        assert response.status_code == 201
        assert response.json()["title"] == title

 

class TestNotesUI:
    def test_create_note(self, page: Page, random_suffix: str):
        page.goto("http://127.0.0.1:15000/ui/notes/")
        
        page.get_by_role("button", name="Create note").click()
        page.wait_for_selector("text='Create a new note'")
        assert page.is_visible("text='Create a new note'")
        title = f"Foo-{random_suffix}"
        page.locator('input[name="title"]').type(title)
        page.get_by_label("Create a new note").get_by_role(
            "button", name="Create note"
        ).click()
        created_successfully_alert_text = f"Note '{title}' created successfully!"
        selector = f"text='{created_successfully_alert_text}'"
        page.wait_for_selector(selector)
        assert page.is_visible(selector)

        page.get_by_role("heading", name=title).click(force=True)
        selector = f"text='{title}'"
        page.wait_for_selector(selector)
        assert page.is_visible(selector)

    def test_edit_note(self, note, page: Page, random_suffix: str):
        page.goto(f"http://127.0.0.1:15000/ui/notes/{note.id}")
        
        title = note.title
        page.get_by_role("heading", name=title).click(force=True)
        selector = f"text='{title}'"
        page.wait_for_selector(selector)
        assert page.is_visible(selector)
        page.get_by_role("button", name="Edit note").click()
        title = f"{title} edited."
        page.locator('input[id="noteEditFormTitleInput"][name="title"]').fill("")
        page.locator('input[id="noteEditFormTitleInput"][name="title"]').type(title)
        page.get_by_role("button", name="Edit note").click()
        
        selector = f"text='{title}'"
        page.wait_for_selector(selector)
        assert page.is_visible(selector)