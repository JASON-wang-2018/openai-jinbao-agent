#!/usr/bin/env python3
"""
检查提醒状态 - 返回需要发送的提醒
用法: python3 check_reminders.py "提醒内容"
返回: 需要发送返回 0，不需要发送返回 1
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

def should_notify(content, cooldown_minutes=30):
    """
    检查是否需要发送提醒
    - 不在 active 中: 返回 False (新提醒或已取消)
    - 已发送且在冷却期内: 返回 False
    - 需要发送: 返回 True 并更新 last_notified
    """
    data = load_reminders()
    
    # 检查是否在 active 中
    if content not in data["active"]:
        return False
    
    info = data["active"][content]
    last_notified = info.get("last_notified")
    
    if last_notified is None:
        # 从未发送过，需要发送
        info["last_notified"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        save_reminders(data)
        return True
    
    # 检查是否在冷却期内
    last_time = datetime.strptime(last_notified, "%Y-%m-%d %H:%M")
    now = datetime.now()
    minutes_since = (now - last_time).total_seconds() / 60
    
    if minutes_since < cooldown_minutes:
        # 在冷却期内，不发送
        return False
    
    # 超过冷却期，更新并发送
    info["last_notified"] = now.strftime("%Y-%m-%d %H:%M")
    save_reminders(data)
    return True

def complete_reminder(content):
    """标记提醒为已完成"""
    data = load_reminders()
    if content in data["active"]:
        info = data["active"].pop(content)
        data["completed"][content] = {
            "created": info.get("created"),
            "completed_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        save_reminders(data)

def list_reminders():
    """列出所有提醒状态"""
    data = load_reminders()
    print("📋 提醒状态:")
    print(f"  活跃: {list(data['active'].keys())}")
    print(f"  已完成: {list(data['completed'].keys())}")
    print(f"  已取消: {list(data['cancelled'].keys())}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        list_reminders()
        sys.exit(0)
    
    content = sys.argv[1]
    if should_notify(content):
        print(f"🔔 需要发送提醒: {content}")
        sys.exit(0)
    else:
        print(f"⏳ 跳过提醒: {content}")
        sys.exit(1)
