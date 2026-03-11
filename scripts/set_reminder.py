#!/usr/bin/env python3
"""
设置提醒 - 写入 reminders.json
用法: python3 set_reminder.py "提醒内容" [--repeat]
"""
import json
import sys
import os
from datetime import datetime

REMINDER_FILE = "/home/jason/.openclaw/workspace/reminders.json"

def load_reminders():
    if os.path.exists(REMINDER_FILE):
        with open(REMINDER_FILE, 'r') as f:
            return json.load(f)
    return {"active": {}, "completed": {}, "cancelled": {}}

def save_reminders(data):
    with open(REMINDER_FILE, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def set_reminder(content, repeat=False):
    data = load_reminders()
    
    # 检查是否已存在
    if content in data["active"]:
        print(f"⚠️ 提醒已存在: {content}")
        return False
    
    if content in data["cancelled"]:
        # 从取消记录中恢复
        del data["cancelled"][content]
    
    data["active"][content] = {
        "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "last_notified": None,
        "repeat": repeat
    }
    
    save_reminders(data)
    print(f"✅ 提醒已设置: {content}")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 set_reminder.py \"提醒内容\"")
        sys.exit(1)
    
    content = sys.argv[1]
    repeat = "--repeat" in sys.argv
    set_reminder(content, repeat)
