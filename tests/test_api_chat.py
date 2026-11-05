def test_same_session_continuous(client):
    r1 = client.post("/chat", json={"session_id": "u1", "message": "你好"})
    assert r1.status_code == 200
    assert r1.json()["reply"] == "echo:你好"

    r2 = client.post("/chat", json={"session_id": "u1", "message": "再见"})
    assert r2.status_code == 200
    assert r2.json()["reply"] == "echo:再见"


def test_different_sessions_isolated(client):
    client.post("/chat", json={"session_id": "u1", "message": "A"})
    client.post("/chat", json={"session_id": "u2", "message": "B"})

    m1 = client.get("/sessions/u1/messages").json()["messages"]
    m2 = client.get("/sessions/u2/messages").json()["messages"]
    assert [m["content"] for m in m1] == ["A", "echo:A"]
    assert [m["content"] for m in m2] == ["B", "echo:B"]


def test_study_feature(client):
    r = client.post("/study/correct", json={"text": "He go to school."})
    assert r.status_code == 200
    assert "feedback" in r.json()


def test_empty_message_rejected(client):
    r = client.post("/chat", json={"session_id": "u1", "message": "   "})
    assert r.status_code == 400