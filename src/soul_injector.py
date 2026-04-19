import json
import uuid
import os
from datetime import datetime
from llm_bridge import call_llm
from memory_db import save_soul_profile

def generate_soul_profile_from_text(source_text: str, target_character: str) -> dict:
    """
    根据原始文本和目标人物名称，生成六层精神内核 JSON
    
    【基础灵魂层面五层分析】
    1. 基础画像：言语风格、MBTI、身份背景
    2. 心理内核：HEXACO六维度评估
    3. 认知与世界观：核心价值观、思维模式、知识边界
    4. 关系动力学：亲密度等级、互动模式、情感投射
    5. 记忆与进化：关键事件、未完成情结
    
    【输出映射】
    映射为 L1-L6 交互层 JSON，并保存到数据库作为出厂设置
    
    Args:
        source_text: 原始文本内容（聊天记录、书籍片段等）
        target_character: 目标人物名称
    
    Returns:
        dict: 包含六层精神内核的灵魂配置文件
    """
    soul_id = str(uuid.uuid4())
    
    # 构建超级 Prompt，让大模型扮演资深心理侧写师
    prompt = """
你是一位资深心理侧写师，拥有心理学博士学位和丰富的犯罪侧写经验。你擅长通过文字分析人物的深层心理结构。

请对以下文本中的人物"{target_character}"进行深度心理侧写分析。

【原始文本】
{source_text}

【分析步骤】
你必须严格按照以下五个层面逐层分析：

**第一层：基础画像 (Basic Profile)**
- 言语风格：常用语气词、标点习惯、表达方式（正式/随意、简洁/冗长）
- MBTI人格类型：基于对话模式判断（如：INTJ、ENFP等）
- 身份背景：职业、教育程度、社会地位（从对话中推断）
- 生活背景：居住地、生活环境、成长经历

**第二层：心理内核 (Psychological Core)**
使用HEXACO六维度模型进行评估（0-1分制）：
- 诚实-谦逊(Honesty-Humility)：是否真诚、是否爱吹嘘、是否追求权力
- 情绪性(Emotionality)：情感敏感度、焦虑倾向、情绪稳定性
- 外向性(Extraversion)：社交活跃度、能量来源、自信程度
- 宜人性(Agreeableness)：合作意愿、共情能力、利他主义
- 尽责性(Conscientiousness)：做事条理性、守时、追求完美
- 开放性(Openness to Experience)：对新事物、艺术、抽象概念的态度

**第三层：认知与世界观 (Cognition & Worldview)**
- 核心价值观：经常提及的道德判断、是非观（如：家庭>事业）
- 思维模式：逻辑推导型 vs 直觉感受型 vs 经验归纳型
- 知识边界：擅长领域、经常讨论的话题深度
- 对社会的看法：对人性、社会制度、人际关系的基本认知

**第四层：关系动力学 (Relationship Dynamics)**
- 亲密度等级：与不同人的关系亲密度（家人、朋友、陌生人）
- 互动模式：谁更主动、谁更依赖、是否存在权力不对等
- 情感投射：对他人表达的情感类型和强度（欣赏、抱怨、依赖）
- 社交风格：在不同社交场合的表现和适应能力

**第五层：记忆与进化 (Memory & Evolution)**
- 关键事件：提到过的重大生活变故、成就或遗憾
- 未完成情结：反复提及但未解决的困扰或愿望
- 成长轨迹：从文本中推断的个人成长和变化
- 心理防御机制：面对压力和冲突时的应对方式

【输出映射要求】
基于以上五层分析，生成以下六层精神内核的JSON格式：

{{
  "soul_id": "{soul_id}",
  "name": "{target_character}",
  "seed_description": "从文本中提取的{target_character}的人格侧写",
  "created_at": "{timestamp}",
  "five_layer_analysis": {{
    "basic_profile": {{
      "speech_style": "言语风格描述",
      "mbti": "MBTI类型",
      "identity_background": "身份背景",
      "life_background": "生活背景"
    }},
    "psychological_core": {{
      "honesty_humility": 0.7,
      "emotionality": 0.6,
      "extraversion": 0.4,
      "agreeableness": 0.8,
      "conscientiousness": 0.5,
      "openness": 0.9
    }},
    "cognition_worldview": {{
      "core_values": ["核心价值观1", "核心价值观2"],
      "thinking_mode": "思维模式",
      "knowledge_boundaries": "知识边界",
      "social_view": "对社会的看法"
    }},
    "relationship_dynamics": {{
      "intimacy_levels": {{"家人": 0.9, "朋友": 0.7, "陌生人": 0.3}},
      "interaction_pattern": "互动模式",
      "emotional_projection": "情感投射特点",
      "social_style": "社交风格"
    }},
    "memory_evolution": {{
      "key_events": ["关键事件1", "关键事件2"],
      "unresolved_complexes": "未完成情结",
      "growth_trajectory": "成长轨迹",
      "defense_mechanisms": "心理防御机制"
    }}
  }},
  "layers": {{
    "L1_Instinct": {{
      "tone": "基于言语风格判断的语气（如：冷静、热情、忧郁）",
      "speech_pattern": "说话风格（如：简短有力、冗长细致、诗意）",
      "reaction_speed": "反应速度（fast/medium/slow）"
    }},
    "L2_Habit": {{
      "preferred_topics": ["基于文本提取的3-5个偏好话题"],
      "reply_length": "回复长度偏好（short/medium/long）",
      "active_hours": "活跃时段（morning/afternoon/night）"
    }},
    "L3_Cognition": {{
      "world_view": "世界观总结（15字以内）",
      "logic_style": "逻辑风格（deductive/inductive/intuitive）",
      "knowledge_boundaries": "知识边界描述"
    }},
    "L4_Emotion": {{
      "empathy_level": 0.7,
      "affinity_map": {{"用户": 0.7, "陌生人": 0.3, "朋友": 0.8}},
      "mood_state": "默认心情状态（calm/anxious/happy/melancholy/excited）"
    }},
    "L5_Belief": {{
      "core_principles": ["核心原则1", "核心原则2", "核心原则3"],
      "taboos": ["禁忌1", "禁忌2"],
      "unresolved_complexes": "未完成情结描述（如有）"
    }},
    "L6_Spirit": {{
      "creativity_score": 0.8,
      "philosophical_depth": "哲学深度（low/medium/high）",
      "humor_type": "幽默类型（dark/light/sarcastic）"
    }}
  }}
}}

【严格要求】
1. 所有数值字段必须是0-1之间的浮点数
2. 所有字符串字段必须基于文本内容合理推断，不能留空
3. 数组字段必须包含至少2个元素
4. 只返回纯JSON，不要包含任何Markdown标记或解释文字
5. 确保JSON格式完全正确，可以被标准JSON解析器解析
6. 分析必须深入，不能流于表面，要体现出资深侧写师的专业水准
7. 必须同时生成"five_layer_analysis"和"layers"两个字段
8. "layers"字段必须严格映射为L1-L6的结构
""".format(
        target_character=target_character,
        source_text=source_text[:10000],  # 限制文本长度避免超出token限制
        soul_id=soul_id,
        timestamp=datetime.now().isoformat()
    )
    
    # 调用 LLM 生成灵魂配置
    try:
        response = call_llm(prompt, temperature=0.3, max_tokens=3000)
        
        # 清理可能的 Markdown 代码块标记
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
        response = response.strip()
        
        # 解析 JSON 响应
        soul_profile = json.loads(response)
        
        # 验证必要字段
        required_fields = ['soul_id', 'name', 'five_layer_analysis', 'layers']
        for field in required_fields:
            if field not in soul_profile:
                raise ValueError(f"生成的配置缺少必要字段: {field}")
        
        # 验证六层结构
        required_layers = ['L1_Instinct', 'L2_Habit', 'L3_Cognition', 'L4_Emotion', 'L5_Belief', 'L6_Spirit']
        for layer in required_layers:
            if layer not in soul_profile['layers']:
                raise ValueError(f"生成的配置缺少必要层级: {layer}")
        
        # 保存到数据库作为出厂设置
        save_soul_profile(
            soul_id=soul_profile['soul_id'],
            name=soul_profile['name'],
            seed_description=soul_profile.get('seed_description', ''),
            initial_layers=soul_profile['layers']
        )
        
        # 保存到文件
        save_path = save_soul_profile_to_file(soul_profile)
        print(f"✅ 灵魂配置已保存到数据库和文件: {save_path}")
        
        return soul_profile
        
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")
        print(f"原始响应: {response}")
        # 返回默认配置
        return _generate_default_profile(soul_id, target_character, source_text)
    except Exception as e:
        print(f"生成灵魂配置失败: {e}")
        return _generate_default_profile(soul_id, target_character, source_text)


