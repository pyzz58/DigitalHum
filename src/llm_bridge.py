import os
import json
import requests
from dotenv import load_dotenv   # 需要安装 python-dotenv

load_dotenv()

API_KEY = os.getenv("DASHSCOPE_API_KEY")
BASE_URL = os.getenv("LLM_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
MODEL_NAME = os.getenv("LLM_MODEL", "qwen-plus")

def call_llm(prompt_or_messages, model=MODEL_NAME, temperature=0.7, max_tokens=2048):
    """
    统一大模型调用接口：支持单条字符串，也支持完整的对话历史(List)
    """
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    # 兼容处理：如果是字符串（如灵魂注入器），转化为 messages 格式
    if isinstance(prompt_or_messages, str):
        messages = [{"role": "user", "content": prompt_or_messages}]
    else:
        # 如果已经是多轮对话列表（如聊天界面）
        messages = prompt_or_messages
        
    data = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/chat/completions",
            headers=headers,
            json=data,
            timeout=30  # 设置30秒超时防止卡死
        )
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content']
    except Exception as e:
        print(f"大模型接口调用彻底失败: {e}")
        error_detail = response.text if 'response' in locals() and response else '无响应详情'
        print(f"API 错误详情: {error_detail}")
        return f"【系统提示：神经元连接失败，请检查网络或API_KEY是否欠费。错误信息：{e}】"

if __name__ == "__main__":
    print("正在测试千问接口连通性...")
    test_res = call_llm("你好，测试一下连接。")
    print("千问回复:", test_res)
