import sqlite3
import os
import json
import threading
from datetime import datetime

# 全局锁，确保线程安全
_db_lock = threading.Lock()

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'db', 'memory.db')

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 1. 原始对话历史
    c.execute('''CREATE TABLE IF NOT EXISTS chat_history 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, soul_id TEXT, role TEXT, content TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
    # 2. 升级后的记忆宫殿表
    c.execute('''CREATE TABLE IF NOT EXISTS memories 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  soul_id TEXT, 
                  summary TEXT,           -- 记忆摘要
                  anchors TEXT,           -- 记忆锚点（人、物、地、概念）
                  spatial_context TEXT,   -- 场景描述
                  weight FLOAT,           -- 重要程度 (0-1)
                  valence FLOAT,          -- 情感极性 (-1到1)
                  created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
    # 3. 演化日志
    c.execute('''CREATE TABLE IF NOT EXISTS evolution_log 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, soul_id TEXT, layer_changed TEXT, 
                  old_value TEXT, new_value TEXT, reason TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
    conn.commit()
    conn.close()

def save_memory(soul_id, summary, weight, anchors, valence, spatial="默认场景"):
    # anchors 应为 list of str
    anchors_json = json.dumps(anchors, ensure_ascii=False)
    with _db_lock:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        conn.execute("""INSERT INTO memories (soul_id, summary, weight, anchors, valence, spatial_context)
                        VALUES (?, ?, ?, ?, ?, ?)""",
                     (soul_id, summary, weight, anchors_json, valence, spatial))
        conn.commit()
        conn.close()

def get_palace_memories(soul_id, query_anchors=None, limit=30):
    """根据锚点检索记忆宫殿，返回包含所有维度的字典列表以便前端渲染"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if query_anchors:
        cursor.execute("SELECT summary, anchors, spatial_context, weight, valence, created_at FROM memories WHERE soul_id=? AND anchors LIKE ? ORDER BY weight DESC LIMIT ?",
                       (soul_id, f"%{query_anchors}%", limit))
    else:
        cursor.execute("SELECT summary, anchors, spatial_context, weight, valence, created_at FROM memories WHERE soul_id=? ORDER BY created_at DESC LIMIT ?",
                       (soul_id, limit))
    rows = cursor.fetchall()
    conn.close()
    
    memories = []
    for row in rows:
        anchors_str = row[1]
        try:
            anchors_list = json.loads(anchors_str)
        except:
            anchors_list = anchors_str.split(',') if anchors_str else []
        memories.append({ 
            "summary": row[0],
            "anchors": anchors_list,          # 现在是 list
            "spatial_context": row[2],
            "weight": row[3],
            "valence": row[4],
            "created_at": row[5]
        })
    return memories

def save_soul_profile(soul_id, name, seed_description, initial_layers):
    """保存初始的灵魂配置作为出厂设置"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 确保 soul_profiles 表存在
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS soul_profiles 
    (id INTEGER PRIMARY KEY AUTOINCREMENT, 
     soul_id TEXT UNIQUE, 
     name TEXT, 
     seed_description TEXT, 
     initial_layers TEXT, 
     created_at DATETIME DEFAULT CURRENT_TIMESTAMP)
    ''')
    
    # 检查是否已存在
    cursor.execute("SELECT id FROM soul_profiles WHERE soul_id=?", (soul_id,))
    if cursor.fetchone():
        # 更新
        cursor.execute(
            "UPDATE soul_profiles SET name=?, seed_description=?, initial_layers=? WHERE soul_id=?",
            (name, seed_description, json.dumps(initial_layers, ensure_ascii=False), soul_id)
        )
    else:
        # 插入
        cursor.execute(
            "INSERT INTO soul_profiles (soul_id, name, seed_description, initial_layers) VALUES (?, ?, ?, ?)",
            (soul_id, name, seed_description, json.dumps(initial_layers, ensure_ascii=False))
        )
    
    conn.commit()
    conn.close()

def save_chat(soul_id, role, content):
    """保存聊天记录"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT INTO chat_history (soul_id, role, content) VALUES (?, ?, ?)", 
                 (soul_id, role, content))
    conn.commit()
    conn.close()

def get_chat_history(soul_id, limit=50):
    """获取聊天历史"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT role, content, timestamp FROM chat_history WHERE soul_id=? ORDER BY timestamp DESC LIMIT ?", 
                  (soul_id, limit))
    rows = cursor.fetchall()
    conn.close()
    return [{'role': row[0], 'content': row[1], 'timestamp': row[2]} for row in reversed(rows)]

