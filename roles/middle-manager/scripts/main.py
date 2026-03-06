#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中层管理者助手 - 主程序
提供知识查询、模型查找、问题解答等功能
"""

import sqlite3
import os
import json
from datetime import datetime

# 数据库路径
SCRIPT_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(SCRIPT_DIR, '../data/management_knowledge.db')


class MiddleManagerAssistant:
    """中层管理者助手"""
    
    def __init__(self):
        self.db_path = DB_PATH
        self.ensure_db_exists()
    
    def ensure_db_exists(self):
        """确保数据库存在"""
        if not os.path.exists(self.db_path):
            # 运行初始化脚本
            init_script = os.path.join(SCRIPT_DIR, 'init_db.py')
            os.system(f"python3 {init_script}")
    
    def get_connection(self):
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    # ==================== 知识查询 ====================
    
    def get_categories(self, parent_id=0):
        """获取分类列表"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM knowledge_categories WHERE parent_id = ? ORDER BY sort_order",
            (parent_id,)
        )
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def get_knowledge_points(self, category_id=None, limit=20):
        """获取知识点"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if category_id:
            cursor.execute(
                "SELECT * FROM knowledge_points WHERE category_id = ? ORDER BY importance DESC LIMIT ?",
                (category_id, limit)
            )
        else:
            cursor.execute(
                "SELECT * FROM knowledge_points ORDER BY importance DESC LIMIT ?",
                (limit,)
            )
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def search_knowledge(self, keyword):
        """搜索知识"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT * FROM knowledge_points 
               WHERE title LIKE ? OR content LIKE ? OR tags LIKE ?
               ORDER BY importance DESC""",
            (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%')
        )
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    # ==================== 模型查询 ====================
    
    def get_all_models(self):
        """获取所有管理模型"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM management_models ORDER BY category, name")
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def get_model(self, name):
        """获取特定模型"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM management_models WHERE name LIKE ?", (f'%{name}%',))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def get_models_by_category(self, category):
        """按分类获取模型"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM management_models WHERE category = ? ORDER BY name",
            (category,)
        )
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    # ==================== 问题解答 ====================
    
    def get_faq(self, question):
        """获取常见问题答案"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM faqs WHERE question LIKE ? ORDER BY useful_count DESC",
            (f'%{question}%',)
        )
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def get_all_faqs(self, category=None):
        """获取所有FAQ"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if category:
            cursor.execute(
                "SELECT * FROM faqs WHERE category = ? ORDER BY views DESC",
                (category,)
            )
        else:
            cursor.execute("SELECT * FROM faqs ORDER BY views DESC")
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def increase_faq_views(self, faq_id):
        """增加FAQ浏览次数"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE faqs SET views = views + 1 WHERE id = ?", (faq_id,))
        conn.commit()
        conn.close()
    
    def mark_faq_useful(self, faq_id):
        """标记FAQ有用"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE faqs SET useful_count = useful_count + 1 WHERE id = ?", (faq_id,))
        conn.commit()
        conn.close()
    
    # ==================== 案例查询 ====================
    
    def get_cases(self, category=None, limit=10):
        """获取案例"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if category:
            cursor.execute(
                "SELECT * FROM cases WHERE category = ? ORDER BY rating DESC LIMIT ?",
                (category, limit)
            )
        else:
            cursor.execute(
                "SELECT * FROM cases ORDER BY rating DESC LIMIT ?",
                (limit,)
            )
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def search_cases(self, keyword):
        """搜索案例"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT * FROM cases 
               WHERE title LIKE ? OR problem LIKE ? OR solution LIKE ?
               ORDER BY rating DESC""",
            (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%')
        )
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    # ==================== 模板查询 ====================
    
    def get_templates(self, template_type=None):
        """获取模板"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if template_type:
            cursor.execute(
                "SELECT * FROM templates WHERE type = ? ORDER BY name",
                (template_type,)
            )
        else:
            cursor.execute("SELECT * FROM templates ORDER BY type, name")
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def get_template(self, name):
        """获取特定模板"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM templates WHERE name LIKE ?", (f'%{name}%',))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    # ==================== 技能评估 ====================
    
    def get_all_skills(self):
        """获取所有技能"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM skills ORDER BY category, name")
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def get_skills_by_category(self, category):
        """按分类获取技能"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM skills WHERE category = ? ORDER BY name",
            (category,)
        )
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    # ==================== 行动清单 ====================
    
    def create_action_item(self, user_id, title, description, category, priority=3, due_date=None):
        """创建行动项"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO action_items 
               (user_id, title, description, category, priority, due_date) 
               VALUES (?, ?, ?, ?, ?, ?)""",
            (user_id, title, description, category, priority, due_date)
        )
        conn.commit()
        item_id = cursor.lastrowid
        conn.close()
        return item_id
    
    def get_action_items(self, user_id, status=None, limit=20):
        """获取行动项"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if status:
            cursor.execute(
                """SELECT * FROM action_items 
                   WHERE user_id = ? AND status = ? 
                   ORDER BY priority DESC, due_date ASC LIMIT ?""",
                (user_id, status, limit)
            )
        else:
            cursor.execute(
                """SELECT * FROM action_items 
                   WHERE user_id = ? 
                   ORDER BY priority DESC, due_date ASC LIMIT ?""",
                (user_id, limit)
            )
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def update_action_status(self, item_id, status):
        """更新行动项状态"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if status == 'done':
            cursor.execute(
                "UPDATE action_items SET status = ?, completed_at = ? WHERE id = ?",
                (status, datetime.now().isoformat(), item_id)
            )
        else:
            cursor.execute(
                "UPDATE action_items SET status = ? WHERE id = ?",
                (status, item_id)
            )
        
        conn.commit()
        conn.close()
    
    # ==================== 进度跟踪 ====================
    
    def update_learning_progress(self, user_id, item_type, item_id, status, progress=0, notes=None):
        """更新学习进度"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT OR REPLACE INTO learning_progress 
               (user_id, item_type, item_id, status, progress_percent, notes, last_accessed) 
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (user_id, item_type, item_id, status, progress, notes, datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
    
    def get_learning_progress(self, user_id):
        """获取学习进度"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM learning_progress WHERE user_id = ? ORDER BY last_accessed DESC",
            (user_id,)
        )
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    # ==================== 收藏管理 ====================
    
    def add_favorite(self, user_id, item_type, item_id):
        """添加收藏"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO favorites (user_id, item_type, item_id) VALUES (?, ?, ?)",
            (user_id, item_type, item_id)
        )
        conn.commit()
        conn.close()
    
    def get_favorites(self, user_id):
        """获取收藏"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM favorites WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,)
        )
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results


# ==================== 便捷函数 ====================

def quick_help():
    """快速帮助信息"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                  中层管理者助手 - 使用指南                      ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  【查询管理模型】                                             ║
