#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
管理模型选择器

功能:
1. 根据场景推荐合适的模型
2. 展示模型详情和使用方法
3. 提供模型使用指南
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from db_manager import ManagementDatabase

import json


class ModelSelector:
    """模型选择器"""
    
    def __init__(self):
        self.db = ManagementDatabase()
        
        # 场景到模型的映射
        self.scenario_mapping = {
            '目标设定': ['SMART目标', 'OKR目标'],
            '目标管理': ['SMART目标', 'OKR目标'],
            '项目规划': ['WBS分解', '甘特图'],
            '进度管理': ['WBS分解', '甘特图', 'PDCA循环'],
            '需求分析': ['KANO模型', '5W2H分析'],
            '产品设计': ['KANO模型', 'A/B测试'],
            '问题分析': ['5W2H分析', '麦肯锡七步法', '鱼骨图'],
            '问题解决': ['5W2H分析', 'PDCA循环', '麦肯锡七步法'],
            '沟通表达': ['STAR法则', '金字塔原理'],
            '汇报': ['STAR法则', '金字塔原理'],
            '时间管理': ['艾森豪威尔矩阵', '80/20法则'],
            '效率': ['艾森豪威尔矩阵', '80/20法则', 'PDCA循环'],
            '决策': ['六顶思考帽', 'SWOT分析', '决策矩阵'],
            '团队决策': ['六顶思考帽', '头脑风暴法'],
            '战略分析': ['SWOT分析', '波特五力'],
            '团队管理': ['Tuckman模型', '情境领导'],
            '团队建设': ['Tuckman模型', '情境领导'],
            '绩效': ['OKR目标', 'KPI'],
            '创新': ['头脑风暴法', '六顶思考帽'],
            '风险管理': ['风险矩阵', '应急预案'],
            '质量': ['PDCA循环', '六西格玛'],
        }
        
        # 场景关键词
        self.scenarios = {
            '目标设定': {
                'keywords': ['目标', 'KPI', 'OKR', '计划', '指标'],
                'description': '制定清晰、可执行的目标',
                'recommend': ['SMART目标', 'OKR目标']
            },
            '项目规划': {
                'keywords': ['项目', 'WBS', '里程碑', '分解', '任务'],
                'description': '规划和分解项目工作',
                'recommend': ['WBS分解']
            },
            '问题分析': {
                'keywords': ['问题', '原因', '分析', '诊断'],
                'description': '系统化分析问题',
                'recommend': ['5W2H分析', '麦肯锡七步法']
            },
            '需求分析': {
                'keywords': ['需求', '用户', '优先级', '功能'],
                'description': '分析用户需求',
                'recommend': ['KANO模型']
            },
            '时间管理': {
                'keywords': ['时间', '优先级', '紧急', '重要'],
                'description': '管理时间和优先级',
                'recommend': ['艾森豪威尔矩阵', '80/20法则']
            },
            '团队管理': {
                'keywords': ['团队', '建设', '冲突', '激励'],
                'description': '建设和领导团队',
                'recommend': ['Tuckman模型']
            },
            '沟通汇报': {
                'keywords': ['汇报', '沟通', '表达', '演讲'],
                'description': '高效沟通和汇报',
                'recommend': ['STAR法则', '金字塔原理']
            },
            '战略决策': {
                'keywords': ['战略', '决策', '选择', '方向'],
                'description': '制定战略和决策',
                'recommend': ['SWOT分析', '六顶思考帽']
            },
            '质量改进': {
                'keywords': ['质量', '改进', '优化', '持续'],
                'description': '持续改进和质量控制',
                'recommend': ['PDCA循环']
            }
        }
    
    def recommend_by_scenario(self, scenario: str) -> list:
        """根据场景推荐模型"""
        # 直接匹配
        if scenario in self.scenarios:
            models = self.scenarios[scenario]['recommend']
            return self._get_models_by_names(models)
        
        # 模糊匹配
        for name, info in self.scenarios.items():
            for keyword in info['keywords']:
                if keyword in scenario:
                    return self._get_models_by_names(info['recommend'])
        
        # 数据库搜索
        results = self.db.search_knowledge(scenario)
        model_names = set()
        for r in results:
            if '模型' in r.get('title', ''):
                model_names.add(r['title'])
        
        if model_names:
            return self._get_models_by_names(list(model_names))
        
        return []
    
    def _get_models_by_names(self, names: list) -> list:
        """根据名称获取模型详情"""
        models = []
        for name in names:
            model = self.db.get_model_by_name(name)
            if model:
                models.append(model)
        return models
    
    def get_model_detail(self, model_name: str) -> dict:
        """获取模型详情"""
        model = self.db.get_model_by_name(model_name)
        if model:
            # 解析步骤
            if model['steps']:
                try:
                    model['steps_list'] = json.loads(model['steps'])
                except:
                    model['steps_list'] = model['steps'].split(',')
            else:
                model['steps_list'] = []
        
        return model
    
    def list_all_scenarios(self) -> str:
        """列出所有场景"""
        output = ["\n📋 可用场景分类:\n"]
        output.append("=" * 50)
        
        for name, info in self.scenarios.items():
            output.append(f"\n🎯 {name}")
            output.append(f"   {info['description']}")
            output.append(f"   推荐: {', '.join(info['recommend'])}")
        
        output.append("\n" + "=" * 50)
        return '\n'.join(output)
    
    def how_to_use_model(self, model_name: str) -> str:
        """生成模型使用指南"""
        model = self.get_model_detail(model_name)
        
        if not model:
            return f"❌ 未找到模型: {model_name}"
        
        output = []
        output.append(f"\n🧩 模型: {model['name']}")
        output.append(f"📂 分类: {model['category']}")
        output.append(f"\n📖 描述: {model['description']}")
        output.append(f"\n📐 公式/框架: {model['formula']}")
        output.append(f"\n🎯 应用场景: {model['application_scenario']}")
        
        if model['steps_list']:
            output.append(f"\n📝 使用步骤:")
            for i, step in enumerate(model['steps_list'], 1):
                output.append(f"   {i}. {step.strip()}")
        
        if model['examples']:
            output.append(f"\n💡 使用示例:")
            output.append(f"   {model['examples']}")
        
        if model['limitations']:
            output.append(f"\n⚠️ 注意事项:")
            output.append(f"   {model['limitations']}")
        
        return '\n'.join(output)


