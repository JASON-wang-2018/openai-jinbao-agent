#!/usr/bin/env python3
"""
产品设计方法论整合工具箱

功能:
- TRIZ矛盾分析
- DFMA评估
- VAVE价值分析
- DFSS稳健设计
- 精益改善

使用方式:
    python3 design_toolbox.py --module=triz --problem="问题描述"
    python3 design_toolbox.py --module=dfma --input=product_bom.csv
    python3 design_toolbox.py --module=vave --function=功能 --cost=成本
"""

import argparse
import json
import csv
import re
from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum


# ==================== TRIZ模块 ====================

class TRIZPrinciples:
    """TRIZ 40发明原理"""
    
    # 发明原理映射 (简化版矛盾矩阵)
    CONTRADICTION_MAP = {
        # 重量 vs 强度
        (1, 14): [10, 20, 29, 37],  # 改善重量，恶化强度
        (14, 1): [10, 14, 15, 40],  # 改善强度，恶化重量
        
        # 体积 vs 功能
        (7, 26): [1, 7, 17, 30],   # 改善体积，恶化功能数
        (26, 7): [1, 5, 6, 13],    # 改善功能数，恶化体积
        
        # 速度 vs 振动
        (9, 13): [1, 15, 19, 35],  # 改善速度，恶化稳定性
        (13, 9): [1, 15, 22, 28],  # 改善稳定性，恶化速度
        
        # 温度 vs 能耗
        (17, 19): [2, 21, 22, 35], # 改善温度，恶化能耗
        (19, 17): [2, 21, 22, 35], # 改善能耗，恶化温度
        
        # 可靠性 vs 成本
        (27, 26): [3, 6, 27, 40],  # 改善可靠性，恶化成本
        (26, 27): [3, 11, 27, 35], # 改善成本，恶化可靠性
        
        # 复杂度 vs 精度
        (36, 29): [1, 13, 17, 26], # 改善复杂度，恶化精度
        (29, 36): [1, 10, 27, 35], # 改善精度，恶化复杂度
    }
    
    PRINCIPLES = {
        1: "分割 - 将物体分成独立部分",
        2: "分离 - 将干扰部分分离",
        3: "局部质量 - 各部分最优状态",
        4: "不对称 - 使用不对称形状",
        5: "合并 - 相同/相似物体合并",
        6: "多功能 - 一个零件执行多种功能",
        7: "嵌套 - 物体放置在另一个物体中",
        8: "重量补偿 - 用反作用力补偿",
        9: "预先反作用 - 预先施加反作用",
        10: "预先作用 - 预先完成部分作用",
        11: "预先紧急措施 - 预先准备紧急措施",
        12: "等势 - 改变位置使势能不变",
        13: "逆向作用 - 颠倒执行操作",
        14: "曲面化 - 用曲线代替直线",
        15: "动态化 - 使物体自动调整",
        16: "部分或超额作用 - 稍微超额完成功能",
        17: "空间维数变化 - 一维→二维→三维",
        18: "机械振动 - 使物体振动",
        19: "周期性作用 - 用连续作用代替周期作用",
        20: "有效运动连续性 - 各部分同时工作",
        21: "快速通过 - 高速通过有害过程",
        22: "变害为利 - 利用有害因素",
        23: "反馈 - 引入反馈",
        24: "中介物 - 使用中介物",
        25: "自服务 - 物体自我服务",
        26: "复制 - 用简化复制品代替",
        27: "一次性用品 - 用低成本一次性代替",
        28: "机械系统替代 - 用电场磁场代替",
        29: "气动/液压 - 用气体液体代替固体",
        30: "柔性壳体 - 用柔性薄膜代替",
        31: "多孔材料 - 使物体多孔",
        32: "颜色改变 - 改变物体颜色",
        33: "同质性 - 用相同材料",
        34: "抛弃与修复 - 已完成功能部件消失",
        35: "参数变化 - 改变物体状态",
        36: "相变 - 利用相变效应",
        37: "热膨胀 - 利用热膨胀",
        38: "加速氧化 - 用富氧环境",
        39: "惰性环境 - 用惰性环境",
        40: "复合材料 - 用复合材料代替单一材料"
    }
    
    @classmethod
    def get_principles(cls, improve_param: int, worsen_param: int) -> List[str]:
        """获取推荐原理"""
        key = (improve_param, worsen_param)
        principle_ids = cls.CONTRADICTION_MAP.get(key, [1, 5, 10, 15])
        return [cls.PRINCIPLES.get(pid, f"原理{pid}") for pid in principle_ids]


