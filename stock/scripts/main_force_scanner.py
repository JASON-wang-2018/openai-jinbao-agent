#!/usr/bin/env python3
"""
主力坐庄量化扫描 v1.0
全市场扫描主力运作各阶段个股

使用方式:
    python3 main_force_scanner.py              # 全量扫描
    python3 main_force_scanner.py --stage 吸筹  # 只扫吸筹阶段
    python3 main_force_scanner.py --top 20      # 显示前N只
    python3 main_force_scanner.py --min-score 60  # 最低评分过滤
"""

import struct
import os
import sys
import json
import time
import argparse
from pathlib import Path
from multiprocessing import Pool, cpu_count
from collections import defaultdict

# ============ 数据路径 ============
SH_PATH = '/home/jason/.openclaw/exchanger/vipdoc/sh/lday/'
SZ_PATH = '/home/jason/.openclaw/exchanger/vipdoc/sz/lday/'

# ============ 二进制解析 ============
def parse_day_file(filepath):
    """解析通达信.day文件"""
    try:
        with open(filepath, 'rb') as f:
            data = f.read()
        record_size = 32
        num_records = len(data) // record_size
        records = []
        for i in range(num_records):
            offset = i * record_size
            chunk = data[offset:offset + record_size]
            date   = struct.unpack('<I', chunk[0:4])[0]
            open_p = struct.unpack('<I', chunk[4:8])[0] / 100.0
            high   = struct.unpack('<I', chunk[8:12])[0] / 100.0
            low    = struct.unpack('<I', chunk[12:16])[0] / 100.0
            close  = struct.unpack('<I', chunk[16:20])[0] / 100.0
            amount = struct.unpack('<I', chunk[20:24])[0] / 100000000.0
            volume = struct.unpack('<I', chunk[24:28])[0]
            year   = date // 10000
            month  = (date % 10000) // 100
            day    = date % 100
            pct = (close - open_p) / open_p * 100 if open_p > 0 else 0
            records.append({
                'date': f"{year}-{month:02d}-{day:02d}",
                'open': open_p, 'high': high, 'low': low, 'close': close,
                'amount': amount, 'volume': volume, 'pct': pct
            })
        return records
    except Exception:
        return None

# ============ 均线计算 ============
def ma(data, n):
    result = []
    for i in range(len(data)):
        if i < n - 1:
            result.append(None)
        else:
            result.append(sum(data[i-n+1:i+1]) / n)
    return result

def ema(data, n):
    """指数移动平均"""
    if len(data) < n:
        return [None] * len(data)
    k = 2 / (n + 1)
    result = [None] * (n - 1)
    result.append(data[0])
    for i in range(n, len(data)):
        result.append(data[i] * k + result[-1] * (1 - k))
    return result

# ============ 单股票分析 ============
# ============ 股票类型过滤 ============
# 排除：ETF(5开头)、可转债(11xxxx/12xxxx)、B股(9xxxx)
EXCLUDE_PREFIXES = (
    '511', '512', '513', '515', '517', '518', '588',  # ETF基金
    '501', '502', '503',                               # 封闭式基金/LOF
    '150', '160', '161', '162', '163', '164',          # 分级基金
    '11',  # 可转债(sh)
    '12',  # 可转债(sz)
    '90',  # B股(sh)
)

def is_excluded(code):
    """判断是否为需排除的证券类型"""
    # 去掉sh/sz前缀
    c = code[2:] if code.startswith(('sh', 'sz')) else code
    # ETF/基金
    if c.startswith(('511','512','513','515','517','518','588','501','502','503',
                     '150','160','161','162','163','164')):
        return True
    # 可转债: 11xxxx(sh) / 12xxxx(sz)
    if c.startswith(('11', '12')) and len(c) == 6:
        return True
    # B股: 9xxxx(sh)
    if c.startswith(('90',)) and len(c) == 6:
        return True
    return False

