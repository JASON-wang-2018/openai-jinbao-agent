#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股模式快速分析脚本

使用方法:
    python scripts/analyze_pattern.py --code 002642
    python scripts/analyze_pattern.py --code 000001 --save
"""

import sys
import os
import requests
import argparse
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from stock.analysis.patterns.pattern_detector import PatternDetector, format_report


def get_stock_data(symbol: str) -> object:
    """获取股票数据"""
    try:
        # 使用新浪K线接口
        url = f"https://finance.sina.com.cn/realstock/company/sz{symbol}/hisdata/klc_kl.js"
        if symbol.startswith('6'):
            url = f"https://finance.sina.com.cn/realstock/company/sh{symbol}/hisdata/klc_kl.js"
        
        resp = requests.get(url, timeout=15)
        text = resp.text
        start = text.find('[')
        end = text.rfind(']') + 1
        data = eval(text[start:end])
        
        import pandas as pd
        df = pd.DataFrame(data[-60:], columns=['日期','开盘','收盘','最高','最低','成交量','成交额','振幅','涨跌幅','涨跌额','换手率'])
        df['close'] = df['收盘'].astype(float)
        df['open'] = df['开盘'].astype(float)
        df['high'] = df['最高'].astype(float)
        df['low'] = df['最低'].astype(float)
        df['volume'] = df['成交量'].astype(float)
        
        return df.iloc[::-1]
    except Exception as e:
        print(f"获取数据失败: {e}")
        return None


def get_stock_name(symbol: str) -> str:
    """获取股票名称"""
    try:
        url = f"https://hq.sinajs.cn/list=sz{symbol}" if not symbol.startswith('6') else f"https://hq.sinajs.cn/list=sh{symbol}"
        resp = requests.get(url, headers={'Referer':'https://finance.sina.com.cn'}, timeout=10)
        return resp.text.split('"')[1].split(',')[0]
    except:
        return "未知"


def main():
    parser = argparse.ArgumentParser(description='A股模式快速分析')
    parser.add_argument('--code', required=True, help='股票代码')
    parser.add_argument('--save', action='store_true', help='保存报告')
    
    args = parser.parse_args()
    
    print("=" * 70)
    print(f"正在分析 {args.code}...")
    print("=" * 70)
    
    # 获取数据
    df = get_stock_data(args.code)
    
    if df is not None and len(df) >= 20:
        name = get_stock_name(args.code)
        print(f"\n股票: {name} ({args.code})")
        
        # 运行分析
        detector = PatternDetector()
        result = detector.analyze(df)
        
        # 输出报告
        print(format_report(result))
        
        # 保存
        if args.save:
            filename = f"pattern_{args.code}_{datetime.now().strftime('%Y%m%d')}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"股票: {name} ({args.code})\n")
                f.write(format_report(result))
            print(f"\n报告已保存: {filename}")
    else:
        print("数据获取失败或不足")


if __name__ == '__main__':
    main()
