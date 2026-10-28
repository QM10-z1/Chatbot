from unittest.mock import MagicMock
from main import stream_chat
from config import get_settings

def test_stream_chat_params(monkeypatch):
    monkeypatch.setenv("CHATBOT_API_KEY", "sk-test")
    monkeypatch.setenv("CHATBOT_TEMPERATURE", "0.3")
    get_settings.cache_clear()

    settings = get_settings()

    
    client = MagicMock()

   
    chunk1 = MagicMock()
    chunk1.choices = [MagicMock(delta=MagicMock(content="你"))]
    chunk2 = MagicMock()
    chunk2.choices = [MagicMock(delta=MagicMock(content="好"))]

    client.chat.completions.create.return_value = [chunk1, chunk2]

    messages = [{"role": "user", "content": "你好"}]
    reply = stream_chat(client, messages)

    assert reply == "你好"

    
    client.chat.completions.create.assert_called_once_with(
        model=settings.model,
        messages=messages,
        temperature=settings.temperature,
        stream=True
    )
