#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日股票复盘报告 - 定时任务
每天 8:00 和 21:00 执行
"""

import sys
import os
import requests
from datetime import datetime

OUTPUT_DIR = '/home/jason/.openclaw/workspace/stock/reports'
os.makedirs(OUTPUT_DIR, exist_ok=True)


def is_trading_day():
    """判断是否为交易日"""
    now = datetime.now()
    # 周末休市
    if now.weekday() >= 5:
        return False
    return True


def get_market():
    """获取大盘数据"""
    if not is_trading_day():
        return None
    
    try:
        # 上证指数
        sh = requests.get(
            "https://push2.eastmoney.com/api/qt/stock/get",
            params={'fields': 'f2,f3', 'secid': '1.000001'},
            timeout=10
        ).json()
        
        # 深证成指
        sz = requests.get(
            "https://push2.eastmoney.com/api/qt/stock/get",
            params={'fields': 'f2,f3', 'secid': '0.399001'},
            timeout=10
        ).json()
        
        # 创业板
        cy = requests.get(
            "https://push2.eastmoney.com/api/qt/stock/get",
            params={'fields': 'f2,f3', 'secid': '0.399006'},
            timeout=10
        ).json()
        
        result = {}
        if sh.get('data'):
            result['上证指数'] = (sh['data']['f2'], sh['data']['f3'])
        if sz.get('data'):
            result['深证成指'] = (sz['data']['f2'], sz['data']['f3'])
        if cy.get('data'):
            result['创业板指'] = (cy['data']['f2'], cy['data']['f3'])
        
        return result if result else None
    except Exception as e:
        print(f"获取失败: {e}")
        return None


def get_hot():
    """获取热点板块（节流备用）"""
    if not is_trading_day():
        return []
    return []


def main():
    now = datetime.now()
    report_type = '早盘' if now.hour < 12 else '晚间'
    
    if not is_trading_day():
        print(f"\n今日 {now.strftime('%Y-%m-%d %H:%M')} ({report_type})")
        print("股市休市中（周末/节假日）")
        return
    
    print(f"\n正在生成{report_type}复盘报告...")
    
    market = get_market()
    
    if market is None:
        print("数据获取失败")
        return
    
    lines = []
    lines.append("=" * 60)
    lines.append(f"【A股复盘报告】- {now.strftime('%Y-%m-%d %H:%M')} ({report_type})")
    lines.append("=" * 60)
    lines.append("")
    lines.append("【一、大盘】")
    for name, (price, change) in market.items():
        sign = '+' if change >= 0 else ''
        lines.append(f"  {name}: {price:.2f} ({sign}{change:.2f}%)")
    lines.append("")
    lines.append("【二、北向资金】")
    lines.append("  (请查看龙虎榜)")
    lines.append("")
    lines.append("【三、热点板块】")
    lines.append("  (请使用券商APP)")
    lines.append("")
    lines.append("=" * 60)
    
    report = '\n'.join(lines)
    print(report)
    
    filename = f"{OUTPUT_DIR}/report_{now.strftime('%Y-%m-%d')}_{'am' if now.hour < 12 else 'pm'}.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\n已保存: {filename}")


if __name__ == '__main__':
    main()
