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


def test_get_note_by_id(client):
    r = client.post("/notes/", json={"title": "Find me", "content": "Details here"})
    assert r.status_code == 201
    note_id = r.json()["id"]

    r = client.get(f"/notes/{note_id}")
    assert r.status_code == 200
    assert r.json()["title"] == "Find me"


def test_get_note_not_found(client):
    r = client.get("/notes/9999")
    assert r.status_code == 404


def test_update_note_title(client):
    r = client.post("/notes/", json={"title": "Original", "content": "Content"})
    assert r.status_code == 201
    note_id = r.json()["id"]

    r = client.put(f"/notes/{note_id}", json={"title": "Updated"})
    assert r.status_code == 200
    data = r.json()
    assert data["title"] == "Updated"
    assert data["content"] == "Content"  # unchanged


def test_update_note_content(client):
    r = client.post("/notes/", json={"title": "Title", "content": "Old content"})
    assert r.status_code == 201
    note_id = r.json()["id"]

    r = client.put(f"/notes/{note_id}", json={"content": "New content"})
    assert r.status_code == 200
    data = r.json()
    assert data["title"] == "Title"  # unchanged
    assert data["content"] == "New content"


def test_update_note_not_found(client):
    r = client.put("/notes/9999", json={"title": "Nope"})
    assert r.status_code == 404


def test_delete_note(client):
    r = client.post("/notes/", json={"title": "Delete me", "content": "Bye"})
    assert r.status_code == 201
    note_id = r.json()["id"]

    r = client.delete(f"/notes/{note_id}")
    assert r.status_code == 204

    r = client.get(f"/notes/{note_id}")
    assert r.status_code == 404


def test_delete_note_not_found(client):
    r = client.delete("/notes/9999")
    assert r.status_code == 404


def test_create_note_empty_title(client):
    r = client.post("/notes/", json={"title": "", "content": "Some content"})
    assert r.status_code == 422


def test_create_note_empty_content(client):
    r = client.post("/notes/", json={"title": "Title", "content": ""})
    assert r.status_code == 422


def test_search_notes_no_match(client):
    client.post("/notes/", json={"title": "Apple", "content": "Fruit"})
    r = client.get("/notes/search/", params={"q": "xyznonexistent"})
    assert r.status_code == 200
    assert len(r.json()) == 0
