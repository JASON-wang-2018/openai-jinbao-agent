#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文本处理专家 - 主程序入口
集成 Excel、Word、PPT 处理器和文档转换器
"""

import sys
import os
from pathlib import Path

# 添加 scripts 目录到路径
SCRIPT_DIR = Path(__file__).parent

# 导入处理器
from excel_processor import ExcelProcessor
from word_processor import WordProcessor
from ppt_processor import PPTProcessor
from document_converter import DocumentConverter


class TextProcessor:
    """文本处理专家主类"""
    
    def __init__(self):
        self.excel = ExcelProcessor()
        self.word = WordProcessor()
        self.ppt = PPTProcessor()
        self.converter = DocumentConverter()
    
    # ==================== Excel 快捷方法 ====================
    
    def read_excel(self, filepath):
        """读取 Excel"""
        self.excel.read(filepath)
        return self.excel
    
    def analyze_excel(self, filepath):
        """分析 Excel"""
        self.excel.read(filepath)
        self.excel.info()
        return self.excel
    
    def create_excel_template(self, template_type, output_path):
        """创建 Excel 模板"""
        if template_type == 'progress':
            ExcelProcessor.create_progress_tracker(output_path)
        elif template_type == 'resource':
            ExcelProcessor.create_resource_allocation(output_path)
        elif template_type == 'risk':
            ExcelProcessor.create_risk_register(output_path)
        return output_path
    
    # ==================== Word 快捷方法 ====================
    
    def create_word(self):
        """创建 Word 文档"""
        self.word.create()
        return self.word
    
    def create_project_report(self, output_path, project_info, progress_data):
        """创建项目报告"""
        return WordProcessor.create_project_report(output_path, project_info, progress_data)
    
    def create_weekly_report(self, output_path, week_info):
        """创建周报"""
        return WordProcessor.create_weekly_report(output_path, week_info)
    
    # ==================== PPT 快捷方法 ====================
    
    def create_ppt(self):
        """创建 PPT"""
        self.ppt.create()
        return self.ppt
    
    def create_weekly_ppt(self, output_path, week_info):
        """创建周报 PPT"""
        return PPTProcessor.create_weekly_report(output_path, week_info)
    
    def create_project_ppt(self, output_path, project_info):
        """创建项目报告 PPT"""
        return PPTProcessor.create_project_report(output_path, project_info)
    
    # ==================== 转换快捷方法 ====================
    
    def convert(self, input_path, output_path, convert_type=None):
        """文件转换"""
        suffix = Path(input_path).suffix.lower()
        
        if convert_type == 'excel2csv' or suffix in ['.xlsx', '.xls']:
            if suffix in ['.xlsx', '.xls']:
                if output_path.endswith('.csv'):
                    return DocumentConverter.excel_to_csv(input_path, output_path)
                elif output_path.endswith('.json'):
                    return DocumentConverter.excel_to_json(input_path, output_path)
                elif output_path.endswith('.md'):
                    return DocumentConverter.excel_to_markdown(input_path, output_path)
        
        elif convert_type == 'csv2excel' or suffix == '.csv':
            if output_path.endswith('.xlsx'):
                return DocumentConverter.csv_to_excel(input_path, output_path)
        
        elif suffix == '.json':
            if output_path.endswith('.xlsx'):
                return DocumentConverter.json_to_excel(input_path, output_path)
        
        return None
    
    def batch_convert(self, input_dir, output_dir, format='csv'):
        """批量转换"""
        return DocumentConverter.batch_excel_to_csv(input_dir, output_dir)


# ==================== 帮助信息 ====================

def show_help():
    print("""
╔══════════════════════════════════════════════════════════════╗
║                    文本处理专家 - 使用指南                      ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  【Excel 处理】                                              ║
║    processor.read_excel('file.xlsx')                         ║
║    processor.analyze_excel('file.xlsx')                      ║
║    processor.create_excel_template('progress', 'out.xlsx')   ║
║                                                              ║
║  【Word 处理】                                               ║
║    processor.create_word()                                   ║
║    processor.create_project_report('out.docx', info, data)  ║
║    processor.create_weekly_report('out.docx', info)        ║
║                                                              ║
║  【PPT 处理】                                                ║
║    processor.create_ppt()                                   ║
║    processor.create_weekly_ppt('out.pptx', info)           ║
║    processor.create_project_ppt('out.pptx', info)          ║
║                                                              ║
║  【格式转换】                                                ║
║    processor.convert('file.xlsx', 'out.csv')                ║
║    processor.batch_convert('input_dir', 'output_dir')       ║
║                                                              ║
║  【命令行用法】                                              ║
║    python main.py excel <file>          # 分析 Excel        ║
║    python main.py template <type> <out> # 创建模板           ║
║    python main.py convert <in> <out>    # 转换文件           ║
║    python main.py help                 # 显示帮助           ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)


# ==================== 命令行入口 ====================

if __name__ == "__main__":
    processor = TextProcessor()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'help':
            show_help()
        
        elif command == 'excel':
            if len(sys.argv) > 2:
                processor.analyze_excel(sys.argv[2])
            else:
                print("⚠️ 请指定 Excel 文件")
        
        elif command == 'template':
            if len(sys.argv) > 3:
                template_type = sys.argv[2]
                output_path = sys.argv[3]
                processor.create_excel_template(template_type, output_path)
            else:
                print("⚠️ 用法: python main.py template <type> <output>")
                print("   类型: progress, resource, risk")
        
        elif command == 'convert':
            if len(sys.argv) > 3:
                input_path = sys.argv[2]
                output_path = sys.argv[3]
                result = processor.convert(input_path, output_path)
                if result:
                    print(f"✅ 转换完成: {result}")
                else:
                    print("⚠️ 转换失败或格式不支持")
            else:
                print("⚠️ 用法: python main.py convert <input> <output>")
        
        else:
            print(f"⚠️ 未知命令: {command}")
            print("使用 'python main.py help' 查看帮助")
    else:
        show_help()