# ==================== DFMA模块 ====================

@dataclass
class DFMAComponent:
    """DFMA组件"""
    name: str
    function: str
    dfm_score: int  # 1-5分
    dfa_score: int  # 1-5分
    cost: float
    weight: float
    material: str
    process: str


class DFMAScorer:
    """DFMA评分器"""
    
    # DFM评分标准
    DFM_CRITERIA = {
        1: "零件可直接制造",
        2: "零件可简化制造",
        3: "需详细分析",
        4: "不建议制造",
        5: "无法制造"
    }
    
    # DFA评分标准
    DFA_CRITERIA = {
        1: "易于装配",
        2: "可接受",
        3: "需评估",
        4: "困难",
        5: "无法装配"
    }
    
    @classmethod
    def calculate_efficiency(cls, components: List[DFMAComponent]) -> Dict:
        """计算DFMA效率"""
        n = len(components)
        if n == 0:
            return {"efficiency": 0, "recommendation": "无零件"}
        
        # 计算等效零件数
        equivalent_parts = sum(c.dfm_score * c.dfa_score for c in components)
        
        # 计算成本分布
        total_cost = sum(c.cost for c in components)
        cost_by_material = {}
        cost_by_process = {}
        for c in components:
            cost_by_material[c.material] = cost_by_material.get(c.material, 0) + c.cost
            cost_by_process[c.process] = cost_by_process.get(c.process, 0) + c.cost
        
        # 评分
        efficiency = (1 - equivalent_parts / (n * 25)) * 100
        
        if efficiency >= 80:
            recommendation = "优秀 - 设计优化良好"
        elif efficiency >= 60:
            recommendation = "良好 - 可进一步优化"
        elif efficiency >= 40:
            recommendation = "一般 - 需要改进"
        else:
            recommendation = "较差 - 建议重新设计"
        
        return {
            "total_parts": n,
            "equivalent_parts": equivalent_parts,
            "efficiency": round(efficiency, 2),
            "recommendation": recommendation,
            "cost_distribution": {
                "total": total_cost,
                "by_material": cost_by_material,
                "by_process": cost_by_process
            },
            "weight_distribution": {c.name: c.weight for c in components}
        }
    
    @classmethod
    def generate_suggestions(cls, components: List[DFMAComponent]) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        for c in components:
            # DFM建议
            if c.dfm_score >= 4:
                suggestions.append(f"【DFM】{c.name}: 建议简化制造工艺或更换材料")
            
            # DFA建议
            if c.dfa_score >= 4:
                suggestions.append(f"【DFA】{c.name}: 建议优化装配设计")
            
            # 成本优化
            if c.cost > 10:
                suggestions.append(f"【成本】{c.name}: 当前成本{c.cost}元，建议优化")
        
        return suggestions


# ==================== VAVE模块 ====================

@dataclass
class VAVEComponent:
    """VAVE组件"""
    name: str
    function: str
    importance: int  # 1-10
    current_cost: float
    target_cost: float
    value_score: float  # F/C


