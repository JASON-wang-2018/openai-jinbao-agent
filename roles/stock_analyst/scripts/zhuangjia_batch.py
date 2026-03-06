#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主力坐庄流程批量分析脚本
一次性分析多只股票，判断各自处于哪个坐庄阶段

使用方法: 
  python stock/scripts/zhuangjia_batch.py --codes "600519,000001,300750"
  python stock/scripts/zhuangjia_batch.py --file stock/scripts/watchlist.txt
"""

import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime
import argparse
import os
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# 路径配置
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT_DIR = os.path.join(BASE_DIR, 'reports/zhuangjia/batch')
os.makedirs(REPORT_DIR, exist_ok=True)


def get_stock_data(code):
    """获取股票数据"""
    try:
        if code.startswith('6'):
            market = "sh"
        else:
            market = "sz"
        
        df = ak.stock_zh_a_hist(symbol=code, period="daily", start_date="20240101", adjust="qfq")
        if df is None or len(df) < 60:
            return None, "数据不足"
        
        df = df.rename(columns={
            '日期': 'date', '开盘': 'open', '收盘': 'close',
            '最高': 'high', '最低': 'low', '成交量': 'volume',
            '成交额': 'amount', '振幅': 'amplitude', '涨跌幅': 'change',
            '涨跌额': 'change_amount', '换手率': 'turnover'
        })
        df['date'] = pd.to_datetime(df['date'])
        return df.sort_values('date').reset_index(drop=True), "成功"
    except Exception as e:
        return None, str(e)


def calculate_ma(df, periods=[5, 10, 20, 60]):
    """计算均线"""
    for p in periods:
        df[f'ma{p}'] = df['close'].rolling(p).mean()
    return df


def detect_stage(df):
    """检测当前处于哪个阶段"""
    latest = df.iloc[-1]
    ma5, ma10, ma20, ma60 = latest['ma5'], latest['ma10'], latest['ma20'], latest['ma60']
    vol = latest['volume']
    vol_ma20 = df['volume'].rolling(20).mean().iloc[-1]
    
    # 计算各指标
    vol_ratio = vol / vol_ma20
    price_vs_ma20 = (latest['close'] - ma20) / ma20 * 100
    volatility = (latest['high'] - latest['low']) / latest['close']
    
    scores = {}
    
    # 吸筹建仓检测
    acc_score = 0
    if vol / df['volume'].rolling(5).mean().iloc[-1] > 0.9:
        acc_score += 25
    if volatility < 0.03:
        acc_score += 25
    if abs(ma5 - ma20) / ma20 < 0.03:
        acc_score += 25
    price_pos = (latest['close'] - df['close'].min()) / (df['close'].max() - df['close'].min() + 0.001)
    if 0.3 < price_pos < 0.7:
        acc_score += 25
    scores['吸筹建仓'] = acc_score
    
    # 洗盘整理检测
    wash_score = 0
    if vol / vol_ma20 < 0.8:
        wash_score += 30
    if latest['close'] > ma20 * 0.98:
        wash_score += 30
    lower_shadow = latest['low'] < latest['close'] * 0.99
    if lower_shadow:
        wash_score += 20
    amp_5d = df.iloc[-5:].apply(lambda x: (x['high']-x['low'])/x['close'], axis=1).mean()
    if amp_5d < 0.04:
        wash_score += 20
    scores['洗盘整理'] = wash_score
    
    # 试盘检测
    test_score = 0
    if vol_ratio > 1.5:
        test_score += 40
    upper_shadow = (latest['high'] - max(latest['open'], latest['close'])) / latest['close']
    if upper_shadow > 0.02:
        test_score += 30
    if volatility > 0.04:
        test_score += 30
    scores['试盘'] = test_score
    
    # 拉升阶段检测
    rally_score = 0
    if vol_ratio > 1.3:
        rally_score += 25
    if ma5 > ma10 > ma20:
        rally_score += 25
    change_5d = (latest['close'] - df['close'].iloc[-5]) / df['close'].iloc[-5]
    if change_5d > 0.08:
        rally_score += 25
    if latest['close'] >= df['high'].rolling(20).max().iloc[-1]:
        rally_score += 25
    scores['拉升阶段'] = rally_score
    
    # 高位派发检测
    dist_score = 0
    if vol_ratio > 1.5 and change_5d < 0.02:
        dist_score += 30
    if amp_5d > 0.05:
        dist_score += 25
    if price_vs_ma20 > 20:
        dist_score += 25
    is_bearish = latest['close'] < latest['open']
    long_shadow = (latest['high'] - max(latest['open'], latest['close'])) / latest['close'] > 0.02
    if is_bearish and long_shadow:
        dist_score += 20
    scores['高位派发'] = dist_score
    
    # 下跌出清检测
    clear_score = 0
    if ma5 < ma10 < ma20 < ma60:
        clear_score += 40
    if change_5d < -0.1:
        clear_score += 30
    if vol_ratio < 0.7:
        clear_score += 30
    scores['下跌出清'] = clear_score
    
    # 找出得分最高的阶段
    current_stage = max(scores, key=scores.get)
    max_score = scores[current_stage]
    
    return {
        '当前阶段': current_stage,
        '置信度': max_score,
        '各阶段得分': scores,
        '价格': latest['close'],
        'MA5': ma5, 'MA20': ma20, 'MA60': ma60,
        '涨跌幅': change_5d * 100,
        '量比': vol_ratio
    }


def get_stock_name(code):
    """获取股票名称"""
    return '未知'  # 跳过名称获取，加快速度


def analyze_single(code):
    """分析单只股票"""
    df, status = get_stock_data(code)
    if df is None:
        return {'code': code, 'status': '失败', 'reason': status}
    
    df = calculate_ma(df)
    result = detect_stage(df)
    name = get_stock_name(code)
    
    return {
        'code': code,
        'name': name,
        'status': '成功',
        **result
    }


def print_result(results):
    """打印结果"""
    print("\n" + "=" * 80)
    print(f"🏗️ 主力坐庄流程批量分析报告")
    print(f"📅 分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📊 分析数量: {len(results)}只")
    print("=" * 80)
    
    # 统计各阶段分布
    stage_count = {}
    success_results = [r for r in results if r['status'] == '成功']
    
    for r in success_results:
        stage = r['当前阶段']
        stage_count[stage] = stage_count.get(stage, 0) + 1
    
    print("\n【阶段分布】")
    for stage, count in sorted(stage_count.items(), key=lambda x: x[1], reverse=True):
        pct = count / len(success_results) * 100
        print(f"  {stage}: {count}只 ({pct:.1f}%)")
    
    # 按阶段分组显示
    print("\n" + "-" * 80)
    print("【详细结果】")
    print("-" * 80)
    
    # 按置信度排序
    success_results.sort(key=lambda x: x['置信度'], reverse=True)
    
    for r in success_results:
        print(f"\n{r['code']} | {r['name']}")
        print(f"  当前阶段: {r['当前阶段']} (置信度: {r['置信度']}%)")
        print(f"  最新价: {r['价格']:.2f} | 5日涨跌: {r['涨跌幅']:.1f}% | 量比: {r['量比']:.2f}")
        
        # 给出操作建议
        stage = r['当前阶段']
        if stage == '吸筹建仓':
            print("  💡 建议: 逢低分批建仓 (30%仓位)")
        elif stage == '洗盘整理':
            print("  💡 建议: 持股不动，可回调加仓 (50%仓位)")
        elif stage == '试盘':
            print("  💡 建议: 等待方向选择，突破后介入")
        elif stage == '拉升阶段':
            print("  💡 建议: 顺势持有，不轻易下车 (70%仓位)")
        elif stage == '高位派发':
            print("  ⚠️ 建议: 分批减仓，准备离场 (30%仓位)")
        elif stage == '下跌出清':
            print("  ❌ 建议: 空仓等待，不抄底")
    
    # 失败列表
    failed = [r for r in results if r['status'] == '失败']
    if failed:
        print("\n" + "-" * 80)
        print("【失败列表】")
        for r in failed:
            print(f"  {r['code']}: {r.get('reason', '未知错误')}")
    
    print("\n" + "=" * 80)


def save_results(results, filename):
    """保存结果到JSON"""
    report_path = os.path.join(REPORT_DIR, filename)
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    return report_path


def main():
    parser = argparse.ArgumentParser(description='主力坐庄流程批量分析')
    parser.add_argument('--codes', type=str, help='股票代码列表 (逗号分隔)')
    parser.add_argument('--file', type=str, help='股票代码文件路径 (每行一个代码)')
    parser.add_argument('--output', type=str, help='输出文件名 (默认: batch_YYYY-MM-DD.json)')
    parser.add_argument('--parallel', type=int, default=5, help='并行数 (默认: 5)')
    args = parser.parse_args()
    
    # 解析股票代码
    codes = []
    
    if args.codes:
        codes = [c.strip() for c in args.codes.split(',') if c.strip()]
    elif args.file:
        if os.path.exists(args.file):
            with open(args.file, 'r') as f:
                codes = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
        else:
            print(f"文件不存在: {args.file}")
            return
    else:
        print("请提供 --codes 或 --file 参数")
        print("示例: python zhuangjia_batch.py --codes '600519,000001'")
        print("示例: python zhuangjia_batch.py --file watchlist.txt")
        return
    
    print(f"🚀 开始分析 {len(codes)} 只股票...")
    
    # 并行分析
    results = []
    with ThreadPoolExecutor(max_workers=min(args.parallel, 10)) as executor:
        future_to_code = {executor.submit(analyze_single, code): code for code in codes}
        completed = 0
        for future in as_completed(future_to_code):
            completed += 1
            if completed % 10 == 0 or completed == len(codes):
                print(f"  进度: {completed}/{len(codes)} ({completed/len(codes)*100:.1f}%)")
            result = future.result()
            results.append(result)
    
    print("\n")
    
    # 打印结果
    print_result(results)
    
    # 保存结果
    if args.output:
        filename = args.output
    else:
        today = datetime.now().strftime('%Y-%m-%d')
        filename = f"batch_{today}.json"
    
    report_path = save_results(results, filename)
    print(f"\n📁 报告已保存: {report_path}")
    
    # 生成简洁版报告
    summary = []
    for r in results:
        if r['status'] == '成功':
            summary.append({
                '代码': r['code'],
                '名称': r['name'],
                '阶段': r['当前阶段'],
                '置信度': r['置信度'],
                '价格': r['价格'],
                '5日涨跌': f"{r['涨跌幅']:.1f}%"
            })
    
    summary_path = report_path.replace('.json', '_summary.txt')
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(f"主力坐庄流程分析摘要\n")
        f.write("=" * 60 + "\n")
        f.write(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"分析数量: {len(summary)}只\n\n")
        f.write("代码    名称    阶段    置信度    价格    5日涨跌\n")
        f.write("-" * 60 + "\n")
        for s in summary:
            f.write(f"{s['代码']}    {s['名称'][:4]}    {s['阶段']}    {s['置信度']}%    {s['价格']:.2f}    {s['5日涨跌']}\n")
    
    print(f"📄 摘要已保存: {summary_path}")


if __name__ == "__main__":
    main()