def interactive_mode():
    """交互式模式"""
    selector = ModelSelector()
    
    print("\n🎯 管理模型选择器")
    print("=" * 50)
    print("输入应用场景，获取推荐的模型")
    print("输入 'list' 查看所有场景")
    print("输入 'quit' 退出\n")
    
    while True:
        scenario = input("🎯 场景: ").strip()
        
        if scenario.lower() == 'quit':
            print("\n👋 再见！")
            break
        
        if scenario.lower() == 'list':
            print(selector.list_all_scenarios())
            continue
        
        if not scenario:
            continue
        
        models = selector.recommend_by_scenario(scenario)
        
        if models:
            print(f"\n📌 推荐模型 ({len(models)} 个):\n")
            for i, m in enumerate(models, 1):
                print(f"   {i}. {m['name']}")
                print(f"      {m['description'][:60]}...")
                print()
            
            # 询问是否查看详情
            while True:
                choice = input("输入编号查看详情 (直接回车返回): ").strip()
                if not choice:
                    break
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(models):
                        print(selector.how_to_use_model(models[idx]['name']))
                    else:
                        print("❌ 无效编号")
                except ValueError:
                    print("❌ 请输入数字")
        else:
            print("\n❌ 未找到相关模型")
            print("💡 建议: 尝试更通用的关键词，如 '目标'、'项目'、'问题' 等")
    
    selector.db.close()


def quick_recommend(scenario: str):
    """快速推荐"""
    selector = ModelSelector()
    models = selector.recommend_by_scenario(scenario)
    
    if models:
        print(f"\n📌 '{scenario}' 推荐模型:\n")
        for m in models:
            print(f"🧩 {m['name']}")
            print(f"   公式: {m['formula']}")
            print(f"   描述: {m['description'][:80]}...")
            print()
    else:
        print(f"❌ 未找到模型")
    
    selector.db.close()


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="管理模型选择工具")
    parser.add_argument('scenario', nargs='?', help='应用场景')
    parser.add_argument('--interactive', '-i', action='store_true', help='交互模式')
    parser.add_argument('--list', '-l', action='store_true', help='列出所有场景')
    parser.add_argument('--detail', '-d', type=str, help='查看模型详情')
    
    args = parser.parse_args()
    
    selector = ModelSelector()
    
    if args.interactive:
        interactive_mode()
    elif args.list:
        print(selector.list_all_scenarios())
    elif args.detail:
        print(selector.how_to_use_model(args.detail))
    elif args.scenario:
        quick_recommend(args.scenario)
    else:
        parser.print_help()
    
    selector.db.close()


if __name__ == "__main__":
    main()