class VAVEAnalyzer:
    """VAVE价值分析器"""
    
    @classmethod
    def analyze_function(cls, components: List[VAVEComponent]) -> Dict:
        """分析功能价值"""
        total_current = sum(c.current_cost for c in components)
        total_target = sum(c.target_cost for c in components)
        
        # 计算价值指数
        result = {
            "total_current_cost": total_current,
            "total_target_cost": total_target,
            "target_reduction": total_current - total_target,
            "reduction_rate": (total_current - total_target) / total_current * 100,
            "components_analysis": []
        }
        
        for c in components:
            value_ratio = c.current_cost / c.target_cost if c.target_cost > 0 else 0
            
            # 价值判断
            if value_ratio > 1.3:
                status = "功能过剩"
            elif value_ratio > 1.0:
                status = "功能略高"
            elif value_ratio >= 0.9:
                status = "合理"
            else:
                status = "功能不足"
            
            result["components_analysis"].append({
                "name": c.name,
                "function": c.function,
                "importance": c.importance,
                "current_cost": c.current_cost,
                "target_cost": c.target_cost,
                "value_ratio": round(value_ratio, 2),
                "status": status,
                "suggestion": cls._get_suggestion(c, value_ratio)
            })
        
        return result
    
    @staticmethod
    def _get_suggestion(c: VAVEComponent, value_ratio: float) -> str:
        """获取建议"""
        if value_ratio > 1.3:
            return "考虑降低配置或简化功能"
        elif value_ratio > 1.0:
            return "可适度优化成本"
        elif value_ratio >= 0.9:
            return "保持现状"
        else:
            return "需确保功能满足要求"


# ==================== 主程序 ====================

class DesignToolbox:
    """产品设计方法论整合工具"""
    
    MODULES = {
        "triz": TRIZPrinciples,
        "dfma": DFMAScorer,
        "vave": VAVEAnalyzer
    }
    
    @staticmethod
    def run_triz(improve_param: str, worsen_param: str, description: str):
        """运行TRIZ分析"""
        print(f"\n{'='*60}")
        print("🔧 TRIZ发明原理分析")
        print(f"{'='*60}")
        print(f"问题描述: {description}")
        print(f"改善参数: {improve_param}")
        print(f"恶化参数: {worsen_param}")
        print()
        
        # 获取推荐原理
        principles = TRIZPrinciples.get_principles(
            int(improve_param), int(worsen_param)
        )
        
        print("推荐TRIZ发明原理:")
        print("-" * 40)
        for i, p in enumerate(principles, 1):
            print(f"  {i}. {p}")
        print()
        
        # 典型案例
        print("家电行业典型应用:")
        print("  - 洗衣机脱水桶: 分割、动态化、嵌套")
        print("  - 空调室内机: 合并、多功能、柔性壳体")
        print("  - 冰箱门封: 嵌套、柔性壳体、颜色改变")
    
    @staticmethod
    def run_dfma(csv_file: str):
        """运行DFMA分析"""
        print(f"\n{'='*60}")
        print("📊 DFMA设计制造装配分析")
        print(f"{'='*60}")
        print(f"输入文件: {csv_file}")
        print()
        
        # 读取CSV
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                components = []
                for row in reader:
                    components.append(DFMAComponent(
                        name=row['name'],
                        function=row['function'],
                        dfm_score=int(row['dfm_score']),
                        dfa_score=int(row['dfm_score']),
                        cost=float(row['cost']),
                        weight=float(row['weight']),
                        material=row['material'],
                        process=row['process']
                    ))
        except Exception as e:
            print(f"错误: 无法读取文件 - {e}")
            return
        
        # 计算效率
        result = DFMAScorer.calculate_efficiency(components)
        
        print(f"总零件数: {result['total_parts']}")
        print(f"等效零件数: {result['equivalent_parts']}")
        print(f"DFMA效率: {result['efficiency']}%")
        print(f"评价: {result['recommendation']}")
        print()
        print(f"总成本: {result['cost_distribution']['total']:.2f}元")
        print()
        
        # 生成建议
        suggestions = DFMAScorer.generate_suggestions(components)
        if suggestions:
            print("改进建议:")
            for s in suggestions:
                print(f"  • {s}")
    
    @staticmethod
    def run_vave(json_file: str):
        """运行VAVE分析"""
        print(f"\n{'='*60}")
        print("💰 VAVE价值分析")
        print(f"{'='*60}")
        print(f"输入文件: {json_file}")
        print()
        
        # 读取JSON
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                components = []
                for item in data['components']:
                    components.append(VAVEComponent(
                        name=item['name'],
                        function=item['function'],
                        importance=item['importance'],
                        current_cost=item['current_cost'],
                        target_cost=item['target_cost'],
                        value_score=item['current_cost']/item['target_cost'] if item['target_cost'] > 0 else 0
                    ))
        except Exception as e:
            print(f"错误: 无法读取文件 - {e}")
            return
        
        # 分析
        result = VAVEAnalyzer.analyze_function(components)
        
        print(f"当前总成本: {result['total_current_cost']:.2f}元")
        print(f"目标总成本: {result['total_target_cost']:.2f}元")
        print(f"目标降本: {result['target_reduction']:.2f}元 ({result['reduction_rate']:.1f}%)")
        print()
        
        print("功能价值分析:")
        print("-" * 60)
        for c in result['components_analysis']:
            status_icon = "⚠️" if c['status'] != "合理" else "✅"
            print(f"{status_icon} {c['name']} ({c['function']})")
            print(f"   重要性: {c['importance']} | 成本: {c['current_cost']:.1f}→{c['target_cost']:.1f}元")
            print(f"   价值比: {c['value_ratio']:.2f} | {c['status']}")
            print(f"   建议: {c['suggestion']}")
            print()


