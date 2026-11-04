"""模型调用封装。测试时可 mock 本模块的 call_model / call_model_stream。"""

from typing import Iterable
from config import get_settings


def _build_client():
    from openai import OpenAI
    settings = get_settings()
    return OpenAI(
        api_key=settings.api_key.get_secret_value(),
        base_url=settings.base_url,
    )


def call_model(messages: list[dict]) -> str:
    """非流式调用，返回完整回复。"""
    client = _build_client()
    settings = get_settings()
    resp = client.chat.completions.create(
        model=settings.model,
        messages=messages,
        temperature=settings.temperature,
    )
    return resp.choices[0].message.content or ""


def call_model_stream(messages: list[dict]) -> Iterable[str]:
    """流式调用，逐块 yield 文本。"""
    client = _build_client()
    settings = get_settings()
    stream = client.chat.completions.create(
        model=settings.model,
        messages=messages,
        temperature=settings.temperature,
        stream=True,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta
        if delta and delta.content:
            yield delta.content