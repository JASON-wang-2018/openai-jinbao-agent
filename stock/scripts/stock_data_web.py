#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票数据获取 - 网页数据源版本
支持: AKShare, 新浪财经, 腾讯财经, 东方财富

使用方法:
    python stock_data_web.py --source sina      # 新浪
    python stock_data_web.py --source eastmoney  # 东方财富
    python stock_data_web.py --source all       # 全部
"""

import akshare as ak
import pandas as pd
import sqlite3
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os
import sys
import time
import json
import re
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# 路径配置
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DB_PATH = os.path.join(DATA_DIR, 'stock_analysis.db')

END_DATE = datetime.now().strftime('%Y-%m-%d')


class SinaFinance:
    """新浪财经数据源"""
    
    BASE_URL = "https://finance.sina.com.cn/realstock/company/"
    
    @staticmethod
    def get_stock_quote(symbol):
        """获取股票实时行情"""
        # 新浪接口：sh600000 或 sz000001
        if symbol.startswith('6'):
            code = f"sh{symbol}"
        else:
            code = f"sz{symbol}"
        
        url = f"https://hq.sinajs.cn/list={code}"
        headers = {'Referer': 'https://finance.sina.com.cn'}
        
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code == 200:
                text = resp.text
                # 解析: hq_sh600000="..." 
                data = text.split('"')[1].split(',')
                return {
                    'symbol': symbol,
                    'open': float(data[1]),
                    'high': float(data[2]),
                    'low': float(data[3]),
                    'close': float(data[4]),
                    'volume': int(data[5]) / 100,  # 手
                    'amount': float(data[6]) / 10000,  # 万元
                    'update_time': data[31]
                }
        except Exception as e:
            logger.error(f"新浪获取 {symbol} 失败: {e}")
        return None
    
    @staticmethod
    def get_plate_data(symbol):
        """获取所属板块"""
        url = f"https://finance.sina.com.cn/realstock/company/{symbol}/plate.shtml"
        try:
            resp = requests.get(url, timeout=10)
            soup = BeautifulSoup(resp.text, 'lxml')
            plates = [a.text for a in soup.select('. plate-list a')]
            return plates
        except:
            return []


class EastMoney:
    """东方财富数据源"""
    
    BASE_URL = "https://push2.eastmoney.com/api"
    
    @staticmethod
    def get_stock_list():
        """获取全部股票列表"""
        url = "https://push2.eastmoney.com/api/qy/getList"
        params = {
            'pagesize': 5000,
            'pageindex': 1,
            'isty': 0,
            'fs': 'm',
            'fields': '1,2,3,4,5,6,7,8,9,10'
        }
        
        try:
            resp = requests.get(url, params=params, timeout=30)
            data = resp.json()
            stocks = []
            for item in data['data']['list']:
                stocks.append({
                    'symbol': item['2'],  # 代码
                    'name': item['1'],   # 名称
                    'market': item['3'],  # 市场
                    'type': item['4']     # 类型
                })
            return pd.DataFrame(stocks)
        except Exception as e:
            logger.error(f"东方财富获取股票列表失败: {e}")
            return None
    
    @staticmethod
    def get_daily_kline(symbol, days=250):
        """获取日K线数据"""
        # 上海: sh600000, 深圳: sz000001
        if symbol.startswith('6'):
            market = '1'
            code = f"sh{symbol}"
        else:
            market = '0'
            code = f"sz{symbol}"
        
        url = f"https://push2.eastmoney.com/api/qh/stock/kline"
        params = {
            'fields1': 'f1,f2,f3,f4,f5,f6',
            'fields2': 'f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61',
            'klt': '101',  # 日K
            'fqt': '1',    # 前复权
            'secid': f"{market}.{symbol}",
            'beg': '0',
            'end': str(days * 2)
        }
        
        try:
            resp = requests.get(url, params=params, timeout=30)
            data = resp.json()
            df = pd.DataFrame(data['data']['klines'])
            df.columns = ['trade_date,open,high,low,close,volume,amount,turnover_rate,pct_chg,change,vol_rate'.split(',')]
            return df
        except Exception as e:
            logger.error(f"东方财富获取 {symbol} K线失败: {e}")
            return None
    
    @staticmethod
    def get_fund_flow(symbol):
        """获取资金流向"""
        if symbol.startswith('6'):
            market = '1'
            code = f"sh{symbol}"
        else:
            market = '0'
            code = f"sz{symbol}"
        
        url = "https://push2.eastmoney.com/api/qh/klc"
        params = {
            'type': 'kline',
            'sty': 'HSR,HSGZZ,XXL',
            'symbol': code,
            'fields': 'f1,f2,f3,f4,f5,f6'
        }
        
        try:
            resp = requests.get(url, params=params, timeout=10)
            return resp.json()
        except Exception as e:
            logger.error(f"东方财富获取 {symbol} 资金流向失败: {e}")
            return None
    
    @staticmethod
    def get_market_hot():
        """获取市场热点板块"""
        url = "https://push2.eastmoney.com/api/qt/clist/get"
        params = {
            'pn': 1,
            'pz': 50,
            'fs': 'm',
            'fields': 'f1,f2,f3,f4,f12,f13,f14,f15,f16,f17,f18'
        }
        
        try:
            resp = requests.get(url, params=params, timeout=30)
            data = resp.json()
            return pd.DataFrame(data['data']['list'])
        except Exception as e:
            logger.error(f"获取热点板块失败: {e}")
            return None


class TencentFinance:
    """腾讯财经数据源"""
    
    BASE_URL = "https://stockapp.finance.qq.com"
    
    @staticmethod
    def get_stock_quote(symbol):
        """获取股票实时行情"""
        if symbol.startswith('6'):
            code = f"sh{symbol}"
        else:
            code = f"sz{symbol}"
        
        url = f"https://stockapp.finance.qq.com/mstats/"
        params = {'id': code}
        
        try:
            resp = requests.get(url, params=params, timeout=10)
            data = resp.json()
            if 'data' in data and code in data['data']:
                info = data['data'][code]
                return {
                    'symbol': symbol,
                    'open': info['open'],
                    'high': info['high'],
                    'low': info['low'],
                    'close': info['price'],
                    'volume': info['vol'],
                    'amount': info['amount'],
                    'chg': info['chg'],
                    'pct_chg': info['pct_chg']
                }
        except Exception as e:
            logger.error(f"腾讯获取 {symbol} 失败: {e}")
        return None


class StockDataFetcher:
    """统一数据获取接口"""
    
    def __init__(self):
        self.sina = SinaFinance()
        self.eastmoney = EastMoney()
        self.tencent = TencentFinance()
        self._init_dirs()
        self._init_db()
    
    def _init_dirs(self):
        """初始化目录"""
        dirs = [DATA_DIR, os.path.join(DATA_DIR, 'raw/sina'),
                os.path.join(DATA_DIR, 'raw/eastmoney'),
                os.path.join(DATA_DIR, 'raw/tencent')]
        for d in dirs:
            os.makedirs(d, exist_ok=True)
    
    def _init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(DB_PATH)
        with open(os.path.join(BASE_DIR, 'database/sql/00-init.sql'), 'r') as f:
            conn.executescript(f.read())
        conn.close()
    
    # ========== 实时行情 ==========
    
    def fetch_realtime_quote(self, symbols=None, source='sina'):
        """获取实时行情"""
        logger.info(f"获取实时行情 from {source}...")
        
        if symbols is None:
            # 先获取全部股票列表
            conn = sqlite3.connect(DB_PATH)
            df = pd.read_sql("SELECT symbol FROM stocks", conn)
            conn.close()
            symbols = df['symbol'].tolist()[:100]  # 先取100只
        
        quotes = []
        for sym in symbols:
            if source == 'sina':
                quote = self.sina.get_stock_quote(sym)
            elif source == 'tencent':
                quote = self.tencent.get_stock_quote(sym)
            
            if quote:
                quotes.append(quote)
            
            time.sleep(0.1)  # 避免请求过快
        
        df = pd.DataFrame(quotes)
        if not df.empty:
            csv_path = os.path.join(DATA_DIR, f'raw/{source}/quote_{datetime.now().strftime("%Y%m%d")}.csv')
            df.to_csv(csv_path, index=False)
            logger.info(f"获取 {len(df)} 条实时行情")
        
        return df
    
    # ========== K线数据 ==========
    
    def fetch_kline(self, symbol, source='eastmoney', days=250):
        """获取K线数据"""
        logger.info(f"获取 {symbol} K线 from {source}...")
        
        if source == 'eastmoney':
            df = self.eastmoney.get_daily_kline(symbol, days)
        
        return df
    
    # ========== 资金流向 ==========
    
    def fetch_fundflow(self, symbols=None, source='eastmoney'):
        """获取资金流向"""
        logger.info(f"获取资金流向 from {source}...")
        
        if symbols is None:
            conn = sqlite3.connect(DB_PATH)
            df = pd.read_sql("SELECT symbol FROM stocks", conn)
            conn.close()
            symbols = df['symbol'].tolist()[:100]
        
        results = []
        for sym in symbols:
            if source == 'eastmoney':
                data = self.eastmoney.get_fund_flow(sym)
                if data:
                    results.append({'symbol': sym, 'data': data})
            time.sleep(0.2)
        
        return results
    
    # ========== 热点板块 ==========
    
    def fetch_market_hot(self, source='eastmoney'):
        """获取市场热点"""
        logger.info(f"获取市场热点 from {source}...")
        
        if source == 'eastmoney':
            df = self.eastmoney.get_market_hot()
            if df is not None:
                csv_path = os.path.join(DATA_DIR, f'raw/{source}/hot_{END_DATE}.csv')
                df.to_csv(csv_path, index=False)
            return df
        
        return None
    
    # ========== 股票列表 ==========
    
    def fetch_stock_list(self, source='eastmoney'):
        """获取股票列表"""
        logger.info(f"获取股票列表 from {source}...")
        
        if source == 'eastmoney':
            df = self.eastmoney.get_stock_list()
            if df is not None:
                conn = sqlite3.connect(DB_PATH)
                df.to_sql('stocks', conn, if_exists='replace', index=False)
                conn.close()
                logger.info(f"获取 {len(df)} 只股票")
            return df
        
        return None
    
    # ========== 批量更新 ==========
    
    def update_all_sources(self):
        """更新所有数据源"""
        logger.info("=" * 50)
        logger.info("开始从网页数据源更新")
        logger.info("=" * 50)
        
        # 股票列表
        self.fetch_stock_list('eastmoney')
        
        # 市场热点
        self.fetch_market_hot('eastmoney')
        
        # 实时行情（取部分）
        self.fetch_realtime_quote(symbols=['000001', '600000', '300001'], source='sina')
        
        logger.info("=" * 50)
        logger.info("网页数据源更新完成")
        logger.info("=" * 50)


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='股票数据获取 - 网页数据源')
    parser.add_argument('--source', type=str, default='all',
                       choices=['sina', 'tencent', 'eastmoney', 'all'],
                       help='数据源')
    parser.add_argument('--symbol', type=str, default=None,
                       help='指定股票代码')
    parser.add_argument('--action', type=str, default='quote',
                       choices=['quote', 'kline', 'fundflow', 'hot', 'list', 'all'],
                       help='获取类型')
    
    args = parser.parse_args()
    
    fetcher = StockDataFetcher()
    
    if args.source == 'all':
        fetcher.update_all_sources()
    else:
        if args.action == 'quote':
            fetcher.fetch_realtime_quote(args.symbol, args.source)
        elif args.action == 'kline':
            fetcher.fetch_kline(args.symbol, args.source)
        elif args.action == 'fundflow':
            fetcher.fetch_fundflow(args.symbol, args.source)
        elif args.action == 'hot':
            fetcher.fetch_market_hot(args.source)
        elif args.action == 'list':
            fetcher.fetch_stock_list(args.source)
        elif args.action == 'all':
            if args.symbol:
                fetcher.fetch_kline(args.symbol, args.source)
                fetcher.fetch_fundflow(args.symbol, args.source)
            else:
                fetcher.fetch_stock_list(args.source)
                fetcher.fetch_market_hot(args.source)


if __name__ == '__main__':
    main()
