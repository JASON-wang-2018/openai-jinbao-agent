#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel 数据处理器
提供 Excel 数据读取、清洗、分析、模板生成等功能
"""

import pandas as pd
import json
from datetime import datetime, timedelta
from pathlib import Path


class ExcelProcessor:
    """Excel 数据处理类"""
    
    def __init__(self):
        self.data = None
        self.filepath = None
    
    # ==================== 读取操作 ====================
    
    def read(self, filepath, sheet_name=0):
        """读取 Excel 文件"""
        self.filepath = filepath
        self.data = pd.read_excel(filepath, sheet_name=sheet_name)
        print(f"✅ 成功读取: {filepath}")
        print(f"   数据量: {len(self.data)} 行, {len(self.data.columns)} 列")
        return self
    
    def read_multiple_sheets(self, filepath):
        """读取多个工作表"""
        xlsx = pd.ExcelFile(filepath)
        sheets = {}
        for name in xlsx.sheet_names:
            sheets[name] = pd.read_excel(xlsx, sheet_name=name)
        self.data = sheets
        return sheets
    
    # ==================== 数据概览 ====================
    
    def info(self):
        """查看数据概览"""
        if self.data is None:
            print("⚠️ 请先读取数据")
            return
        
        print("\n📊 数据概览:")
        print(f"   行数: {len(self.data)}")
        print(f"   列数: {len(self.data.columns)}")
        print(f"\n列名: {list(self.data.columns)}")
        print(f"\n数据类型:\n{self.data.dtypes}")
        print(f"\n前5行:\n{self.data.head()}")
    
    def describe(self):
        """统计摘要"""
        if self.data is not None:
            print(f"\n统计摘要:\n{self.data.describe()}")
    
    # ==================== 数据筛选 ====================
    
    def filter(self, column, value, operator='=='):
        """条件筛选"""
        if operator == '==':
            result = self.data[self.data[column] == value]
        elif operator == '>':
            result = self.data[self.data[column] > value]
        elif operator == '<':
            result = self.data[self.data[column] < value]
        elif operator == '>=':
            result = self.data[self.data[column] >= value]
        elif operator == '<=':
            result = self.data[self.data[column] <= value]
        elif operator == '!=':
            result = self.data[self.data[column] != value]
        elif operator == 'in':
            result = self.data[self.data[column].isin(value)]
        else:
            result = self.data
        
        print(f"✅ 筛选结果: {len(result)} 行")
        return result
    
    def filter_multiple(self, conditions):
        """多条件筛选"""
        result = self.data.copy()
        for col, value in conditions.items():
            result = result[result[col] == value]
        return result
    
    # ==================== 数据清洗 ====================
    
    def clean_null(self, method='fill_zero', column=None):
        """处理空值"""
        if column:
            if method == 'fill_zero':
                self.data[column] = self.data[column].fillna(0)
            elif method == 'fill_mean':
                self.data[column] = self.data[column].fillna(self.data[column].mean())
            elif method == 'drop':
                self.data = self.data.dropna(subset=[column])
        else:
            if method == 'drop':
                self.data = self.data.dropna()
            elif method == 'fill_zero':
                self.data = self.data.fillna(0)
        print(f"✅ 空值处理完成: {method}")
        return self
    
    def clean_duplicates(self):
        """删除重复值"""
        before = len(self.data)
        self.data = self.data.drop_duplicates()
        after = len(self.data)
        print(f"✅ 删除重复: {before - after} 行")
        return self
    
    def convert_date(self, column):
        """日期格式转换"""
        self.data[column] = pd.to_datetime(self.data[column])
        print(f"✅ 日期转换完成: {column}")
        return self
    
    # ==================== 数据分析 ====================
    
    def group_by(self, column, agg='sum'):
        """分组统计"""
        if agg == 'sum':
            result = self.data.groupby(column).sum()
        elif agg == 'mean':
            result = self.data.groupby(column).mean()
        elif agg == 'count':
            result = self.data.groupby(column).count()
        elif agg == 'size':
            result = self.data.groupby(column).size()
        return result
    
    def pivot(self, index, columns, values, aggfunc='sum'):
        """数据透视"""
        return self.data.pivot_table(
            index=index,
            columns=columns,
            values=values,
            aggfunc=aggfunc
        )
    
    def sort(self, column, ascending=False):
        """排序"""
        return self.data.sort_values(column, ascending=ascending)
    
    # ==================== 写入操作 ====================
    
    def save(self, filepath, sheet_name='Sheet1'):
        """保存到 Excel"""
        self.data.to_excel(filepath, sheet_name=sheet_name, index=False)
        print(f"✅ 已保存: {filepath}")
        return filepath
    
    def save_multiple(self, filepath, sheets_dict):
        """保存多个 sheet"""
        with pd.ExcelWriter(filepath) as writer:
            for sheet_name, df in sheets_dict.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        print(f"✅ 已保存多个工作表: {filepath}")
        return filepath
    
    # ==================== 模板生成 ====================
    
    @staticmethod
    def create_progress_tracker(filepath):
        """创建项目进度跟踪表"""
        data = {
            '任务ID': [f'T{str(i+1).zfill(3)}' for i in range(10)],
            '任务名称': [f'任务{i+1}' for i in range(10)],
            '负责人': ['张三'] * 3 + ['李四'] * 3 + ['王五'] * 4,
            '开始日期': [(datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')] * 10,
            '计划完成': [(datetime.now() + timedelta(days=i*3+5)).strftime('%Y-%m-%d') for i in range(10)],
            '状态': ['进行中'] * 3 + ['待开始'] * 7,
            '进度(%)': [30, 60, 90] + [0] * 7,
            '优先级': ['高', '高', '中'] + ['中', '中', '高', '高', '低', '低', '中'],
            '备注': [''] * 10
        }
        df = pd.DataFrame(data)
        df.to_excel(filepath, index=False)
        print(f"✅ 进度跟踪表已创建: {filepath}")
        return filepath
    
    @staticmethod
    def create_resource_allocation(filepath):
        """创建资源分配表"""
        data = {
            '资源ID': [f'R{str(i+1).zfill(3)}' for i in range(8)],
            '资源名称': [f'角色{i+1}' for i in range(8)],
            '技能': ['Python', 'Java', '测试', 'UI', '产品', '项目管理', '运维', '数据'][:8],
            '可用性(%)': [80, 100, 60, 70, 90, 50, 80, 100][:8],
            '当前项目': ['项目A', '项目A', '项目B', '项目A', '项目A', '项目A', '项目B', '项目A'][:8],
            '成本/小时': [200, 180, 150, 220, 250, 300, 200, 180][:8],
            '联系方式': [f'email{i}@company.com' for i in range(1, 9)]
        }
        df = pd.DataFrame(data)
        df.to_excel(filepath, index=False)
        print(f"✅ 资源分配表已创建: {filepath}")
        return filepath
    
    @staticmethod
    def create_risk_register(filepath):
        """创建风险登记册"""
        data = {
            '风险ID': [f'RISK{str(i+1).zfill(3)}' for i in range(5)],
            '风险描述': [f'风险{i+1}' for i in range(5)],
            '风险类别': ['技术', '人员', '需求', '进度', '外部'][:5],
            '可能性(1-5)': [3, 2, 4, 3, 2],
            '影响程度(1-5)': [4, 5, 3, 4, 5],
            '风险等级': ['高', '中', '高', '高', '中'],
            '应对策略': ['策略1', '策略2', '策略3', '策略4', '策略5'][:5],
            '责任人': ['张三'] * 5,
            '状态': ['监控中', '已缓解', '监控中', '处理中', '待定'],
            '更新日期': [datetime.now().strftime('%Y-%m-%d')] * 5
        }
        df = pd.DataFrame(data)
        df.to_excel(filepath, index=False)
        print(f"✅ 风险登记册已创建: {filepath}")
        return filepath
    
    # ==================== 报告生成 ====================
    
    def generate_summary_report(self):
        """生成数据摘要报告"""
        report = []
        report.append("# 数据摘要报告")
        report.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        report.append("")
        report.append("## 基本信息")
        report.append(f"- 总行数: {len(self.data)}")
        report.append(f"- 总列数: {len(self.data.columns)}")
        report.append(f"- 列名: {', '.join(self.data.columns)}")
        report.append("")
        report.append("## 统计摘要")
        report.append(str(self.data.describe()))
        
        report_text = '\n'.join(report)
        print(report_text)
        return report_text


# ==================== 便捷函数 ====================

def quick_read(filepath):
    """快速读取并概览"""
    processor = ExcelProcessor()
    processor.read(filepath)
    processor.info()
    return processor


def create_all_templates(output_dir):
    """创建所有项目管理模板"""
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    ExcelProcessor.create_progress_tracker(f"{output_dir}/项目进度表.xlsx")
    ExcelProcessor.create_resource_allocation(f"{output_dir}/资源分配表.xlsx")
    ExcelProcessor.create_risk_register(f"{output_dir}/风险登记册.xlsx")
    
    print(f"✅ 所有模板已创建到: {output_dir}")


if __name__ == "__main__":
    print("🧪 测试 Excel 处理器")
    
    # 测试读取
    print("\n1. 创建测试数据...")
    import os
    test_file = "/tmp/test_data.xlsx"
    ExcelProcessor.create_progress_tracker(test_file)
    
    print("\n2. 读取并分析...")
    processor = ExcelProcessor()
    processor.read(test_file)
    processor.info()
    
    print("\n3. 测试完成！")
