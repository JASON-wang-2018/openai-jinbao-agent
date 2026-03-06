#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中层管理者知识库 - 数据库管理工具

功能:
1. 初始化数据库
2. 查询知识
3. 统计信息
4. 备份恢复
"""

import sqlite3
import json
import os
import shutil
from datetime import datetime
from pathlib import Path

# 配置
DB_PATH = Path(__file__).parent.parent / "database" / "management_knowledge.db"
BACKUP_DIR = Path(__file__).parent.parent / "database" / "backups"


class ManagementDatabase:
    """管理者知识库数据库类"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or DB_PATH
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
    
    # ==================== 查询方法 ====================
    
    def get_categories(self, parent_id: int = 0) -> list:
        """获取分类列表"""
        self.cursor.execute(
            "SELECT * FROM knowledge_categories WHERE parent_id = ? ORDER BY sort_order",
            (parent_id,)
        )
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_knowledge_by_category(self, category_id: int) -> list:
        """获取分类下的知识点"""
        self.cursor.execute(
            "SELECT * FROM knowledge_points WHERE category_id = ? ORDER BY importance DESC",
            (category_id,)
        )
        return [dict(row) for row in self.cursor.fetchall()]
    
    def search_knowledge(self, keyword: str) -> list:
        """搜索知识点"""
        self.cursor.execute(
            """SELECT k.*, c.name as category_name 
               FROM knowledge_points k 
               LEFT JOIN knowledge_categories c ON k.category_id = c.id
               WHERE k.title LIKE ? OR k.content LIKE ? OR k.tags LIKE ?
               ORDER BY k.importance DESC""",
            (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%")
        )
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_all_models(self) -> list:
        """获取所有管理模型"""
        self.cursor.execute("SELECT * FROM management_models ORDER BY category")
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_models_by_category(self, category: str) -> list:
        """按分类获取模型"""
        self.cursor.execute(
            "SELECT * FROM management_models WHERE category = ?",
            (category,)
        )
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_model_by_name(self, name: str) -> dict:
        """按名称获取模型"""
        self.cursor.execute(
            "SELECT * FROM management_models WHERE name LIKE ?",
            (f"%{name}%",)
        )
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def get_templates(self, template_type: str = None) -> list:
        """获取模板"""
        if template_type:
            self.cursor.execute(
                "SELECT * FROM templates WHERE type = ?",
                (template_type,)
            )
        else:
            self.cursor.execute("SELECT * FROM templates")
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_cases(self, category: str = None) -> list:
        """获取案例"""
        if category:
            self.cursor.execute(
                "SELECT * FROM cases WHERE category = ? ORDER BY views DESC",
                (category,)
            )
        else:
            self.cursor.execute("SELECT * FROM cases ORDER BY views DESC")
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_faqs(self, category: str = None) -> list:
        """获取FAQ"""
        if category:
            self.cursor.execute(
                "SELECT * FROM faqs WHERE category = ? ORDER BY views DESC",
                (category,)
            )
        else:
            self.cursor.execute("SELECT * FROM faqs ORDER BY views DESC")
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_skills(self, category: str = None) -> list:
        """获取技能清单"""
        if category:
            self.cursor.execute(
                "SELECT * FROM skills WHERE category = ?",
                (category,)
            )
        else:
            self.cursor.execute("SELECT * FROM skills")
        return [dict(row) for row in self.cursor.fetchall()]
    
    def search_faq(self, question: str) -> dict:
        """搜索FAQ"""
        self.cursor.execute(
            "SELECT * FROM faqs WHERE question LIKE ? OR keywords LIKE ? LIMIT 1",
            (f"%{question}%", f"%{question}%")
        )
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    # ==================== 统计方法 ====================
    
    def get_stats(self) -> dict:
        """获取统计信息"""
        stats = {}
        
        # 分类统计
        self.cursor.execute("SELECT COUNT(*) as count FROM knowledge_categories WHERE parent_id = 0")
        stats['top_categories'] = self.cursor.fetchone()['count']
        
        # 知识点统计
        self.cursor.execute("SELECT COUNT(*) as count FROM knowledge_points")
        stats['knowledge_points'] = self.cursor.fetchone()['count']
        
        # 模型统计
        self.cursor.execute("SELECT COUNT(*) as count FROM management_models")
        stats['models'] = self.cursor.fetchone()['count']
        
        # 模板统计
        self.cursor.execute("SELECT COUNT(*) as count FROM templates")
        stats['templates'] = self.cursor.fetchone()['count']
        
        # 案例统计
        self.cursor.execute("SELECT COUNT(*) as count FROM cases")
        stats['cases'] = self.cursor.fetchone()['count']
        
        # FAQ统计
        self.cursor.execute("SELECT COUNT(*) as count FROM faqs")
        stats['faqs'] = self.cursor.fetchone()['count']
        
        # 技能统计
        self.cursor.execute("SELECT COUNT(*) as count FROM skills")
        stats['skills'] = self.cursor.fetchone()['count']
        
        return stats
    
    # ==================== 备份恢复 ====================
    
    def backup(self, backup_path: str = None) -> str:
        """备份数据库"""
        BACKUP_DIR.mkdir(exist_ok=True)
        
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            backup_path = BACKUP_DIR / f"management_knowledge_{timestamp}.db"
        
        # 关闭连接后复制
        self.close()
        shutil.copy2(self.db_path, backup_path)
        
        # 重新连接
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        
        return str(backup_path)
    
    def restore(self, backup_path: str):
        """恢复数据库"""
        self.close()
        shutil.copy2(backup_path, self.db_path)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
    
    # ==================== 工具方法 ====================
    
    def export_to_json(self, output_path: str):
        """导出全部数据到JSON"""
        data = {
            'categories': self.get_categories(),
            'models': self.get_all_models(),
            'templates': self.get_templates(),
            'cases': self.get_cases(),
            'faqs': self.get_faqs(),
            'skills': self.get_skills(),
            'exported_at': datetime.now().isoformat()
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return output_path
    
    def add_knowledge_point(self, category_id: int, title: str, content: str, 
                            key_takeaways: list = None, tags: str = None):
        """添加知识点"""
        self.cursor.execute(
            """INSERT INTO knowledge_points 
               (category_id, title, content, key_takeaways, tags) 
               VALUES (?, ?, ?, ?, ?)""",
            (category_id, title, content, 
             json.dumps(key_takeaways or [], ensure_ascii=False), 
             tags)
        )
        self.conn.commit()
        return self.cursor.lastrowid
    
    def add_action_item(self, user_id: str, title: str, description: str = None,
                        category: str = None, priority: int = 3, due_date: str = None):
        """添加行动项"""
        self.cursor.execute(
            """INSERT INTO action_items 
               (user_id, title, description, category, priority, due_date) 
               VALUES (?, ?, ?, ?, ?, ?)""",
            (user_id, title, description, category, priority, due_date)
        )
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_action_items(self, user_id: str, status: str = None):
        """获取行动项"""
        if status:
            self.cursor.execute(
                """SELECT * FROM action_items 
                   WHERE user_id = ? AND status = ? 
                   ORDER BY priority DESC, due_date""",
                (user_id, status)
            )
        else:
            self.cursor.execute(
                """SELECT * FROM action_items 
                   WHERE user_id = ? 
                   ORDER BY priority DESC, due_date""",
                (user_id,)
            )
        return [dict(row) for row in self.cursor.fetchall()]
    
    def update_action_status(self, item_id: int, status: str):
        """更新行动项状态"""
        if status == 'done':
            self.cursor.execute(
                """UPDATE action_items 
                   SET status = ?, completed_at = datetime('now') 
                   WHERE id = ?""",
                (status, item_id)
            )
        else:
            self.cursor.execute(
                """UPDATE action_items SET status = ? WHERE id = ?""",
                (status, item_id)
            )
        self.conn.commit()


def print_stats():
    """打印统计信息"""
    db = ManagementDatabase()
    stats = db.get_stats()
    
    print("\n📊 中层管理者知识库统计")
    print("=" * 40)
    print(f"📂 顶级分类: {stats['top_categories']}")
    print(f"📝 知识点: {stats['knowledge_points']}")
    print(f"🧩 管理模型: {stats['models']}")
    print(f"📄 模板: {stats['templates']}")
    print(f"📁 案例: {stats['cases']}")
    print(f"❓ FAQ: {stats['faqs']}")
    print(f"⚡ 技能: {stats['skills']}")
    print("=" * 40)
    
    db.close()


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="中层管理者知识库管理工具")
    parser.add_argument('--init', action='store_true', help='初始化数据库')
    parser.add_argument('--stats', action='store_true', help='显示统计')
    parser.add_argument('--search', type=str, help='搜索知识')
    parser.add_argument('--model', type=str, help='搜索模型')
    parser.add_argument('--backup', action='store_true', help='备份数据库')
    parser.add_argument('--export', type=str, help='导出JSON')
    
    args = parser.parse_args()
    
    if args.init:
        print("✅ 数据库已初始化")
        print_stats()
    elif args.stats:
        print_stats()
    elif args.search:
        db = ManagementDatabase()
        results = db.search_knowledge(args.search)
        print(f"\n🔍 搜索: {args.search}")
        print(f"找到 {len(results)} 条结果:\n")
        for r in results[:5]:
            print(f"  • {r['title']} ({r['category_name']})")
        db.close()
    elif args.model:
        db = ManagementDatabase()
        model = db.get_model_by_name(args.model)
        if model:
            print(f"\n🧩 模型: {model['name']}")
            print(f"分类: {model['category']}")
            print(f"描述: {model['description']}")
            print(f"公式: {model['formula']}")
            print(f"场景: {model['application_scenario']}")
        else:
            print(f"❌ 未找到模型: {args.model}")
        db.close()
    elif args.backup:
        db = ManagementDatabase()
        path = db.backup()
        print(f"✅ 备份完成: {path}")
        db.close()
    elif args.export:
        db = ManagementDatabase()
        path = db.export_to_json(args.export)
        print(f"✅ 导出完成: {path}")
        db.close()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
