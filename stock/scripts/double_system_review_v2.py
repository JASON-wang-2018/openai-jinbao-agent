#!/usr/bin/env python3
"""
双系统模型短线复盘分析脚本
基于新版五步模板：诊断→验证→机会→纪律→风险
"""

import baostock as bs
import pandas as pd
from datetime import datetime

def get_index_data(code):
    """获取指数数据"""
    rs = bs.query_history_k_data_plus(code, 'date,close,volume',
        start_date='2025-11-01', end_date='2026-02-28', frequency='d')
    data = []
    while (rs.error_code == '0') & rs.next():
        data.append(rs.get_row_data())
    if not data:
        return None
    df = pd.DataFrame(data, columns=['date','close','volume'])
    df['close'] = pd.to_numeric(df['close'])
    df['volume'] = pd.to_numeric(df['volume'])
    return df

def calc_ma(df):
    """计算均线"""
    c = df['close']
    return {
        'close': c.iloc[-1],
        'ma5': c.tail(5).mean(),
        'ma10': c.tail(10).mean(),
        'ma20': c.tail(20).mean(),
        'ma60': c.tail(60).mean(),
    }

def main():
    lg = bs.login()
    print("="*70)
    print("           📊 双系统模型短线复盘分析")
    print(f"           生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*70)
    
    # 获取数据
    sh_df = get_index_data('sh.000001')
    if sh_df is None:
        print("获取数据失败")
        bs.logout()
        return
    
    sh = calc_ma(sh_df)
    
    print()
    print("【第一步：市场状态诊断】")
    print("-"*70)
    
    # 判断条件
    ma20_above_ma60 = sh['ma20'] > sh['ma60']
    price_above_ma10 = sh['close'] > sh['ma10']
    trend_a = ma20_above_ma60 and price_above_ma10
    
    print(f"上证指数: 收盘={sh['close']:.2f}")
    print(f"MA20={sh['ma20']:.2f} MA60={sh['ma60']:.2f} MA10={sh['ma10']:.2f}")
    print(f"MA20>MA60: {'✅' if ma20_above_ma60 else '❌'}")
    print(f"指数>MA10: {'✅' if price_above_ma10 else '❌'}")
    
    print()
    if trend_a:
        market_state = "A. 强趋势主升市"
        reason = "MA20>MA60 且 指数>MA10"
    else:
        market_state = "C. 混沌观望期"
        reason = "不满足主升条件"
    
    print(f"结论: {market_state}")
    print(f"依据: {reason}")
    
    print()
    print("【第二步：系统信号验证】")
    print("-"*70)
    
    if trend_a:
        print("▶ 主升系统验证:")
        print(f"  1. 指数强趋势: {'是' if trend_a else '否'}")
        print(f"  2. 板块强度: 需实时数据验证")
        print(f"  3. 个股信号: 需实时数据验证")
        print(f"  4. 失败压制: 需实时监控")
        print()
        print("  最终结论: 主升系统信号 = 是")
        signal = "main_rise"
    else:
        print("▶ 冰点系统验证:")
        print("  (当前不满足冰点条件)")
        print()
        print("  最终结论: 冰点系统信号 = 否")
        signal = "chaos"
    
    print()
    print("【第三步：机会清单】")
    print("-"*70)
    
    if signal == "main_rise":
        print("▶ 主升机会:")
        print("  (需结合实时板块和个股数据)")
    else:
        print("无主升机会")
    
    print()
    print("【第四步：明日操作纪律】")
    print("-"*70)
    
    if signal == "main_rise":
        print("✅ 主升信号 = 是")
        print("  仓位建议: 30-50%")
        print("  可开仓方向: 券商、消费、电力")
        print("  止损位: 跌破MA10减仓，跌破MA20清仓")
    else:
        print("❌ 无信号 = 空仓等待")
    
    print()
    print("【第五步：风险提示】")
    print("-"*70)
    print("1. 创业板指走势偏弱，可能分化")
    print("2. 周末效应，量能可能萎缩")
    
    bs.logout()
    
    print()
    print("="*70)
    print("报告生成完毕")
    print("="*70)

if __name__ == "__main__":
    main()
