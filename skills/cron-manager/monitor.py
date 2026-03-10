#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cron Monitor - 定时任务监控脚本
定时检查任务执行状态，失败时告警
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path("/home/jason/.openclaw/workspace")
HISTORY_FILE = WORKSPACE / "skills/cron-manager/config/history.json"
ISSUES_FILE = WORKSPACE / "memory/issues.json"

# 任务类型定义（与 task-scheduler 配合使用）
TASK_TYPES = {
    "开会提醒": "critical",
    "每日英语": "important", 
    "股票复盘": "important",
    "股票推送": "important",
    "daily-review": "important",
    "每日复盘": "important",
    "英语": "important",
    "股票": "important",
    "task-scheduler": "important",  # 系统任务
}


def get_task_type(task_name: str) -> str:
    """根据任务名判断类型"""
    for keyword, task_type in TASK_TYPES.items():
        if keyword in task_name:
            return task_type
    return "normal"


def check_recent_failures() -> dict:
    """检查最近失败的任务"""
    if not HISTORY_FILE.exists():
        return {"has_issues": False, "issues": [], "total_checked": 0}
    
    with open(HISTORY_FILE) as f:
        history = json.load(f)
    
    executions = history.get("executions", [])
    if not executions:
        return {"has_issues": False, "issues": []}
    
    # 只检查最近1小时内的执行
    one_hour_ago = datetime.now() - timedelta(hours=1)
    recent = []
    
    for exec in executions[-30:]:  # 检查最近30条
        exec_time = datetime.fromisoformat(exec.get("time", ""))
        if exec_time > one_hour_ago:
            recent.append(exec)
    
    # 找出失败的任务
    issues = []
    for exec in recent:
        if exec.get("status") == "failed":
            task_name = exec.get("task", "unknown")
            task_type = get_task_type(task_name)
            issues.append({
                "task": task_name,
                "type": task_type,
                "time": exec.get("time"),
                "output": exec.get("output", "")[:200]
            })
    
    return {
        "has_issues": len(issues) > 0,
        "issues": issues,
        "total_checked": len(recent) if recent else 0
    }


def check_missed_tasks() -> dict:
    """检查错过的任务"""
    # 读取 cron jobs.json 获取预期执行的任务
    cron_file = Path("/home/jason/.openclaw/cron/jobs.json")
    if not cron_file.exists():
        return {"has_issues": False, "issues": []}
    
    with open(cron_file) as f:
        cron_data = json.load(f)
    
    # 这个需要更复杂的逻辑，暂时简化处理
    return {"has_issues": False, "issues": []}


def should_alert(issues: list) -> bool:
    """判断是否需要告警"""
    if not issues:
        return False
    
    for issue in issues:
        task_type = issue.get("type", "normal")
        if task_type == "critical":
            return True
        if task_type == "important":
            return True
    
    return False


def format_alert(issues: list) -> str:
    """格式化告警消息"""
    lines = ["⚠️ 定时任务异常", ""]
    
    critical = [i for i in issues if i.get("type") == "critical"]
    important = [i for i in issues if i.get("type") == "important"]
    
    if critical:
        lines.append("🔴 关键任务失败:")
        for i in critical:
            lines.append(f"  - {i['task']}")
            lines.append(f"    {i['time']}")
    
    if important:
        lines.append("🟡 重要任务失败:")
        for i in important:
            lines.append(f"  - {i['task']}")
            lines.append(f"    {i['time']}")
    
    return "\n".join(lines)


def main():
    print(f"🕐 Cron Monitor - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 检查失败任务
    failure_result = check_recent_failures()
    print(f"检查执行数: {failure_result['total_checked']}")
    
    if failure_result["has_issues"]:
        print(f"发现问题: {len(failure_result['issues'])}")
        for issue in failure_result["issues"]:
            print(f"  - {issue['task']}: {issue.get('type')} - {issue['status']}")
        
        if should_alert(failure_result["issues"]):
            alert_msg = format_alert(failure_result["issues"])
            print()
            print(alert_msg)
            
            # 可以在这里发送通知
            # 例如：发送到飞书、发送邮件等
            sys.exit(1)  # 返回错误码表示需要关注
    else:
        print("✅ 无异常")
    
    sys.exit(0)


if __name__ == "__main__":
    main()
