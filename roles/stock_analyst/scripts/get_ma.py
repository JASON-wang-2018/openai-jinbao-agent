#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MA均线数据获取脚本
使用Baostock获取历史K线，自动计算MA5/10/20/60

使用方法：
    python get_ma.py --code 000001
    python get_ma.py --code 000001 --days 120
    python get_ma.py --all  # 获取所有主要指数
"""

import sys
import os
import baostock as bs
import pandas as pd
import argparse
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class MADataFetcher:
    """MA均线数据获取器"""
    
    def __init__(self):
        self.data = {}
    
    def get_stock_ma(self, code, days=120):
        """
        获取个股MA数据
        
        Args:
            code: 股票代码 (如: 000001)
            days: 获取天数
        
        Returns:
            dict: MA数据
        """
        bs.login()
        
        try:
            # 确定市场
            if code.startswith('6'):
                bs_code = f"sh.{code}"
            else:
                bs_code = f"sz.{code}"
            
            # 计算起始日期
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=days * 1.5)).strftime('%Y-%m-%d')
            
            # 获取日线数据
            rs = bs.query_history_k_data_plus(
                bs_code,
                "date,code,open,high,low,close,volume,amount",
                start_date=start_date,
                end_date=end_date,
                frequency="d",
                adjustflag="2"
            )
            
            data_list = []
            while (rs.error_code == '0') & rs.next():
                data_list.append(rs.get_row_data())
            
            if not data_list:
                return None
            
            # 转换为DataFrame
            df = pd.DataFrame(data_list, columns=[
                'date', 'code', 'open', 'high', 'low', 'close', 'volume', 'amount'
            ])
            
            # 转换为数值
            for col in ['open', 'high', 'low', 'close', 'volume', 'amount']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # 过滤空值
            df = df.dropna(subset=['close'])
            
            if len(df) == 0:
                return None
            
            # 计算MA
            df['MA5'] = df['close'].rolling(window=5).mean()
            df['MA10'] = df['close'].rolling(window=10).mean()
            df['MA20'] = df['close'].rolling(window=20).mean()
            df['MA60'] = df['close'].rolling(window=60).mean()
            df['MA120'] = df['close'].rolling(window=120).mean()
            
            # 计算MACD
            exp12 = df['close'].ewm(span=12).mean()
            exp26 = df['close'].ewm(span=26).mean()
            df['DIF'] = exp12 - exp26
            df['DEA'] = df['DIF'].ewm(span=9).mean()
            df['MACD'] = (df['DIF'] - df['DEA']) * 2
            
            # 计算RSI
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            
            # 获取最新数据
            latest = df.iloc[-1]
            prev = df.iloc[-2] if len(df) > 1 else latest
            
            # 计算MA斜率（近5日变化）
            ma5_series = df['MA5'].dropna()
            if len(ma5_series) >= 5:
                ma5_slope = (ma5_series.iloc[-1] - ma5_series.iloc[-5]) / ma5_series.iloc[-5] * 100
            else:
                ma5_slope = 0
            
            # 计算价格位置（相对于MA60）
            price = latest['close']
            ma60 = latest['MA60']
            if pd.notna(ma60) and ma60 > 0:
                position = (price - ma60) / ma60 * 100
            else:
                position = 0
            
            # 均线结构判断
            ma5 = latest['MA5']
            ma10 = latest['MA10']
            ma20 = latest['MA20']
            ma60 = latest['MA60']
            
            if pd.notna(ma5) and pd.notna(ma10) and pd.notna(ma20) and pd.notna(ma60):
                if ma5 > ma10 > ma20 > ma60:
                    structure = "多头发散"
                elif ma5 < ma10 < ma20 < ma60:
                    structure = "空头下压"
                elif ma5 > ma10 > ma20:
                    structure = "多头初期"
                elif ma5 < ma10 < ma20:
                    structure = "空头初期"
                elif abs(ma5 - ma10) < price * 0.01:
                    structure = "震荡缠绕"
                else:
                    structure = "震荡整理"
            else:
                structure = "数据不足"
            
            return {
                'code': code,
                'date': latest['date'],
                'close': latest['close'],
                'open': latest['open'],
                'high': latest['high'],
                'low': latest['low'],
                'volume': latest['volume'],
                'MA5': ma5,
                'MA10': ma10,
                'MA20': ma20,
                'MA60': ma60,
                'MA120': latest['MA120'],
                'MA5_slope': ma5_slope,
                'position': position,
                'structure': structure,
                'MACD': latest['MACD'],
                'RSI': latest['RSI'],
                '涨跌幅': (latest['close'] - prev['close']) / prev['close'] * 100 if len(df) > 1 else 0
            }
            
        finally:
            bs.logout()
    
    def get_index_ma(self, code, days=120):
        """获取指数MA数据"""
        return self.get_stock_ma(code, days)
    
    def get_all_indices(self, days=120):
        """获取所有主要指数MA"""
        indices = [
            ('sh000001', '上证指数'),
            ('sh000016', '上证50'),
            ('sz399001', '深证成指'),
            ('sz399006', '创业板指'),
            ('sz399905', '中小板指'),
        ]
        
        results = []
        for code, name in indices:
            # 转换代码格式
            bs_code = code.replace('sh', '').replace('sz', '')
            result = self.get_stock_ma(bs_code, days)
            if result:
                result['name'] = name
                results.append(result)
        
        return results


def format_ma_data(data):
    """格式化MA数据输出"""
    if data is None:
        return "数据获取失败"
    
    lines = []
    lines.append("=" * 60)
    lines.append(f"【{data['code']}】MA数据分析")
    lines.append(f"日期: {data['date']}")
    lines.append("=" * 60)
    lines.append("")
    
    # 价格信息
    lines.append("【价格信息】")
    lines.append(f"  当前价格: {data['close']:.2f}")
    lines.append(f"  今日涨跌: {data['涨跌幅']:+.2f}%")
    lines.append(f"  开盘: {data['open']:.2f}")
    lines.append(f"  最高: {data['high']:.2f}")
    lines.append(f"  最低: {data['low']:.2f}")
    lines.append("")
    
    # MA均线
    lines.append("【MA均线】")
    lines.append(f"  MA5:  {data['MA5']:.2f} {'↑' if data['MA5_slope'] > 0 else '↓' if data['MA5_slope'] < 0 else '→'}")
    lines.append(f"  MA10: {data['MA10']:.2f}")
    lines.append(f"  MA20: {data['MA20']:.2f}")
    lines.append(f"  MA60: {data['MA60']:.2f}")
    lines.append(f"  MA120: {data['MA120']:.2f}")
    lines.append("")
    
    # 位置判断
    lines.append("【位置判断】")
    lines.append(f"  均线结构: {data['structure']}")
    lines.append(f"  相对MA60: {data['position']:+.2f}%")
    lines.append("")
    
    # 技术指标
    lines.append("【技术指标】")
    rsi = data['RSI']
    if rsi > 70:
        rsi_status = "超买"
    elif rsi < 30:
        rsi_status = "超卖"
    elif rsi > 50:
        rsi_status = "偏强"
    else:
        rsi_status = "偏弱"
    
    lines.append(f"  RSI(14): {rsi:.1f} ({rsi_status})")
    
    macd = data['MACD']
    if macd > 0:
        macd_status = "多头"
    elif macd < 0:
        macd_status = "空头"
    else:
        macd_status = "中性"
    
    lines.append(f"  MACD: {macd:.3f} ({macd_status})")
    lines.append("")
    
    # 操作建议
    lines.append("【操作建议】")
    structure = data['structure']
    position = data['position']
    rsi = data['RSI']
    
    if structure == "多头发散" and position > 0:
        advice = "趋势良好，可顺势做多"
    elif structure == "空头下压" and position < 0:
        advice = "下降趋势，建议观望"
    elif structure == "震荡缠绕":
        advice = "震荡整理，高抛低吸"
    elif rsi > 70:
        advice = "RSI超买，谨慎追高"
    elif rsi < 30:
        advice = "RSI超卖，可适当关注"
    elif position > 10:
        advice = "价格远离均线，警惕回调"
    elif position < -10:
        advice = "价格偏离均线，可能修复"
    else:
        advice = "观察方向选择"
    
    lines.append(f"  {advice}")
    lines.append("")
    lines.append("=" * 60)
    
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='MA均线数据获取')
    parser.add_argument('--code', type=str, help='股票代码 (如: 000001)')
    parser.add_argument('--days', type=int, default=120, help='获取天数 (默认: 120)')
    parser.add_argument('--all', action='store_true', help='获取所有主要指数')
    parser.add_argument('--json', action='store_true', help='JSON格式输出')
    
    args = parser.parse_args()
    
    fetcher = MADataFetcher()
    
    if args.all:
        # 获取所有指数
        results = fetcher.get_all_indices(days=args.days)
        for data in results:
            print(format_ma_data(data))
    
    elif args.code:
        # 获取单只股票
        data = fetcher.get_stock_ma(args.code, args.days)
        
        if args.json:
            # JSON格式
            import json
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(format_ma_data(data))
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
