import sys
from openai import OpenAI
from config import settings

def main():
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
        
        response = client.chat.completions.create(
            model=settings.model,
            messages=messages,
            temperature=settings.temperature
        )
        
        reply = response.choices[0].message.content
        messages.append({"role": "assistant", "content": reply})
        print(f"机器人: {reply}")

if __name__ == "__main__":
    main()
