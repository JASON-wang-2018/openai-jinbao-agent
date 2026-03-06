#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
老股民警个股分析模型 v2.0 - 升级版
新增：倍量识别、主力行为分析

使用方法: python stock/scripts/stock_analysis_v2.py --code 600519
"""

import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime
import argparse
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT_DIR = os.path.join(BASE_DIR, 'reports/stock_analysis')
os.makedirs(REPORT_DIR, exist_ok=True)


def get_stock_data(code):
    try:
        df = ak.stock_zh_a_hist(symbol=code, period="daily", start_date="20240101", adjust="qfq")
        if df is None or len(df) < 60:
            return None, "数据不足"
        df = df.rename(columns={'日期': 'date', '开盘': 'open', '收盘': 'close',
            '最高': 'high', '最低': 'low', '成交量': 'volume'})
        df['date'] = pd.to_datetime(df['date'])
        return df.sort_values('date').reset_index(drop=True), "成功"
    except Exception as e:
        return None, str(e)


def calculate_indicators(df):
    df = df.copy()
    # 均线
    for p in [5, 10, 20, 60]:
        df[f'ma{p}'] = df['close'].rolling(p).mean()
    # 量能均线
    df['vol_ma5'] = df['volume'].rolling(5).mean()
    df['vol_ma20'] = df['volume'].rolling(20).mean()
    # 量比
    df['vol_ratio'] = df['volume'] / df['vol_ma20']
    # 倍量标记
    df['倍量'] = df['vol_ratio'] >= 2.0
    df['巨量'] = df['vol_ratio'] >= 3.0
    # 涨跌幅
    df['change_5d'] = (df['close'] - df['close'].shift(5)) / df['close'].shift(5)
    return df


def analyze_volume_pattern(df):
    """分析成交量模式 - 倍量识别"""
    latest = df.iloc[-1]
    
    # 统计近60天的倍量/巨量次数
    last_60 = df.tail(60)
    倍量次数 = last_60['倍量'].sum()
    巨量次数 = last_60['巨量'].sum()
    
    # 倍量日期
    倍量_dates = df[df['倍量'] == True].tail(5)
    
    # 近3次倍量后的走势
    recent_bei_liang = []
    for i in range(len(df)-1, max(len(df)-6, 0), -1):
        if df.iloc[i]['倍量']:
            future_3d = df.iloc[min(i+1, len(df)-1):min(i+4, len(df))]
            avg_change = future_3d['close'].pct_change().mean() * 100
            recent_bei_liang.append({
                'date': str(df.iloc[i]['date'])[:10],
                'vol_ratio': df.iloc[i]['vol_ratio'],
                'future_change': avg_change
            })
    
    return {
        '倍量次数': int(倍量次数),
        '巨量次数': int(巨量次数),
        '当前量比': latest['vol_ratio'],
        'recent_bei_liang': recent_bei_liang[:3]
    }


def analyze_main_force(df):
    """分析主力行为"""
    latest = df.iloc[-1]
    vol_ratio = latest['vol_ratio']
    change = latest.get('change_5d', 0) or 0
    
    # 主力行为判断
    if change > 0 and vol_ratio >= 2.0:
        behavior = "主动拉升"
        score = 20
    elif change > 0 and vol_ratio >= 1.5:
        behavior = "温和上涨"
        score = 15
    elif change > 0 and vol_ratio < 0.8:
        behavior = "缩量上涨-诱多可能"
        score = 8
    elif change < 0 and vol_ratio >= 2.0:
        behavior = "放量下跌-出货可能"
        score = 5
    elif change < 0 and vol_ratio < 0.7:
        behavior = "缩量回调-洗盘特征"
        score = 15
    else:
        behavior = "观望"
        score = 10
    
    return {'behavior': behavior, 'score': score, 'vol_ratio': vol_ratio}


def analyze(code):
    df, status = get_stock_data(code)
    if df is None:
        return {"error": status}
    
    df = calculate_indicators(df)
    latest = df.iloc[-1]
    
    ma5, ma10, ma20, ma60 = latest['ma5'], latest['ma10'], latest['ma20'], latest['ma60']
    close = latest['close']
    vol_ratio = latest['vol_ratio']
    
    # 1. 均线结构
    if ma5 > ma10 > ma20 > ma60:
        ma_structure = "多头排列"
        ma_score = 20
    elif ma5 < ma10 < ma20 < ma60:
        ma_structure = "空头排列"
        ma_score = 0
    else:
        ma_structure = "震荡整理"
        ma_score = 10
    
    # 2. 位置
    low_60d = df['low'].min()
    high_60d = df['high'].max()
    price_pos = (close - low_60d) / (high_60d - low_60d + 0.001)
    pos_label = "低位" if price_pos < 0.3 else ("高位" if price_pos > 0.7 else "中位")
    
    # 3. 阶段判断
    if ma5 > ma20 and vol_ratio > 1.3 and latest['change_5d'] > 0.05:
        stage = "主升浪"
    elif ma5 > ma20 and vol_ratio < 0.8:
        stage = "洗盘整理"
    elif price_pos < 0.3:
        stage = "吸筹建仓"
    elif price_pos > 0.8 and vol_ratio > 1.5:
        stage = "高位派发"
    else:
        stage = "震荡整理"
    
    # 4. 倍量分析
    vol_pattern = analyze_volume_pattern(df)
    
    # 5. 主力行为
    main_force = analyze_main_force(df)
    
    # 6. 综合评分
    change_5d = latest.get('change_5d', 0) or 0
    
    vol_score = 25 if (change_5d > 0 and vol_ratio > 1.2) else (15 if vol_ratio < 0.8 else 10)
    kline_score = 10
    main_score = main_force['score']
    
    total = ma_score + vol_score + kline_score + main_score + 15
    rating = "强势主升" if total >= 80 else ("可操作" if total >= 60 else ("观望" if total >= 40 else "风险"))
    
    return {
        'code': code,
        'close': close,
        'ma5': ma5, 'ma10': ma10, 'ma20': ma20, 'ma60': ma60,
        'ma_structure': ma_structure,
        'ma_score': ma_score,
        'pos_label': pos_label,
        'pos_pct': price_pos * 100,
        'stage': stage,
        'vol_pattern': vol_pattern,
        'main_force': main_force,
        'total': total,
        'rating': rating,
        'change_5d': change_5d * 100
    }


def print_report(r):
    if "error" in r:
        print(f"错误: {r['error']}")
        return
    
    print(f"\n{'='*70}")
    print(f"【{r['code']}】老股民警技术分析报告 v2.0 (升级版)")
    print(f"{'='*70}")
    
    print(f"\n【一、综合判断】")
    print(f"  阶段: {r['stage']} | 均线: {r['ma_structure']} | 位置: {r['pos_label']}({r['pos_pct']:.0f}%)")
    print(f"  收盘: {r['close']:.2f} | MA5: {r['ma5']:.2f} | MA20: {r['ma20']:.2f}")
    
    print(f"\n【二、倍量分析】(新增)")
    vp = r['vol_pattern']
    print(f"  60日倍量次数: {vp['倍量次数']}次")
    print(f"  60日巨量次数: {vp['巨量次数']}次")
    print(f"  当前量比: {vp['当前量比']:.2f}x")
    
    print(f"\n【三、主力行为分析】(新增)")
    mf = r['main_force']
    print(f"  行为判断: {mf['behavior']}")
    print(f"  得分: {mf['score']}/20")
    print(f"  量比: {mf['vol_ratio']:.2f}x")
    
    print(f"\n【四、综合评分】 {r['total']}分 → 【{r['rating']}】")
    
    print(f"\n【五、操作建议】")
    if r['stage'] == "主升浪":
        print("  建议: 顺势持有")
    elif r['stage'] == "洗盘整理":
        print("  建议: 回调企稳可加仓")
    elif r['stage'] == "吸筹建仓":
        print("  建议: 分批建仓")
    else:
        print("  建议: 观望等待")
    
    print(f"\n{'='*70}")


def main():
    parser = argparse.ArgumentParser(description='老股民警v2.0分析(升级版)')
    parser.add_argument('--code', required=True, help='股票代码')
    args = parser.parse_args()
    
    result = analyze(args.code)
    print_report(result)


if __name__ == "__main__":
    main()
