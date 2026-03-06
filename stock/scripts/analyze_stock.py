#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
个股分析报告生成器
基于6步技术分析工作流

使用方法:
    python analyze_stock.py --code 002642          # 分析单只
    python analyze_stock.py --code 002642 --save    # 分析并保存
    python analyze_stock.py --code 002642 000001    # 多只对比
    python analyze_stock.py --scan --limit 50       # 盘中快速扫描
"""

import sys
import os
import argparse
import requests
from datetime import datetime
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from stock.analysis.technical_analysis import 完整技术分析, 快速分析


def get_stock_data(symbol):
    """获取股票历史数据"""
    try:
        # 新浪K线数据
        if symbol.startswith('6'):
            url = f"https://finance.sina.com.cn/realstock/company/sh{symbol}/hisdata/klc_kl.js"
        else:
            url = f"https://finance.sina.com.cn/realstock/company/sz{symbol}/hisdata/klc_kl.js"
        
        resp = requests.get(url, timeout=15)
        text = resp.text
        
        # 解析JS数据
        start = text.find('[')
        end = text.rfind(']') + 1
        data = eval(text[start:end])
        
        # 转换为DataFrame
        df = pd.DataFrame(data, columns=['日期', '开盘', '收盘', '最高', '最低', '成交量', '成交额', '振幅', '涨跌幅', '涨跌额', '换手率'])
        
        df['open'] = df['开盘'].astype(float)
        df['close'] = df['收盘'].astype(float)
        df['high'] = df['最高'].astype(float)
        df['low'] = df['最低'].astype(float)
        df['volume'] = df['成交量'].astype(float)
        
        return df.iloc[::-1]  # 升序排列
        
    except Exception as e:
        print(f"获取 {symbol} 数据失败: {e}")
        return None


def get_stock_name(symbol):
    """获取股票名称"""
    try:
        url = f"https://hq.sinajs.cn/list=sz{symbol}" if not symbol.startswith('6') else f"https://hq.sinajs.cn/list=sh{symbol}"
        resp = requests.get(url, headers={'Referer': 'https://finance.sina.com.cn'}, timeout=10)
        name = resp.text.split('"')[1].split(',')[0]
        return name
    except:
        return "未知"


def generate_report(stock_code, df):
    """生成分析报告"""
    # 获取股票名称
    name = get_stock_name(stock_code)
    
    # 获取并处理数据
    if df is None:
        df = get_stock_data(stock_code)
    
    if df is None or len(df) < 30:
        return None
    
    # 运行分析
    result = 完整技术分析(stock_code, df)
    
    # 格式化输出
    report = f"""
═══════════════════════════════════════════════════════════════════════
【{stock_code}】{name} - 技术分析报告 - {datetime.now().strftime('%Y-%m-%d %H:%M')}
═══════════════════════════════════════════════════════════════════════

【一、综合判断】
该股目前处于【{result['stage']}】阶段，
均线结构【{result['ma_structure']}】，
量价关系【{result['volume_price']}】，
主力行为偏向【{result['main_force']}】。

【二、多维分析结果】
├─ 均线结构（{result['ma_structure']}）：{result['ma_structure']}
├─ 量价关系（{result['volume_price']}）：{result['volume_price']}
├─ K线形态：{result['volume_price']}
├─ 主力行为（{result['main_force']}）：{result['main_force']}
└─ 板块环境：板块数据待接入

【三、综合评分】{result['score']}分/100 → {result['level']}

【四、关键位】
├─ 支撑位：{list(result['supports'].values()) if result['supports'] else '计算中'}
└─ 压力位：{list(result['resistances'].values()) if result['resistances'] else '计算中'}

【五、走势推演】
├─ 主升延续（{result['paths']['主升延续']['概率']}%）：{result['paths']['主升延续']['条件']}
├─ 震荡洗盘（{result['paths']['震荡洗盘']['概率']}%）：{result['paths']['震荡洗盘']['条件']}
└─ 趋势破坏（{result['paths']['趋势破坏']['概率']}%）：{result['paths']['趋势破坏']['条件']}

【六、主力意图推断】
当前更符合【{result['main_force']}】模型。

【七、操作建议】
├─ 空仓者：{result['level']}，建议{'积极参与' if result['score'] >= 60 else '观望等待'}
├─ 轻仓者：{'回调加仓' if result['score'] >= 60 else '谨慎操作'}
└─ 重仓者：【以支撑位为止损参考】

【八、风控要点】
├─ 关键支撑：{list(result['supports'].values())[0] if result['supports'] else '待计算'}
├─ 止损位：【跌破{list(result['supports'].values())[0] if result['supports'] else '5%'}纪律止损】
└─ 止盈策略：【涨幅超20%分批止盈，跌破5日均线清仓】

═══════════════════════════════════════════════════════════════════════
"""
    return report


def main():
    parser = argparse.ArgumentParser(description='个股分析报告生成器')
    parser.add_argument('--code', nargs='+', help='股票代码，如：002642')
    parser.add_argument('--save', action='store_true', help='保存报告到文件')
    parser.add_argument('--scan', action='store_true', help='快速扫描模式')
    parser.add_argument('--limit', type=int, default=20, help='扫描数量限制')
    
    args = parser.parse_args()
    
    if not args.code and not args.scan:
        print("请指定股票代码，或使用 --scan 进行快速扫描")
        print("示例: python analyze_stock.py --code 002642")
        return
    
    if args.scan:
        # 快速扫描模式
        print("=" * 60)
        print("【快速扫描模式】")
        print("=" * 60)
        print("\n注：快速扫描需要先获取股票列表...")
        print("建议使用: python analyze_stock.py --code 002642")
        return
    
    # 单只或多只分析
    for code in args.code:
        print("\n" + "=" * 60)
        print(f"正在分析 {code}...")
        print("=" * 60)
        
        report = generate_report(code, None)
        
        if report:
            print(report)
            
            # 保存报告
            if args.save:
                filename = f"report_{code}_{datetime.now().strftime('%Y%m%d')}.txt"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(report)
                print(f"\n报告已保存: {filename}")
        else:
            print(f"\n{code} 数据获取失败")


if __name__ == '__main__':
    main()
