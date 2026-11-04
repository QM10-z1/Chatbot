from unittest.mock import MagicMock
import app.llm as llm

def test_stream_returns_content_and_saves(client):
    with client.stream(
        "POST", "/chat/stream", json={"session_id": "u1", "message": "你好"}
    ) as resp:
        assert resp.status_code == 200
        body = "".join(resp.iter_text())

    assert "echo:你好" in body

    msgs = client.get("/sessions/u1/messages").json()["messages"]
    assert msgs[-1] == {"role": "assistant", "content": "echo:你好"}


def test_model_receives_stream_true(monkeypatch):
    # 1. 伪造一个 OpenAI 的客户端
    fake_client = MagicMock()
    fake_client.chat.completions.create.return_value = []
    
    # 2. 替换掉真实的建客户端函数
    monkeypatch.setattr(llm, "_build_client", lambda: fake_client)
    
    # 3. 直接调用真实的底层函数（这会触发 fake_client）
    list(llm.call_model_stream([{"role": "user", "content": "hi"}]))
    
    # 4. 抓取底层 create 函数收到的参数，断言确实传了 stream=True
    kwargs = fake_client.chat.completions.create.call_args.kwargs
    assert kwargs["stream"] is True