#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票数据分析工具函数
快速查询、分析股票数据

使用方法:
    from stock_data_utils import StockDataUtils
    utils = StockDataUtils()
    utils.get_stock_price('000001')
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '../data/stock_analysis.db')


class StockDataUtils:
    """股票数据工具类"""
    
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
    
    # ========== 查询函数 ==========
    
    def query(self, sql, params=None):
        """通用查询"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql(sql, conn, params=params)
        conn.close()
        return df
    
    def get_stock_list(self):
        """获取全部股票"""
        return self.query("SELECT * FROM stocks")
    
    def get_stock_price(self, ts_code, days=30):
        """获取股票价格"""
        sql = """
            SELECT * FROM daily_data 
            WHERE ts_code = ? 
            ORDER BY trade_date DESC 
            LIMIT ?
        """
        return self.query(sql, [ts_code, days])
    
    def get_stock_fundflow(self, ts_code, days=30):
        """获取资金流向"""
        sql = """
            SELECT * FROM fund_flow 
            WHERE ts_code = ? 
            ORDER BY trade_date DESC 
            LIMIT ?
        """
        return self.query(sql, [ts_code, days])
    
    def get_market_sentiment(self, days=10):
        """获取市场情绪"""
        return self.query(f"""
            SELECT * FROM market_sentiment 
            ORDER BY trade_date DESC 
            LIMIT {days}
        """)
    
    def get_top_list(self, date=None):
        """获取龙虎榜"""
        if date:
            return self.query("SELECT * FROM top_list WHERE trade_date = ?", [date])
        return self.query("SELECT * FROM top_list ORDER BY trade_date DESC LIMIT 100")
    
    # ========== 筛选函数 ==========
    
    def filter_by_pe(self, low=0, high=50):
        """按PE筛选"""
        return self.query("""
            SELECT * FROM stocks 
            WHERE pe BETWEEN ? AND ? 
            ORDER BY pe ASC
        """, [low, high])
    
    def filter_by_turnover(self, min_rate=1, max_rate=10):
        """按换手率筛选"""
        return self.query("""
            SELECT * FROM stocks 
            WHERE turnover_rate BETWEEN ? AND ? 
            ORDER BY turnover_rate DESC
        """, [min_rate, max_rate])
    
    def filter_by_change(self, min_change=-5, max_change=10):
        """按涨跌幅筛选"""
        return self.query("""
            SELECT * FROM stocks 
            WHERE 涨跌幅 BETWEEN ? AND ? 
            ORDER BY 涨跌幅 DESC
        """, [min_change, max_change])
    
    # ========== 排行榜 ==========
    
    def get_rising_stocks(self, days=5, limit=20):
        """涨幅榜"""
        return self.query(f"""
            SELECT ts_code, MAX(涨跌幅) as max_change 
            FROM daily_data 
            WHERE trade_date >= date('now', '-{days} days')
            GROUP BY ts_code 
            ORDER BY max_change DESC 
            LIMIT {limit}
        """)
    
    def get_volume_leaders(self, days=1, limit=20):
        """成交量榜"""
        return self.query(f"""
            SELECT ts_code, SUM(vol) as total_vol 
            FROM daily_data 
            WHERE trade_date >= date('now', '-{days} days')
            GROUP BY ts_code 
            ORDER BY total_vol DESC 
            LIMIT {limit}
        """)
    
    def get_fundflow_leaders(self, days=5, limit=20):
        """资金流向榜"""
        return self.query(f"""
            SELECT ts_code, SUM(main_net_inflow) as total_flow 
            FROM fund_flow 
            WHERE trade_date >= date('now', '-{days} days')
            GROUP BY ts_code 
            ORDER BY total_flow DESC 
            LIMIT {limit}
        """)
    
    # ========== 技术指标 ==========
    
    def calc_ma(self, ts_code, periods=[5, 10, 20, 60]):
        """计算均线"""
        df = self.get_stock_price(ts_code, 250)
        if df is None or df.empty:
            return None
        
        df = df.sort_values('trade_date')
        result = {}
        
        for p in periods:
            result[f'ma{p}'] = df['close'].rolling(p).mean().iloc[-1]
        
        return result
    
    def get_technical_signal(self, ts_code):
        """技术面综合信号"""
        df = self.get_stock_price(ts_code, 60)
        if df is None or df.empty:
            return {'signal': '无数据'}
        
        df = df.sort_values('trade_date')
        close = df['close']
        
        # 均线
        ma5 = close.rolling(5).mean().iloc[-1]
        ma10 = close.rolling(10).mean().iloc[-1]
        ma20 = close.rolling(20).mean().iloc[-1]
        ma60 = close.rolling(60).mean().iloc[-1]
        
        # 趋势判断
        if close.iloc[-1] > ma20 > ma60:
            trend = "上升趋势"
        elif close.iloc[-1] < ma20 < ma60:
            trend = "下降趋势"
        else:
            trend = "震荡整理"
        
        # 均线排列
        if ma5 > ma10 > ma20 > ma60:
            ma_signal = "多头排列"
        elif ma5 < ma10 < ma20 < ma60:
            ma_signal = "空头排列"
        else:
            ma_signal = "均线混乱"
        
        # 动量
        change_5d = (close.iloc[-1] / close.iloc[-6] - 1) * 100 if len(close) >= 6 else 0
        change_20d = (close.iloc[-1] / close.iloc[-21] - 1) * 100 if len(close) >= 21 else 0
        
        return {
            'trend': trend,
            'ma_signal': ma_signal,
            'ma5': round(ma5, 2),
            'ma20': round(ma20, 2),
            'change_5d': round(change_5d, 2),
            'change_20d': round(change_20d, 2),
            'current_price': close.iloc[-1]
        }
    
    # ========== 导出 ==========
    
    def export_to_csv(self, sql, filename):
        """导出CSV"""
        df = self.query(sql)
        df.to_csv(filename, index=False)
        return filename


# 便捷函数
def get_daily_summary():
    """每日行情汇总"""
    utils = StockDataUtils()
    
    return {
        'sentiment': utils.get_market_sentiment(1).to_dict('records'),
        'rising': utils.get_rising_stocks(5).to_dict('records'),
        'fundflow': utils.get_fundflow_leaders(3).to_dict('records'),
        'total_stocks': len(utils.get_stock_list())
    }


if __name__ == '__main__':
    # 测试
    utils = StockDataUtils()
    
    print("=" * 50)
    print("股票数据工具测试")
    print("=" * 50)
    
    # 股票总数
    stocks = utils.get_stock_list()
    print(f"股票总数: {len(stocks)}")
    
    # 涨幅榜
    rising = utils.get_rising_stocks(5)
    print(f"\n近5日涨幅榜:")
    print(rising.head(10))
    
    # 技术信号
    signal = utils.get_technical_signal('000001')
    print(f"\n平安银行技术信号:")
    print(signal)
