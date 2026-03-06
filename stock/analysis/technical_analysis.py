#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票技术分析实战模块
基于主力行为识别的完整分析框架

使用方法:
    from stock.analysis.technical_analysis import 完整技术分析
    
    报告 = 完整技术分析('002642', df)
    print(报告)
"""

import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ========== 核心分析函数 ==========

def 判断均线结构(df, periods=[5, 10, 20, 60]):
    """判断均线结构"""
    if df is None or len(df) < 60:
        return "数据不足", 0, {}
    
    close = df['close']
    mas = {}
    scores = {}
    
    for p in periods:
        mas[f'ma{p}'] = close.rolling(p).mean().iloc[-1]
        scores[f'ma{p}'] = close.rolling(p).mean().iloc[-1]
    
    # 判断排列
    if mas['ma5'] > mas['ma10'] > mas['ma20'] > mas['ma60']:
        结构 = "多头排列"
        得分 = 20
        斜率 = "上行"
    elif mas['ma5'] < mas['ma10'] < mas['ma20'] < mas['ma60']:
        结构 = "空头排列"
        得分 = 0
        斜率 = "下行"
    else:
        结构 = "震荡整理"
        得分 = 10
        斜率 = "走平"
    
    return 结构, 得分, {'ma': mas, '斜率': 斜率}


def 判断股价位置(df):
    """判断当前股价相对历史位置"""
    if df is None or len(df) < 250:
        return "数据不足", 0
    
    high_250 = df['high'].max()
    low_250 = df['low'].min()
    current = df['close'].iloc[-1]
    
    range_val = high_250 - low_250
    position = (current - low_250) / range_val * 100
    
    if position < 30:
        return "历史低位", 15
    elif position < 70:
        return "中位震荡", 10
    else:
        return "历史高位", 5


def 推断生命周期阶段(df, 结构, 位置):
    """推断股票运行阶段"""
    ma5 = df['close'].rolling(5).mean().iloc[-1]
    ma20 = df['close'].rolling(20).mean().iloc[-1]
    ma60 = df['close'].rolling(60).mean().iloc[-1]
    
    # 计算近期涨幅
    close_20d_ago = df['close'].iloc[-20]
    current = df['close'].iloc[-1]
    change_20d = (current - close_20d_ago) / close_20d_ago * 100
    
    if ma5 > ma20 > ma60 and change_20d > 20:
        return "主升浪", "股价处于强势上涨阶段，均线多头排列，20日涨幅超过20%"
    elif ma5 > ma20 and ma20 > ma60:
        return "拉升启动", "短期均线金叉向上，有望进入主升"
    elif ma5 < ma20 and ma20 > ma60:
        return "高位震荡", "中期均线向上，但短期回调，注意风险"
    elif ma5 > ma20 and ma20 < ma60:
        return "洗盘整理", "短期上穿中期，可能处于洗盘阶段"
    elif ma20 < ma60 and change_20d < -20:
        return "出清末期", "中长期均线空头，跌幅较大，可能接近底部"
    elif ma5 < ma20 < ma60:
        return "下跌趋势", "均线空头排列，下降趋势中"
    else:
        return "筑底阶段", "均线走平，可能在构筑底部"


def 分析量价关系(df):
    """分析量价关系健康度"""
    if df is None or len(df) < 10:
        return "数据不足", 0
    
    close = df['close']
    volume = df['volume']
    
    # 最近5日量价关系
    recent = df.tail(5)
    
    # 涨跌幅
    change_5d = (close.iloc[-1] - close.iloc[-6]) / close.iloc[-6] * 100 if len(df) >= 6 else 0
    vol_5d = volume.iloc[-5:].mean()
    vol_20d = volume.rolling(20).mean().iloc[-1]
    
    # 量价配合判断
    if len(df) >= 6:
        if change_5d > 0 and vol_5d > vol_20d:
            量价状态 = "价涨量增"
            得分 = 25
            描述 = "健康上涨，量能配合良好"
        elif change_5d > 0 and vol_5d < vol_20d:
            量价状态 = "价涨量缩"
            得分 = 12
            描述 = "量能不足，需警惕诱多"
        elif change_5d < 0 and vol_5d < vol_20d:
            量价状态 = "价跌量缩"
            得分 = 10
            描述 = "阴跌行情，可能还有下探"
        elif change_5d < 0 and vol_5d > vol_20d:
            量价状态 = "价跌量增"
            得分 = 15
            描述 = "恐慌抛售，可能接近底部"
        else:
            量价状态 = "量价平稳"
            得分 = 15
    else:
        量价状态 = "数据不足"
        得分 = 10
        描述 = ""
    
    return 量价状态, 得分, {'change_5d': change_5d, 'vol_ratio': vol_5d/vol_20d if vol_20d > 0 else 0, '描述': 描述}


def 分析K线形态(df):
    """分析K线形态"""
    if df is None or len(df) < 10:
        return "数据不足", 0, []
    
    recent = df.tail(10)
    close = recent['close']
    open_p = recent['open']
    high = recent['high']
    low = recent['low']
    vol = recent['volume']
    
    signals = []
    得分 = 10  # 基础分
    
    # 最近一根K线
    last_close = close.iloc[-1]
    last_open = open_p.iloc[-1]
    last_high = high.iloc[-1]
    last_low = low.iloc[-1]
    last_vol = vol.iloc[-1]
    prev_close = close.iloc[-2]
    
    # 判断阳线/阴线
    is_bullish = last_close > last_open
    body = abs(last_close - last_open)
    upper_shadow = last_high - max(last_close, last_open)
    lower_shadow = min(last_close, last_open) - last_low
    
    # 锤子线（底部信号）
    if last_low < min(last_open, last_close) - body and upper_shadow < body * 0.5:
        signals.append("锤子线（可能触底）")
        得分 += 5
    
    # 上吊线（顶部信号）
    if last_high > max(last_open, last_close) + body and lower_shadow < body * 0.5:
        signals.append("上吊线（警惕回落）")
        得分 -= 3
    
    # 放量中阳
    vol_ma5 = vol.rolling(5).mean().iloc[-1]
    if is_bullish and body > (last_high - last_low) * 0.5 and last_vol > vol_ma5 * 1.5:
        signals.append("放量中阳（启动信号）")
        得分 += 5
    
    # 连续阳线
    consecutive_bull = 0
    for i in range(min(5, len(close))):
        if close.iloc[-1-i] > open_p.iloc[-1-i]:
            consecutive_bull += 1
        else:
            break
    
    if consecutive_bull >= 3:
        signals.append(f"连续{consecutive_bull}日阳线")
        得分 += 3
    
    # 均线支撑
    ma5 = close.rolling(5).mean().iloc[-1]
    ma10 = close.rolling(10).mean().iloc[-1]
    if last_close > ma5 > ma10:
        signals.append("均线多头支撑")
        得分 += 2
    
    return " / ".join(signals) if signals else "无明显形态", min(得分, 15), signals


def 分析主力行为(df):
    """分析主力资金行为"""
    if df is None or len(df) < 20:
        return "数据不足", 0, {}
    
    close = df['close']
    volume = df['volume']
    
    # 计算资金流向指标
    vol_ma10 = volume.rolling(10).mean()
    vol_ma20 = volume.rolling(20).mean()
    
    # 近期量能趋势
    recent_vol = volume.tail(10)
    vol_trend = recent_vol.iloc[-1] - recent_vol.iloc[0]
    
    # 价格趋势
    price_10d_ago = close.iloc[-10]
    current_price = close.iloc[-1]
    price_trend = (current_price - price_10d_ago) / price_10d_ago * 100
    
    # 判断主力行为
    行为 = {}
    得分 = 10
    
    if vol_trend > 0 and price_trend > 5:
        行为['类型'] = "资金推升"
        得分 = 20
        描述 = "量价齐升，主力持续买入"
    elif vol_trend > 0 and abs(price_trend) < 2:
        行为['类型'] = "对倒/出货"
        得分 = 8
        描述 = "放量不涨，警惕主力出货"
    elif vol_trend < 0 and price_trend > 0:
        行为['类型'] = "缩量上涨"
        得分 = 12
        描述 = "量能萎缩，可能虚涨"
    elif vol_trend < 0 and price_trend < 0:
        行为['类型'] = "缩量下跌"
        得分 = 10
        描述 = "阴跌行情，无资金承接"
    elif vol_trend > 0 and price_trend < -5:
        行为['类型'] = "恐慌抛售/吸筹"
        得分 = 15
        描述 = "放量下跌，可能是恐慌盘出逃，主力吸筹"
    else:
        行为['类型'] = "震荡整理"
        得分 = 12
    
    行为['描述'] = 描述
    行为['价格趋势'] = f"{price_trend:+.2f}%"
    行为['量能趋势'] = "放大" if vol_trend > 0 else "萎缩"
    
    return 行为['类型'], 得分, 行为


def 分析板块环境(stock_code, 所属板块=None):
    """分析板块环境（需外部数据）"""
    # 这里需要接入板块数据
    # 暂时返回基础分析
    return "板块数据待接入", 10, {}


def 识别关键位(df):
    """识别关键支撑/压力位"""
    if df is None or len(df) < 30:
        return {}, {}
    
    high = df['high']
    low = df['low']
    close = df['close']
    
    # 支撑位
    supports = {}
    # 前低支撑
    low_20 = low.tail(20).min()
    supports['前低支撑'] = low_20
    
    # 均线支撑
    ma20 = close.rolling(20).mean().iloc[-1]
    supports['20日均线'] = ma20
    
    ma60 = close.rolling(60).mean().iloc[-1]
    supports['60日均线'] = ma60
    
    # 压力位
    resistances = {}
    high_20 = high.tail(20).max()
    resistances['前高压力'] = high_20
    
    return supports, resistances


def 走势推演(df, 支撑位, 压力位, 总分):
    """推演三种可能走势"""
    current = df['close'].iloc[-1]
    
    # 路径1：主升延续
    if 总分 >= 60:
        path1_prob = 50
        path1_cond = "缩量回踩不破关键均线"
    else:
        path1_prob = 30
        path1_cond = "放量突破压力位"
    
    # 路径2：震荡洗盘
    path2_prob = 35
    path2_cond = "放量不涨、反复假突破"
    
    # 路径3：趋势破坏
    path3_prob = 15
    path3_cond = "放量跌破关键结构位"
    
    return {
        "主升延续": {"概率": path1_prob, "条件": path1_cond},
        "震荡洗盘": {"概率": path2_prob, "条件": path2_cond},
        "趋势破坏": {"概率": path3_prob, "条件": path3_cond}
    }


# ========== 完整分析工作流 ==========

def 完整技术分析(stock_code, df, 所属板块=None, 资金数据=None):
    """
    股票技术分析 - 完整工作流
    
    参数:
        stock_code: 股票代码
        df: 包含 open/high/low/close/vol 的DataFrame
        所属板块: 板块信息（可选）
        资金数据: 主力资金数据（可选）
    
    返回:
        dict: 分析报告
    """
    
    # 1. 定性定位
    结构, 均线得分, 均线详情 = 判断均线结构(df)
    位置, 位置得分 = 判断股价位置(df)
    阶段, 阶段描述 = 推断生命周期阶段(df, 结构, 位置)
    
    # 2. 多维分析
    量价状态, 量价得分, 量价详情 = 分析量价关系(df)
    K线形态, K线得分, K线信号 = 分析K线形态(df)
    主力类型, 主力得分, 主力详情 = 分析主力行为(df)
    板块状态, 板块得分, 板块详情 = 分析板块环境(stock_code, 所属板块)
    
    # 3. 综合评分
    总分 = 均线得分 + 量价得分 + K线得分 + 主力得分 + 板块得分
    
    if 总分 >= 80:
        等级 = "【强势主升】"
        建议 = "积极参与，趋势持有"
    elif 总分 >= 60:
        等级 = "【可操作】"
        建议 = "回调买入，择时操作"
    elif 总分 >= 40:
        等级 = "【观望】"
        建议 = "等信号，不追高"
    else:
        等级 = "【风险区】"
        建议 = "回避或仅短线"
    
    # 4. 关键位识别
    支撑位, 压力位 = 识别关键位(df)
    
    # 5. 走势推演
    路径推演 = 走势推演(df, 支撑位, 压力位, 总分)
    
    # 6. 生成报告
    report = f"""