def is_valid_a_stock(code, price):
    """判断是否为有效A股（过滤高价债、低价债等异常）"""
    c = code[2:] if code.startswith(('sh', 'sz')) else code
    # 排除沪深B股
    if c.startswith(('90',)) and len(c) == 6:
        return False
    # 排除可转债（价格通常>100）
    if price > 500:
        return False
    # 排除价格极低的（可能是流动性极差的）
    if price < 0.3:
        return False
    return True

def analyze_stock(args):
    """分析单只股票，返回主力量化评分"""
    filepath, code = args

    # 过滤ETF/可转债/B股
    if is_excluded(code):
        return None

    records = parse_day_file(filepath)
    if records is None or len(records) < 120:
        return None

    # 获取最新价格用于过滤
    last_price = records[-1]['close']
    if not is_valid_a_stock(code, last_price):
        return None

    try:
        result = analyze_main_force(records, code)
        return result
    except Exception as e:
        return None

def analyze_main_force(records, code):
    """主力坐庄量化分析"""
    closes = [r['close'] for r in records]
    volumes = [r['volume'] for r in records]
    highs = [r['high'] for r in records]
    lows = [r['low'] for r in records]
    pcts = [r['pct'] for r in records]

    last = records[-1]
    last5 = records[-5:]
    last10 = records[-10:]
    last20 = records[-20:]
    last60 = records[-60:]
    last120 = records[-120:]

    n = len(records)

    # === 均线 ===
    ma5  = ma(closes, 5)
    ma10 = ma(closes, 10)
    ma20 = ma(closes, 20)
    ma60 = ma(closes, 60)
    ma120 = ma(closes, 120)

    # === 均线趋势打分 ===
    ma_trend_score = 0
    if ma5[-1] > ma10[-1] > ma20[-1] > ma60[-1]:
        ma_trend_score = 25
    elif ma5[-1] > ma10[-1] > ma20[-1]:
        ma_trend_score = 15
    elif ma5[-1] < ma10[-1] < ma20[-1]:
        ma_trend_score = -15
    else:
        ma_trend_score = 0

    if ma60[-1] and ma120[-1]:
        if ma60[-1] > ma60[-20] if len(closes) >= 20 else False:
            ma_trend_score += 10
        else:
            ma_trend_score -= 10

    # === 各阶段量化分析 ===
    stage_scores = {}
    stage_details = {}

    # ---------- 1. 吸筹阶段 ----------
    score_accum = 0
    details_accum = []

    # (1) 量能萎缩至极低水平：日均成交量萎缩至前期峰值的20%以下
    vol_120_peak = max(volumes[-120:]) if len(volumes) >= 120 else max(volumes)
    vol_20_avg = sum(volumes[-20:]) / 20 if len(volumes) >= 20 else sum(volumes) / len(volumes)
    vol_ratio = vol_20_avg / vol_120_peak if vol_120_peak > 0 else 1

    if vol_ratio < 0.15:
        score_accum += 25
        details_accum.append(f"地量(均量仅{vol_ratio:.0%}峰值)")
    elif vol_ratio < 0.25:
        score_accum += 15
        details_accum.append(f"缩量({vol_ratio:.0%}峰值)")

    # (2) 偶尔脉冲式放量：近60日有2-3倍倍量
    vol_60_avg = sum(volumes[-60:]) / 60 if len(volumes) >= 60 else sum(volumes) / len(volumes)
    pulse_count = 0
    pulse_days = []
    for i, vol in enumerate(volumes[-60:]):
        if vol > vol_60_avg * 2.5:
            pulse_count += 1
            pulse_days.append(i)

    if pulse_count >= 2:
        score_accum += 20
        details_accum.append(f"脉冲放量{pulse_count}次")
    elif pulse_count == 1:
        score_accum += 10
        details_accum.append(f"脉冲放量1次")

    # (3) 价格维持低振幅横盘
    price_range_60 = (max(closes[-60:]) - min(closes[-60:])) / min(closes[-60:]) * 100
    if price_range_60 < 15:
        score_accum += 15
        details_accum.append(f"低位横盘(振幅{price_range_60:.1f}%)")
    elif price_range_60 < 25:
        score_accum += 8
        details_accum.append(f"低振幅({price_range_60:.1f}%)")

    # (4) 低位区间判断：价格在120日低位
    hh120 = max(highs[-120:]) if len(highs) >= 120 else max(highs)
    ll120 = min(lows[-120:]) if len(lows) >= 120 else min(lows)
    pos_120 = (last['close'] - ll120) / (hh120 - ll120) * 100 if hh120 > ll120 else 50
    if pos_120 < 35:
        score_accum += 15
        details_accum.append(f"120日低位({pos_120:.0f}%)")
    elif pos_120 < 50:
        score_accum += 8
        details_accum.append(f"偏低位置({pos_120:.0f}%)")

    # (5) 近60日涨幅不大（吸筹期不应大涨）
    gain_60 = (closes[-1] - closes[-60]) / closes[-60] * 100 if len(closes) >= 60 else 0
    if 0 < gain_60 < 20:
        score_accum += 10
        details_accum.append(f"温和涨幅({gain_60:.1f}%)")
    elif gain_60 < 0:
        score_accum += 5
        details_accum.append(f"近60日下跌({gain_60:.1f}%)")

    # (6) 出现长上影线（主力试盘+吸筹特征）
    long_shadow = 0
    for r in records[-60:]:
        if r['high'] > r['close']:
            shadow = (r['high'] - max(r['close'], r['open'])) / (r['high'] - r['low'] + 0.001) * 100
            if shadow > 50:
                long_shadow += 1
    if long_shadow >= 3:
        score_accum += 10
        details_accum.append(f"长上影线{long_shadow}次")

    stage_scores['吸筹'] = score_accum
    stage_details['吸筹'] = details_accum

    # ---------- 2. 洗盘阶段 ----------
    score_wash = 0
    details_wash = []

    # (1) 近20日内有快速下跌 >3%
    big_drop_days = [(i, r) for i, r in enumerate(records[-20:]) if r['pct'] < -3]
    if big_drop_days:
        # (2) 下跌时缩量：成交量相比拉升时萎缩50%以上
        drop_volumes = [abs(r['volume']) for _, r in big_drop_days]
        rise_volumes = [r['volume'] for r in records[-20:] if r['pct'] > 1]
        if rise_volumes:
            avg_rise_vol = sum(rise_volumes) / len(rise_volumes)
            avg_drop_vol = sum(drop_volumes) / len(drop_volumes)
            vol_shrink = avg_drop_vol / avg_rise_vol if avg_rise_vol > 0 else 1
            if vol_shrink < 0.5:
                score_wash += 25
                details_wash.append(f"下跌缩量({vol_shrink:.0%})")
            elif vol_shrink < 0.7:
                score_wash += 15
                details_wash.append(f"下跌相对缩量({vol_shrink:.0%})")

        # (3) 随后3日内缩量止跌
        for idx, _ in big_drop_days:
            if idx >= 3:
                post_volumes = [abs(records[-20:][idx-3]['volume']), abs(records[-20:][idx-2]['volume']), abs(records[-20:][idx-1]['volume'])]
                if all(post_volumes[i] <= post_volumes[i-1] for i in range(1, len(post_volumes))):
                    score_wash += 15
                    details_wash.append("洗盘后缩量止跌")
                    break

    # (4) 深V走势（开盘砸盘后拉回）
    deep_v_count = 0
    for r in records[-20:]:
        if r['high'] != r['low']:
            day_range = r['high'] - r['low']
            lower_shadow = (r['open'] - r['low']) / day_range * 100 if r['open'] > r['low'] else 0
            upper_real = r['close'] - r['open']
            if lower_shadow > 50 and r['close'] > r['open']:
                deep_v_count += 1
    if deep_v_count >= 1:
        score_wash += 10
        details_wash.append(f"深V走势{deep_v_count}次")

    # (5) 低点未破重要支撑
    ll60 = min(lows[-60:]) if len(lows) >= 60 else min(lows)
    ll20 = min(lows[-20:]) if len(lows) >= 20 else min(lows)
    if big_drop_days:
        last_drop_close = abs(big_drop_days[-1][1]['close'])
        if last_drop_close > ll60 * 0.98:  # 未有效跌破60日低点
            score_wash += 10
            details_wash.append("未破60日支撑")

    stage_scores['洗盘'] = score_wash
    stage_details['洗盘'] = details_wash

    # ---------- 3. 试盘阶段 ----------
    score_test = 0
    details_test = []

    # (1) 脉冲式放量冲高回落：成交量放大2-3倍
    test_pulse = 0
    for i in range(max(0, n-30), n):
        if i >= 1:
            vol_ratio_i = volumes[i] / (sum(volumes[max(0,i-5):i]) / 5) if i >= 5 else volumes[i] / volumes[i-1]
            if vol_ratio_i > 2.0:
                # 检查当日是否有较大振幅
                day_amplitude = (highs[i] - lows[i]) / lows[i] * 100
                if day_amplitude > 4:
                    test_pulse += 1

    if test_pulse >= 2:
        score_test += 25
        details_test.append(f"试盘脉冲{test_pulse}次")
    elif test_pulse == 1:
        score_test += 15
        details_test.append(f"试盘脉冲1次")

    # (2) 长上影线/长下影线
    long_shadow_up = sum(1 for r in records[-20:] if r['high'] > r['close'] and (r['high'] - max(r['close'], r['open'])) / (r['high'] - r['low'] + 0.001) > 0.5)
    long_shadow_down = sum(1 for r in records[-20:] if r['low'] < r['close'] and (min(r['close'], r['open']) - r['low']) / (r['high'] - r['low'] + 0.001) * 100 > 40)
    if long_shadow_up >= 2:
        score_test += 15
        details_test.append(f"长上影线{long_shadow_up}次")
    if long_shadow_down >= 2:
        score_test += 10
        details_test.append(f"长下影线{long_shadow_down}次")

    # (3) 试盘后缩量止跌确认
    for i in range(max(0, n-20), n):
        if i >= 2:
            vol_ratio_i = volumes[i] / (sum(volumes[max(0,i-5):i]) / 5) if i >= 5 else volumes[i] / volumes[i-1]
            if vol_ratio_i > 2.0 and i < n - 3:
                post_vols = volumes[i+1:i+4]
                if post_vols and max(post_vols) < volumes[i] * 0.55:  # 缩量45%以上
                    score_test += 20
                    details_test.append("试盘后缩量止跌确认")
                    break

    stage_scores['试盘'] = score_test
    stage_details['试盘'] = details_test

    # ---------- 4. 拉升阶段 ----------
    score_rally = 0
    details_rally = []

    # (1) 放量突破关键位
    vol_20_avg_r = sum(volumes[-20:]) / 20
    vol_5_avg = sum(volumes[-5:]) / 5
    if vol_5_avg > vol_20_avg_r * 1.5:
        score_rally += 20
        details_rally.append(f"放量突破({vol_5_avg/vol_20_avg_r:.1f}倍均量)")

    # (2) 均线多头排列
    if ma5[-1] > ma10[-1] > ma20[-1] > ma60[-1]:
        score_rally += 20
        details_rally.append("均线多头排列")
    elif ma5[-1] > ma10[-1] > ma20[-1]:
        score_rally += 10
        details_rally.append("短期多头")

    # (3) 连续3日创新高
    high_3d = 0
    for i in range(n-3, n):
        if i >= 3:
            if highs[i] > max(highs[i-3:i]):
                high_3d += 1
    if high_3d >= 3:
        score_rally += 20
        details_rally.append("连续3日创新高")
    elif high_3d >= 2:
        score_rally += 10
        details_rally.append("近2日新高")

    # (4) 突破年线/重要均线
    if last['close'] > ma60[-1] and ma20[-1] > ma60[-1]:
        score_rally += 15
        details_rally.append("突破+均线共振")

    # (5) 量价齐升（涨幅>3%的日子占比）
    strong_days = sum(1 for r in records[-10:] if r['pct'] > 3)
    if strong_days >= 3:
        score_rally += 15
        details_rally.append(f"量价齐升({strong_days}日涨幅>3%)")
    elif strong_days >= 2:
        score_rally += 8
        details_rally.append(f"间歇强涨({strong_days}日)")

    # (6) 近10日涨幅
    gain_10 = (closes[-1] - closes[-10]) / closes[-10] * 100 if len(closes) >= 10 else 0
    if 5 < gain_10 < 25:
        score_rally += 10
        details_rally.append(f"健康涨幅({gain_10:.1f}%)")
    elif gain_10 >= 25:
        score_rally -= 10
        details_rally.append(f"涨幅过大({gain_10:.1f}%)谨慎")

    stage_scores['拉升'] = score_rally
    stage_details['拉升'] = details_rally

    # ---------- 综合评分 ----------
    total_score = max(stage_scores.values()) if stage_scores else 0
    primary_stage = max(stage_scores, key=stage_scores.get) if stage_scores else '未知'
    primary_score = stage_scores.get(primary_stage, 0)

    return {
        'code': code,
        'name': code,
        'date': last['date'],
        'close': last['close'],
        'pct_5d': (closes[-1] - closes[-5]) / closes[-5] * 100 if len(closes) >= 5 else 0,
        'gain_20d': (closes[-1] - closes[-20]) / closes[-20] * 100 if len(closes) >= 20 else 0,
        'pos_120d': pos_120,
        'vol_ratio': vol_ratio,
        'primary_stage': primary_stage,
        'primary_score': primary_score,
        'scores': stage_scores,
        'details': stage_details,
        'total_score': total_score,
        'ma_trend_score': ma_trend_score,
        # 额外维度（用于过滤）
        'is_zt': any(r['pct'] >= 9.4 and abs(r['close'] - r['high']) < 0.02 for r in records[-120:]),
        'vol_5d_avg': vol_5_avg,
        'vol_20d_avg': vol_20_avg_r,
    }