def main():
    parser = argparse.ArgumentParser(
        description="产品设计方法论整合工具箱",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    # TRIZ分析
    python3 design_toolbox.py --module=triz --improve=14 --worsen=1 --desc="需要高强度但要轻"

    # DFMA分析 (需要CSV文件)
    python3 design_toolbox.py --module=dfma --input=product_bom.csv

    # VAVE分析 (需要JSON文件)
    python3 design_toolbox.py --module=vave --input=component_analysis.json

CSV格式示例:
    name,function,dfm_score,dfa_score,cost,weight,material,process
    内胆,盛放米饭,2,2,20,1.5,不锈钢,冲压
    加热管,加热,2,3,15,0.3,合金,焊接

JSON格式示例:
    {
      "components": [
        {"name": "内胆", "function": "盛放米饭", "importance": 9, "current_cost": 20, "target_cost": 15}
      ]
    }
        """
    )
    
    parser.add_argument(
        "--module", "-m",
        type=str,
        required=True,
        choices=["triz", "dfma", "vave"],
        help="选择分析模块"
    )
    
    # TRIZ参数
    parser.add_argument(
        "--improve", "-i",
        type=str,
        help="改善的参数编号 (1-39)"
    )
    parser.add_argument(
        "--worsen", "-w",
        type=str,
        help="恶化的参数编号 (1-39)"
    )
    parser.add_argument(
        "--description", "-d",
        type=str,
        default="",
        help="问题描述"
    )
    
    # 通用参数
    parser.add_argument(
        "--input", "-f",
        type=str,
        help="输入文件路径"
    )
    
    args = parser.parse_args()
    
    # 验证参数
    if args.module == "triz":
        if not args.improve or not args.worsen:
            parser.error("TRIZ分析需要 --improve 和 --worsen 参数")
        DesignToolbox.run_triz(args.improve, args.worsen, args.description)
    
    elif args.module == "dfma":
        if not args.input:
            parser.error("DFMA分析需要 --input 参数（CSV文件）")
        DesignToolbox.run_dfma(args.input)
    
    elif args.module == "vave":
        if not args.input:
            parser.error("VAVE分析需要 --input 参数（JSON文件）")
        DesignToolbox.run_vave(args.input)


if __name__ == "__main__":
    main()