═══════════════════════════════════════════════════════════════════════
【{stock_code}】技术分析报告 - {datetime.now().strftime('%Y-%m-%d %H:%M')}
═══════════════════════════════════════════════════════════════════════

【一、综合判断】
该股目前处于【{阶段}】阶段，
均线结构【{结构}】，
股价位置【{位置}】，
量价关系【{量价状态}】，
主力行为偏向【{主力类型}】。

{阶段描述}

【二、多维分析结果】
├─ 均线结构（{均线得分}/20）：{结构}，{均线详情.get('斜率', '')}
├─ 量价关系（{量价得分}/25）：{量价状态}
│   └─ {量价详情.get('描述', '')}
├─ K线形态（{K线得分}/15）：{K线形态}
├─ 主力行为（{主力得分}/20）：{主力类型}
│   └─ {主力详情.get('描述', '')}
└─ 板块环境（{板块得分}/20）：{板块状态}

【三、综合评分】{总分}分/100 → {等级}

【四、关键位】
├─ 支撑位：{list(支撑位.values())}
└─ 压力位：{list(压力位.values())}

【五、走势推演】
├─ 主升延续（{路径推演['主升延续']['概率']}%）：{路径推演['主升延续']['条件']}
├─ 震荡洗盘（{路径推演['震荡洗盘']['概率']}%）：{路径推演['震荡洗盘']['条件']}
└─ 趋势破坏（{路径推演['趋势破坏']['概率']}%）：{路径推演['趋势破坏']['条件']}

