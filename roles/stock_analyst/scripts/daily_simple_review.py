#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
晚间复盘脚本 - 低Token消耗版
每日执行一次，自动复盘并保存简短报告

原则: 最少Token，仅获取数据 + 简单判断
"""

import akshare as ak
import pandas as pd
from datetime import datetime
import os

# 路径配置
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT_DIR = os.path.join(BASE_DIR, 'reports/daily')
os.makedirs(REPORT_DIR, exist_ok=True)

today = datetime.now().strftime('%Y-%m-%d')
report_file = os.path.join(REPORT_DIR, f'report_{today}.txt')


def get_market_data():
    """获取最简市场数据"""
    try:
        # 上证指数
        df = ak.stock_zh_index_daily(symbol="sh000001")
        close = df['close'].iloc[-1]
        ma10 = df['close'].rolling(10).mean().iloc[-1]
        ma20 = df['close'].rolling(20).mean().iloc[-1]
        ma60 = df['close'].rolling(60).mean().iloc[-1]
        
        return {
            'close': close,
            'ma10': ma10,
            'ma20': ma20,
            'ma60': ma60,
            'index_trend': ma20 > ma60 and close > ma10
        }
    except:
        return None


def get_zt_count():
    """获取涨停家数"""
    try:
        df = ak.stock_zt_pool_em(date=today)
        return len(df)
    except:
        return 0


def main():
    """主程序 - 极简复盘"""
    lines = []
    lines.append("="*60)
    lines.append(f"📅 晚间复盘 - {today}")
    lines.append("="*60)
    
    # 1. 指数数据
    lines.append("\n【一、指数】")
    market = get_market_data()
    if market:
        lines.append(f"  收盘: {market['close']:.2f}")
        lines.append(f"  MA10: {market['ma10']:.2f} | MA20: {market['ma20']:.2f} | MA60: {market['ma60']:.2f}")
        lines.append(f"  强趋势: {'是' if market['index_trend'] else '否'}")
    else:
        lines.append("  数据获取失败")
    
    # 2. 情绪数据
    lines.append("\n【二、情绪】")
    zt_count = get_zt_count()
    lines.append(f"  涨停: {zt_count}家")
    
    # 3. 系统判断
    lines.append("\n【三、系统信号】")
    if market and market['index_trend'] and zt_count >= 50:
        lines.append("  主升系统: ✅ 触发")
        action = "可开仓"
    elif zt_count < 30:
        lines.append("  冰点系统: ⚠️ 观察")
        action = "轻仓试错"
    else:
        lines.append("  系统: ❌ 无信号")
        action = "空仓等待"
    
    # 4. 操作建议
    lines.append("\n【四、操作】")
    lines.append(f"  建议: {action}")
    
    # 5. 次日关注
    lines.append("\n【五、关注】")
    lines.append("  观察: 指数能否站稳MA10")
    lines.append("  关注: 成交量能否放大")
    lines.append("  关注: 主线板块能否形成")
    
    lines.append("\n" + "="*60)
    lines.append(f"⏰ 复盘时间: {datetime.now().strftime('%H:%M:%S')}")
    lines.append("="*60)
    
    # 保存报告
    report = '\n'.join(lines)
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    # 打印简洁版
    print(f"\n📊 复盘完成: {today}")
    print(f"📁 报告: {report_file}")
    print(f"\n操作: {action}")


if __name__ == "__main__":
    main()
