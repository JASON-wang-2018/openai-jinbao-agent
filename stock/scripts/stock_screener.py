#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
精选股池筛选器 - 双系统模型 v1.0
基于六层过滤体系，从全市场筛选符合主升系统条件的股票

使用说明:
    python3 stock/scripts/stock_screener.py              # 筛选今日
    python3 stock/scripts/stock_screener.py --date=2026-04-23  # 指定日期
    python3 stock/scripts/stock_screener.py --strict            # 严格模式(全6层)
    python3 stock/scripts/stock_screener.py --sector=半导体       # 指定板块
"""

import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
import json
import os
import sys

warnings.filterwarnings('ignore')

# ========== 配置 ==========
REPORT_DIR = os.path.join(os.path.dirname(__file__), '../reports/screener')
os.makedirs(REPORT_DIR, exist_ok=True)

CACHE_DIR = os.path.join(os.path.dirname(__file__), '../data/cache')
os.makedirs(CACHE_DIR, exist_ok=True)

# ========== 第一层：指数强趋势 ==========
def get_index_trend():
    """获取上证指数趋势，判断是否满足开仓条件"""
    try:
        df = ak.stock_zh_index_daily(symbol="sh000001")
        df = df.tail(80).sort_values('date')
        
        ma10 = df['close'].rolling(10).mean().iloc[-1]
        ma20 = df['close'].rolling(20).mean().iloc[-1]
        ma60 = df['close'].rolling(60).mean().iloc[-1]
        current = df['close'].iloc[-1]
        
        strong_trend = (ma20 > ma60) and (current > ma10)
        
        return {
            'index': '上证指数',
            'close': current,
            'ma10': ma10,
            'ma20': ma20,
            'ma60': ma60,
            'strong_trend': strong_trend,
            'trend_status': '多头' if strong_trend else '空头/混沌'
        }
    except Exception as e:
        print(f"指数数据获取失败: {e}")
        return None

# ========== 第二层：板块筛选 ==========
def get_sector_data():
    """获取行业板块涨跌数据"""
    try:
        df = ak.stock_board_industry_name_em()
        df = df.sort_values('涨跌幅', ascending=False)
        return df
    except Exception as e:
        print(f"板块数据获取失败: {e}")
        return None

def get_hot_sectors(sector_df, index_change=0):
    """筛选涨幅超过指数1.05倍的板块"""
    if sector_df is None:
        return []
    
    threshold = index_change * 1.05 if index_change > 0 else 1.0
    hot = sector_df[sector_df['涨跌幅'] >= threshold].head(10)
    
    return hot.to_dict('records')

# ========== 第三层：个股均线筛选 ==========
def get_stock_list_a():
    """获取A股全部股票列表"""
    try:
        df = ak.stock_info_a_code_name()
        # 过滤ST、退市股
        df = df[~df['name'].str.contains('ST|退市', na=False)]
        return df
    except Exception as e:
        print(f"股票列表获取失败: {e}")
        return None

def check_ma_trend(stock_code):
    """检查个股均线状态"""
    try:
        # 转换代码格式
        if stock_code.startswith('6'):
            code = f"sh{stock_code}"
        else:
            code = f"sz{stock_code}"
        
        df = ak.stock_zh_a_hist(symbol=stock_code, period="daily", adjust="qfq", adjust_num=120)
        if df is None or len(df) < 60:
            return None
        
        df = df.tail(60).sort_values('日期')
        
        ma10 = df['收盘'].rolling(10).mean().iloc[-1]
        ma20 = df['收盘'].rolling(20).mean().iloc[-1]
        ma60 = df['收盘'].rolling(60).mean().iloc[-1]
        current = df['收盘'].iloc[-1]
        
        # 多头排列: MA10 > MA20 > MA60
        is多头 = ma10 > ma20 > ma60
        # 价格在均线上方
        above_ma = current > ma20
        
        return {
            'ma10': round(ma10, 2),
            'ma20': round(ma20, 2),
            'ma60': round(ma60, 2),
            'current': current,
            'is多头排列': is多头,
            'above_ma20': above_ma,
            'close_ma10_pct': round((current / ma10 - 1) * 100, 2)
        }
    except Exception:
        return None

# ========== 第四层：量价健康度 ==========
def check_volume_price(stock_code, days=20):
    """检查量价关系：放量突破 + 回调缩量"""
    try:
        df = ak.stock_zh_a_hist(symbol=stock_code, period="daily", adjust="qfq", adjust_num=60)
        if df is None or len(df) < 30:
            return None
        
        df = df.tail(30).sort_values('日期')
        
        volumes = df['成交量'].values
        closes = df['收盘'].values
        
        # 最近5日平均成交量 vs 前10日平均成交量
        vol_recent = np.mean(volumes[-5:])
        vol_before = np.mean(volumes[-15:-5])
        vol_ratio = vol_recent / vol_before if vol_before > 0 else 0
        
        # 今日是否放量（成交量 > 前日1.5倍）
        today_vol = volumes[-1]
        yesterday_vol = volumes[-2]
        is放量 = today_vol > yesterday_vol * 1.5
        
        # 今日涨幅
        change_pct = (closes[-1] / closes[-2] - 1) * 100 if len(closes) >= 2 else 0
        
        # 突破：价格创20日新高 or 接近新高
        high_20d = np.max(closes[-20:])
        is突破 = closes[-1] >= high_20d * 0.98
        
        # 回调缩量：近期有回调但缩量
        max_idx = np.argmax(closes)
        if max_idx < len(closes) - 3:  # 最近创新高后有回调
            # 从高点回调幅度
            pullback_pct = (high_20d - closes[-1]) / high_20d * 100
            # 回调期间缩量
            pullback_vol = np.mean(volumes[max_idx:])
            pre_pullback_vol = np.mean(volumes[max_idx-5:max_idx])
            is缩量回调 = pullback_vol < pre_pullback_vol * 0.7
        else:
            pullback_pct = 0
            is缩量回调 = False
        
        return {
            'vol_ratio': round(vol_ratio, 2),
            'is放量': is放量,
            'change_pct': round(change_pct, 2),
            'is突破': is突破,
            'pullback_pct': round(pullback_pct, 2),
            'is缩量回调': is缩量回调,
            'volume_healthy': (is放量 or vol_ratio > 1.3) and (is突破 or is缩量回调)
        }
    except Exception:
        return None

# ========== 第五层：形态质量 ==========
def check_pattern(stock_code):
    """检查形态：近5日新高 or 涨停"""
    try:
        df = ak.stock_zh_a_hist(symbol=stock_code, period="daily", adjust="qfq", adjust_num=30)
        if df is None or len(df) < 10:
            return None
        
        df = df.tail(10).sort_values('日期')
        
        closes = df['收盘'].values
        highs = df['最高'].values
        lows = df['最低'].values
        
        # 近5日新高
        high_5d = np.max(highs[:-1]) if len(highs) > 1 else highs[-1]
        is新5日高 = highs[-1] >= high_5d
        
        # 今日涨停检测
        # 涨停价 = 昨日收盘 * 1.1 (主板10%), * 1.2 (创业板/科创板)
        yesterday_close = closes[-2] if len(closes) > 1 else closes[-1]
        
        # 判断是否科创/创业板（简单用代码判断）
        # 000/001/002开头主板，300开头创业板，688开头科创板
        # 这里用akshare数据里的涨跌幅更准确
        
        # 计算近5日最大涨幅
        changes = []
        for i in range(1, len(closes)):
            ch = (closes[i] / closes[i-1] - 1) * 100
            changes.append(ch)
        
        max_change_5d = max(changes) if changes else 0
        is涨停 = abs(changes[-1]) > 9.5 if changes else False
        
        # 近5日有涨停
        has_limit_up = any(abs(c) > 9.5 for c in changes[-5:])
        
        return {
            'is新5日高': is新5日高,
            'is涨停': is涨停,
            'has_limit_up_5d': has_limit_up,
            'max_change_5d': round(max_change_5d, 2),
            'pattern_score': sum([is新5日高, has_limit_up_5d])
        }
    except Exception:
        return None

# ========== 第六层：风险排除 ==========
def check_risk(stock_code):
    """排除高位放量滞涨、巨量阴等风险形态"""
    try:
        df = ak.stock_zh_a_hist(symbol=stock_code, period="daily", adjust="qfq", adjust_num=30)
        if df is None or len(df) < 10:
            return None
        
        df = df.tail(15).sort_values('日期')
        
        closes = df['收盘'].values
        volumes = df['成交量'].values
        highs = df['最高'].values
        
        risk_signals = []
        
        # 1. 高位放量滞涨：连续3日创新高但涨幅缩小
        for i in range(3, len(closes)):
            if highs[i] > highs[i-1] > highs[i-2]:
                # 连续创新高
                changes = [(closes[i-j] / closes[i-j-1] - 1) * 100 for j in range(1, min(4, i+1))]
                if all(c < 3 for c in changes) and volumes[i] > volumes[i-1] * 1.5:
                    risk_signals.append('高位放量滞涨')
                    break
        
        # 2. 巨量阴线
        for i in range(len(closes) - 3, len(closes)):
            vol_ratio = volumes[i] / np.mean(volumes[max(0,i-5):i]) if i > 0 else 1
            change = (closes[i] / closes[i-1] - 1) * 100 if i > 0 else 0
            if vol_ratio > 2 and change < -5:
                risk_signals.append('巨量阴线')
                break
        
        # 3. 连续下跌
        if len(closes) >= 5:
            recent_changes = [(closes[i] / closes[i-1] - 1) * 100 for i in range(-5, 0)]
            if all(c < -2 for c in recent_changes):
                risk_signals.append('连续急跌')
        
        return {
            'risk_signals': risk_signals,
            'is_safe': len(risk_signals) == 0
        }
    except Exception:
        return None

# ========== 综合筛选 ==========
def screen_stocks(date=None, strict=False, target_sector=None):
    """精选股池筛选主函数"""
    print("=" * 60)
    print("精选股池筛选 - 双系统模型 v1.0")
    print("=" * 60)
    
    # 第一步：指数趋势判断
    print("\n[第一层] 检查指数趋势...")
    index_info = get_index_trend()
    if index_info:
        print(f"  上证: {index_info['close']:.2f} | MA20={'%.2f'%index_info['ma20']} | MA60={'%.2f'%index_info['ma60']}")
        print(f"  趋势: {index_info['trend_status']}")
        if not index_info['strong_trend']:
            print("  ⚠️ 指数未满足强趋势条件，筛选结果仅供参考")
    
    # 第二步：获取板块数据
    print("\n[第二层] 扫描板块...")
    sector_df = get_sector_data()
    index_change = index_info['close'] / index_info['ma10'] - 1 if index_info else 0
    hot_sectors = get_hot_sectors(sector_df, index_change * 100)
    print(f"  主线板块(涨跌幅≥指数1.05倍): {len(hot_sectors)} 个")
    for s in hot_sectors[:5]:
        print(f"    - {s.get('板块名称', 'N/A')}: {s.get('涨跌幅', 0):.2f}%")
    
    # 第三步：获取股票列表
    print("\n[第三层] 扫描全市场股票...")
    stock_list = get_stock_list_a()
    if stock_list is None:
        print("  ❌ 股票列表获取失败")
        return []
    
    total = len(stock_list)
    print(f"  A股总数: {total} (已过滤ST/退市)")
    
    # 第四-六层：逐层筛选
    print("\n[第四-六层] 个股深度筛选...")
    
    candidates = []
    screened = {'layer3': 0, 'layer4': 0, 'layer5': 0, 'layer6_pass': 0, 'failed': 0}
    
    # 优先扫描主线板块的个股
    sector_stocks = []
    if sector_df is not None and len(hot_sectors) > 0:
        for hs in hot_sectors[:3]:
            sector_name = hs.get('板块名称', '')
            try:
                sector_stocks_df = ak.stock_board_industry_cons_em(symbol=sector_name)
                if sector_stocks_df is not None:
                    for _, row in sector_stocks_df.iterrows():
                        code = str(row.get('代码', '')).zfill(6)
                        if code not in sector_stocks:
                            sector_stocks.append(code)
                print(f"  板块 {sector_name} 包含 {len(sector_stocks)} 只股票")
            except Exception as e:
                pass
    
    # 先扫主线板块，再扫其他
    codes_to_scan = sector_stocks[:50]  # 限制数量避免超时
    
    # 补充一些ETF和热门股
    etf_codes = ['159919', '510300', '512000', '515050', '159995', '512760', '588000']
    codes_to_scan = list(set(codes_to_scan + etf_codes))[:80]
    
    print(f"  实际扫描: {len(codes_to_scan)} 只股票")
    
    for i, code in enumerate(codes_to_scan):
        if (i + 1) % 20 == 0:
            print(f"  进度: {i+1}/{len(codes_to_scan)}...")
        
        # 第三层：均线筛选
        ma_info = check_ma_trend(code)
        if ma_info is None:
            continue
        screened['layer3'] += 1
        
        if not (ma_info['is多头排列'] and ma_info['above_ma20']):
            if not strict:
                continue  # 非严格模式跳过
        
        # 第四层：量价筛选
        vol_info = check_volume_price(code)
        if vol_info is None:
            continue
        screened['layer4'] += 1
        
        if strict and not vol_info['volume_healthy']:
            continue
        
        # 第五层：形态筛选
        pattern_info = check_pattern(code)
        if pattern_info is None:
            continue
        screened['layer5'] += 1
        
        if strict and pattern_info['pattern_score'] == 0:
            continue
        
        # 第六层：风险排除
        risk_info = check_risk(code)
        if risk_info is None:
            continue
        
        if risk_info['is_safe']:
            screened['layer6_pass'] += 1
            # 获取股票名称
            name = stock_list[stock_list['code'] == code]['name'].values
            name = name[0] if len(name) > 0 else code
            
            candidate = {
                'code': code,
                'name': name,
                **ma_info,
                **vol_info,
                **pattern_info,
                **risk_info
            }
            candidates.append(candidate)
        else:
            screened['failed'] += 1
    
    # 排序：优先涨停 > 多头排列 > 放量突破
    candidates.sort(key=lambda x: (
        -x.get('has_limit_up_5d', 0) * 100,
        -x.get('is新5日高', 0) * 50,
        -x.get('close_ma10_pct', 0),
        x.get('vol_ratio', 0)
    ))
    
    # 输出结果
    print("\n" + "=" * 60)
    print(f"筛选结果: {len(candidates)} 只股票通过六层过滤")
    print("=" * 60)
    
    if candidates:
        print(f"\n{'代码':<8} {'名称':<10} {'现价':>8} {'MA10':>8} {'MA20':>8} {'MA60':>8} {'多头':>4} {'放量':>5} {'突破':>4} {'新高':>4} {'涨停':>4} {'风险':>6}")
        print("-" * 100)
        
        for c in candidates[:20]:
            risk_str = ','.join(c['risk_signals']) if c['risk_signals'] else '无'
            print(f"{c['code']:<8} {c['name']:<10} {c['current']:>8.2f} {c['ma10']:>8.2f} {c['ma20']:>8.2f} {c['ma60']:>8.2f} "
                  f"{'Y' if c['is多头排列'] else 'N':>4} {c['vol_ratio']:>5.1f} {'Y' if c['is突破'] else 'N':>4} "
                  f"{'Y' if c['is新5日高'] else 'N':>4} {'Y' if c['has_limit_up_5d'] else 'N':>4} {risk_str:>6}")
    
    # 保存报告
    report_file = os.path.join(REPORT_DIR, f"screener_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(f"精选股池筛选报告 - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"指数状态: {index_info['trend_status'] if index_info else 'N/A'}\n")
        f.write(f"主线板块数: {len(hot_sectors)}\n")
        f.write(f"扫描股票数: {len(codes_to_scan)}\n")
        f.write(f"通过筛选数: {len(candidates)}\n\n")
        f.write("-" * 60 + "\n")
        f.write(f"{'代码':<8} {'名称':<10} {'现价':>8} {'涨幅%':>8} {'量比':>5} {'多头':>4} {'新高':>4} {'涨停':>4}\n")
        f.write("-" * 60 + "\n")
        for c in candidates:
            f.write(f"{c['code']:<8} {c['name']:<10} {c['current']:>8.2f} {c.get('change_pct', 0):>8.2f} "
                    f"{c.get('vol_ratio', 0):>5.1f} {'Y' if c['is多头排列'] else 'N':>4} "
                    f"{'Y' if c['is新5日高'] else 'N':>4} {'Y' if c['has_limit_up_5d'] else 'N':>4}\n")
    
    print(f"\n📁 报告已保存: {report_file}")
    
    return candidates


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='精选股池筛选器')
    parser.add_argument('--date', type=str, help='指定日期 (YYYY-MM-DD)')
    parser.add_argument('--strict', action='store_true', help='严格模式(需通过全部6层)')
    parser.add_argument('--sector', type=str, help='指定板块')
    
    args = parser.parse_args()
    
    candidates = screen_stocks(date=args.date, strict=args.strict, target_sector=args.sector)
    
    print(f"\n✅ 筛选完成，共 {len(candidates)} 只股票入选精选股池")