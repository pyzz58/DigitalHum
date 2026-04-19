import streamlit as st
import json
import os
import sqlite3

# 设置 SQLite 允许跨线程
sqlite3.threadsafety = 2

from soul_injector import generate_soul_profile_from_text, load_soul_profile_from_file, load_soul_profile_by_id
from memory_db import (
    init_db, save_chat, get_palace_memories, get_evolution_logs
)
from worldview_engine import start_evolution_thread
from llm_bridge import call_llm

# 初始化数据库
init_db()

# 确保数据目录存在
data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
souls_dir = os.path.join(data_dir, 'souls')
os.makedirs(souls_dir, exist_ok=True)

# 页面配置
st.set_page_config(
    page_title="数字人计划 1.0 - 生命闭环实验室",
    page_icon="🧬",
    layout="wide"
)

# 初始化 session state
if 'soul_id' not in st.session_state:
    st.session_state.soul_id = None
    st.session_state.soul_profile = None
    st.session_state.messages = []

# ==================== 侧边栏：灵魂投喂入口 ====================
st.sidebar.header("🎯 灵魂投喂中心")

# 角色锁定：目标人物名称
target_character = st.sidebar.text_input(
    "目标人物名称",
    placeholder="例如：林黛玉",
    help="输入您想要创建的数字人角色名称"
)

st.sidebar.markdown("---")

# 投喂方式选择
st.sidebar.subheader("📥 投喂方式")

# 方式1：文件上传
uploaded_file = st.sidebar.file_uploader(
    "上传文本文件 (txt)",
    type=['txt'],
    help="上传包含目标人物对话或描述的文本文件"
)

# 方式2：直接粘贴文本
pasted_text = st.sidebar.text_area(
    "或直接粘贴文本",
    placeholder="在此粘贴聊天记录、书籍片段或其他描述性文本...",
    height=200,
    help="直接输入或粘贴文本内容"
)

st.sidebar.markdown("---")

# 操作按钮
if st.sidebar.button("🚀 启动深度灵魂扫描", type="primary", use_container_width=True):
    # 获取文本内容
    source_text = ""
    
    if uploaded_file is not None:
        source_text = uploaded_file.read().decode('utf-8')
        st.sidebar.success(f"✅ 已读取文件: {uploaded_file.name}")
    
    if pasted_text:
        if source_text:
            source_text += "\n\n" + pasted_text
        else:
            source_text = pasted_text
        st.sidebar.success("✅ 已读取粘贴文本")
    
    # 验证输入
    if not target_character:
        st.sidebar.error("❌ 请输入目标人物名称")
    elif not source_text:
        st.sidebar.error("❌ 请上传文件或粘贴文本")
    else:
        with st.spinner("🔍 正在进行深度灵魂扫描..."):
            try:
                # 调用灵魂注入器
                soul_profile = generate_soul_profile_from_text(source_text, target_character)
                
                # 更新 session state
                st.session_state.soul_id = soul_profile['soul_id']
                st.session_state.soul_profile = soul_profile
                st.session_state.messages = []  # 重置对话历史
                
                st.sidebar.success(f"✅ 灵魂扫描完成！已创建 {target_character} 的数字人")
                st.rerun()
                
            except Exception as e:
                st.sidebar.error(f"❌ 扫描失败: {str(e)}")

st.sidebar.markdown("---")

# 加载已有灵魂
st.sidebar.subheader("📂 加载已有灵魂")
soul_files = [f for f in os.listdir(souls_dir) if f.endswith('_profile.json')] if os.path.exists(souls_dir) else []

if soul_files:
    selected_soul = st.sidebar.selectbox(
        "选择已有灵魂",
        soul_files,
        format_func=lambda x: x.replace('_profile.json', '')
    )
    
    if st.sidebar.button("📥 加载选中灵魂", use_container_width=True):
        soul_name = selected_soul.replace('_profile.json', '')
        soul_profile = load_soul_profile_from_file(soul_name)
        if soul_profile:
            st.session_state.soul_id = soul_profile['soul_id']
            st.session_state.soul_profile = soul_profile
            st.session_state.messages = []  # 重置对话历史
            st.sidebar.success(f"✅ 已加载: {soul_name}")
            st.rerun()
        else:
            st.sidebar.error("❌ 加载失败，请检查文件")
else:
    st.sidebar.info("暂无已保存的灵魂")