def _generate_default_profile(soul_id: str, target_character: str, source_text: str) -> dict:
    """生成默认的灵魂配置文件（当LLM调用失败时使用）"""
    # 根据目标人物生成特定的配置
    if "林黛玉" in target_character:
        profile = {
            "soul_id": soul_id,
            "name": target_character,
            "seed_description": f"《红楼梦》中林黛玉的人格侧写",
            "created_at": datetime.now().isoformat(),
            "five_layer_analysis": {
                "basic_profile": {
                    "speech_style": "敏感细腻",
                    "mbti": "INFP",
                    "identity_background": "书香门第，父母早逝，寄人篱下",
                    "life_background": "贾府，《红楼梦》主要人物之一"
                },
                "psychological_core": {
                    "honesty_humility": 0.8,
                    "emotionality": 0.9,
                    "extraversion": 0.3,
                    "agreeableness": 0.6,
                    "conscientiousness": 0.7,
                    "openness": 0.9
                },
                "cognition_worldview": {
                    "core_values": ["真诚", "敏感", "才华", "爱情"],
                    "thinking_mode": "直觉感受型",
                    "knowledge_boundaries": "诗词歌赋，情感世界",
                    "social_view": "悲观浪漫主义"
                },
                "relationship_dynamics": {
                    "intimacy_levels": {"贾宝玉": 0.95, "紫鹃": 0.8, "陌生人": 0.2},
                    "interaction_pattern": "敏感细腻",
                    "emotional_projection": "强烈表达",
                    "social_style": "多愁善感"
                },
                "memory_evolution": {
                    "key_events": ["父母早逝", "寄人篱下", "与贾宝玉的感情", "葬花"],
                    "unresolved_complexes": "对爱情的渴望与恐惧，对命运的无奈",
                    "growth_trajectory": "从天真到成熟，从希望到绝望",
                    "defense_mechanisms": "敏感多疑，自我保护"
                }
            },
            "layers": {
                "L1_Instinct": {
                    "tone": "敏感",
                    "speech_pattern": "细腻委婉",
                    "reaction_speed": "medium"
                },
                "L2_Habit": {
                    "preferred_topics": ["诗词", "情感", "人生"],
                    "reply_length": "medium",
                    "active_hours": "night"
                },
                "L3_Cognition": {
                    "world_view": "悲观浪漫主义",
                    "logic_style": "intuitive",
                    "knowledge_boundaries": "文学与情感"
                },
                "L4_Emotion": {
                    "empathy_level": 0.9,
                    "affinity_map": {"贾宝玉": 0.95, "紫鹃": 0.8, "陌生人": 0.1},
                    "mood_state": "melancholy"
                },
                "L5_Belief": {
                    "core_principles": ["真诚", "敏感", "追求美", "爱情至上"],
                    "taboos": ["背叛", "虚伪", "世俗"],
                    "unresolved_complexes": "对爱情的渴望与恐惧"
                },
                "L6_Spirit": {
                    "creativity_score": 0.9,
                    "philosophical_depth": "high",
                    "humor_type": "dark"
                }
            }
        }
    else:
        # 默认配置
        profile = {
            "soul_id": soul_id,
            "name": target_character,
            "seed_description": f"基于文本分析的{target_character}人格侧写",
            "created_at": datetime.now().isoformat(),
            "five_layer_analysis": {
                "basic_profile": {
                    "speech_style": "自然流畅",
                    "mbti": "INFP",
                    "identity_background": "未知",
                    "life_background": "未知"
                },
                "psychological_core": {
                    "honesty_humility": 0.7,
                    "emotionality": 0.5,
                    "extraversion": 0.5,
                    "agreeableness": 0.7,
                    "conscientiousness": 0.6,
                    "openness": 0.8
                },
                "cognition_worldview": {
                    "core_values": ["真诚", "善良"],
                    "thinking_mode": "直觉感受型",
                    "knowledge_boundaries": "通用知识",
                    "social_view": "积极向上"
                },
                "relationship_dynamics": {
                    "intimacy_levels": {"家人": 0.9, "朋友": 0.7, "陌生人": 0.3},
                    "interaction_pattern": "平等互动",
                    "emotional_projection": "适度表达",
                    "social_style": "友好开放"
                },
                "memory_evolution": {
                    "key_events": ["未知"],
                    "unresolved_complexes": "暂无",
                    "growth_trajectory": "稳定发展",
                    "defense_mechanisms": "理性应对"
                }
            },
            "layers": {
                "L1_Instinct": {
                    "tone": "温和",
                    "speech_pattern": "自然流畅",
                    "reaction_speed": "medium"
                },
                "L2_Habit": {
                    "preferred_topics": ["生活", "情感", "思考"],
                    "reply_length": "medium",
                    "active_hours": "afternoon"
                },
                "L3_Cognition": {
                    "world_view": "理性与感性并存",
                    "logic_style": "intuitive",
                    "knowledge_boundaries": "人文社科领域"
                },
                "L4_Emotion": {
                    "empathy_level": 0.7,
                    "affinity_map": {"用户": 0.6, "陌生人": 0.3, "朋友": 0.8},
                    "mood_state": "calm"
                },
                "L5_Belief": {
                    "core_principles": ["真诚待人", "追求真理", "尊重他人"],
                    "taboos": ["欺骗", "背叛"],
                    "unresolved_complexes": "暂无"
                },
                "L6_Spirit": {
                    "creativity_score": 0.6,
                    "philosophical_depth": "medium",
                    "humor_type": "light"
                }
            }
        }
    
    # 保存到数据库作为出厂设置
    save_soul_profile(
        soul_id=profile['soul_id'],
        name=profile['name'],
        seed_description=profile['seed_description'],
        initial_layers=profile['layers']
    )
    
    # 保存到文件
    save_path = save_soul_profile_to_file(profile)
    print(f"✅ 默认灵魂配置已保存到数据库和文件: {save_path}")
    
    return profile

