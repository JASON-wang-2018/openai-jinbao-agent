#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通达信 .day 文件六维信号分析工具 v1.0

支持:
- 读取通达信 .day 二进制日线文件
- 计算六维信号 (Delta/Gamma/Vega/Theta/Alpha/Sigma)
- 综合评分 + 操作建议

使用方法:
    python3 stock_screener_greeks.py                        # 分析所有day文件
    python3 stock_screener_greeks.py --code sh000001      # 分析指定股票
    python3 stock_screener_greeks.py --dir /path/to/lday/  # 指定目录
    python3 stock_screener_greeks.py --min_score 60        # 最低评分
"""

import struct
import os
import sys
import numpy as np
from datetime import datetime
from pathlib import Path

# ========== 通达信 .day 文件格式解析 ==========

DAY_FILE_STRUCT = '<IIIIIfII'  # 小端序
DAY_FILE_FIELDS = ['date', 'open', 'high', 'low', 'close', 'amount', 'volume', 'reserved']
RECORD_SIZE = 32


def read_day_file(filepath):
    """
    读取通达信 .day 文件
    返回: list of dict, 每条记录包含 date/open/high/low/close/amount/volume
    """
    records = []
    
    with open(filepath, 'rb') as f:
        while True:
            data = f.read(RECORD_SIZE)
            if not data:
                break
            
            values = struct.unpack(DAY_FILE_STRUCT, data)
            record = {
                'date': values[0],
                'open': values[1] / 100.0,
                'high': values[2] / 100.0,
                'low': values[3] / 100.0,
                'close': values[4] / 100.0,
                'amount': values[5],
                'volume': values[6],
            }
            records.append(record)
    
    return records


def get_stock_code(filepath):
    """从文件名提取股票代码"""
    filename = os.path.basename(filepath)
    code = filename.replace('.day', '').upper()
    return code


# ========== 六维信号计算 ==========

def calc_signals(records):
    """计算六维信号"""
    if len(records) < 60:
        return None
    
    closes = np.array([r['close'] for r in records])
    volumes = np.array([r['volume'] for r in records])
    highs = np.array([r['high'] for r in records])
    lows = np.array([r['low'] for r in records])
    n = len(records)
    
    current = closes[-1]
    
    # === Delta ===
    ma10 = np.mean(closes[-10:])
    ma20 = np.mean(closes[-20:])
    ma60 = np.mean(closes[-60:])
    
    delta = 0.0
    if ma10 > ma20 > ma60: delta += 0.4
    elif ma10 < ma20 < ma60: delta -= 0.4
    if current > ma60: delta += 0.3
    elif current < ma60: delta -= 0.3
    if current > ma20: delta += 0.2
    delta = max(-1.0, min(1.0, delta))
    
    # === Gamma ===
    ch5 = (closes[-1] / closes[-6] - 1) * 100 if n >= 6 else 0
    ch5_before = (closes[-6] / closes[-11] - 1) * 100 if n >= 11 else 0
    vol5 = np.mean(volumes[-5:])
    vol10 = np.mean(volumes[-10:-5]) if n >= 10 else volumes[0]
    vol_ratio = vol5 / vol10 if vol10 > 0 else 1.0
    
    gamma = 0.0
    if ch5 > ch5_before + 2: gamma += 0.4
    elif ch5 < ch5_before - 2: gamma -= 0.4
    if vol_ratio > 1.3: gamma += 0.3
    if closes[-1] > np.max(closes[-6:-1]): gamma += 0.2
    gamma = max(-1.0, min(1.0, gamma))
    
    # === Vega ===
    # VOL比例用成交量相对均量近似
    vol120_avg = np.mean(volumes[-120:]) if n >= 120 else np.mean(volumes)
    vol_ratio_col = vol5 / vol120_avg if vol120_avg > 0 else 1.0
    
    vega = 0.0
    if vol_ratio_col >= 2: vega += 0.4
    elif vol_ratio_col >= 1: vega += 0.2
    if vol_ratio > 1.3: vega += 0.3
    elif vol_ratio < 0.7: vega -= 0.2
    vega = max(-1.0, min(1.0, vega))
    
    # === Theta ===
    theta = 0.0
    for i in range(1, min(10, n)):
        pch = (closes[i] / closes[i-1] - 1) * 100
        vr = volumes[i] / np.mean(volumes[max(0,i-5):i]) if i > 0 else 1.0
        if pch > 2 and vr > 1.3: theta += 0.15
        elif pch > 2 and vr < 0.7: theta -= 0.1
        elif pch < -2 and vr > 1.5: theta -= 0.2
        elif pch < -2 and vr < 0.7: theta += 0.1
    
    if closes[-1] >= np.max(closes[-20:]) * 0.98: theta += 0.2
    theta = max(-1.0, min(1.0, theta))
    
    # === Alpha ===
    alpha = 0.0
    if ch5 > 10: alpha += 0.3
    elif ch5 > 5: alpha += 0.2
    elif ch5 < -5: alpha -= 0.3
    if closes[-1] > np.max(closes[-11:-1]): alpha += 0.2
    if current > ma10 > ma20: alpha += 0.3
    alpha = max(-1.0, min(1.0, alpha))
    
    # === Sigma ===
    sigma = 0.3
    risk_signals = []
    
    # HV
    if n >= 20:
        returns = np.diff(np.log(closes[-20:]))
        hv = np.std(returns) * np.sqrt(250) * 100
        if hv > 40: sigma += 0.4
        elif hv > 30: sigma += 0.2
    
    # 高位滞涨
    for i in range(3, min(10, n)):
        if highs[i] > highs[i-1] > highs[i-2]:
            chs = [(closes[i-j]/closes[i-j-1]-1)*100 for j in range(1,min(4,i+1))]
            if all(0<c<2 for c in chs) and volumes[i] > volumes[i-1]*1.5:
                sigma += 0.5
                risk_signals.append('高位滞涨')
                break
    
    # 巨量阴
    for i in range(max(0,n-5), n):
        vr = volumes[i]/np.mean(volumes[max(0,i-5):i]) if i>0 else 1.0
        ch = (closes[i]/closes[i-1]-1)*100 if i>0 else 0
        if vr > 2 and ch < -5:
            sigma += 0.6
            risk_signals.append('巨量阴')
            break
    
    sigma = max(0.0, min(2.0, sigma))
    
    # === 综合评分 ===
    score = delta*20 + gamma*15 + vega*15 + theta*10 + alpha*25 + (1-sigma)*15
    if sigma > 1.0: score = min(score, 30)
    score = max(0, min(100, score))
    
    if score >= 80: grade = 'S'
    elif score >= 70: grade = 'A'
    elif score >= 60: grade = 'B'
    elif score >= 50: grade = 'C'
    else: grade = 'D'
    
    if sigma > 1.0: action = '清仓回避'
    elif grade in ['S','A']: action = '积极参与'
    elif grade == 'B': action = '择时操作'
    elif grade == 'C': action = '观望'
    else: action = '回避'
    
    # RSI 简化计算
    rsi = 50.0
    try:
        gains = []
        losses = []
        for i in range(1, min(15, n)):
            diff = closes[-i] - closes[-i-1]
            if diff > 0: gains.append(diff)
            else: losses.append(abs(diff))
        if gains and losses:
            avg_gain = np.mean(gains)
            avg_loss = np.mean(losses)
            if avg_loss > 0:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
    except:
        pass
    
    return {
        'delta': round(delta, 2),
        'gamma': round(gamma, 2),
        'vega': round(vega, 2),
        'theta': round(theta, 2),
        'alpha': round(alpha, 2),
        'sigma': round(sigma, 2),
        'score': round(score, 1),
        'grade': grade,
        'action': action,
        'risk_signals': risk_signals,
        'rsi': round(rsi, 1),
        'ch5': round(ch5, 2),
        'ma10': round(ma10, 2),
        'ma20': round(ma20, 2),
        'ma60': round(ma60, 2),
        'current': round(current, 2),
        'vol_ratio': round(vol_ratio, 2),
    }


# ========== 主程序 ==========

def analyze_day_file(filepath):
    """分析单个 .day 文件"""
    code = get_stock_code(filepath)
    records = read_day_file(filepath)
    
    if len(records) < 60:
        return None
    
    signals = calc_signals(records)
    if signals is None:
        return None
    
    last_date = records[-1]['date']
    signals['code'] = code
    signals['date'] = f"{last_date // 10000}-{last_date % 10000 // 100:02d}-{last_date % 100:02d}"
    signals['records'] = len(records)
    
    return signals


def batch_analyze(directory, min_score=50, limit=None):
    """批量分析目录下所有 .day 文件"""
    day_files = sorted(Path(directory).glob('*.day'))
    
    if limit:
        day_files = day_files[:limit]
    
    results = []
    
    for i, fpath in enumerate(day_files):
        signals = analyze_day_file(str(fpath))
        if signals and signals['score'] >= min_score:
            results.append(signals)
        
        if (i + 1) % 100 == 0:
            print(f"  已分析 {i+1}/{len(day_files)}... 通过 {len(results)}")
    
    # 排序
    results.sort(key=lambda x: -x['score'])
    
    return results


def main():
    import argparse
    parser = argparse.ArgumentParser(description='通达信 .day 文件六维信号分析')
    parser.add_argument('--code', type=str, help='指定股票代码 (如 sh000001)')
    parser.add_argument('--dir', type=str, default='/home/jason/.openclaw/exchanger/vipdoc/sh/lday',
                        help='.day 文件目录')
    parser.add_argument('--min_score', type=int, default=50, help='最低评分')
    parser.add_argument('--limit', type=int, help='最多分析数量')
    args = parser.parse_args()
    
    print("=" * 70)
    print("六维信号分析 - 通达信 .day 文件版 v1.0")
    print("=" * 70)
    
    if args.code:
        # 单个分析
        day_file = os.path.join(args.dir, f"{args.code}.day")
        if not os.path.exists(day_file):
            # 尝试自动识别 sh/sz
            for prefix in ['sh', 'sz']:
                path = os.path.join(args.dir, f"{prefix}{args.code}.day")
                if os.path.exists(path):
                    day_file = path
                    break
        
        print(f"\n分析: {args.code}")
        signals = analyze_day_file(day_file)
        
        if signals:
            print(f"\n{'='*60}")
            print(f"{signals['code']} - {signals['date']}")
            print(f"{'='*60}")
            print(f"  现价: {signals['current']}  5日涨跌: {signals['ch5']:+.2f}%  RSI: {signals['rsi']}")
            print(f"  MA10={signals['ma10']}  MA20={signals['ma20']}  MA60={signals['ma60']}")
            print()
            print(f"  Delta  = {signals['delta']:+.2f}")
            print(f"  Gamma  = {signals['gamma']:+.2f}")
            print(f"  Vega   = {signals['vega']:+.2f}")
            print(f"  Theta  = {signals['theta']:+.2f}")
            print(f"  Alpha  = {signals['alpha']:+.2f}")
            print(f"  Sigma  = {signals['sigma']:.2f}  {'⚠️ ' + ' '.join(signals['risk_signals']) if signals['risk_signals'] else ''}")
            print()
            print(f"  综合评分: {signals['score']} 分  ({signals['grade']}级)")
            print(f"  操作建议: {signals['action']}")
        else:
            print("  分析失败")
    
    else:
        # 批量分析
        print(f"\n目录: {args.dir}")
        print(f"最低评分: {args.min_score}")
        print()
        
        results = batch_analyze(args.dir, min_score=args.min_score, limit=args.limit)
        
        print(f"\n{'='*70}")
        print(f"批量分析结果 (共 {len(results)} 只通过筛选)")
        print(f"{'='*70}")
        
        if results:
            print(f"{'代码':<12} {'日期':<12} {'现价':>7} {'评分':>5} {'等级':>3} "
                  f"{'Δ':>5} {'γ':>5} {'ν':>5} {'θ':>5} {'α':>5} {'σ':>4}  {'操作':<10}")
            print("-" * 90)
            
            for r in results[:30]:
                risk = ','.join(r['risk_signals'][:1]) if r['risk_signals'] else ''
                print(f"{r['code']:<12} {r['date']:<12} {r['current']:>7.2f} {r['score']:>5.1f} {r['grade']:>3} "
                      f"{r['delta']:>+5.2f} {r['gamma']:>+5.2f} {r['vega']:>+5.2f} "
                      f"{r['theta']:>+5.2f} {r['alpha']:>+5.2f} {r['sigma']:>4.2f}  {r['action']:<10}")
            
            if len(results) > 30:
                print(f"  ... 还有 {len(results)-30} 只")
            
            print()
            print(f"信号均值: Delta={np.mean([r['delta'] for r in results]):.2f}  "
                  f"Gamma={np.mean([r['gamma'] for r in results]):.2f}  "
                  f"Alpha={np.mean([r['alpha'] for r in results]):.2f}")
        else:
            print("  没有股票通过筛选")


if __name__ == '__main__':
    main()
