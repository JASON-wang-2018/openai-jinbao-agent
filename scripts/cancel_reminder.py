#!/usr/bin/env python3
"""
取消提醒 - 从 active 移到 cancelled
用法: python3 cancel_reminder.py "提醒内容"
"""
import json
import sys
import os

REMINDER_FILE = "/home/jason/.openclaw/workspace/reminders.json"

def load_reminders():
    with open(REMINDER_FILE, 'r') as f:
        return json.load(f)

def save_reminders(data):
    with open(REMINDER_FILE, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def cancel_reminder(content):
    data = load_reminders()
    
    if content in data["active"]:
        del data["active"][content]
        data["cancelled"][content] = {
            "cancelled_at": "手动取消"
        }
        save_reminders(data)
        print(f"❌ 提醒已取消: {content}")
        return True
    elif content in data["cancelled"]:
        print(f"⚠️ 提醒已在取消列表: {content}")
        return False
    else:
        print(f"⚠️ 提醒不存在: {content}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 cancel_reminder.py \"提醒内容\"")
        sys.exit(1)
    
    cancel_reminder(sys.argv[1])
