#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cron Manager - 定时任务管理核心模块
确保任务不被错过，提供可靠性保障
"""

import json
import os
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List

CRON_DIR = Path("/home/jason/.openclaw/cron")
WORKSPACE = Path("/home/jason/.openclaw/workspace")
TASK_CONFIG = WORKSPACE / "skills/cron-manager/config/tasks.json"
HISTORY_FILE = WORKSPACE / "skills/cron-manager/config/history.json"


class CronManager:
    """定时任务管理器"""
    
    def __init__(self):
        self._ensure_config_dir()
        self.tasks = self._load_tasks()
        self.history = self._load_history()
    
    def _ensure_config_dir(self):
        """确保配置目录存在"""
        config_dir = WORKSPACE / "skills/cron-manager/config"
        config_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_tasks(self) -> Dict:
        """加载任务配置"""
        if TASK_CONFIG.exists():
            with open(TASK_CONFIG) as f:
                return json.load(f)
        return {"tasks": []}
    
    def _save_tasks(self):
        """保存任务配置"""
        with open(TASK_CONFIG, 'w') as f:
            json.dump(self.tasks, f, indent=2, ensure_ascii=False)
    
    def _load_history(self) -> Dict:
        """加载执行历史"""
        if HISTORY_FILE.exists():
            with open(HISTORY_FILE) as f:
                return json.load(f)
        return {"executions": []}
    
    def _save_history(self):
        """保存执行历史"""
        with open(HISTORY_FILE, 'w') as f:
            json.dump(self.history, f, indent=2, ensure_ascii=False)
    
    def add_task(self, name: str, schedule: str, command: str, 
                 task_type: str = "normal", retry: int = 1,
                 description: str = "") -> bool:
        """添加新任务"""
        task = {
            "name": name,
            "schedule": schedule,
            "command": command,
            "type": task_type,
            "retry": retry,
            "description": description,
            "enabled": True,
            "created": datetime.now().isoformat()
        }
        self.tasks.setdefault("tasks", []).append(task)
        self._save_tasks()
        print(f"✅ 已添加任务: {name}")
        return True
    
    def remove_task(self, name: str) -> bool:
        """移除任务"""
        tasks = self.tasks.get("tasks", [])
        self.tasks["tasks"] = [t for t in tasks if t["name"] != name]
        self._save_tasks()
        print(f"✅ 已移除任务: {name}")
        return True
    
    def list_tasks(self) -> List[Dict]:
        """列出所有任务"""
        return self.tasks.get("tasks", [])
    
    def run_task(self, name: str) -> bool:
        """执行指定任务"""
        task = self._find_task(name)
        if not task:
            print(f"❌ 任务不存在: {name}")
            return False
        
        command = task.get("command")
        if not command:
            print(f"❌ 任务无命令: {name}")
            return False
        
        # 记录执行开始
        execution_id = self._record_execution(name, "running", "")
        
        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, 
                text=True, timeout=300
            )
            status = "success" if result.returncode == 0 else "failed"
            output = result.stdout + result.stderr
            
            self._record_execution(name, status, output, execution_id)
            print(f"{'✅' if status == 'success' else '❌'} 任务 {name}: {status}")
            return status == "success"
            
        except subprocess.TimeoutExpired:
            self._record_execution(name, "failed", "Timeout after 300s", execution_id)
            print(f"❌ 任务超时: {name}")
            return False
        except Exception as e:
            self._record_execution(name, "failed", str(e), execution_id)
            print(f"❌ 任务失败: {name} - {e}")
            return False
    
    def catchup(self, name: str) -> bool:
        """补偿执行错过的任务"""
        task = self._find_task(name)
        if not task:
            print(f"❌ 任务不存在: {name}")
            return False
        
        print(f"⏰ 补偿执行任务: {name}")
        return self.run_task(name)
    
    def check_health(self) -> Dict:
        """检查任务健康状态"""
        now = datetime.now()
        issues = []
        
        # 检查最近失败的任务
        recent = self.history.get("executions", [])[-20:]
        for exec in reversed(recent):
            if exec.get("status") == "failed":
                task_name = exec.get("task")
                task = self._find_task(task_name)
                if task and task.get("type") in ["critical", "important"]:
                    issues.append({
                        "task": task_name,
                        "issue": "failed",
                        "time": exec.get("time"),
                        "output": exec.get("output", "")[:100]
                    })
        
        return {
            "healthy": len(issues) == 0,
            "issues": issues,
            "total_tasks": len(self.tasks.get("tasks", [])),
            "recent_failures": len([e for e in recent if e.get("status") == "failed"])
        }
    
    def _find_task(self, name: str) -> Optional[Dict]:
        """查找任务"""
        for task in self.tasks.get("tasks", []):
            if task.get("name") == name:
                return task
        return None
    
    def _record_execution(self, name: str, status: str, output: str, 
                          execution_id: str = None) -> str:
        """记录执行历史"""
        if not execution_id:
            execution_id = f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        record = {
            "task": name,
            "status": status,
            "output": output[:500],  # 限制输出长度
            "time": datetime.now().isoformat()
        }
        
        self.history.setdefault("executions", []).append(record)
        
        # 保留最近100条记录
        if len(self.history["executions"]) > 100:
            self.history["executions"] = self.history["executions"][-100:]
        
        self._save_history()
        return execution_id
    
    def status(self) -> str:
        """显示状态"""
        tasks = self.list_tasks()
        if not tasks:
            return "暂无任务"
        
        lines = ["📋 任务列表:", ""]
        for t in tasks:
            status_icon = "✅" if t.get("enabled", True) else "⏸"
            lines.append(f"{status_icon} {t['name']} ({t.get('type', 'normal')})")
            lines.append(f"   调度: {t.get('schedule', 'N/A')}")
            lines.append("")
        
        health = self.check_health()
        lines.append(f"🟢 健康: {'是' if health['healthy'] else '否'}")
        if health['issues']:
            lines.append("⚠️ 问题:")
            for issue in health['issues']:
                lines.append(f"   - {issue['task']}: {issue['issue']}")
        
        return "\n".join(lines)


def main():
    import sys
    manager = CronManager()
    
    if len(sys.argv) < 2:
        print(manager.status())
        return
    
    cmd = sys.argv[1]
    
    if cmd == "status":
        print(manager.status())
    
    elif cmd == "list":
        for t in manager.list_tasks():
            print(f"{t['name']} - {t.get('schedule', '')}")
    
    elif cmd == "run" and len(sys.argv) > 2:
        manager.run_task(sys.argv[2])
    
    elif cmd == "catchup" and len(sys.argv) > 2:
        manager.catchup(sys.argv[2])
    
    elif cmd == "health":
        health = manager.check_health()
        print(f"健康: {'🟢 是' if health['healthy'] else '🔴 否'}")
        print(f"任务数: {health['total_tasks']}")
        print(f"失败数: {health['recent_failures']}")
    
    elif cmd == "add" and len(sys.argv) > 2:
        name = sys.argv[2]
        schedule = sys.argv[3] if len(sys.argv) > 3 else "0 * * * *"
        command = sys.argv[4] if len(sys.argv) > 4 else ""
        task_type = sys.argv[5] if len(sys.argv) > 5 else "normal"
        manager.add_task(name, schedule, command, task_type)
    
    else:
        print("用法:")
        print("  python cron_manager.py status      # 查看状态")
        print("  python cron_manager.py list       # 列出任务")
        print("  python cron_manager.py run <name> # 执行任务")
        print("  python cron_manager.py catchup <name> # 补偿执行")
        print("  python cron_manager.py health     # 健康检查")
        print("  python cron_manager.py add <name> <schedule> <command> <type>")


if __name__ == "__main__":
    main()
