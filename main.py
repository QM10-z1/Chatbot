import openai
from config import get_config

cfg = get_config()
client = openai.OpenAI(api_key=cfg["api_key"], base_url=cfg["base_url"])

history = []

print("开始多轮对话（输入 'exit' 退出）")
while True:
    user_input = input("你: ")
    if user_input.lower() == "exit":
        break
    
    history.append({"role": "user", "content": user_input})
    
    response = client.chat.completions.create(
        model=cfg["model"],
        messages=history,
        stream=False
    )
    
    answer = response.choices[0].message.content
    history.append({"role": "assistant", "content": answer})
    
    print(f"AI: {answer}")
