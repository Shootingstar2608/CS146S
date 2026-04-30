def test_create_and_list_notes(client):
    payload = {"title": "Test", "content": "Hello world"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["title"] == "Test"

    r = client.get("/notes/")
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1

    r = client.get("/notes/search/")
    assert r.status_code == 200

    r = client.get("/notes/search/", params={"q": "Hello"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1


def test_get_note(client):
    r = client.post("/notes/", json={"title": "Get me", "content": "body"})
    note_id = r.json()["id"]
    r = client.get(f"/notes/{note_id}")
    assert r.status_code == 200
    assert r.json()["title"] == "Get me"


def test_get_note_not_found(client):
    r = client.get("/notes/99999")
    assert r.status_code == 404
    body = r.json()
    assert body["ok"] is False
    assert body["error"]["code"] == "NOT_FOUND"


def test_update_note(client):
    r = client.post("/notes/", json={"title": "Old", "content": "old"})
    note_id = r.json()["id"]

    r = client.put(f"/notes/{note_id}", json={"title": "New"})
    assert r.status_code == 200
    assert r.json()["title"] == "New"
    assert r.json()["content"] == "old"


def test_update_note_not_found(client):
    r = client.put("/notes/99999", json={"title": "X"})
    assert r.status_code == 404


def test_delete_note(client):
    r = client.post("/notes/", json={"title": "Del", "content": "bye"})
    note_id = r.json()["id"]

    r = client.delete(f"/notes/{note_id}")
    assert r.status_code == 204

    r = client.get(f"/notes/{note_id}")
    assert r.status_code == 404


def test_delete_note_not_found(client):
    r = client.delete("/notes/99999")
    assert r.status_code == 404


def test_create_note_validation_empty_title(client):
    r = client.post("/notes/", json={"title": "", "content": "x"})
    assert r.status_code == 422
    body = r.json()
    assert body["ok"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"


def test_extract_from_note(client):
    r = client.post(
        "/notes/",
        json={
            "title": "Extraction test",
            "content": "Hello #python #ai\n- [ ] write tests\nTODO: deploy!",
        },
    )
    note_id = r.json()["id"]

    r = client.post(f"/notes/{note_id}/extract")
    assert r.status_code == 200
    data = r.json()
    assert "python" in data["hashtags"]
    assert "ai" in data["hashtags"]
    assert any("write tests" in item for item in data["action_items"])


def test_extract_with_apply(client):
    r = client.post(
        "/notes/",
        json={"title": "Apply", "content": "- [ ] task one\n- [ ] task two"},
    )
    note_id = r.json()["id"]

    r = client.post(f"/notes/{note_id}/extract", params={"apply": "true"})
    assert r.status_code == 200

    r = client.get("/action-items/")
    descs = [a["description"] for a in r.json()]
    assert "task one" in descs
    assert "task two" in descs


def test_extract_not_found(client):
    r = client.post("/notes/99999/extract")
    assert r.status_code == 404
