#!/usr/bin/env python3
# 测试灵魂注入器

import sys
import os

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from soul_injector import generate_soul_profile_from_text

if __name__ == "__main__":
    # 测试文本 - 林黛玉的描述
    test_text = """
    林黛玉是《红楼梦》中的主要人物之一。她生性敏感，多愁善感，才华横溢。
    她说话常常带刺，但内心善良。她喜欢诗词，经常独自葬花，感叹人生无常。
    她对贾宝玉有着深厚的感情，但又常常因为小事而生气、哭泣。
    她出身于书香门第，父母早逝，寄人篱下在贾府。
    她体弱多病，常常咳嗽，但依然坚持写诗作画。
    """
    
    print("🔍 开始深度灵魂扫描...")
    profile = generate_soul_profile_from_text(test_text, "林黛玉")
    print("\n✅ 扫描完成！")
    print(f"\n📋 灵魂基本信息:")
    print(f"ID: {profile['soul_id']}")
    print(f"名称: {profile['name']}")
    print(f"创建时间: {profile['created_at']}")
    
    print("\n🧠 五层分析摘要:")
    analysis = profile['five_layer_analysis']
    print(f"基础画像: {analysis['basic_profile']['speech_style']}, {analysis['basic_profile']['mbti']}")
    print(f"心理内核: 诚实-谦逊 {analysis['psychological_core']['honesty_humility']}, 情绪性 {analysis['psychological_core']['emotionality']}")
    print(f"核心价值观: {', '.join(analysis['cognition_worldview']['core_values'])}")
    print(f"关键事件: {', '.join(analysis['memory_evolution']['key_events'])}")
    
    print("\n🎯 L1-L6 交互层:")
    layers = profile['layers']
    for layer_name, layer_data in layers.items():
        print(f"{layer_name}: {layer_data}")
    
    print("\n🎉 测试完成！")
