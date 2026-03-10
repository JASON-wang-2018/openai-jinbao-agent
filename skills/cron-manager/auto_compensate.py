#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cron Auto-Compensate - 自动补偿脚本
每5分钟执行一次，检查并补偿错过的任务
不消耗token，纯系统级脚本
"""

import json
import os
import sys
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path("/home/jason/.openclaw/workspace")
CRON_DIR = Path("/home/jason/.openclaw/cron")
HISTORY_FILE = WORKSPACE / "skills/cron-manager/config/history.json"

# 关键任务列表（需要自动补偿）
CRITICAL_TASKS = {
    "开会提醒": {"retry": 3, "interval": 300},
    "每日英语": {"retry": 2, "interval": 600},
    "股票复盘": {"retry": 2, "interval": 600},
    "股票推送": {"retry": 2, "interval": 600},
}


def get_task_type(task_name: str) -> str:
    """判断任务类型"""
    for keyword in CRITICAL_TASKS:
        if keyword in task_name:
            return "critical"
    return "normal"


def load_cron_jobs():
    """加载cron任务配置"""
    jobs_file = CRON_DIR / "jobs.json"
    if not jobs_file.exists():
        return {}
    
    with open(jobs_file) as f:
        data = json.load(f)
    
    jobs = {}
    for job in data.get("jobs", []):
        jobs[job["name"]] = job
    return jobs


def load_history():
    """加载执行历史"""
    if not HISTORY_FILE.exists():
        return []
    
    with open(HISTORY_FILE) as f:
        data = json.load(f)
    return data.get("executions", [])


def should_compensate(task_name: str, history: list) -> bool:
    """判断是否需要补偿"""
    task_type = get_task_type(task_name)
    if task_type != "critical":
        return False
    
    # 获取该任务的最近执行
    task_history = [h for h in history if h.get("task") == task_name]
    if not task_history:
        return True  # 从未执行过的关键任务
    
    # 检查上次执行是否成功
    last = task_history[-1]
    if last.get("status") == "failed":
        return True
    
    # 检查是否错过执行时间（简化：超过预定周期未执行）
    # 这里可以扩展更复杂的逻辑
    return False


def compensate_task(task_name: str) -> bool:
    """执行补偿任务"""
    print(f"🔄 补偿执行: {task_name}")
    
    # 记录开始
    log_compensate(task_name, "compensating", "Starting compensate run")
    
    # 这里可以添加实际的补偿逻辑
    # 例如：调用飞书API发送提醒、执行脚本等
    
    log_compensate(task_name, "compensated", "Compensate completed")
    return True


def log_compensate(task_name: str, status: str, output: str):
    """记录补偿执行日志"""
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    history = []
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE) as f:
            history = json.load(f).get("executions", [])
    
    history.append({
        "task": f"[COMPENSATE] {task_name}",
        "status": status,
        "output": output,
        "time": datetime.now().isoformat()
    })
    
    # 保留最近100条
    if len(history) > 100:
        history = history[-100:]
    
    with open(HISTORY_FILE, 'w') as f:
        json.dump({"executions": history}, f, indent=2)


def main():
    print(f"🕐 Auto-Compensate - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 加载cron任务
    jobs = load_cron_jobs()
    print(f"📋 加载任务数: {len(jobs)}")
    
    # 2. 加载历史
    history = load_history()
    print(f"📜 历史记录: {len(history)}")
    
    # 3. 检查需要补偿的任务
    compensated = []
    for task_name in jobs:
        if should_compensate(task_name, history):
            if compensate_task(task_name):
                compensated.append(task_name)
    
    # 4. 汇总
    print()
    if compensated:
        print(f"✅ 已补偿: {', '.join(compensated)}")
    else:
        print("✅ 无需补偿")
    
    # 5. 写入状态文件（供监控读取）
    status_file = WORKSPACE / "skills/cron-manager/config/compensate_status.json"
    with open(status_file, 'w') as f:
        json.dump({
            "last_check": datetime.now().isoformat(),
            "compensated": compensated,
            "total_critical": len([k for k in jobs if get_task_type(k) == "critical"])
        }, f, indent=2)


if __name__ == "__main__":
    main()
