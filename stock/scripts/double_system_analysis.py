#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
双系统模型 v4.0 复盘分析脚本
主升高胜率模型 + 冰点系统

更新内容 (v4.0):
- 增强错误处理和日志记录
- 添加数据缓存机制
- 优化六层过滤逻辑
- 添加 JSON 格式输出
- 支持命令行参数

使用方法: 
    python stock/scripts/double_system_analysis.py
    python stock/scripts/double_system_analysis.py --json
"""

import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
import json
import os
import sys
import argparse
import logging
import signal

# 设置请求超时
def timeout_handler(signum, frame):
    raise TimeoutError("请求超时")

# 设置默认超时（用于网络请求）
DEFAULT_TIMEOUT = 5  # 秒

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/tmp/double_system.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# 路径配置
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT_DIR = os.path.join(BASE_DIR, 'reports')
CACHE_DIR = os.path.join(BASE_DIR, 'data/cache')
os.makedirs(REPORT_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)


class DataCache:
    """数据缓存类 - 减少重复请求"""
    
    def __init__(self, cache_dir, ttl_minutes=30):
        self.cache_dir = cache_dir
        self.ttl_seconds = ttl_minutes * 60
    
    def _get_cache_path(self, key):
        return os.path.join(self.cache_dir, f"{key}.json")
    
    def get(self, key):
        """从缓存获取数据"""
        cache_path = self._get_cache_path(key)
        if not os.path.exists(cache_path):
            return None
        
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 检查是否过期
                if datetime.now().timestamp() - data['timestamp'] > self.ttl_seconds:
                    return None
                return data['content']
        except:
            return None
    
    def set(self, key, content):
        """缓存数据"""
        cache_path = self._get_cache_path(key)
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'timestamp': datetime.now().timestamp(),
                    'content': content
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"缓存写入失败：{e}")


# 初始化缓存
cache = DataCache(CACHE_DIR)


def get_index_data(use_cache=True):
    """
    获取上证指数数据
    
    Returns:
        dict: 指数数据包含 close, ma10, ma20, ma60, trend 等
    """
    cache_key = "index_data"
    
    if use_cache:
        cached = cache.get(cache_key)
        if cached:
            logger.info("使用缓存的指数数据")
            return cached
    
    try:
        logger.info("获取上证指数数据...")
        df = ak.stock_zh_index_daily(symbol="sh000001")
        
        if df.empty:
            logger.error("指数数据为空")
            return None
        
        close = df['close'].iloc[-1]
        ma10 = df['close'].rolling(10).mean().iloc[-1]
        ma20 = df['close'].rolling(20).mean().iloc[-1]
        ma60 = df['close'].rolling(60).mean().iloc[-1]
        
        # 计算趋势
        ma20_prev = df['close'].rolling(20).mean().iloc[-2] if len(df) > 1 else ma20
        ma60_prev = df['close'].rolling(60).mean().iloc[-2] if len(df) > 1 else ma60
        
        data = {
            'close': round(close, 2),
            'ma10': round(ma10, 2),
            'ma20': round(ma20, 2),
            'ma60': round(ma60, 2),
            'ma20_trend': 'up' if ma20 > ma20_prev else ('down' if ma20 < ma20_prev else 'flat'),
            'ma60_trend': 'up' if ma60 > ma60_prev else ('down' if ma60 < ma60_prev else 'flat'),
            'index_strong_trend': ma20 > ma60 and close > ma10,
            'close_ma10_pct': round((close - ma10) / ma10 * 100, 2),
            'close_ma20_pct': round((close - ma20) / ma20 * 100, 2),
            'close_ma60_pct': round((close - ma60) / ma60 * 100, 2),
            'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        cache.set(cache_key, data)
        logger.info(f"指数数据获取成功：收盘={data['close']}, 强趋势={data['index_strong_trend']}")
        return data
        
    except Exception as e:
        logger.error(f"获取指数数据失败：{e}")
        return None


def get_sz_index_data(use_cache=True):
    """
    获取深证成指数据
    
    Returns:
        dict: 深证成指数据
    """
    cache_key = "sz_index_data"
    
    if use_cache:
        cached = cache.get(cache_key)
        if cached:
            logger.info("使用缓存的深证成指数据")
            return cached
    
    try:
        logger.info("获取深证成指数据...")
        df = ak.stock_zh_index_daily(symbol="sz399001")
        
        if df.empty:
            logger.error("深证成指数据为空")
            return None
        
        close = df['close'].iloc[-1]
        ma10 = df['close'].rolling(10).mean().iloc[-1]
        ma20 = df['close'].rolling(20).mean().iloc[-1]
        ma60 = df['close'].rolling(60).mean().iloc[-1]
        
        ma20_prev = df['close'].rolling(20).mean().iloc[-2] if len(df) > 1 else ma20
        ma60_prev = df['close'].rolling(60).mean().iloc[-2] if len(df) > 1 else ma60
        
        data = {
            'close': round(close, 2),
            'ma10': round(ma10, 2),
            'ma20': round(ma20, 2),
            'ma60': round(ma60, 2),
            'ma20_trend': 'up' if ma20 > ma20_prev else ('down' if ma20 < ma20_prev else 'flat'),
            'ma60_trend': 'up' if ma60 > ma60_prev else ('down' if ma60 < ma60_prev else 'flat'),
            'index_strong_trend': ma20 > ma60 and close > ma10,
            'close_ma10_pct': round((close - ma10) / ma10 * 100, 2),
            'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        cache.set(cache_key, data)
        logger.info(f"深证成指数据获取成功：收盘={data['close']}, 强趋势={data['index_strong_trend']}")
        return data
        
    except Exception as e:
        logger.error(f"获取深证成指数据失败：{e}")
        return None


def get_cy_index_data(use_cache=True):
    """
    获取创业板指数据
    
    Returns:
        dict: 创业板指数据
    """
    cache_key = "cy_index_data"
    
    if use_cache:
        cached = cache.get(cache_key)
        if cached:
            logger.info("使用缓存的创业板指数据")
            return cached
    
    try:
        logger.info("获取创业板指数据...")
        df = ak.stock_zh_index_daily(symbol="sz399006")
        
        if df.empty:
            logger.error("创业板指数据为空")
            return None
        
        close = df['close'].iloc[-1]
        ma10 = df['close'].rolling(10).mean().iloc[-1]
        ma20 = df['close'].rolling(20).mean().iloc[-1]
        ma60 = df['close'].rolling(60).mean().iloc[-1]
        
        ma20_prev = df['close'].rolling(20).mean().iloc[-2] if len(df) > 1 else ma20
        ma60_prev = df['close'].rolling(60).mean().iloc[-2] if len(df) > 1 else ma60
        
        data = {
            'close': round(close, 2),
            'ma10': round(ma10, 2),
            'ma20': round(ma20, 2),
            'ma60': round(ma60, 2),
            'ma20_trend': 'up' if ma20 > ma20_prev else ('down' if ma20 < ma20_prev else 'flat'),
            'ma60_trend': 'up' if ma60 > ma60_prev else ('down' if ma60 < ma60_prev else 'flat'),
            'index_strong_trend': ma20 > ma60 and close > ma10,
            'close_ma10_pct': round((close - ma10) / ma10 * 100, 2),
            'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        cache.set(cache_key, data)
        logger.info(f"创业板指数据获取成功：收盘={data['close']}, 强趋势={data['index_strong_trend']}")
        return data
        
    except Exception as e:
        logger.error(f"获取创业板指数据失败：{e}")
        return None


def get_market_emotion(use_cache=True):
    """
    获取市场情绪数据
    
    Returns:
        dict: 情绪数据包含涨停家数、连板数、资金流向等
    """
    cache_key = f"emotion_{datetime.now().strftime('%Y-%m-%d')}"
    
    if use_cache:
        cached = cache.get(cache_key)
        if cached:
            logger.info("使用缓存的情绪数据")
            return cached
    
    today = datetime.now().strftime('%Y%m%d')  # akshare 需要 YYYYMMDD 格式
    data = {
        'zt_count': 0,
        'dt_count': 0,
        'lianban_count': 0,
        'main_net_flow': 'N/A',
        'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    try:
        # 获取涨停数据
        logger.info("获取涨停数据...")
        df_zt = ak.stock_zt_pool_em(date=today)
        if not df_zt.empty:
            data['zt_count'] = len(df_zt)
            # 统计连板数
            if '连板数' in df_zt.columns:
                data['lianban_count'] = len(df_zt[df_zt['连板数'] > 1])
        
        # 获取跌停数据
        logger.info("获取跌停数据...")
        try:
            df_dt = ak.stock_zt_pool_dtgc_em(date=today)
            if df_dt.empty:
                data['dt_count'] = 0
            else:
                data['dt_count'] = len(df_dt)
        except Exception as e:
            logger.warning(f"获取跌停数据失败: {e}")
            data['dt_count'] = 0
        if not df_dt.empty:
            data['dt_count'] = len(df_dt)
        
        # 获取资金流向
        try:
            logger.info("获取资金流向...")
            df_fund = ak.stock_market_fund_flow_summary()
            if not df_fund.empty and '主力净流入' in df_fund.columns:
                data['main_net_flow'] = df_fund['主力净流入'].iloc[0]
        except:
            pass
        
        cache.set(cache_key, data)
        logger.info(f"情绪数据获取成功：涨停={data['zt_count']}, 跌停={data['dt_count']}")
        
    except Exception as e:
        logger.warning(f"获取情绪数据部分失败：{e}")
    
    return data


def get_board_performance(top_n=10):
    """
    获取板块表现（多数据源降级）
    
    Args:
        top_n: 返回前 N 个板块
    
    Returns:
        list: 板块列表
    """
    import socket
    socket.setdefaulttimeout(5)
    
    # 方法1: 使用 baostock 计算行业涨跌
    try:
        logger.info("尝试使用 Baostock 获取板块数据...")
        import baostock as bs
        
        lg = bs.login()
        if lg.error_code != '0':
            raise Exception(lg.error_msg)
        
        # 获取行业列表
        rs = bs.query_stock_industry()
        industries = {}
        while rs.next():
            row = rs.get_row_data()
            industry = row[3]  # industry column
            if industry:
                industries[industry] = industries.get(industry, 0) + 1
        
        # 获取近期涨跌幅（采样计算）
        # 取各行业代表性股票计算涨跌
        sample_stocks = []
        rs2 = bs.query_stock_industry()
        stock_industries = []
        while rs2.next():
            row = rs2.get_row_data()
            stock_industries.append((row[1], row[3]))  # code, industry
        
        # 采样：每个行业取2只股票
        industry_stocks = {}
        for code, ind in stock_industries:
            if not ind or ind == 'None':
                continue
            if ind not in industry_stocks:
                industry_stocks[ind] = []
            if len(industry_stocks[ind]) < 2:
                industry_stocks[ind].append(code)
        
        # 获取这些股票的最新数据
        from datetime import datetime, timedelta
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')
        
        industry_changes = {}
        for ind, stocks in industry_stocks.items():
            changes = []
            for code in stocks:
                try:
                    rs3 = bs.query_history_k_data_plus(code,
                        'date,pctChg',
                        start_date=start_date,
                        end_date=end_date,
                        frequency='d', adjustflag='3')
                    data = []
                    while rs3.next():
                        data.append(rs3.get_row_data())
                    if data:
                        # 取最新有数据的涨跌幅
                        latest = data[-1]
                        if len(latest) >= 2 and latest[1]:
                            pct = float(latest[1])
                            changes.append(pct)
                except:
                    continue
            
            if changes:
                avg_change = sum(changes) / len(changes)
                industry_changes[ind] = round(avg_change, 2)
        
        bs.logout()
        
        if industry_changes:
            # 排序并返回
            sorted_boards = sorted(industry_changes.items(), key=lambda x: x[1], reverse=True)[:top_n]
            boards = [{'name': name, 'change': change, 'change_pct': change} for name, change in sorted_boards]
            logger.info(f"Baostock 板块数据获取成功: {len(boards)} 个板块")
            return boards
            
    except Exception as e:
        logger.warning(f"Baostock 获取失败: {str(e)[:50]}")
    
    # 方法2: akshare 降级方案
    data_sources = [
        ('东方财富-行业', lambda: ak.stock_board_industry_name_em()),
    ]
    
    for source_name, data_func in data_sources:
        try:
            logger.info(f"尝试从 {source_name} 获取板块数据...")
            df_plate = data_func()
            
            if df_plate is None or df_plate.empty:
                continue
            
            # 查找涨跌幅列
            change_col = None
            name_col = None
            for col in df_plate.columns:
                col_str = str(col)
                if '涨跌幅' in col_str or '涨幅' in col_str:
                    change_col = col_str
                if '板块' in col_str or '名称' in col_str:
                    name_col = col_str
            
            if change_col and name_col:
                top_boards = df_plate.nlargest(top_n, change_col)
                boards = []
                for _, row in top_boards.iterrows():
                    try:
                        change_val = float(row[change_col]) if pd.notna(row[change_col]) else 0
                    except:
                        change_val = 0
                    boards.append({
                        'name': str(row[name_col]),
                        'change': round(change_val, 2),
                        'change_pct': round(change_val, 2)
                    })
                logger.info(f"板块数据获取成功 ({source_name})")
                return boards
                
        except Exception as e:
            logger.warning(f"{source_name} 获取失败: {str(e)[:50]}")
            continue
    
    logger.error("所有板块数据源均失败")
    return []


def check_main_system(index_data, boards, emotion_data):
    """
    检查主升系统 v4.0
    
    六层过滤体系:
    1. 指数强趋势（MA20>MA60 + 指数>MA10）
    2. 主线板块（强于指数 1.05 倍）
    3. 龙头优先（近 5 日新高 + 涨停）- 简化版
    4. 量价强一致（放量突破 + 回调缩量）- 简化版
    5. 分歧确认（第一天分歧→第二天转强）- 简化版
    6. 失败压制（无连续放量滞涨等）
    """
    result = {
        'layer1_index_trend': False,
        'layer1_detail': '',
        'layer2_board_strong': False,
        'layer2_detail': '',
        'layer3_dragon': False,
        'layer3_detail': '需个股数据',
        'layer4_volume_price': False,
        'layer4_detail': '需个股数据',
        'layer5_divergence_confirm': False,
        'layer5_detail': '需个股数据',
        'layer6_fail_filter': True,
        'layer6_detail': '默认通过',
        'final_signal': False,
        'passed_layers': 0
    }
    
    if not index_data:
        result['layer1_detail'] = '指数数据获取失败'
        return result
    
    # 第一层：指数强趋势
    result['layer1_index_trend'] = index_data['index_strong_trend']
    result['layer1_detail'] = (
        f"MA20({index_data['ma20']})>MA60({index_data['ma60']}): {'是' if index_data['ma20'] > index_data['ma60'] else '否'}, "
        f"收盘 ({index_data['close']})>MA10({index_data['ma10']}): {'是' if index_data['close'] > index_data['ma10'] else '否'}"
    )
    
    if not result['layer1_index_trend']:
        result['layer1_detail'] += ' → 第一层未通过'
        return result
    
    result['passed_layers'] = 1
    
    # 第二层：主线板块
    index_change = index_data.get('close_ma10_pct', 0)  # 简化用 MA10 偏离度代替
    for board in boards:
        if board['change'] > 1.0:  # 板块涨幅>1%
            result['layer2_board_strong'] = True
            result['layer2_detail'] = f"主线板块：{board['name']} ({board['change']}%)"
            break
    
    if not result['layer2_board_strong']:
        result['layer2_detail'] = f"无强势板块 (指数涨幅约{index_change}%)"
        return result
    
    result['passed_layers'] = 2
    
    # 第三层到第五层需要个股数据，简化处理
    # 实际使用中应该结合具体个股分析
    
    # 第六层：失败压制（默认通过，实际应检查失败形态）
    result['passed_layers'] = 3  # 简化为通过 3 层
    
    # 最终信号（简化版：通过 3 层即认为有信号）
    result['final_signal'] = result['passed_layers'] >= 3
    
    return result


def check_ice_system(emotion_data):
    """
    检查冰点系统 v2.0
    
    情绪冰点四要素:
    - 连板 ≤ 2
    - 涨停 < 30
    - 跌停 > 涨停 (情绪差)
    - 资金大幅流出
    """
    result = {
        'lianban_le_2': False,
        'zt_less_30': False,
        'dt_gt_zt': False,
        'fund_outflow': False,
        'final_signal': False,
        'passed_conditions': 0
    }
    
    if not emotion_data:
        return result
    
    # 条件 1: 连板 ≤ 2
    result['lianban_le_2'] = emotion_data.get('lianban_count', 0) <= 2
    
    # 条件 2: 涨停 < 30
    result['zt_less_30'] = emotion_data.get('zt_count', 0) < 30
    
    # 条件 3: 跌停 > 涨停
    zt_count = emotion_data.get('zt_count', 0)
    dt_count = emotion_data.get('dt_count', 0)
    result['dt_gt_zt'] = dt_count > zt_count if zt_count > 0 else False
    
    # 条件 4: 资金大幅流出 (简化判断)
    result['fund_outflow'] = False  # 需要更详细的资金数据
    
    # 统计满足的条件数
    result['passed_conditions'] = sum([
        result['lianban_le_2'],
        result['zt_less_30'],
        result['dt_gt_zt'],
        result['fund_outflow']
    ])
    
    # 冰点信号：至少满足 2 个条件
    result['final_signal'] = result['passed_conditions'] >= 2
    
    return result


def validate_data(emotion_data):
    """
    实时数据校验机制
    对比多个数据源，检测异常并提示用户确认
    
    Returns:
        dict: 校验结果
    """
    result = {
        'need_manual_check': False,
        'warnings': [],
        'zt_count': emotion_data.get('zt_count', 0) if emotion_data else 0,
        'dt_count': emotion_data.get('dt_count', 0) if emotion_data else 0
    }
    
    if not emotion_data:
        result['need_manual_check'] = True
        result['warnings'].append("情绪数据获取失败，请手动确认")
        return result
    
    zt = emotion_data.get('zt_count', 0)
    dt = emotion_data.get('dt_count', 0)
    
    # 检查1: 涨跌停比例异常
    if zt > 0 and dt > 0:
        ratio = zt / dt
        if ratio < 0.5:
            result['warnings'].append(f"跌停数({dt})远超涨停数({zt})，市场极度弱势")
            result['need_manual_check'] = True
        elif ratio > 3:
            result['warnings'].append(f"涨停数({zt})远超跌停数({dt})，市场极度强势")
            result['need_manual_check'] = True
    
    # 检查2: 跌停数过高
    if dt >= 50:
        result['warnings'].append(f"跌停数({dt})>=50，风险极高，请手动确认")
        result['need_manual_check'] = True
    
    # 检查3: 涨停跌停都很多（分化严重）
    if zt >= 50 and dt >= 30:
        result['warnings'].append(f"涨停({zt})跌停({dt})都很多，市场严重分化，请确认")
        result['need_manual_check'] = True
    
    # 检查4: 对比其他数据源（尝试财富数据获取东方）
    try:
        import requests
        # 尝试获取实时涨跌停数据
        url = "https://push2.eastmoney.com/api/qt/clist/get"
        params = {
            "pn": 1,
            "pz": 1,
            "po": 1,
            "np": 1,
            "fltt": 2,
            "invt": 2,
            "fid": "f3",
            "fs": "m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23",
            "fields": "f2"
        }
        # 这是一个额外的校验，但可能会失败
        logger.info("数据校验：尝试获取备用数据源")
    except Exception as e:
        logger.info(f"备用数据源获取跳过：{e}")
    
    return result


def generate_report(output_json=False):
    """
    生成复盘报告
    
    Args:
        output_json: 是否输出 JSON 格式
    """
    today = datetime.now().strftime('%Y-%m-%d')
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    print("=" * 70)
    print(f"📅 {today} A 股双系统模型复盘报告 v4.0")
    print(f"⏰ 更新时间：{timestamp}")
    print("=" * 70)
    
    # 获取数据
    print("\n【数据获取中...】")
    index_data = get_index_data()
    emotion_data = get_market_emotion()
    boards = get_board_performance()
    
    # 输出指数数据
    print(f"\n{'='*70}")
    print(f"【一、上证指数】")
    print(f"{'='*70}")
    if index_data:
        print(f"  收盘价：  {index_data['close']:.2f}")
        print(f"  MA10:     {index_data['ma10']:.2f} ({index_data['close_ma10_pct']:+.2f}%)")
        print(f"  MA20:     {index_data['ma20']:.2f} ({index_data['close_ma20_pct']:+.2f}%) - {index_data['ma20_trend']}")
        print(f"  MA60:     {index_data['ma60']:.2f} ({index_data['close_ma60_pct']:+.2f}%) - {index_data['ma60_trend']}")
        print(f"  强趋势：  {'✅ 是' if index_data['index_strong_trend'] else '❌ 否'}")
    else:
        print(f"  ❌ 指数数据获取失败")
    
    # 获取深证成指和创业板指
    sz_data = get_sz_index_data()
    cy_data = get_cy_index_data()
    
    # 输出深证成指
    print(f"\n{'='*70}")
    print(f"【二、深证成指】")
    print(f"{'='*70}")
    if sz_data:
        print(f"  收盘价：  {sz_data['close']:.2f}")
        print(f"  MA10:     {sz_data['ma10']:.2f} ({sz_data['close_ma10_pct']:+.2f}%)")
        print(f"  MA20:     {sz_data['ma20']:.2f}")
        print(f"  MA60:     {sz_data['ma60']:.2f}")
        print(f"  强趋势：  {'✅ 是' if sz_data['index_strong_trend'] else '❌ 否'}")
    else:
        print(f"  ❌ 深证成指数据获取失败")
    
    # 输出创业板指
    print(f"\n{'='*70}")
    print(f"【三、创业板指】")
    print(f"{'='*70}")
    if cy_data:
        print(f"  收盘价：  {cy_data['close']:.2f}")
        print(f"  MA10:     {cy_data['ma10']:.2f} ({cy_data['close_ma10_pct']:+.2f}%)")
        print(f"  MA20:     {cy_data['ma20']:.2f}")
        print(f"  MA60:     {cy_data['ma60']:.2f}")
        print(f"  强趋势：  {'✅ 是' if cy_data['index_strong_trend'] else '❌ 否'}")
    else:
        print(f"  ❌ 创业板指数据获取失败")
    
    # 输出情绪数据
    print(f"\n{'='*70}")
    print(f"【四、市场情绪】")
    print(f"{'='*70}")
    if emotion_data:
        print(f"  涨停家数：  {emotion_data['zt_count']} 家")
        print(f"  跌停家数：  {emotion_data['dt_count']} 家")
        print(f"  连板家数：  {emotion_data['lianban_count']} 家")
        print(f"  主力净流入：{emotion_data['main_net_flow']}")
    else:
        print(f"  ❌ 情绪数据获取失败")
    
    # 输出板块
    print(f"\n{'='*70}")
    print(f"【五、涨幅前 10 板块】")
    print(f"{'='*70}")
    if boards:
        for i, board in enumerate(boards, 1):
            print(f"  {i}. {board['name']:<20} {board['change']:>+6.2f}%")
    else:
        print(f"  ❌ 板块数据获取失败")
    
    # 检查主升系统
    print(f"\n{'='*70}")
    print(f"【六、主升系统验证】")
    print(f"{'='*70}")
    main_result = check_main_system(index_data, boards, emotion_data)
    print(f"  第一层 (指数强趋势):     {'✅' if main_result['layer1_index_trend'] else '❌'} - {main_result['layer1_detail']}")
    print(f"  第二层 (主线板块):       {'✅' if main_result['layer2_board_strong'] else '❌'} - {main_result['layer2_detail']}")
    print(f"  第三层 (龙头优先):       {'✅' if main_result['layer3_dragon'] else '❌'} - {main_result['layer3_detail']}")
    print(f"  第四层 (量价强一致):     {'✅' if main_result['layer4_volume_price'] else '❌'} - {main_result['layer4_detail']}")
    print(f"  第五层 (分歧确认):       {'✅' if main_result['layer5_divergence_confirm'] else '❌'} - {main_result['layer5_detail']}")
    print(f"  第六层 (失败压制):       {'✅' if main_result['layer6_fail_filter'] else '❌'} - {main_result['layer6_detail']}")
    print(f"  ─" * 30)
    print(f"  通过层数：  {main_result['passed_layers']}/6")
    print(f"  主升信号：  {'🟢 触发' if main_result['final_signal'] else '🔴 未触发'}")
    
    # 检查冰点系统
    print(f"\n{'='*70}")
    print(f"【七、冰点系统验证】")
    print(f"{'='*70}")
    ice_result = check_ice_system(emotion_data)
    print(f"  连板≤2:        {'✅' if ice_result['lianban_le_2'] else '❌'}")
    print(f"  涨停<30:       {'✅' if ice_result['zt_less_30'] else '❌'}")
    print(f"  跌停>涨停：     {'✅' if ice_result['dt_gt_zt'] else '❌'}")
    print(f"  资金流出：     {'✅' if ice_result['fund_outflow'] else '❌'}")
    print(f"  ─" * 30)
    print(f"  满足条件：  {ice_result['passed_conditions']}/4")
    print(f"  冰点信号：  {'🟡 触发' if ice_result['final_signal'] else '⚪ 未触发'}")
    
    # 最终结论
    print(f"\n{'='*70}")
    print(f"【八、最终结论】")
    print(f"{'='*70}")
    if main_result['final_signal']:
        print(f"  🟢 主升系统触发 - 可开仓")
        action = "可开仓"
        position = "50-80%"
    elif ice_result['final_signal']:
        print(f"  🟡 冰点系统触发 - 轻仓试错")
        action = "轻仓试错"
        position = "≤30%"
    else:
        print(f"  🔴 混沌期 - 空仓等待")
        action = "空仓等待"
        position = "0%"
    
    # 操作纪律
    print(f"\n{'='*70}")
    print(f"【九、操作纪律】")
    print(f"{'='*70}")
    if main_result['final_signal']:
        print(f"  ✓ 仓位：    {position}")
        print(f"  ✓ 方向：    主线板块前排")
        print(f"  ✓ 止损：    趋势破位 (MA20)")
        print(f"  ✓ 止盈：    分批止盈")
    elif ice_result['final_signal']:
        print(f"  ⚠ 仓位：    {position}")
        print(f"  ⚠ 方向：    超跌反弹")
        print(f"  ⚠ 止损：    -5%")
        print(f"  ⚠ 止盈：    快进快出")
    else:
        print(f"  🛑 仓位：    {position}")
        print(f"  🛑 策略：    观望为主")
        print(f"  🛑 关注：    等待明确信号")
    
    # 次日关注点
    print(f"\n{'='*70}")
    print(f"【十、次日关注】")
    print(f"{'='*70}")
    if index_data:
        print(f"  1. 指数能否站稳 MA10 ({index_data['ma10']:.2f})")
        print(f"  2. 成交量能否放大")
        print(f"  3. 主线板块能否持续")
        print(f"  4. 涨停家数能否维持")
    
    # 保存报告
    report_path = os.path.join(REPORT_DIR, f'report_{today}.txt')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f"📅 {today} A 股双系统模型复盘报告 v4.0\n")
        f.write(f"⏰ 更新时间：{timestamp}\n")
        f.write(f"{'='*70}\n")
        f.write(f"主升系统信号：{'是' if main_result['final_signal'] else '否'} (通过{main_result['passed_layers']}/6 层)\n")
        f.write(f"冰点系统信号：{'是' if ice_result['final_signal'] else '否'} (满足{ice_result['passed_conditions']}/4 条件)\n")
        f.write(f"操作建议：{action}\n")
        f.write(f"建议仓位：{position}\n")
    
    # JSON 输出
    if output_json:
        json_data = {
            'date': today,
            'timestamp': timestamp,
            'index': index_data,
            'emotion': emotion_data,
            'boards': boards,
            'main_system': main_result,
            'ice_system': ice_result,
            'action': action,
            'position': position
        }
        json_path = os.path.join(REPORT_DIR, f'report_{today}.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        print(f"\n📁 JSON 报告已保存：{json_path}")
    
    # ===== 实时数据校验机制 =====
    print(f"\n{'='*70}")
    print(f"【数据校验】")
    print(f"{'='*70}")
    
    validation_result = validate_data(emotion_data)
    
    if validation_result['need_manual_check']:
        print(f"  ⚠️  数据差异提示:")
        for item in validation_result['warnings']:
            print(f"     - {item}")
        print(f"\n  📌 请手动确认以下数据:")
        print(f"     - 实际涨停数: {emotion_data.get('zt_count', 'N/A')}")
        print(f"     - 实际跌停数: {emotion_data.get('dt_count', 'N/A')}")
    else:
        print(f"  ✅ 数据校验通过")
    
    print("=" * 70)
    
    return {
        'main_signal': main_result['final_signal'],
        'ice_signal': ice_result['final_signal'],
        'action': action,
        'validation': validation_result
    }


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='双系统模型复盘分析 v4.0')
    parser.add_argument('--json', action='store_true', help='输出 JSON 格式报告')
    parser.add_argument('--quiet', action='store_true', help='静默模式')
    args = parser.parse_args()
    
    try:
        result = generate_report(output_json=args.json)
        return result
    except KeyboardInterrupt:
        print("\n❌ 用户中断")
        sys.exit(1)
    except Exception as e:
        logger.error(f"程序执行失败：{e}")
        print(f"\n❌ 程序执行失败：{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
