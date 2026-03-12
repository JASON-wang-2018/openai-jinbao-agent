#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日股票复盘报告 - 定时任务
每天 8:00 和 21:00 执行
"""

import sys
import os
import baostock as bs
from datetime import datetime, timedelta

OUTPUT_DIR = '/home/jason/.openclaw/workspace/stock/reports'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 指数代码映射
INDEX_CODES = {
    '上证指数': 'sh.000001',
    '深证成指': 'sz.399001',
    '创业板指': 'sz.399006',
    '沪深300': 'sh.000300',
    '中证500': 'sh.000905',
}


def is_trading_day():
    """判断是否为交易日"""
    now = datetime.now()
    # 周末休市
    if now.weekday() >= 5:
        return False
    return True


def get_trade_date():
    """获取最近一个有数据的交易日（早盘取昨天，盘后取今日）"""
    now = datetime.now()
    
    # 早盘时间（9:30之前）取前一天
    if now.hour < 9:
        yesterday = now - timedelta(days=1)
        while yesterday.weekday() >= 5:  # 跳过周末
            yesterday -= timedelta(days=1)
        return yesterday.strftime('%Y-%m-%d')
    elif now.hour < 16:
        # 盘中或盘前（9:00-15:30），取昨日数据更可靠
        yesterday = now - timedelta(days=1)
        while yesterday.weekday() >= 5:  # 跳过周末
            yesterday -= timedelta(days=1)
        return yesterday.strftime('%Y-%m-%d')
    else:
        # 盘后（16:00后），取今日
        return now.strftime('%Y-%m-%d')


def get_market():
    """获取大盘数据"""
    if not is_trading_day():
        return None
    
    # 登录 baostock
    lg = bs.login()
    if lg.error_code != '0':
        print(f"Baostock登录失败: {lg.error_msg}")
        return None
    
    trade_date = get_trade_date()
    result = {}
    
    try:
        for name, code in INDEX_CODES.items():
            rs = bs.query_history_k_data_plus(
                code,
                'date,code,open,high,low,close,volume,amount,pctChg',
                start_date=trade_date, 
                end_date=trade_date,
                frequency='d', 
                adjustflag='2'
            )
            
            if rs.error_code == '0' and rs.next():
                data = rs.get_row_data()
                close = float(data[5]) if data[5] else 0
                pct = float(data[8]) if data[8] else 0
                volume = int(data[6]) if data[6] else 0
                
                if close > 0:
                    result[name] = {
                        'close': close,
                        'pct': pct,
                        'volume': volume,
                    }
            
            # baostock 新版不需要手动 free()
        
    finally:
        bs.logout()
    
    return result if result else None


def get_zt_count():
    """获取涨停家数（使用东财涨停统计）"""
    try:
        import requests
        # 东方财富涨停统计
        url = "https://push2.eastmoney.com/api/qt/clist/get"
        params = {
            'pn': 1,
            'pz': 1,
            'po': 1,
            'np': 1,
            'ut': 'bd1d9ddb04089700cf9c27f6f7426281',
            'fltt': 2,
            'invt': 2,
            'fid': 'f3',
            'fs': 'm:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23',
            'fields': 'f2,f3,f4,f12,f13,f14',
        }
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        if data.get('data') and data['data'].get('total'):
            return data['data']['total']
    except:
        pass
    return None


def get_ma_status():
    """获取均线状态"""
    lg = bs.login()
    if lg.error_code != '0':
        return None
    
    trade_date = get_trade_date()
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    result = {}
    for name, code in [('上证指数', 'sh.000001'), ('创业板指', 'sz.399006')]:
        rs = bs.query_history_k_data_plus(
            code,
            'date,close',
            start_date=start_date, 
            end_date=trade_date,
            frequency='d', 
            adjustflag='2'
        )
        
        closes = []
        while rs.error_code == '0' and rs.next():
            row = rs.get_row_data()
            if row[1]:
                closes.append(float(row[1]))
        
        if len(closes) >= 20:
            ma5 = sum(closes[-5:]) / 5
            ma10 = sum(closes[-10:]) / 10
            ma20 = sum(closes[-20:]) / 20
            ma60 = sum(closes[-60:]) / 60 if len(closes) >= 60 else None
            
            current = closes[-1]
            trend = "↑" if ma10 > ma20 else "↓"
            if ma60:
                trend += "↑" if ma20 > ma60 else "↓"
            
            result[name] = {
                'ma10': ma10,
                'ma20': ma20,
                'ma60': ma60,
                'trend': trend,
            }
    
    bs.logout()
    return result


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--time', type=str, default='', help='早盘/午盘/晚间')
    parser.add_argument('--save', action='store_true', help='保存报告')
    args = parser.parse_args()
    
    now = datetime.now()
    
    # 支持命令行参数指定报告类型
    if args.time == '晚间':
        report_type = '晚间'
    elif args.time in ['早盘', '午盘']:
        report_type = args.time
    else:
        report_type = '早盘' if now.hour < 12 else '晚间'
    
    if not is_trading_day():
        print(f"\n今日 {now.strftime('%Y-%m-%d %H:%M')} ({report_type})")
        print("股市休市中（周末/节假日）")
        return
    
    print(f"\n正在生成{report_type}复盘报告...")
    
    # 获取数据
    market = get_market()
    ma_status = get_ma_status()
    zt_count = get_zt_count()
    
    if market is None:
        print("数据获取失败")
        return
    
    lines = []
    lines.append("=" * 60)
    lines.append(f"【A股复盘报告】- {now.strftime('%Y-%m-%d %H:%M')} ({report_type})")
    lines.append("=" * 60)
    lines.append("")
    
    # 一、大盘
    lines.append("【一、大盘】")
    for name in ['上证指数', '深证成指', '创业板指', '沪深300', '中证500']:
        if name in market:
            data = market[name]
            pct = data['pct']
            sign = '+' if pct >= 0 else ''
            vol = data['volume'] / 1e8  # 亿
            lines.append(f"  {name}: {data['close']:.2f} ({sign}{pct:.2f}%) 量:{vol:.0f}亿")
    lines.append("")
    
    # 二、均线状态
    if ma_status:
        lines.append("【二、均线趋势】")
        for name, data in ma_status.items():
            trend = data['trend']
            lines.append(f"  {name}: MA10>{'MA20<' if '↓' in trend else 'MA20>'} {trend}")
        lines.append("")
    
    # 三、情绪指标
    lines.append("【三、情绪指标】")
    if zt_count:
        lines.append(f"  涨停家数: {zt_count}")
    else:
        lines.append("  涨停家数: (获取失败)")
    lines.append("")
    
    # 四、系统信号（简单版）
    lines.append("【四、系统信号】")
    if '上证指数' in market:
        sh_pct = market['上证指数']['pct']
        if sh_pct > 0.5:
            lines.append("  大盘状态: 强势")
        elif sh_pct < -0.5:
            lines.append("  大盘状态: 弱势")
        else:
            lines.append("  大盘状态: 震荡")
    lines.append("")
    
    lines.append("=" * 60)
    
    report = '\n'.join(lines)
    print(report)
    
    # 保存
    # 保存 - 使用命令行指定的time类型，否则根据当前时间判断
    if args.time == '晚间':
        time_suffix = 'pm'
    elif args.time == '早盘':
        time_suffix = 'am'
    else:
        time_suffix = 'am' if now.hour < 12 else 'pm'
    
    filename = f"{OUTPUT_DIR}/report_{now.strftime('%Y-%m-%d')}_{time_suffix}.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\n已保存: {filename}")


if __name__ == '__main__':
    main()