║    assistant.get_all_models()                                ║
║    assistant.get_model('OKR')                                ║
║    assistant.get_models_by_category('目标管理')             ║
║                                                              ║
║  【查询常见问题】                                             ║
║    assistant.get_faq('团队执行力')                           ║
║    assistant.get_all_faqs('团队管理')                       ║
║                                                              ║
║  【查询知识】                                                 ║
║    assistant.get_categories()                               ║
║    assistant.get_knowledge_points(category_id=4)           ║
║    assistant.search_knowledge('沟通')                       ║
║                                                              ║
║  【查询案例】                                                 ║
║    assistant.get_cases('团队管理')                           ║
║    assistant.search_cases('冲突')                           ║
║                                                              ║
║  【获取模板】                                                 ║
║    assistant.get_templates('report')                        ║
║    assistant.get_template('周报')                           ║
║                                                              ║
║  【技能评估】                                                 ║
║    assistant.get_all_skills()                               ║
║    assistant.get_skills_by_category('团队管理')              ║
║                                                              ║
║  【行动清单】                                                 ║
║    assistant.create_action_item(...)                        ║
║    assistant.get_action_items('user123')                    ║
║    assistant.update_action_status(item_id, 'done')          ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)


if __name__ == "__main__":
    import sys
    
    assistant = MiddleManagerAssistant()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == 'help':
            quick_help()
        elif cmd == 'models':
            models = assistant.get_all_models()
            print(f"📊 共 {len(models)} 个管理模型:")
            for m in models:
                print(f"  • {m['name']} ({m['category']})")
        elif cmd == 'faqs':
            faqs = assistant.get_all_faqs()
            print(f"💡 共 {len(faqs)} 个常见问题:")
            for f in faqs:
                print(f"  • {f['question']}")
        elif cmd == 'skills':
            skills = assistant.get_all_skills()
            print(f"🎯 共 {len(skills)} 项核心技能:")
            for s in skills:
                print(f"  • {s['name']} ({s['category']}) - 级别: {s['level_required']}")
        else:
            print(f"未知命令: {cmd}")
            print("使用 'python main.py help' 查看帮助")
    else:
        quick_help()
