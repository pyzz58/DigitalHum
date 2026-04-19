import threading
import json
import re
from llm_bridge import call_llm
from memory_db import save_memory, get_palace_memories

def start_evolution_thread(soul_id, old_layers, user_input, ai_response):
    """启动异步反思引擎"""
    thread = threading.Thread(target=reflect_and_memorize, args=(soul_id, old_layers, user_input, ai_response))
    thread.daemon = True
    thread.start()

def reflect_and_memorize(soul_id, old_layers, user_input, ai_response):
    """
    深夜反思算法：分析对话 -> 提炼锚点 -> 存入记忆宫殿 -> 尝试演化性格
    """
    # 1. 记忆提炼 Prompt
    reflection_prompt = f"""
你是一位深层心理分析师。请分析以下这段对话，为数字生命提取“永久记忆碎片”。

【对话上下文】
用户: {user_input}
AI: {ai_response}

【任务】
请以 JSON 格式输出以下分析结果：
1. summary: 简短的记忆摘要（50字内）。
2. anchors: 关键词列表（如：人名、地点、核心情感、重要物品）。
3. weight: 重要程度 (0.0 到 1.0)。
4. valence: 情感极性 (-1.0 极度负面, 1.0 极度正面)。
5. evolve_suggestion: 是否建议微调 L1-L6 性格层？
   - 如果建议调整，请返回：{{"layer": "Lx_xxx", "changes": {{"key": "value"}}, "reason": "演化原因"}}
   - 如果不建议调整，请返回：null

注意：只输出 JSON，不要任何废话。
"""
    try:
        raw_res = call_llm(reflection_prompt, temperature=0.3)
        # 清理可能存在的 markdown 标记
        json_str = re.search(r'\{.*\}', raw_res, re.DOTALL).group()
        data = json.loads(json_str)
        
        # 存入记忆（确保 anchors 是 list）
        anchors_list = data['anchors'] if isinstance(data['anchors'], list) else [a.strip() for a in data['anchors'].split(',')]
        save_memory(
            soul_id,
            data['summary'],
            data['weight'],
            anchors_list,          # 现在是 list
            data['valence']
        )
        print(f"✅ 记忆宫殿已录入新碎片: {data['summary']}")
        
        # --- 新增：性格演化 ---
        evolve_suggestion = data.get('evolve_suggestion')
        if evolve_suggestion and isinstance(evolve_suggestion, dict):
            # evolve_suggestion 格式示例：
            # {"layer": "L4_Emotion", "changes": {"mood_state": "excited"}, "reason": "用户分享了快乐的事"}
            layer = evolve_suggestion.get('layer')
            changes = evolve_suggestion.get('changes')
            reason = evolve_suggestion.get('reason', '记忆提炼触发')
            if layer and changes:
                from memory_db import update_soul_layer
                success = update_soul_layer(soul_id, layer, changes, reason)
                if success:
                    print(f"🔄 灵魂 {soul_id} 的 {layer} 已演化: {changes}")
                else:
                    print(f"⚠️ 演化失败: 未找到灵魂 {soul_id}")
        # ---------------------
        
    except Exception as e:
        print(f"❌ 记忆反思失败: {e}")