# ============ 文件扫描器 ============
def get_all_stock_files():
    """获取所有股票文件路径"""
    stocks = []
    for fname in os.listdir(SH_PATH):
        if fname.endswith('.day'):
            code = fname.replace('.day', '')  # e.g. sh605298
            stocks.append((os.path.join(SH_PATH, fname), code))
    for fname in os.listdir(SZ_PATH):
        if fname.endswith('.day'):
            code = fname.replace('.day', '')  # e.g. sz300001
            stocks.append((os.path.join(SZ_PATH, fname), code))
    return stocks

def scan_worker(args):
    """并行扫描worker"""
    return analyze_stock(args)

def run_scan(stage_filter=None, min_score=0, top_n=50, n_workers=None):
    """运行全市场扫描"""
    print(f"🚀 主力坐庄量化扫描 v1.0")
    print(f"   {'='*50}")
    print(f"   {'过滤器':<10}: {'无' if not stage_filter else stage_filter}")
    print(f"   {'最低评分':<10}: {min_score}")
    print(f"   {'显示数量':<10}: {top_n}")
    print()

    t0 = time.time()
    stocks = get_all_stock_files()
    print(f"📋 待扫描: {len(stocks)} 只股票")

    if n_workers is None:
        n_workers = min(cpu_count(), 16)

    print(f"⚙️  使用 {n_workers} 个进程...")

    results = []
    batch_size = 500
    total_batches = (len(stocks) + batch_size - 1) // batch_size

    with Pool(n_workers) as pool:
        for batch_idx in range(total_batches):
            batch = stocks[batch_idx * batch_size : (batch_idx + 1) * batch_size]
            batch_results = pool.map(scan_worker, batch)
            results.extend([r for r in batch_results if r is not None])
            pct = (batch_idx + 1) / total_batches * 100
            print(f"\r   进度: {pct:.1f}% ({len(results)} 只通过初筛)", end='', flush=True)

    print(f"\n\n✅ 扫描完成! 耗时: {time.time()-t0:.1f}秒")
    print(f"   通过分析: {len(results)} 只")

    # 过滤
    if stage_filter:
        results = [r for r in results if stage_filter in r['scores']]
    if min_score > 0:
        results = [r for r in results if r['total_score'] >= min_score]

    # 按总分排序
    results.sort(key=lambda x: x['total_score'], reverse=True)

    return results[:top_n]

