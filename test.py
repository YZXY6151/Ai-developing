# test_persona_chat.py

import requests

NLP_URL = "http://localhost:8182"
MODEL = "gentle"  # 可替换为 tsundere / energetic / cool

def create_session(persona_id):
    res = requests.post(f"{NLP_URL}/api/nlp/session/create", json={
        "persona_id": persona_id,
        "titlename": f"测试-{persona_id}",
        "user_id": "test"
    })
    return res.json()["session_id"]

def send_message(session_id, message):
    res = requests.post(f"{NLP_URL}/api/nlp/chat_with_session", json={
        "session_id": session_id,
        "user_input": message
    })
    data = res.json()
    print(f"🗨️ 用户：{message}")
    print(f"🤖 AI（{data['meta']['persona']}）回复：{data['reply']}")
    if data["meta"]["memory_used"]:
        print(f"📌 注入记忆：\n{data['meta']['memory_summary']}")
    print("-" * 40)

if __name__ == "__main__":
    for persona in ["gentle", "tsundere", "energetic", "cool"]:
        print(f"\n=== 测试 persona：{persona} ===")
        session_id = create_session(persona)
        send_message(session_id, "你好，可以介绍一下你自己吗？")
        send_message(session_id, "我今天心情不好。")
