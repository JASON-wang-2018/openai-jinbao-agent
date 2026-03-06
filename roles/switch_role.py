#!/usr/bin/env python3
"""
角色切换脚本

功能:
- 在不同角色之间快速切换
- 加载对应的知识库、脚本和技能
- 维护角色专属记忆

使用方式:
    python switch_role.py --role=stock_analyst
    python switch_role.py --role=project_manager
    python switch_role.py --role=product_designer
    python switch_role.py --role=english_learner
    python switch_role.py --role=text_processor
"""

import os
import sys
import json
import argparse
from pathlib import Path

# 基础路径 (修复路径问题)
SCRIPT_PATH = Path(__file__).resolve()
BASE_PATH = SCRIPT_PATH.parent.parent
ROLES_PATH = SCRIPT_PATH.parent

# 角色配置
ROLES = {
    "stock_analyst": {
        "name": "股票分析师",
        "readme": "stock_analyst/README.md",
        "knowledge_base": "knowledge_base/",
        "scripts": "stock/scripts/",
        "skills": [
            "data-analysis",
            "data-anomaly-detector",
            "technical-analyst"
        ],
        "memory_file": "memory/role_stock_analyst.md"
    },
    "project_manager": {
        "name": "项目经理",
        "readme": "project_manager/README.md",
        "knowledge_base": "knowledge_base/pmp/",
        "scripts": "scripts/project/",
        "skills": [
            "project-risk-management",
            "excel-data-processor",
            "task-management-system",
            "git-workflows"
        ],
        "memory_file": "memory/role_project_manager.md"
    },
    "product_designer": {
        "name": "产品设计师",
        "readme": "product_designer/README.md",
        "knowledge_base": "knowledge_base/product/",
        "scripts": "scripts/design/",
        "skills": [
            "find-skills",
            "diagram-generator",
            "first-principles-decomposer",
            "reasoning-personas"
        ],
        "memory_file": "memory/role_product_designer.md"
    },
    "english_learner": {
        "name": "英语学习者",
        "readme": "english_learner/README.md",
        "knowledge_base": "knowledge_base/english/",
        "scripts": "scripts/english/",
        "skills": [
            "Humanizer",
            "adaptive-learning-agents",
            "self-reflection"
        ],
        "memory_file": "memory/role_english_learner.md"
    },
    "text_processor": {
        "name": "文本处理专家",
        "readme": "text_processor/README.md",
        "knowledge_base": "knowledge_base/text/",
        "scripts": "scripts/text/",
        "skills": [
            "Humanizer"
        ],
        "memory_file": "memory/role_text_processor.md"
    }
}


def load_role_config(role_name: str) -> dict:
    """加载角色配置"""
    if role_name not in ROLES:
        print(f"❌ 错误: 未知角色 '{role_name}'")
        print(f"\n可用角色:")
        for name, config in ROLES.items():
            print(f"  - {name}: {config['name']}")
        sys.exit(1)
    
    return ROLES[role_name]


def load_readme(role_name: str) -> str:
    """加载角色 README"""
    config = load_role_config(role_name)
    readme_path = ROLES_PATH / config["readme"]
    
    if readme_path.exists():
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        return f"# {config['name']}\n\nREADME 文件不存在"


def list_available_roles():
    """列出所有可用角色"""
    print("\n📋 可用角色列表:\n")
    
    for name, config in ROLES.items():
        readme_path = ROLES_PATH / config["readme"]
        status = "✅" if readme_path.exists() else "❌"
        
        print(f"  {status} {name}")
        print(f"     名称: {config['name']}")
        print(f"     技能: {', '.join(config['skills'][:3])}...")
        print()
    
    print("使用方式: python switch_role.py --role=<角色名>")
    print("示例: python switch_role.py --role=stock_analyst")


def switch_role(role_name: str, verbose: bool = True):
    """
    切换角色
    
    Args:
        role_name: 角色名称
        verbose: 是否显示详细信息
    """
    config = load_role_config(role_name)
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"🎭 切换到角色: {config['name']}")
        print(f"{'='*60}\n")
        
        print(f"📚 知识库: {config['knowledge_base']}")
        print(f"🛠️  脚本: {config['scripts']}")
        print(f"⚙️  技能: {', '.join(config['skills'])}")
        print()
    
    # 加载 README
    readme = load_readme(role_name)
    
    # 保存当前角色到状态文件
    state_file = ROLES_PATH / "current_role.json"
    state = {
        "current_role": role_name,
        "role_name": config["name"],
        "timestamp": str(Path(__file__).stat().st_mtime)
    }
    
    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    
    if verbose:
        print(f"✅ 角色切换成功!")
        print(f"\n📖 角色说明:")
        print("-" * 60)
        # 打印前 30 行
        lines = readme.split("\n")[:30]
        for line in lines:
            print(line)
        print("-" * 60)
        print(f"\n💡 提示: 查看完整说明请阅读 {config['readme']}")
    
    return config


def get_current_role() -> str:
    """获取当前角色"""
    state_file = ROLES_PATH / "current_role.json"
    
    if state_file.exists():
        with open(state_file, "r", encoding="utf-8") as f:
            state = json.load(f)
            return state.get("current_role", "none")
    
    return "none"


def main():
    parser = argparse.ArgumentParser(
        description="角色切换工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python switch_role.py --role=stock_analyst    # 切换到股票分析师
    python switch_role.py --role=project_manager  # 切换到项目经理
    python switch_role.py --list                  # 列出所有角色
    python switch_role.py --current              # 显示当前角色
        """
    )
    
    parser.add_argument(
        "--role", "-r",
        type=str,
        help="要切换的角色名称"
    )
    
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="列出所有可用角色"
    )
    
    parser.add_argument(
        "--current", "-c",
        action="store_true",
        help="显示当前角色"
    )
    
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="安静模式，不显示详细信息"
    )
    
    args = parser.parse_args()
    
    # 列出所有角色
    if args.list:
        list_available_roles()
        return
    
    # 显示当前角色
    if args.current:
        current = get_current_role()
        if current == "none":
            print("\n📍 当前角色: 无 (使用默认模式)")
        else:
            config = ROLES.get(current, {})
            print(f"\n📍 当前角色: {config.get('name', current)} ({current})")
        return
    
    # 切换角色
    if args.role:
        switch_role(args.role, verbose=not args.quiet)
        return
    
    # 默认: 列出所有角色
    list_available_roles()


if __name__ == "__main__":
    main()
