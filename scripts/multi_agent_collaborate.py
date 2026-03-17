#!/usr/bin/env python3
"""
多Agent协作脚本
让多个助手协同工作，并行处理任务
"""

import asyncio
import json
import sys
from datetime import datetime

# 定义助手列表
ASSISTANTS = {
    "pm": {
        "id": "assistant_pm",
        "name": "PM助手",
        "emoji": "📋",
        "workspace": "~/.openclaw/workspace-assistant-pm"
    },
    "tech": {
        "id": "assistant_tech", 
        "name": "技术专家",
        "emoji": "🔧",
        "workspace": "~/.openclaw/workspace-assistant-tech"
    },
    "stock": {
        "id": "assistant_stock",
        "name": "股市分析师",
        "emoji": "📈",
        "workspace": "~/.openclaw/workspace-assistant-stock"
    }
}

def print_banner():
    print("""
🦞 多Agent协作系统
==================
    """)

def list_assistants():
    """列出所有助手"""
    print("\n📋 可用助手:")
    for key, assistant in ASSISTANTS.items():
        print(f"  {assistant['emoji']} {assistant['name']} ({assistant['id']})")
    print()

def show_status():
    """显示助手状态"""
    print("\n📊 助手状态:")
    for key, assistant in ASSISTANTS.items():
        print(f"  {assistant['emoji']} {assistant['name']}: 就绪")
    print()

async def spawn_assistant(agent_id: str, task: str):
    """调用单个助手执行任务"""
    # 这里使用sessions_spawn的API逻辑
    print(f"🤖 调用 {agent_id}...")
    return {"agent": agent_id, "task": task, "status": "pending"}

async def collaborate(task: str, agents: list = None):
    """多助手协作主函数"""
    if agents is None:
        agents = list(ASSISTANTS.keys())
    
    print(f"\n🚀 开始协作任务: {task}")
    print(f"📌 参与助手: {[ASSISTANTS[a]['name'] for a in agents]}")
    print()
    
    # 并行调用所有助手
    results = await asyncio.gather(*[
        spawn_assistant(ASSISTANTS[a]['id'], task) 
        for a in agents
    ])
    
    print("\n✅ 协作完成")
    return results

def main():
    print_banner()
    
    if len(sys.argv) < 2:
        # 默认显示状态
        list_assistants()
        show_status()
        print("用法:")
        print("  python3 multi_agent_collaborate.py status    - 显示状态")
        print("  python3 multi_agent_collaborate.py list      - 列出助手")
        print("  python3 multi_agent_collaborate.py task <任务> - 执行协作任务")
        return
    
    command = sys.argv[1]
    
    if command == "status":
        show_status()
    elif command == "list":
        list_assistants()
    elif command == "task":
        if len(sys.argv) < 3:
            print("❌ 请输入任务内容")
            return
        task = " ".join(sys.argv[2:])
        asyncio.run(collaborate(task))
    else:
        print(f"❌ 未知命令: {command}")

if __name__ == "__main__":
    main()
