def test_list_sessions_and_messages(client):
    client.post("/chat", json={"session_id": "u1", "message": "hi"})
    sessions = client.get("/sessions").json()["sessions"]
    assert "u1" in sessions

    msgs = client.get("/sessions/u1/messages").json()["messages"]
    assert len(msgs) == 2


def test_delete_clears_history(client):
    client.post("/chat", json={"session_id": "u1", "message": "hi"})
    d = client.delete("/sessions/u1")
    assert d.status_code == 200

    r = client.get("/sessions/u1/messages")
    assert r.status_code == 404


def test_nonexistent_session_404(client):
    assert client.get("/sessions/nope/messages").status_code == 404
    assert client.delete("/sessions/nope").status_code == 404