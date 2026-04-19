#!/usr/bin/env python3
# 测试LLM调用

import sys
import os

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from llm_bridge import call_llm

if __name__ == "__main__":
    print("测试LLM调用...")
    
    # 测试林黛玉相关的问题
    test_prompts = [
        "你是林黛玉，做个自我介绍",
        "你最喜欢谁？",
        "你觉得贾宝玉怎么样？",
        "你为什么喜欢葬花？"
    ]
    
    for i, prompt in enumerate(test_prompts):
        print(f"\n测试 {i+1}: {prompt}")
        try:
            response = call_llm(prompt, temperature=0.7, max_tokens=500)
            print(f"响应: {response}")
        except Exception as e:
            print(f"错误: {e}")
    
    print("\n测试完成！")
