import sys
from openai import OpenAI
from config import get_settings

def stream_chat(client, messages):
    """流式调用大模型并返回完整回复"""
    settings = get_settings()
    stream = client.chat.completions.create(
        model=settings.model,
        messages=messages,
        temperature=settings.temperature,
        stream=True
    )
    reply = ""
    for chunk in stream:
        delta = chunk.choices[0].delta
        if delta and delta.content:
            print(delta.content, end="", flush=True)
            reply += delta.content
    print()
    return reply

def main():
    settings = get_settings()
    client = OpenAI(
        api_key=settings.api_key.get_secret_value(),
        base_url=settings.base_url
    )

    messages = []
    print("聊天机器人已启动（输入 exit 退出）")

    while True:
        user_input = input("你: ")
        if user_input.lower() == "exit":
            break

        messages.append({"role": "user", "content": user_input})

        print("机器人: ", end="", flush=True)
        reply = stream_chat(client, messages)
        messages.append({"role": "assistant", "content": reply})

if __name__ == "__main__":
    main()
