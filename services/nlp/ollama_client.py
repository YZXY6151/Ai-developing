# services/nlp/ollama_client.py

import requests

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "yi:9b-chat"  # 可换为你实际使用的模型名称

def generate_with_ollama(prompt_list):
    """
    调用本地 Ollama 模型生成回复
    """
    payload = {
        "model": MODEL_NAME,
        "messages": prompt_list,
        "stream": False
    }

    response = requests.post(OLLAMA_URL, json=payload)
    if response.status_code == 200:
        data = response.json()
        return data.get("message", {}).get("content", "")
    else:
        raise RuntimeError(f"Ollama request failed: {response.status_code} {response.text}")
