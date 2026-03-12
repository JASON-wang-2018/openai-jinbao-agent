#!/usr/bin/env python3
"""
一次性提醒脚本 - 设置后自动执行并删除
用法: 
  python3 set_onetime_reminder.py "提醒内容" <分钟数>
  python3 set_onetime_reminder.py "提醒内容" "2026-03-12 14:30"

示例:
  python3 set_onetime_reminder.py "喝水" 10      # 10分钟后提醒
  python3 set_onetime_reminder.py "开会" 30     # 30分钟后提醒
  python3 set_onetime_reminder.py "喝水" "2026-03-12 14:30"  # 指定时间提醒
"""
import json
import sys
import os
import subprocess
import uuid
from datetime import datetime, timedelta
import time

# 存储提醒配置的文件
REMINDERS_FILE = "/home/jason/.openclaw/workspace/data/onetime_reminders.json"

def ensure_dir():
    """确保目录存在"""
    os.makedirs(os.path.dirname(REMINDERS_FILE), exist_ok=True)

def load_reminders():
    """加载提醒列表"""
    ensure_dir()
    if os.path.exists(REMINDERS_FILE):
        with open(REMINDERS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_reminders(reminders):
    """保存提醒列表"""
    ensure_dir()
    with open(REMINDERS_FILE, 'w') as f:
        json.dump(reminders, f, ensure_ascii=False, indent=2)

def add_reminder(message, minutes=None, specific_time=None):
    """添加一次性提醒"""
    reminders = load_reminders()
    
    if specific_time:
        # 解析指定时间
        run_time = datetime.strptime(specific_time, "%Y-%m-%d %H:%M")
    elif minutes:
        # 计算几分钟后的时间
        run_time = datetime.now() + timedelta(minutes=int(minutes))
    else:
        print("❌ 请指定时间（分钟数或具体时间）")
        return False
    
    reminder = {
        "id": str(uuid.uuid4())[:8],
        "message": message,
        "run_time": run_time.strftime("%Y-%m-%d %H:%M"),
        "run_timestamp": int(run_time.timestamp()),
        "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    reminders.append(reminder)
    save_reminders(reminders)
    
    print(f"✅ 提醒已设置: {message}")
    print(f"   提醒时间: {run_time.strftime('%Y-%m-%d %H:%M')}")
    
    return True

def check_and_run_reminders():
    """检查并执行到期的提醒"""
    reminders = load_reminders()
    if not reminders:
        return
    
    now = int(time.time())
    remaining = []
    
    for r in reminders:
        if r["run_timestamp"] <= now:
            # 提醒时间到了，发送消息
            send_reminder_message(r["message"])
        else:
            # 还未到时间，保留
            remaining.append(r)
    
    # 保存剩余提醒
    save_reminders(remaining)

def send_reminder_message(message):
    """发送提醒消息到飞书"""
    try:
        # 使用 openclaw message 发送
        cmd = [
            "openclaw", "message", "send",
            "--channel", "feishu",
            "--target", "ou_d9b15939bd786fcffac245aa2265b871",
            "--message", f"⏰ 提醒: {message}"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"✅ 提醒已发送: {message}")
        else:
            print(f"❌ 发送失败: {result.stderr}")
    except Exception as e:
        print(f"❌ 发送出错: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    # 检查是否是检查模式
    if sys.argv[1] == "--check":
        check_and_run_reminders()
    elif len(sys.argv) >= 3:
        message = sys.argv[1]
        time_arg = sys.argv[2]
        
        # 判断是分钟数还是具体时间
        if time_arg.isdigit():
            add_reminder(message, minutes=int(time_arg))
        else:
            add_reminder(message, specific_time=time_arg)
    else:
        print(__doc__)
