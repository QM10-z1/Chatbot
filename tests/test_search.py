def test_search_messages(client):
    # 预置数据
    client.post("/chat", json={"session_id": "u1", "message": "苹果真好吃"})
    client.post("/chat", json={"session_id": "u1", "message": "香蕉也不错"})
    client.post("/chat", json={"session_id": "u2", "message": "苹果手机"})

    # 1. 不传 keyword 返回全量
    res_all = client.get("/sessions/u1/messages")
    assert len(res_all.json()["messages"]) == 4

    # 2. 传 keyword，仅返回当前会话的匹配消息
    res_kw = client.get("/sessions/u1/messages?keyword=苹果")
    msgs = res_kw.json()["messages"]
    assert len(msgs) == 2
    assert "苹果" in msgs[0]["content"]
    assert "苹果" in msgs[1]["content"]
    assert "香蕉" not in str(msgs)