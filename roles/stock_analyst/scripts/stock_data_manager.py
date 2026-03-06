#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中国股票实时交易数据信息库
支持: AKShare, BaoStock

数据范围: 2025-01-01 至今

使用方法:
    python stock_data_manager.py --mode all       # 全量更新
    python stock_data_manager.py --mode daily    # 每日更新
    python stock_data_manager.py --mode stock    # 获取股票列表
"""

import akshare as ak
import baostock as bs
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import os
import sys
import time
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 路径配置
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DB_PATH = os.path.join(DATA_DIR, 'stock_analysis.db')
RAW_DAILY_DIR = os.path.join(DATA_DIR, 'raw/daily')
RAW_FUNDFLOW_DIR = os.path.join(DATA_DIR, 'raw/fundflow')
RAW_MARKET_DIR = os.path.join(DATA_DIR, 'raw/market')

# 日期配置
START_DATE = '2025-01-01'
END_DATE = datetime.now().strftime('%Y-%m-%d')


class StockDataManager:
    """股票数据管理器"""
    
    def __init__(self):
        self._init_dirs()
        self._init_database()
    
    def _init_dirs(self):
        """初始化目录"""
        dirs = [DATA_DIR, RAW_DAILY_DIR, RAW_FUNDFLOW_DIR, RAW_MARKET_DIR]
        for d in dirs:
            os.makedirs(d, exist_ok=True)
        logger.info(f"数据目录: {DATA_DIR}")
    
    def _init_database(self):
        """初始化数据库"""
        if not os.path.exists(DB_PATH):
            logger.info("创建数据库...")
        
        conn = sqlite3.connect(DB_PATH)
        with open(os.path.join(BASE_DIR, 'database/sql/00-init.sql'), 'r') as f:
            conn.executescript(f.read())
        conn.close()
        logger.info("数据库初始化完成")
    
    # ========== 股票基础数据 ==========
    
    def get_stock_list(self):
        """获取A股全部股票列表"""
        logger.info("正在获取股票列表...")
        
        try:
            # AKShare获取
            stock_df = ak.stock_zh_a_spot_em()
            stock_df.columns = [
                '代码', '名称', '最新价', '涨跌幅', '涨跌额', '成交量', '成交额',
                '振幅', '最高', '最低', '今开', '昨收', '量比', '换手率', '市盈率',
                '市净率', '总市值', '流通市值', '涨速', '5分钟涨跌', '60日涨跌幅', '年初至今涨跌幅'
            ]
            stock_df['ts_code'] = stock_df['代码']
            stock_df['list_date'] = None  # akshare不提供上市日期
            
            # 保存CSV
            csv_path = os.path.join(RAW_DAILY_DIR, 'stock_list.csv')
            stock_df.to_csv(csv_path, index=False, encoding='utf-8-sig')
            
            # 保存到数据库
            conn = sqlite3.connect(DB_PATH)
            stock_df[['ts_code', '代码', '名称', '最新价', '涨跌幅', '换手率', '市盈率', '市净率']].to_sql(
                'stocks', conn, if_exists='replace', index=False
            )
            conn.close()
            
            logger.info(f"获取股票 {len(stock_df)} 只")
            return stock_df
            
        except Exception as e:
            logger.error(f"获取股票列表失败: {e}")
            return None
    
    # ========== 日线行情数据 ==========
    
    def get_daily_data(self, symbol=None, start_date=START_DATE, end_date=END_DATE):
        """获取日线行情数据"""
        logger.info(f"正在获取日线数据: {symbol or '全部'}...")
        
        if symbol:
            # 获取单只股票
            df = self._get_single_stock_daily(symbol, start_date, end_date)
            if df is not None:
                self._save_daily_to_db(df)
            return df
        else:
            # 获取全部股票
            stock_df = ak.stock_zh_a_spot_em()
            symbols = stock_df['代码'].tolist()
            
            success, failed = 0, 0
            for i, sym in enumerate(symbols):
                if (i + 1) % 100 == 0:
                    logger.info(f"进度: {i+1}/{len(symbols)}")
                
                try:
                    df = self._get_single_stock_daily(sym, start_date, end_date)
                    if df is not None:
                        self._save_daily_to_db(df)
                        success += 1
                    else:
                        failed += 1
                    time.sleep(0.1)  # 避免请求过快
                except Exception as e:
                    logger.warning(f"{sym} 获取失败: {e}")
                    failed += 1
            
            logger.info(f"完成: 成功 {success}, 失败 {failed}")
            return success
    
    def _get_single_stock_daily(self, symbol, start_date, end_date):
        """获取单只股票日线"""
        try:
            df = ak.stock_zh_a_hist(
                symbol=symbol,
                period="daily",
                start_date=start_date.replace('-', ''),
                end_date=end_date.replace('-', ''),
                adjust="qfq"
            )
            
            if df is not None and not df.empty:
                df['ts_code'] = symbol
                # 转换日期格式
                df['trade_date'] = pd.to_datetime(df['日期']).dt.strftime('%Y-%m-%d')
                return df
            return None
            
        except Exception as e:
            logger.debug(f"{symbol}: {e}")
            return None
    
    def _save_daily_to_db(self, df):
        """保存日线数据到数据库"""
        if df is None or df.empty:
            return
        
        conn = sqlite3.connect(DB_PATH)
        
        # 选择需要的列
        cols = ['ts_code', 'trade_date', '开盘', '最高', '最低', '收盘', 
                '成交量', '成交额', '振幅', '涨跌幅', '涨跌额', '换手率']
        
        # 检查列是否存在
        available_cols = [c for c in cols if c in df.columns]
        save_df = df[available_cols].copy()
        save_df.columns = ['ts_code', 'trade_date', 'open', 'high', 'low', 'close',
                          'vol', 'amount', 'pct_chg', 'change', 'amount_rate', 'turnover']
        
        save_df.to_sql('daily_data', conn, if_exists='append', index=False)
        conn.close()
    
    # ========== 资金流向数据 ==========
    
    def get_fundflow_data(self, date=None):
        """获取资金流向数据"""
        date = date or END_DATE
        logger.info(f"正在获取资金流向: {date}...")
        
        try:
            # AKShare获取
            df = ak.stock_fund_flow_mainboard(symbol="all", date=date)
            
            if df is not None and not df.empty:
                # 保存CSV
                csv_path = os.path.join(RAW_FUNDFLOW_DIR, f'fundflow_{date}.csv')
                df.to_csv(csv_path, index=False, encoding='utf-8-sig')
                
                # 保存到数据库
                conn = sqlite3.connect(DB_PATH)
                df.to_sql('fund_flow', conn, if_exists='append', index=False)
                conn.close()
                
                logger.info(f"获取资金流向 {len(df)} 条")
                return df
            return None
            
        except Exception as e:
            logger.error(f"获取资金流向失败: {e}")
            return None
    
    def get_fundflow_history(self, days=30):
        """获取最近N天资金流向"""
        logger.info(f"获取最近{days}天资金流向...")
        
        end_date = datetime.now()
        dates = []
        
        for i in range(days):
            d = end_date - timedelta(days=i)
            date_str = d.strftime('%Y-%m-%d')
            # 跳过周末
            if d.weekday() < 5:
                dates.append(date_str)
        
        for date in dates:
            self.get_fundflow_data(date)
            time.sleep(0.5)
    
    # ========== 市场情绪数据 ==========
    
    def get_market_sentiment(self, date=None):
        """获取市场情绪数据"""
        date = date or END_DATE
        logger.info(f"正在获取市场情绪: {date}...")
        
        try:
            # 指数数据
            sh_df = ak.stock_zh_index_spot(symbol="sh000001")  # 上证指数
            sz_df = ak.stock_zh_index_spot(symbol="sz399001")  # 深证成指
            cy_df = ak.stock_zh_index_spot(symbol="sz399006")  # 创业板
            
            # 涨跌统计
            market_df = ak.stock_em_market_hot()  # 热门板块
            limit_df = ak.stock_em_analyst()  # 涨跌停
            
            # 合并数据
            sentiment = {
                'trade_date': date,
                'sh_index': sh_df['最新价'].iloc[0] if sh_df is not None else None,
                'sz_index': sz_df['最新价'].iloc[0] if sz_df is not None else None,
                'cy_index': cy_df['最新价'].iloc[0] if cy_df is not None else None,
                'up_limit_count': len(limit_df[limit_df['涨跌幅'] > 9]) if limit_df is not None else 0,
                'down_limit_count': len(limit_df[limit_df['涨跌幅'] < -9]) if limit_df is not None else 0,
                'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # 保存
            df = pd.DataFrame([sentiment])
            conn = sqlite3.connect(DB_PATH)
            df.to_sql('market_sentiment', conn, if_exists='append', index=False)
            conn.close()
            
            logger.info(f"市场情绪数据已保存")
            return sentiment
            
        except Exception as e:
            logger.error(f"获取市场情绪失败: {e}")
            return None
    
    # ========== 龙虎榜数据 ==========
    
    def get_top_list(self, date=None):
        """获取龙虎榜数据"""
        date = date or END_DATE
        logger.info(f"正在获取龙虎榜: {date}...")
        
        try:
            df = ak.stock_em_lhbd(date=date)
            
            if df is not None and not df.empty:
                conn = sqlite3.connect(DB_PATH)
                df.to_sql('top_list', conn, if_exists='append', index=False)
                conn.close()
                
                logger.info(f"获取龙虎榜 {len(df)} 条")
                return df
            return None
            
        except Exception as e:
            logger.error(f"获取龙虎榜失败: {e}")
            return None
    
    # ========== 板块数据 ==========
    
    def get_sector_data(self):
        """获取板块数据"""
        logger.info("正在获取板块数据...")
        
        try:
            # 同花顺板块
            sector_df = ak.stock_em_hsgt_new()
            
            if sector_df is not None and not sector_df.empty:
                conn = sqlite3.connect(DB_PATH)
                sector_df.to_sql('sectors', conn, if_exists='replace', index=False)
                conn.close()
                
                logger.info(f"获取板块 {len(sector_df)} 个")
                return sector_df
            return None
            
        except Exception as e:
            logger.error(f"获取板块数据失败: {e}")
            return None
    
    # ========== 两融数据 ==========
    
    def get_margin_data(self):
        """获取融资融券数据"""
        logger.info("正在获取两融数据...")
        
        try:
            df = ak.stock_margin_detail(symbol="all")
            
            if df is not None and not df.empty:
                conn = sqlite3.connect(DB_PATH)
                df.to_sql('margin_data', conn, if_exists='append', index=False)
                conn.close()
                
                logger.info(f"获取两融数据 {len(df)} 条")
                return df
            return None
            
        except Exception as e:
            logger.error(f"获取两融数据失败: {e}")
            return None
    
    # ========== 批量更新 ==========
    
    def update_all(self, days=30):
        """全量更新"""
        logger.info("=" * 50)
        logger.info("开始全量数据更新")
        logger.info("=" * 50)
        
        # 1. 更新股票列表
        self.get_stock_list()
        
        # 2. 更新日线数据
        self.get_daily_data()
        
        # 3. 更新资金流向
        self.get_fundflow_history(days)
        
        # 4. 更新市场情绪
        self.get_market_sentiment()
        
        # 5. 更新龙虎榜
        self.get_top_list()
        
        # 6. 更新板块
        self.get_sector_data()
        
        logger.info("=" * 50)
        logger.info("数据更新完成!")
        logger.info("=" * 50)
    
    def update_daily(self):
        """每日更新"""
        logger.info("每日数据更新...")
        
        # 更新今日数据
        self.get_fundflow_data()
        self.get_market_sentiment()
        self.get_top_list()
        
        logger.info("每日更新完成")


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='股票数据管理器')
    parser.add_argument('--mode', type=str, default='daily',
                       choices=['all', 'daily', 'stock', 'fundflow', 'market', 'lhb', 'sector'],
                       help='更新模式')
    parser.add_argument('--days', type=int, default=30,
                       help='获取天数')
    parser.add_argument('--symbol', type=str, default=None,
                       help='指定股票代码')
    parser.add_argument('--date', type=str, default=None,
                       help='指定日期')
    
    args = parser.parse_args()
    
    manager = StockDataManager()
    
    if args.mode == 'all':
        manager.update_all(args.days)
    elif args.mode == 'daily':
        manager.update_daily()
    elif args.mode == 'stock':
        manager.get_stock_list()
    elif args.mode == 'fundflow':
        manager.get_fundflow_history(args.days)
    elif args.mode == 'market':
        manager.get_market_sentiment(args.date)
    elif args.mode == 'lhb':
        manager.get_top_list(args.date)
    elif args.mode == 'sector':
        manager.get_sector_data()


if __name__ == '__main__':
    main()
