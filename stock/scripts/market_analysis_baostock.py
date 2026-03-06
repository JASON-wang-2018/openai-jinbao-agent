#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
市场大行情模型 - Baostock版
备用数据源：当AKShare不可用时使用

使用方法：
    python market_analysis_baostock.py
"""

import sys
import os
import baostock as bs
import pandas as pd
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

OUTPUT_DIR = '/home/jason/.openclaw/workspace/stock/reports'
os.makedirs(OUTPUT_DIR, exist_ok=True)


def get_market():
    """获取大盘指数（Baostock版）"""
    indices = [
        ("sh.000001", "上证指数"),
        ("sz.399001", "深证成指"),
        ("sz.399006", "创业板指")
    ]
    
    bs.login()
    
    result = {}
    today = datetime.now().strftime('%Y-%m-%d')
    yesterday = datetime.now().strftime('%Y-%m-%d')
    
    for code, name in indices:
        try:
            rs = bs.query_history_k_data_plus(
                code,
                "date,code,open,high,low,close,volume,amount",
                start_date='2026-02-13',
                end_date='2026-02-14',
                frequency="d",
                adjustflag="2"
            )
            
            data = []
            while (rs.error_code == '0') & rs.next():
                data = rs.get_row_data()
                break
            
            if data and len(data) >= 6:
                close = float(data[5]) if data[5] else 0
                open_price = float(data[2]) if data[2] else close
                
                if open_price > 0:
                    change = (close - open_price) / open_price * 100
                else:
                    change = 0
                
                result[name] = {
                    'close': close,
                    'open': open_price,
                    'change': change,
                    'high': float(data[3]) if data[3] else close,
                    'low': float(data[4]) if data[4] else close,
                    'volume': int(data[6]) if data[6] else 0,
                    'amount': float(data[7]) if data[7] else 0
                }
        except Exception as e:
            print(f"获取{name}失败: {e}")
    
    bs.logout()
    return result


def get_stock_list():
    """获取股票列表（Baostock版）"""
    bs.login()
    
    try:
        rs = bs.query_stock_list("a")
        data_list = []
        while (rs.error_code == '0') & rs.next():
            data_list.append(rs.get_row_data())
        return data_list
    except:
        return []
    finally:
        bs.logout()


def calculate_score(market):
    """计算市场评分"""
    score = 0
    details = {}
    
    if not market:
        return {'score': 0, 'level': '【数据异常】', 'status': '无法判断', 'details': {}}
    
    # 1. 大盘趋势 (25分)
    changes = []
    for name, data in market.items():
        changes.append(abs(data['change']))
    
    avg_change = sum(changes) / len(changes) if changes else 0
    
    if avg_change > 3:
        score += 25
        details['大盘趋势'] = ('强牛市', 25)
    elif avg_change > 1:
        score += 15
        details['大盘趋势'] = ('弱牛市', 15)
    elif avg_change > -1:
        score += 10
        details['大盘趋势'] = ('震荡市', 10)
    elif avg_change > -3:
        score += 5
        details['大盘趋势'] = ('弱熊市', 5)
    else:
        details['大盘趋势'] = ('强熊市', 0)
    
    # 2. 量能 (20分)
    total_amount = sum(data['amount'] for data in market.values())
    if total_amount > 2e12:  # >2万亿
        score += 20
        details['量能'] = ('天量', 20)
    elif total_amount > 1e12:  # >1万亿
        score += 15
        details['量能'] = ('放量', 15)
    elif total_amount > 5e11:  # >5000亿
        score += 10
        details['量能'] = ('适中', 10)
    else:
        score += 5
        details['量能'] = ('缩量', 5)
    
    # 3. 涨跌情况 (20分)
    up_count = sum(1 for data in market.values() if data['change'] > 0)
    if up_count == len(market):
        score += 20
        details['涨跌'] = ('全涨', 20)
    elif up_count > len(market) / 2:
        score += 15
        details['涨跌'] = ('多数涨', 15)
    elif up_count > 0:
        score += 10
        details['涨跌'] = ('涨跌互现', 10)
    else:
        details['涨跌'] = ('全跌', 0)
    
    # 4. 板块轮动（简化估算）(15分)
    if avg_change > 1.5:
        score += 15
        details['板块'] = ('活跃', 15)
    elif avg_change > 0.5:
        score += 10
        details['板块'] = ('一般', 10)
    else:
        details['板块'] = ('低迷', 0)
    
    # 5. 情绪指标（简化）(20分)
    if avg_change > 2:
        score += 20
        details['情绪'] = ('亢奋', 20)
    elif avg_change > 0.5:
        score += 15
        details['情绪'] = ('乐观', 15)
    elif avg_change > -0.5:
        score += 10
        details['情绪'] = ('中性', 10)
    elif avg_change > -2:
        score += 5
        details['情绪'] = ('悲观', 5)
    else:
        details['情绪'] = ('恐慌', 0)
    
    # 评级
    if score >= 80:
        level = "【强牛市】"
        status = "亢奋期"
    elif score >= 60:
        level = "【弱牛市】"
        status = "发酵期"
    elif score >= 40:
        level = "【震荡市】"
        status = "整理期"
    elif score >= 20:
        level = "【弱熊市】"
        status = "下跌期"
    else:
        level = "【强熊市】"
        status = "恐慌期"
    
    return {
        'score': score,
        'level': level,
        'status': status,
        'details': details
    }


def generate_report():
    """生成报告"""
    print("\n正在获取市场数据（Baostock）...")
    market = get_market()
    result = calculate_score(market)
    
    now = datetime.now()
    report = []
    
    report.append("=" * 70)
    report.append(f"【A股市场分析报告】- {now.strftime('%Y-%m-%d %H:%M')} (Baostock版)")
    report.append("=" * 70)
    report.append("")
    
    # 大盘
    report.append("【一、大盘概况】")
    report.append("-" * 50)
    for name, data in market.items():
        change = data['change']
        sign = '+' if change >= 0 else ''
        report.append(f"  {name}: {data['close']:.2f} ({sign}{change:.2f}%)")
        report.append(f"    开盘: {data['open']:.2f}  最高: {data['high']:.2f}  最低: {data['low']:.2f}")
        amount = data['amount'] / 1e8
        report.append(f"    成交额: {amount:.0f}亿")
    report.append("")
    
    # 量能
    total = sum(d['amount'] for d in market.values())
    report.append("【二、量能分析】")
    report.append("-" * 50)
    report.append(f"  总成交额: {total/1e12:.2f}万亿")
    report.append(f"  量能评级: {result['details'].get('量能', ('未知',0))[0]}")
    report.append("")
    
    # 评分
    report.append("【三、市场评分】")
    report.append("-" * 50)
    report.append(f"  {result['level']} {result['score']}分/100")
    report.append(f"  所处阶段: {result['status']}")
    for k, (v, s) in result['details'].items():
        report.append(f"  {k}: {v} (+{s}分)")
    report.append("")
    
    # 路径推演
    report.append("【四、后市推演】")
    report.append("-" * 50)
    if result['score'] >= 60:
        report.append("  路径一：上涨延续（55%）- 成交量配合")
        report.append("  路径二：震荡整理（35%）- 板块分化")
        report.append("  路径三：回踩确认（10%）- 情绪修复")
    elif result['score'] >= 40:
        report.append("  路径一：震荡整理（50%）- 区间波动")
        report.append("  路径二：选择方向（35%）- 需量能配合")
        report.append("  路径三：趋势延续（15%）- 跟随外盘")
    else:
        report.append("  路径一：震荡筑底（50%）- 等待契机")
        report.append("  路径二：反弹修复（30%）- 超跌反抽")
        report.append("  路径三：继续探底（20%）- 情绪低迷")
    report.append("")
    
    # 操作建议
    report.append("【五、操作建议】")
    report.append("-" * 50)
    if result['score'] >= 80:
        report.append("  仓位：70-80%")
        report.append("  策略：持股待涨，分批减仓")
        report.append("  风险：警惕高位放量滞涨")
    elif result['score'] >= 60:
        report.append("  仓位：50-70%")
        report.append("  策略：积极参与主线板块")
        report.append("  关注：券商、科技、新能源")
    elif result['score'] >= 40:
        report.append("  仓位：30-50%")
        report.append("  策略：高抛低吸，不追涨")
        report.append("  关注：板块轮动机会")
    else:
        report.append("  仓位：0-30%")
        report.append("  策略：轻仓观望，等待机会")
        report.append("  关注：超跌反弹机会")
    report.append("")
    
    report.append("=" * 70)
    report.append(f"数据来源: Baostock | {now.strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("=" * 70)
    
    return '\n'.join(report)


def main():
    print("=" * 60)
    print("市场大行情模型 - Baostock版")
    print("=" * 60)
    
    report = generate_report()
    print(report)
    
    # 保存报告
    now = datetime.now()
    filename = f"{OUTPUT_DIR}/market_baostock_{now.strftime('%Y-%m-%d')}.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\n报告已保存: {filename}")


if __name__ == '__main__':
    main()
