#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主力坐庄流程识别脚本
识别当前股价处于哪个坐庄阶段

使用方法: python stock/scripts/zhuangjia_detector.py --code 600xxx
"""

import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime
import argparse
import os

# 路径配置
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT_DIR = os.path.join(BASE_DIR, 'reports/zhuangjia')
os.makedirs(REPORT_DIR, exist_ok=True)


def get_stock_data(code, period='daily', adjust='qfq'):
    """获取股票数据"""
    try:
        if code.startswith('6'):
            market = "sh"
        else:
            market = "sz"
        
        # 使用akshare获取日线数据
        df = ak.stock_zh_a_hist(symbol=code, period="daily", start_date="20240101", adjust=adjust)
        df = df.rename(columns={
            '日期': 'date', '开盘': 'open', '收盘': 'close',
            '最高': 'high', '最低': 'low', '成交量': 'volume',
            '成交额': 'amount', '振幅': 'amplitude', '涨跌幅': 'change',
            '涨跌额': 'change_amount', '换手率': 'turnover'
        })
        df['date'] = pd.to_datetime(df['date'])
        return df.sort_values('date').reset_index(drop=True)
    except Exception as e:
        print(f"获取数据失败: {e}")
        return None


def calculate_ma(df, periods=[5, 10, 20, 60]):
    """计算均线"""
    for p in periods:
        df[f'ma{p}'] = df['close'].rolling(p).mean()
    return df


def calculate_vol_ma(df, periods=[5, 10, 20]):
    """计算量能均线"""
    for p in periods:
        df[f'vol_ma{p}'] = df['volume'].rolling(p).mean()
    return df


def analyze_trend(df):
    """分析趋势"""
    latest = df.iloc[-1]
    
    # 均线状态
    ma5 = latest['ma5']
    ma10 = latest['ma10']
    ma20 = latest['ma20']
    ma60 = latest['ma60']
    
    # 均线排列
    if ma5 > ma10 > ma20 > ma60:
        ma_trend = "多头排列"
    elif ma5 < ma10 < ma20 < ma60:
        ma_trend = "空头排列"
    elif ma20 > ma60:
        ma_trend = "中期向上"
    elif ma20 < ma60:
        ma_trend = "中期向下"
    else:
        ma_trend = "震荡整理"
    
    # 价格位置
    price_vs_ma20 = (latest['close'] - ma20) / ma20 * 100
    price_vs_ma60 = (latest['close'] - ma60) / ma60 * 100
    
    return {
        'ma5': ma5, 'ma10': ma10, 'ma20': ma20, 'ma60': ma60,
        'ma_trend': ma_trend,
        'price_vs_ma20': price_vs_ma20,
        'price_vs_ma60': price_vs_ma60
    }


def analyze_volume(df):
    """分析量能"""
    latest = df.iloc[-1]
    avg_vol = df['volume'].rolling(20).mean().iloc[-1]
    avg_vol5 = df['volume'].rolling(5).mean().iloc[-1]
    
    vol_ratio = latest['volume'] / avg_vol
    vol_trend = df['volume'].iloc[-5:].mean() / df['volume'].iloc[-20:-5].mean()
    
    # 量价关系
    price_change = (df['close'].iloc[-1] - df['close'].iloc[-5]) / df['close'].iloc[-5]
    vol_change = (df['volume'].iloc[-1] - avg_vol) / avg_vol
    
    return {
        'vol_ratio': vol_ratio,
        'vol_trend': vol_trend,
        'avg_vol': avg_vol,
        'price_change_5d': price_change,
        'vol_change': vol_change,
        '量价关系': '量价齐升' if vol_change > 0.5 and price_change > 0.05 else
                   '放量滞涨' if vol_change > 0.5 and price_change < 0 else
                   '缩量回调' if vol_change < -0.3 and price_change < 0 else
                   '量价背离' if vol_change > 0 and price_change < 0 else '量价正常'
    }


def detect_accumulation(df):
    """
    检测吸筹建仓阶段
    
    特征:
    - 成交量温和放大
    - 股价区间震荡
    - 均线走平
    - 利好不涨,利空不跌
    """
    score = 0
    features = []
    
    # 特征1: 量能温和放大 (近5日均量 > 近20日均量)
    vol_ma5 = df['volume'].rolling(5).mean().iloc[-1]
    vol_ma20 = df['volume'].rolling(20).mean().iloc[-1]
    if vol_ma5 > vol_ma20 * 1.1:
        score += 25
        features.append("✓ 量能温和放大")
    else:
        features.append("✗ 量能未明显放大")
    
    # 特征2: 股价波动收窄
    volatility_now = (df['high'].iloc[-1] - df['low'].iloc[-1]) / df['close'].iloc[-1]
    volatility_20d = df.apply(lambda x: (x['high'] - x['low']) / x['close'], axis=1).rolling(20).mean().iloc[-1]
    if volatility_now < volatility_20d * 0.8:
        score += 25
        features.append("✓ 波动收窄")
    else:
        features.append("✗ 波动未明显收窄")
    
    # 特征3: 均线走平 (MA5≈MA20)
    ma5_ma20_diff = abs(df['ma5'].iloc[-1] - df['ma20'].iloc[-1]) / df['ma20'].iloc[-1]
    if ma5_ma20_diff < 0.03:
        score += 25
        features.append("✓ 均线走平")
    else:
        features.append("✗ 均线未走平")
    
    # 特征4: 价格在区间内震荡
    price_range = df['close'].max() - df['close'].min()
    current_vs_range = (df['close'].iloc[-1] - df['close'].min()) / price_range
    if 0.3 < current_vs_range < 0.7:
        score += 25
        features.append("✓ 价格在区间中部")
    else:
        features.append("✗ 价格位置偏")
    
    return {
        '阶段': '吸筹建仓',
        '得分': score,
        '特征': features,
        '结论': '是' if score >= 60 else '否'
    }


def detect_wash(df):
    """
    检测洗盘整理阶段
    
    特征:
    - 回调缩量
    - 不破关键支撑
    - 承接有力
    """
    score = 0
    features = []
    
    # 特征1: 近几日回调缩量
    vol_ma5 = df['volume'].rolling(5).mean().iloc[-1]
    vol_ma20 = df['volume'].rolling(20).mean().iloc[-1]
    if vol_ma5 < vol_ma20 * 0.8:
        score += 30
        features.append("✓ 回调缩量")
    else:
        features.append("✗ 回调未缩量")
    
    # 特征2: 回调不破MA20支撑
    if df['close'].iloc[-1] > df['ma20'].iloc[-1] * 0.98:
        score += 30
        features.append("✓ MA20有支撑")
    else:
        features.append("✗ 跌破MA20支撑")
    
    # 特征3: 近期有下影线企稳
    has_lower_shadow = (df['low'].iloc[-1] < df['close'].iloc[-1] * 0.99) and \
                       (df['close'].iloc[-1] > df['open'].iloc[-1])
    if has_lower_shadow:
        score += 20
        features.append("✓ 出现下影线")
    else:
        features.append("✗ 无明显下影线")
    
    # 特征4: 震荡整理形态
    high_5d = df['high'].iloc[-5:].max()
    low_5d = df['low'].iloc[-5:].min()
    if high_5d - low_5d < df['close'].iloc[-1] * 0.08:
        score += 20
        features.append("✓ 窄幅震荡")
    else:
        features.append("✗ 宽幅震荡")
    
    return {
        '阶段': '洗盘整理',
        '得分': score,
        '特征': features,
        '结论': '是' if score >= 70 else '否'
    }


def detect_test(df):
    """
    检测试盘阶段
    
    特征:
    - 突然放量异动
    - 冲高回落或突破测试
    - 上影线
    """
    score = 0
    features = []
    
    # 特征1: 今日放量
    vol_today = df['volume'].iloc[-1]
    vol_ma20 = df['volume'].rolling(20).mean().iloc[-1]
    if vol_today > vol_ma20 * 1.5:
        score += 40
        features.append("✓ 突然放量")
    else:
        features.append("✗ 量能无明显放大")
    
    # 特征2: 冲高回落 (上影线)
    upper_shadow = (df['high'].iloc[-1] - max(df['open'].iloc[-1], df['close'].iloc[-1])) / df['close'].iloc[-1]
    if upper_shadow > 0.02:
        score += 30
        features.append("✓ 冲高回落(上影线)")
    else:
        features.append("✗ 无明显上影线")
    
    # 特征3: 振幅放大
    amp_today = (df['high'].iloc[-1] - df['low'].iloc[-1]) / df['close'].iloc[-1]
    amp_20d = df.apply(lambda x: (x['high'] - x['low']) / x['close'], axis=1).rolling(20).mean().iloc[-1]
    if amp_today > amp_20d * 1.5:
        score += 30
        features.append("✓ 振幅放大")
    else:
        features.append("✗ 振幅正常")
    
    return {
        '阶段': '试盘',
        '得分': score,
        '特征': features,
        '结论': '是' if score >= 70 else '否'
    }


def detect_rally(df):
    """
    检测拉升阶段
    
    特征:
    - 量价齐升
    - 均线多头
    - 连续上涨
    """
    score = 0
    features = []
    
    # 特征1: 量价齐升
    vol_ma5 = df['volume'].rolling(5).mean().iloc[-1]
    vol_ma20 = df['volume'].rolling(20).mean().iloc[-1]
    price_change = (df['close'].iloc[-1] - df['close'].iloc[-5]) / df['close'].iloc[-5]
    
    if vol_ma5 > vol_ma20 * 1.3 and price_change > 0.08:
        score += 30
        features.append("✓ 量价齐升")
    else:
        features.append("✗ 无量价齐升")
    
    # 特征2: 均线多头排列
    if df['ma5'].iloc[-1] > df['ma10'].iloc[-1] > df['ma20'].iloc[-1]:
        score += 30
        features.append("✓ 均线多头")
    else:
        features.append("✗ 均线未多头")
    
    # 特征3: 强势上涨 (近5日涨幅>10%)
    if price_change > 0.1:
        score += 20
        features.append("✓ 强势上涨")
    else:
        features.append("✗ 涨幅不足")
    
    # 特征4: 创近20日新高
    if df['close'].iloc[-1] >= df['high'].rolling(20).max().iloc[-1]:
        score += 20
        features.append("✓ 创20日新高")
    else:
        features.append("✗ 未创新高")
    
    return {
        '阶段': '拉升阶段',
        '得分': score,
        '特征': features,
        '结论': '是' if score >= 70 else '否'
    }


def detect_distribution(df):
    """
    检测高位派发阶段
    
    特征:
    - 放量滞涨
    - 利好不涨
    - 宽幅震荡
    - 吊颈线等见顶K线
    """
    score = 0
    features = []
    
    # 特征1: 放量滞涨
    vol_ma5 = df['volume'].rolling(5).mean().iloc[-1]
    vol_ma20 = df['volume'].rolling(20).mean().iloc[-1]
    price_change_3d = (df['close'].iloc[-1] - df['close'].iloc[-3]) / df['close'].iloc[-3]
    
    if vol_ma5 > vol_ma20 * 1.5 and price_change_3d < 0.02:
        score += 30
        features.append("✓ 放量滞涨")
    else:
        features.append("✗ 无放量滞涨")
    
    # 特征2: 高位宽幅震荡
    amp_5d = df.apply(lambda x: (x['high'] - x['low']) / x['close'], axis=1).iloc[-5:].mean()
    if amp_5d > 0.05:
        score += 25
        features.append("✓ 宽幅震荡")
    else:
        features.append("✗ 震荡幅度正常")
    
    # 特征3: 价格在高位 (MA60上方20%以上)
    price_vs_ma60 = (df['close'].iloc[-1] - df['ma60'].iloc[-1]) / df['ma60'].iloc[-1]
    if price_vs_ma60 > 0.2:
        score += 25
        features.append("✓ 处于高位")
    else:
        features.append("✗ 位置不算高")
    
    # 特征4: 出现见顶K线形态
    has_top_pattern = (
        (df['close'].iloc[-1] < df['open'].iloc[-1]) and  # 阴线
        (df['high'].iloc[-1] - max(df['open'].iloc[-1], df['close'].iloc[-1])) / df['close'].iloc[-1] > 0.02  # 上影线
    )
    if has_top_pattern:
        score += 20
        features.append("✓ 出现见顶K线")
    else:
        features.append("✗ 无见顶信号")
    
    return {
        '阶段': '高位派发',
        '得分': score,
        '特征': features,
        '结论': '是' if score >= 60 else '否'
    }


def detect_clear(df):
    """
    检测下跌出清阶段
    
    特征:
    - 均线空头排列
    - 持续下跌
    - 成交量萎缩
    """
    score = 0
    features = []
    
    # 特征1: 均线空头排列
    if df['ma5'].iloc[-1] < df['ma10'].iloc[-1] < df['ma20'].iloc[-1] < df['ma60'].iloc[-1]:
        score += 40
        features.append("✓ 均线空头")
    else:
        features.append("✗ 均线未空头")
    
    # 特征2: 持续下跌 (近20日下跌)
    price_change_20d = (df['close'].iloc[-1] - df['close'].iloc[-20]) / df['close'].iloc[-20]
    if price_change_20d < -0.1:
        score += 30
        features.append("✓ 持续下跌")
    else:
        features.append("✗ 未持续下跌")
    
    # 特征3: 成交量萎缩
    vol_ma5 = df['volume'].rolling(5).mean().iloc[-1]
    vol_ma20 = df['volume'].rolling(20).mean().iloc[-1]
    if vol_ma5 < vol_ma20 * 0.7:
        score += 30
        features.append("✓ 成交量萎缩")
    else:
        features.append("✗ 成交量未明显萎缩")
    
    return {
        '阶段': '下跌出清',
        '得分': score,
        '特征': features,
        '结论': '是' if score >= 70 else '否'
    }


def main():
    parser = argparse.ArgumentParser(description='主力坐庄流程识别')
    parser.add_argument('--code', type=str, required=True, help='股票代码 (如: 600xxx)')
    args = parser.parse_args()
    
    print("=" * 60)
    print(f"🏗️ 主力坐庄流程识别")
    print(f"📌 股票代码: {args.code}")
    print("=" * 60)
    
    # 获取数据
    print("\n【数据获取中...】")
    df = get_stock_data(args.code)
    if df is None:
        print("获取数据失败，请检查股票代码")
        return
    
    # 计算指标
    df = calculate_ma(df)
    df = calculate_vol_ma(df)
    
    # 打印基本信息
    latest = df.iloc[-1]
    print(f"\n【基本信息】")
    print(f"最新价: {latest['close']:.2f}")
    print(f"MA5: {latest['ma5']:.2f} | MA20: {latest['ma20']:.2f} | MA60: {latest['ma60']:.2f}")
    print(f"今日成交量: {latest['volume']/10000:.2f}万手")
    
    # 分析各阶段
    print("\n【各阶段检测结果】")
    print("-" * 60)
    
    stages = [
        detect_accumulation(df),
        detect_wash(df),
        detect_test(df),
        detect_rally(df),
        detect_distribution(df),
        detect_clear(df)
    ]
    
    for stage in stages:
        print(f"\n{stage['阶段']}:")
        for f in stage['特征']:
            print(f"  {f}")
        print(f"  得分: {stage['得分']}/100 → {stage['结论']}")
    
    # 确定当前阶段
    active_stages = [s for s in stages if s['结论'] == '是']
    
    print("\n" + "=" * 60)
    print("【最终结论】")
    print("-" * 60)
    
    if active_stages:
        # 按得分排序
        active_stages.sort(key=lambda x: x['得分'], reverse=True)
        current = active_stages[0]
        print(f"🔍 当前阶段: {current['阶段']}")
        print(f"📊 置信度: {current['得分']}%")
        
        # 给出建议
        print("\n【操作建议】")
        if current['阶段'] == '吸筹建仓':
            print("  ✓ 策略: 逢低分批建仓")
            print("  ✓ 仓位: 30%")
            print("  ✓ 原则: 不追高、保持耐心")
        elif current['阶段'] == '洗盘整理':
            print("  ✓ 策略: 持股不动、回调加仓")
            print("  ✓ 仓位: 50%")
            print("  ✓ 原则: 不被洗出")
        elif current['阶段'] == '试盘':
            print("  ✓ 策略: 观察方向选择")
            print("  ✓ 仓位: 等待确认")
            print("  ✓ 原则: 等待突破确认")
        elif current['阶段'] == '拉升阶段':
            print("  ✓ 策略: 顺势而为、沿均线持有")
            print("  ✓ 仓位: 70%")
            print("  ✓ 原则: 不轻易下车")
        elif current['阶段'] == '高位派发':
            print("  ⚠ 策略: 分批减仓、准备离场")
            print("  ⚠ 仓位: 30%")
            print("  ⚠ 原则: 不追高")
        elif current['阶段'] == '下跌出清':
            print("  ✗ 策略: 空仓等待")
            print("  ✗ 仓位: 0%")
            print("  ✗ 原则: 不抄底")
    else:
        print("🔍 当前阶段: 暂无明确信号")
        print("📊 建议: 继续观察，等待信号确认")
    
    # 保存报告
    today = datetime.now().strftime('%Y-%m-%d')
    report_path = os.path.join(REPORT_DIR, f'{args.code}_{today}.txt')
    os.makedirs(REPORT_DIR, exist_ok=True)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f"🏗️ 主力坐庄流程识别报告\n")
        f.write(f"代码: {args.code} | 日期: {today}\n")
        f.write("=" * 60 + "\n")
        f.write(f"当前阶段: {active_stages[0]['阶段'] if active_stages else '未知'}\n")
        f.write(f"置信度: {active_stages[0]['得分'] if active_stages else 0}%\n")
    
    print(f"\n📁 报告已保存: {report_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
