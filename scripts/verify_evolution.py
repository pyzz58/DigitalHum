# verify_evolution.py
import sys, os
sys.path.append('src')
from memory_db import update_soul_layer, get_evolution_logs

test_soul_id = "test-evolve"
update_soul_layer(test_soul_id, "L4_Emotion", {"mood_state": "excited"}, "测试演化")
logs = get_evolution_logs(test_soul_id)
print("演化日志:", logs)