def get_relevant_memories(soul_id, limit=20):
    """获取相关记忆"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT summary, anchors, spatial_context, weight, valence, created_at FROM memories WHERE soul_id=? ORDER BY created_at DESC LIMIT ?", 
                  (soul_id, limit))
    rows = cursor.fetchall()
    conn.close()
    memories = []
    for row in rows:
        anchors_str = row[1]
        try:
            anchors_list = json.loads(anchors_str)
        except:
            anchors_list = anchors_str.split(',') if anchors_str else []
        memories.append({ 
            "summary": row[0],
            "anchors": anchors_list,          # 现在是 list
            "spatial_context": row[2],
            "weight": row[3],
            "valence": row[4],
            "created_at": row[5]
        })
    return memories

def get_evolution_logs(soul_id, limit=20):
    """获取演化日志"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT layer_changed, old_value, new_value, reason, timestamp FROM evolution_log WHERE soul_id=? ORDER BY timestamp DESC LIMIT ?", 
                  (soul_id, limit))
    rows = cursor.fetchall()
    conn.close()
    return [{'layer_changed': row[0], 'old_value': row[1], 'new_value': row[2], 'reason': row[3], 'timestamp': row[4]} for row in rows]

def get_memories_by_emotion(soul_id, min_intensity=0.6):
    """根据情感强度获取记忆"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT summary, anchors, spatial_context, weight, valence, created_at FROM memories WHERE soul_id=? AND weight >= ? ORDER BY weight DESC LIMIT 20", 
                  (soul_id, min_intensity))
    rows = cursor.fetchall()
    conn.close()
    memories = []
    for row in rows:
        anchors_str = row[1]
        try:
            anchors_list = json.loads(anchors_str)
        except:
            anchors_list = anchors_str.split(',') if anchors_str else []
        memories.append({ 
            "summary": row[0],
            "anchors": anchors_list,          # 现在是 list
            "spatial_context": row[2],
            "weight": row[3],
            "valence": row[4],
            "created_at": row[5]
        })
    return memories

def update_soul_layer(soul_id, layer_name, new_value_dict, reason):
    """
    更新灵魂的某个层
    layer_name: 例如 "L4_Emotion"
    new_value_dict: 要更新的子字段字典，如 {"mood_state": "happy"}
    reason: 演化原因字符串
    """
    # 1. 读取当前灵魂配置
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT initial_layers FROM soul_profiles WHERE soul_id=?", (soul_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False
    layers = json.loads(row[0])
    
    # 2. 记录旧值
    old_value = layers.get(layer_name, {}).copy()
    
    # 3. 更新
    if layer_name in layers:
        layers[layer_name].update(new_value_dict)
    else:
        layers[layer_name] = new_value_dict
    
    # 4. 写回数据库
    cursor.execute("UPDATE soul_profiles SET initial_layers=? WHERE soul_id=?", 
                   (json.dumps(layers, ensure_ascii=False), soul_id))
    
    # 5. 写入演化日志
    cursor.execute("""INSERT INTO evolution_log 
                      (soul_id, layer_changed, old_value, new_value, reason) 
                      VALUES (?, ?, ?, ?, ?)""",
                   (soul_id, layer_name, json.dumps(old_value, ensure_ascii=False), 
                    json.dumps(new_value_dict, ensure_ascii=False), reason))
    conn.commit()
    conn.close()
    return True