【六、主力意图推断】
当前更符合【{主力类型}】模型，短期核心任务为：
【{主力详情.get('描述', '震荡整理')}】

【七、操作建议】
├─ 空仓者：{建议}
├─ 轻仓者：【回踩{list(支撑位.values())[0] if 支撑位 else "关键位"}可加仓】
└─ 重仓者：【以{list(支撑位.values())[0] if 支撑位 else "均线"}为止损参考】

【八、风控要点】
├─ 关键支撑：{list(支撑位.values())[0] if 支撑位 else "待计算"}
├─ 止损位：【跌破{list(支撑位.values())[0] if 支撑位 else "5%"}纪律止损】
└─ 止盈策略：【涨幅超20%分批止盈，跌破5日均线清仓】

═══════════════════════════════════════════════════════════════════════
"""
    
    return {
        'report': report,
        'score': 总分,
        'level': 等级,
        'stage': 阶段,
        'ma_structure': 结构,
        'volume_price': 量价状态,
        'main_force': 主力类型,
        'supports': 支撑位,
        'resistances': 压力位,
        'paths': 路径推演
    }


def 快速分析(stock_code, df):
    """
    快速分析 - 精简版
    """
    if df is None or len(df) < 10:
        return "数据不足"
    
    # 简化判断
    ma5 = df['close'].rolling(5).mean().iloc[-1]
    ma20 = df['close'].rolling(20).mean().iloc[-1]
    current = df['close'].iloc[-1]
    
    if ma5 > ma20:
        trend = "【多头】"
    else:
        trend = "【空头】"
    
    # 量价
    vol_now = df['volume'].iloc[-1]
    vol_ma = df['volume'].rolling(10).mean().iloc[-1]
    
    if vol_now > vol_ma * 1.5:
        volume = "【放量】"
    else:
        volume = "【缩量】"
    
    change = (current - df['close'].iloc[-5]) / df['close'].iloc[-5] * 100
    
    return f"{stock_code}: {trend} {volume} 近5日{change:+.1f}%"


# ========== 测试 ==========

if __name__ == '__main__':
    # 测试数据
    import random
    
    # 生成模拟数据
    dates = pd.date_range(end=datetime.now(), periods=60)
    close = [10 + i * 0.1 + random.uniform(-0.3, 0.3) for i in range(60)]
    df = pd.DataFrame({
        'trade_date': dates,
        'open': close,
        'close': close,
        'high': [c + random.uniform(0, 0.2) for c in close],
        'low': [c - random.uniform(0, 0.2) for c in close],
        'volume': [1000000 + random.randint(-200000, 300000) for _ in range(60)]
    })
    
    print("=" * 60)
    print("技术分析模块测试")
    print("=" * 60)
    
    # 快速分析
    print("\n【快速分析】")
    print(快速分析('000001', df))
    
    # 完整分析
    print("\n【完整分析】")
    result = 完整技术分析('000001', df)
    print(result['report'])