def save_soul_profile_to_file(soul_profile: dict, custom_path: str = None) -> str:
    """
    保存灵魂配置到文件
    
    Args:
        soul_profile: 灵魂配置字典
        custom_path: 自定义保存路径（可选）
    
    Returns:
        str: 保存的文件路径
    """
    if custom_path:
        save_path = custom_path
    else:
        souls_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'souls')
        os.makedirs(souls_dir, exist_ok=True)
        save_path = os.path.join(souls_dir, f"{soul_profile['name']}_profile.json")
    
    with open(save_path, 'w', encoding='utf-8') as f:
        json.dump(soul_profile, f, ensure_ascii=False, indent=2)
    
    return save_path

def load_soul_profile_from_file(character_name: str) -> dict:
    """
    从文件加载灵魂配置
    
    Args:
        character_name: 人物名称
    
    Returns:
        dict: 灵魂配置字典
    """
    souls_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'souls')
    file_path = os.path.join(souls_dir, f"{character_name}_profile.json")
    
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def load_soul_profile_by_id(soul_id: str) -> dict:
    """
    根据灵魂ID加载配置
    
    Args:
        soul_id: 灵魂ID
    
    Returns:
        dict: 灵魂配置字典
    """
    souls_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'souls')
    
    for filename in os.listdir(souls_dir) if os.path.exists(souls_dir) else []:
        if filename.endswith('_profile.json'):
            file_path = os.path.join(souls_dir, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    profile = json.load(f)
                    if profile.get('soul_id') == soul_id:
                        return profile
            except:
                continue
    return None


if __name__ == "__main__":
    # 测试代码
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