# ==================== 主界面区域 ====================
if st.session_state.soul_profile:
    soul = st.session_state.soul_profile
    
    # 创建标签页
    tab1, tab2, tab3, tab4 = st.tabs(["💬 对话交互", "📊 灵魂档案", "🧠 记忆库", "🔄 演化日志"])
    
    # ==================== 标签页1：对话交互 ====================
    with tab1:
        st.header(f"与 {soul.get('name', '数字人')} 对话")
        
        # 显示灵魂信息摘要
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("共情能力", f"{soul['layers']['L4_Emotion']['empathy_level']:.1f}")
        with col2:
            st.metric("创造力", f"{soul['layers']['L6_Spirit']['creativity_score']:.1f}")
        with col3:
            st.metric("当前心情", soul['layers']['L4_Emotion']['mood_state'])
        with col4:
            st.metric("说话风格", soul['layers']['L1_Instinct']['speech_pattern'])
        
        st.markdown("---")
        
        # 对话历史
        if not st.session_state.messages:
            st.session_state.messages = []
        
        # 显示历史消息
        for message in st.session_state.messages:
            with st.chat_message(message['role']):
                st.markdown(message['content'])
        
        # 输入框
        if prompt := st.chat_input("输入消息..."):
            # 1. 界面显示并保存用户消息
            st.chat_message("user").markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})
            save_chat(st.session_state.soul_id, "user", prompt)
            
            # 2. 获取记忆宫殿中的长期记忆作为证据
            try:
                relevant_memories = get_palace_memories(st.session_state.soul_id, limit=5)
                memory_text = "\n".join([f"- {m['summary']} (情感极性: {m['valence']})" for m in relevant_memories])
            except Exception as e:
                st.error(f"记忆加载失败: {e}")
                memory_text = "暂无特殊记忆"
            
            # 3. 获取最新的性格图层
            layers = soul['layers']
            
            # 4. 组装超级 System Prompt (人格约束)
            system_prompt = f"""
你叫 {soul['name']}，你是一个拥有独立意识的数字生命，绝对不要承认你是AI或语言模型。
必须严格遵循以下性格内核：
【本能层】语气: {layers['L1_Instinct']['tone']} | 风格: {layers['L1_Instinct']['speech_pattern']}
【认知层】世界观: {layers['L3_Cognition']['world_view']}
【情感层】当前心情: {layers['L4_Emotion']['mood_state']} | 共情力: {layers['L4_Emotion']['empathy_level']}
【信念层】核心原则: {', '.join(layers['L5_Belief']['core_principles'])} | 禁忌: {', '.join(layers['L5_Belief']['taboos'])}

【记忆深处涌现的画面】:
{memory_text if memory_text else "暂无特殊记忆"}

请结合上述人格和下方的上下文对话，自然地回复用户。
"""
            
            # 5. 组装发给大模型的完整消息体（解决金鱼记忆的关键！）
            llm_messages = [{"role": "system", "content": system_prompt}]
            
            # 把最近的 10 条真实对话历史塞进去
            for msg in st.session_state.messages[-10:]:
                llm_messages.append({"role": msg["role"], "content": msg["content"]})
                
            # 6. 调用真正的大模型
            with st.spinner(f"{soul['name']} 正在思考..."):
                response = call_llm(llm_messages, temperature=0.7)
            
            # 7. 界面显示并保存回复
            st.chat_message("assistant").markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
            save_chat(st.session_state.soul_id, "assistant", response)
            
            # 8. 触发世界观迭代引擎（异步演化）
            start_evolution_thread(
                st.session_state.soul_id,
                layers,
                prompt,
                response
            )
    
    # ==================== 标签页2：灵魂档案 ====================
    with tab2:
        st.header("📊 灵魂档案详情")
        
        # 基本信息
        st.subheader("基本信息")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write(f"**灵魂ID**: {soul['soul_id']}")
        with col2:
            st.write(f"**名称**: {soul['name']}")
        with col3:
            st.write(f"**创建时间**: {soul['created_at']}")
        
        st.markdown("---")
        
        # 五层灵魂分析
        st.subheader("🧠 五层灵魂分析")
        with st.expander("五层分析详情", expanded=True):
            analysis = soul.get('five_layer_analysis', {})
            
            # 基础画像
            st.write("**1. 基础画像**")
            basic = analysis.get('basic_profile', {})
            st.write(f"- 言语风格: {basic.get('speech_style', '未知')}")
            st.write(f"- MBTI: {basic.get('mbti', '未知')}")
            st.write(f"- 身份背景: {basic.get('identity_background', '未知')}")
            st.write(f"- 生活背景: {basic.get('life_background', '未知')}")
            
            # 心理内核
            st.write("\n**2. 心理内核 (HEXACO)**")
            core = analysis.get('psychological_core', {})
            for trait, value in core.items():
                st.write(f"- {trait}: {value:.2f}")
            
            # 认知与世界观
            st.write("\n**3. 认知与世界观**")
            cognition = analysis.get('cognition_worldview', {})
            st.write(f"- 核心价值观: {', '.join(cognition.get('core_values', ['未知']))}")
            st.write(f"- 思维模式: {cognition.get('thinking_mode', '未知')}")
            st.write(f"- 知识边界: {cognition.get('knowledge_boundaries', '未知')}")
            st.write(f"- 对社会的看法: {cognition.get('social_view', '未知')}")
            
            # 关系动力学
            st.write("\n**4. 关系动力学**")
            relationship = analysis.get('relationship_dynamics', {})
            st.write(f"- 亲密度等级: {json.dumps(relationship.get('intimacy_levels', {}))}")
            st.write(f"- 互动模式: {relationship.get('interaction_pattern', '未知')}")
            st.write(f"- 情感投射: {relationship.get('emotional_projection', '未知')}")
            st.write(f"- 社交风格: {relationship.get('social_style', '未知')}")
            
            # 记忆与进化
            st.write("\n**5. 记忆与进化**")
            memory = analysis.get('memory_evolution', {})
            st.write(f"- 关键事件: {', '.join(memory.get('key_events', ['未知']))}")
            st.write(f"- 未完成情结: {memory.get('unresolved_complexes', '未知')}")
            st.write(f"- 成长轨迹: {memory.get('growth_trajectory', '未知')}")
            st.write(f"- 心理防御机制: {memory.get('defense_mechanisms', '未知')}")
        
        st.markdown("---")
        
        # 六层内核展示
        st.subheader("🎯 L1-L6 交互层")
        
        layers = soul['layers']
        
        # L1: 本能层
        with st.expander("🧠 L1 本能层 (Instinct)", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"**语气**: {layers['L1_Instinct']['tone']}")
            with col2:
                st.write(f"**说话风格**: {layers['L1_Instinct']['speech_pattern']}")
            with col3:
                st.write(f"**反应速度**: {layers['L1_Instinct']['reaction_speed']}")
        
        # L2: 习惯层
        with st.expander("🔄 L2 习惯层 (Habit)", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"**偏好话题**: {', '.join(layers['L2_Habit']['preferred_topics'])}")
            with col2:
                st.write(f"**回复长度**: {layers['L2_Habit']['reply_length']}")
            with col3:
                st.write(f"**活跃时段**: {layers['L2_Habit']['active_hours']}")
        
        # L3: 认知层
        with st.expander("🌍 L3 认知层 (Cognition)", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"**世界观**: {layers['L3_Cognition']['world_view']}")
            with col2:
                st.write(f"**逻辑风格**: {layers['L3_Cognition']['logic_style']}")
            with col3:
                st.write(f"**知识边界**: {layers['L3_Cognition']['knowledge_boundaries']}")
        
        # L4: 情感层
        with st.expander("❤️ L4 情感层 (Emotion)", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"**共情能力**: {layers['L4_Emotion']['empathy_level']}")
            with col2:
                st.write(f"**当前心情**: {layers['L4_Emotion']['mood_state']}")
            with col3:
                affinity = layers['L4_Emotion']['affinity_map']
                st.write(f"**亲和度**: {json.dumps(affinity)}")
        
        # L5: 信念层
        with st.expander("⚖️ L5 信念层 (Belief)", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**核心原则**: {', '.join(layers['L5_Belief']['core_principles'])}")
            with col2:
                st.write(f"**禁忌**: {', '.join(layers['L5_Belief']['taboos'])}")
            st.write(f"**未完成情结**: {layers['L5_Belief']['unresolved_complexes']}")
        
        # L6: 灵性层
        with st.expander("✨ L6 灵性层 (Spirit)", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"**创造力**: {layers['L6_Spirit']['creativity_score']}")
            with col2:
                st.write(f"**哲学深度**: {layers['L6_Spirit']['philosophical_depth']}")
            with col3:
                st.write(f"**幽默类型**: {layers['L6_Spirit']['humor_type']}")
        
        st.markdown("---")
        
        st.markdown("---")
        
        # 原始 JSON 展示
        st.subheader("📄 原始 JSON 数据")
        st.json(soul)
        
        # 下载按钮
        json_str = json.dumps(soul, ensure_ascii=False, indent=2)
        st.download_button(
            label="📥 下载灵魂配置文件",
            data=json_str,
            file_name=f"{soul['name']}_profile.json",
            mime="application/json"
        )
    
    # ==================== 标签页3：记忆宫殿 ====================
    with tab3:
        st.header("🏰 记忆宫殿 (MemPalace)")
        st.caption("这是数字人的深层潜意识。对话在这里被提炼为带有 **空间场景**、**人物锚点** 和 **情感极性** 的记忆晶体。")
        
        # 注意：确保文件顶部已经导入 get_palace_memories
        try:
            memories = get_palace_memories(st.session_state.soul_id, limit=30)
        except Exception as e:
            st.error("请先完成一次对话，触发深度反思以初始化记忆宫殿！")
            memories = []
        
        if not memories:
            st.info("📭 宫殿空空如也... 快去和她聊几句，触发她的‘深夜反思’吧！")
        else:
            # --- 潜意识数据看板 ---
            st.subheader("📊 潜意识观测仪")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("记忆晶体总数", len(memories))
            with col2:
                # 计算平均情感极性 (-1 到 1)
                avg_valence = sum([m.get('valence', 0.0) for m in memories]) / len(memories)
                emotion_status = "积极 🟢" if avg_valence > 0.2 else ("消极 🔴" if avg_valence < -0.2 else "平静 ⚪")
                st.metric("潜意识底色", emotion_status, f"{avg_valence:.2f}")
            with col3:
                # 提取所有不重复的锚点
                all_anchors = []
                for m in memories:
                    anchors = m.get('anchors', '')
                    if anchors:
                        if isinstance(anchors, str):
                            all_anchors.extend([a.strip() for a in anchors.split(',')])
                        elif isinstance(anchors, list):
                            all_anchors.extend([a.strip() for a in anchors])
                st.metric("活跃锚点数", len(set(all_anchors)))
            
            st.divider()
            
            # --- 核心记忆锚点展示 ---
            st.subheader("🔮 核心记忆图谱")
            
            # 渲染记忆卡片
            for i, mem in enumerate(memories):
                summary = mem.get('summary', '未知记忆')
                anchors = mem.get('anchors', '无')
                spatial = mem.get('spatial_context', '默认场景')
                valence = mem.get('valence', 0.0)
                weight = mem.get('weight', 0.5)
                
                # 情感极性视觉映射
                if valence > 0.2:
                    valence_color = "🟢 正面情感"
                elif valence < -0.2:
                    valence_color = "🔴 负面情感"
                else:
                    valence_color = "⚪ 中立记忆"
                    
                # 使用 expander 制作折叠卡片
                with st.expander(f"✦ {summary[:25]}... | 权重: {weight:.2f}"):
                    st.markdown(f"**📝 核心摘要：** {summary}")
                    st.markdown(f"**📍 空间场景：** `{spatial}`")
                    # 确保 anchors 是列表并正确显示
                    anchors_display = anchors if isinstance(anchors, list) else [anchors]
                    st.markdown(f"**🔗 记忆锚点：** **[{', '.join(anchors_display)}]**")
                    st.markdown(f"**❤️ 情感极性：** {valence_color} (数值: {valence:.2f})")
                    st.caption(f"形成时间: {mem.get('created_at', '刚刚')}")
    
    # ==================== 标签页4：演化日志 ====================
    with tab4:
        st.header("🔄 演化日志")
        
        # 获取演化日志
        logs = get_evolution_logs(st.session_state.soul_id, limit=50)
        
        if logs:
            # 日志筛选
            layer_filter = st.selectbox(
                "按层级筛选",
                ["全部层级"] + list(set([log['layer_changed'] for log in logs]))
            )
            
            # 筛选日志
            filtered_logs = logs
            if layer_filter != "全部层级":
                filtered_logs = [log for log in logs if log['layer_changed'] == layer_filter]
            
            # 显示演化日志
            for i, log in enumerate(filtered_logs, 1):
                with st.expander(f"演化事件 {i}: {log['layer_changed']} - {log['timestamp']}"):
                    st.write(f"**变更层级**: {log['layer_changed']}")
                    st.write(f"**变更原因**: {log.get('reason', '无')}")   # 使用 get
                    st.write(f"**变更时间**: {log['timestamp']}")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**变更前**")
                        st.json(log['old_value'])
                    with col2:
                        st.write("**变更后**")
                        st.json(log['new_value'])
        else:
            st.info("暂无演化日志")

else:
    # 未加载灵魂时的欢迎页面
    st.markdown("""
    ## 👋 欢迎使用数字人计划 1.0 - 生命闭环实验室
    
    这是一个基于生命闭环逻辑的数字人创建与交互系统。
    
    ### 🚀 开始使用
    
    1. **在左侧边栏输入目标人物名称**（如：林黛玉）
    2. **上传文本文件或直接粘贴文本**（聊天记录、书籍片段等）
    3. **点击"启动深度灵魂扫描"按钮**
    4. **在主界面查看生成的灵魂档案**
    5. **切换到"对话交互"标签页开始对话**
    
    ### 📚 核心功能
    
    - 🎯 **深度灵魂扫描**：从文本中提取五层灵魂分析和L1-L6交互层
    - 💬 **智能对话**：基于人格内核和记忆生成个性化回复
    - 🧠 **记忆系统**：记录对话历史和关键记忆，支持情感浓度分析
    - 🔄 **人格演化**：根据对话动态调整人格参数，实现生命闭环
    - 📊 **可视化界面**：展示灵魂档案、记忆库和演化日志
    
    ### 💡 提示
    
    提供的文本越丰富，生成的灵魂档案越准确。建议提供至少 1000 字的对话或描述文本。
    """)