# ============ 输出格式化 ============
def print_result(results, stage_filter=None):
    """打印扫描结果"""
    if not results:
        print("\n❌ 未找到符合条件的股票")
        return

    stage_emoji = {'吸筹': '📥', '洗盘': '🌀', '试盘': '🧪', '拉升': '🚀', '出货': '📤'}
    stage_color = {'吸筹': '🟢', '洗盘': '🟡', '试盘': '🔵', '拉升': '🔴', '出货': '⚪'}

    print(f"\n{'='*90}")
    print(f"{'代码':<10} {'日期':<12} {'现价':<8} {'5日涨幅':<10} {'20日涨幅':<10} {'120日位置':<10} {'主要阶段':<8} {'评分':<6}")
    print(f"{'='*90}")

    for r in results:
        stage = r['primary_stage']
        emoji = stage_emoji.get(stage, '❓')
        print(f"{r['code']:<10} {r['date']:<12} {r['close']:<8.2f} {r['pct_5d']:>+8.1f}%   {r['gain_20d']:>+8.1f}%   {r['pos_120d']:>6.1f}%    {emoji}{stage:<6} {r['total_score']:<6}")

    print(f"{'='*90}")

    # 按阶段分组统计
    print("\n📊 各阶段分布:")
    stage_count = defaultdict(int)
    for r in results:
        stage_count[r['primary_stage']] += 1
    for s, c in sorted(stage_count.items(), key=lambda x: -x[1]):
        emoji = stage_emoji.get(s, '❓')
        print(f"   {emoji} {s}: {c}只")

    # 打印Top10详细信息
    print("\n\n🏆 Top10 详细信息:")
    print(f"{'─'*80}")
    for i, r in enumerate(results[:10], 1):
        stage = r['primary_stage']
        emoji = stage_emoji.get(stage, '❓')
        print(f"\n{i}. {r['code']} {emoji}{stage} 评分:{r['total_score']}  现价:{r['close']:.2f}  5日:{r['pct_5d']:+.1f}%  20日:{r['gain_20d']:+.1f}%")
        details = r['details'].get(stage, [])
        for d in details:
            print(f"   • {d}")
        print(f"   各阶段: 吸筹={r['scores'].get('吸筹',0)} 洗盘={r['scores'].get('洗盘',0)} 试盘={r['scores'].get('试盘',0)} 拉升={r['scores'].get('拉升',0)}")

    return results

# ============ 主程序 ============
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='主力坐庄量化扫描')
    parser.add_argument('--stage', type=str, default=None, help='筛选阶段: 吸筹/洗盘/试盘/拉升')
    parser.add_argument('--top', type=int, default=50, help='显示前N只 (默认50)')
    parser.add_argument('--min-score', type=int, default=0, help='最低评分过滤 (默认0)')
    parser.add_argument('--workers', type=int, default=None, help='进程数')
    parser.add_argument('--output', type=str, default=None, help='输出JSON文件路径')
    args = parser.parse_args()

    results = run_scan(
        stage_filter=args.stage,
        min_score=args.min_score,
        top_n=args.top,
        n_workers=args.workers
    )

    print_result(results, stage_filter=args.stage)

    if args.output:
        # 只保留可序列化字段
        output_data = []
        for r in results:
            d = {k: v for k, v in r.items() if k not in ['details']}
            d['details_str'] = '; '.join(r['details'].get(r['primary_stage'], []))
            output_data.append(d)
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        print(f"\n💾 结果已保存: {args.output}")
