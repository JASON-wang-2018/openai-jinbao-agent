#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
管理知识搜索工具

功能:
1. 搜索知识点
2. 搜索FAQ
3. 搜索案例
4. 搜索技能
"""

import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from db_manager import ManagementDatabase


class KnowledgeSearcher:
    """知识搜索器"""
    
    def __init__(self):
        self.db = ManagementDatabase()
    
    def search_all(self, keyword: str) -> dict:
        """全局搜索"""
        results = {
            'keyword': keyword,
            'knowledge': [],
            'faqs': [],
            'cases': [],
            'models': []
        }
        
        # 搜索知识点
        results['knowledge'] = self.db.search_knowledge(keyword)
        
        # 搜索FAQ
        self.db.cursor.execute(
            """SELECT * FROM faqs 
               WHERE question LIKE ? OR answer LIKE ? OR keywords LIKE ?""",
            (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%")
        )
        results['faqs'] = [dict(row) for row in self.db.cursor.fetchall()]
        
        # 搜索案例
        self.db.cursor.execute(
            """SELECT * FROM cases 
               WHERE title LIKE ? OR problem LIKE ? OR solution LIKE ?""",
            (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%")
        )
        results['cases'] = [dict(row) for row in self.db.cursor.fetchall()]
        
        # 搜索模型
        self.db.cursor.execute(
            """SELECT * FROM management_models 
               WHERE name LIKE ? OR description LIKE ? OR category LIKE ?""",
            (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%")
        )
        results['models'] = [dict(row) for row in self.db.cursor.fetchall()]
        
        return results
    
    def search_faq_by_question(self, question: str) -> dict:
        """按问题搜索FAQ"""
        return self.db.search_faq(question)
    
    def get_recommendations(self, category: str = None) -> dict:
        """获取推荐内容"""
        recommendations = {
            'category': category,
            'models': [],
            'faqs': [],
            'cases': []
        }
        
        if category:
            recommendations['models'] = self.db.get_models_by_category(category)
            recommendations['faqs'] = self.db.get_faqs(category)
            recommendations['cases'] = self.db.get_cases(category)
        else:
            recommendations['models'] = self.db.get_all_models()[:5]
            recommendations['faqs'] = self.db.get_faqs()[:5]
            recommendations['cases'] = self.db.get_cases()[:5]
        
        return recommendations
    
    def format_results(self, results: dict) -> str:
        """格式化搜索结果"""
        output = []
        
        keyword = results.get('keyword', '')
        output.append(f"\n🔍 搜索关键词: {keyword}\n")
        output.append("=" * 50)
        
        # 知识点
        if results['knowledge']:
            output.append(f"\n📚 知识点 ({len(results['knowledge'])} 条)")
            output.append("-" * 40)
            for item in results['knowledge'][:3]:
                output.append(f"  • {item['title']}")
                if item.get('key_takeaways'):
                    takeaways = item['key_takeaways']
                    if isinstance(takeaways, str):
                        takeaways = eval(takeaways)
                    for t in takeaways[:2]:
                        output.append(f"    → {t[:50]}")
        
        # 模型
        if results['models']:
            output.append(f"\n🧩 管理模型 ({len(results['models'])} 条)")
            output.append("-" * 40)
            for item in results['models'][:3]:
                output.append(f"  • {item['name']} ({item['category']})")
                output.append(f"    公式: {item['formula']}")
        
        # FAQ
        if results['faqs']:
            output.append(f"\n❓ FAQ ({len(results['faqs'])} 条)")
            output.append("-" * 40)
            for item in results['faqs'][:3]:
                output.append(f"  Q: {item['question'][:50]}...")
        
        # 案例
        if results['cases']:
            output.append(f"\n📁 案例 ({len(results['cases'])} 条)")
            output.append("-" * 40)
            for item in results['cases'][:3]:
                output.append(f"  • {item['title']} ({item['category']})")
        
        output.append("\n" + "=" * 50)
        
        return '\n'.join(output)


def interactive_search():
    """交互式搜索"""
    searcher = KnowledgeSearcher()
    
    print("\n🔍 中层管理者知识搜索")
    print("=" * 40)
    print("输入关键词搜索，输入 'q' 退出")
    print("示例关键词: 团队、绩效、汇报、冲突、时间管理\n")
    
    while True:
        keyword = input("🔍 搜索: ").strip()
        
        if keyword.lower() == 'q':
            print("\n👋 再见！")
            break
        
        if not keyword:
            continue
        
        results = searcher.search_all(keyword)
        print(searcher.format_results(results))
    
    searcher.db.close()


def quick_search(keyword: str):
    """快速搜索"""
    searcher = KnowledgeSearcher()
    results = searcher.search_all(keyword)
    print(searcher.format_results(results))
    searcher.db.close()


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="管理知识搜索工具")
    parser.add_argument('keyword', nargs='?', help='搜索关键词')
    parser.add_argument('--interactive', '-i', action='store_true', help='交互模式')
    parser.add_argument('--faq', type=str, help='搜索FAQ')
    parser.add_argument('--recommend', type=str, help='获取推荐（分类名）')
    
    args = parser.parse_args()
    
    if args.interactive:
        interactive_search()
    elif args.faq:
        searcher = KnowledgeSearcher()
        result = searcher.search_faq_by_question(args.faq)
        if result:
            print(f"\n❓ 问题: {result['question']}")
            print(f"\n💡 答案: {result['answer']}")
            print(f"\n📂 分类: {result['category']}")
        else
            print(f"\n❌ 未找到相关FAQ")
        searcher.db.close()
    elif args.recommend:
        searcher = KnowledgeSearcher()
        recs = searcher.get_recommendations(args.recommend)
        print(f"\n📌 {recs['category']} 推荐内容")
        print("=" * 40)
        
        if recs['models']:
            print("\n🧩 相关模型:")
            for m in recs['models'][:3]:
                print(f"  • {m['name']}")
        
        if recs['faqs']:
            print("\n❓ 常见问题:")
            for f in recs['faqs'][:3]:
                print(f"  • {f['question'][:40]}...")
        
        if recs['cases']:
            print("\n📁 相关案例:")
            for c in recs['cases'][:3]:
                print(f"  • {c['title']}")
        
        searcher.db.close()
    elif args.keyword:
        quick_search(args.keyword)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
