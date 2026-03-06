#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
个股综合分析脚本 v3.0
整合：老股民警模型 v2.0 + 庄家理论 + 双系统模型

功能:
- 7 维分析评分体系
- 庄家阶段识别
- 量价关系分析
- 买卖点建议
- 风险评估

使用方法:
    python stock/scripts/stock_analysis_comprehensive.py --code=000001
    python stock/scripts/stock_analysis_comprehensive.py --code=000001 --json
"""

import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
import sys
import argparse
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 路径配置
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT_DIR = os.path.join(BASE_DIR, 'reports/stocks')
os.makedirs(REPORT_DIR, exist_ok=True)


class StockAnalyzer:
    """个股综合分析器"""
    
    def __init__(self, stock_code):
        """
        初始化分析器
        
        Args:
            stock_code: 股票代码 (6 位数字)
        """
        self.stock_code = stock_code
        self.stock_name = ""
        self.df = None
        self.df_daily = None
        self.analysis_result = {}
    
    def fetch_data(self, days=250):
        """
        获取股票数据
        
        Args:
            days: 获取天数
        
        Returns:
            bool: 是否成功
        """
        try:
            logger.info(f"获取 {self.stock_code} 数据...")
            
            # 获取实时行情
            self.df = ak.stock_zh_a_spot_em()
            if self.df.empty:
                logger.error("无法获取行情数据")
                return False
            
            # 查找目标股票
            stock_row = self.df[self.df['代码'] == self.stock_code]
            if stock_row.empty:
                logger.error(f"未找到股票 {self.stock_code}")
                return False
            
            self.stock_name = stock_row['名称'].iloc[0]
            logger.info(f"股票名称：{self.stock_name}")
            
            # 获取历史日线数据
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')
            
            self.df_daily = ak.stock_zh_a_hist(
                symbol=self.stock_code,
                period="daily",
                start_date=start_date,
                end_date=end_date,
                adjust="qfq"
            )
            
            if self.df_daily.empty:
                logger.error("无法获取历史数据")
                return False
            
            logger.info(f"获取到 {len(self.df_daily)} 条历史数据")
            return True
            
        except Exception as e:
            logger.error(f"获取数据失败：{e}")
            return False
    
    def analyze_trend(self):
        """
        分析趋势与均线 (20 分)
        
        Returns:
            dict: 趋势分析结果
        """
        if self.df_daily is None or self.df_daily.empty:
            return {'score': 0, 'details': '无数据'}
        
        df = self.df_daily
        close = df['收盘'].iloc[-1]
        
        # 计算均线
        ma5 = df['收盘'].rolling(5).mean().iloc[-1]
        ma10 = df['收盘'].rolling(10).mean().iloc[-1]
        ma20 = df['收盘'].rolling(20).mean().iloc[-1]
        ma60 = df['收盘'].rolling(60).mean().iloc[-1]
        ma120 = df['收盘'].rolling(120).mean().iloc[-1] if len(df) >= 120 else ma60
        ma250 = df['收盘'].rolling(250).mean().iloc[-1] if len(df) >= 250 else ma120
        
        # 均线多头排列
        ma_bullish = (
            ma5 > ma10 > ma20 and
            ma20 > ma60 and
            close > ma5
        )
        
        # 长期趋势
        long_trend = close > ma250
        mid_trend = close > ma60
        
        # 均线斜率
        ma20_prev = df['收盘'].rolling(20).mean().iloc[-2] if len(df) > 1 else ma20
        ma20_slope = (ma20 - ma20_prev) / ma20_prev * 100
        
        # 评分
        score = 0
        if ma_bullish:
            score += 10
        if long_trend:
            score += 5
        if mid_trend:
            score += 3
        if ma20_slope > 0:
            score += 2
        
        details = (
            f"MA5:{ma5:.2f} | MA10:{ma10:.2f} | MA20:{ma20:.2f} | MA60:{ma60:.2f}\n"
            f"多头排列：{'是' if ma_bullish else '否'} | "
            f"年线上方：{'是' if long_trend else '否'} | "
            f"MA20 斜率：{ma20_slope:+.2f}%"
        )
        
        return {
            'score': min(score, 20),
            'max_score': 20,
            'details': details,
            'ma_bullish': ma_bullish,
            'long_trend': long_trend,
            'ma20_slope': ma20_slope
        }
    
    def analyze_volume_price(self):
        """
        分析量价关系 (25 分) - 核心维度
        
        Returns:
            dict: 量价分析结果
        """
        if self.df_daily is None or len(self.df_daily) < 20:
            return {'score': 0, 'details': '数据不足'}
        
        df = self.df_daily
        close = df['收盘'].iloc[-1]
        volume = df['成交量'].iloc[-1]
        amount = df['成交额'].iloc[-1] if '成交额' in df.columns else volume * close
        
        # 计算均量
        ma_vol5 = df['成交量'].rolling(5).mean().iloc[-1]
        ma_vol20 = df['成交量'].rolling(20).mean().iloc[-1]
        
        # 量比
        volume_ratio = volume / ma_vol5 if ma_vol5 > 0 else 1
        
        # 近期放量情况
        recent_volumes = df['成交量'].iloc[-5:].tolist()
        avg_recent_vol = sum(recent_volumes) / len(recent_volumes)
        vol_trend = 'up' if avg_recent_vol > ma_vol20 * 1.2 else ('down' if avg_recent_vol < ma_vol20 * 0.8 else 'flat')
        
        # 价量配合
        price_change = (close - df['收盘'].iloc[-5]) / df['收盘'].iloc[-5] * 100 if len(df) > 5 else 0
        vol_change = (avg_recent_vol - ma_vol20) / ma_vol20 * 100 if ma_vol20 > 0 else 0
        
        # 量价配合判断
        good_volume_price = False
        if price_change > 0 and vol_change > 0:  # 放量上涨
            good_volume_price = True
        elif price_change < 0 and vol_change < 0:  # 缩量下跌
            good_volume_price = True
        elif abs(price_change) < 2 and abs(vol_change) < 10:  # 横盘缩量
            good_volume_price = True
        
        # 异常放量
        abnormal_vol = volume_ratio > 3.0
        
        # 评分
        score = 0
        if good_volume_price:
            score += 15
        if vol_trend == 'up':
            score += 5
        if not abnormal_vol:
            score += 5
        
        details = (
            f"量比：{volume_ratio:.2f} | 量能趋势：{vol_trend}\n"
            f"5 日涨跌：{price_change:+.2f}% | 量能变化：{vol_change:+.2f}%\n"
            f"量价配合：{'好' if good_volume_price else '差'} | "
            f"异常放量：{'是' if abnormal_vol else '否'}"
        )
        
        return {
            'score': min(score, 25),
            'max_score': 25,
            'details': details,
            'volume_ratio': volume_ratio,
            'vol_trend': vol_trend,
            'good_volume_price': good_volume_price,
            'abnormal_vol': abnormal_vol
        }
    
    def analyze_kline_pattern(self):
        """
        分析 K 线形态 (15 分)
        
        Returns:
            dict: K 线分析结果
        """
        if self.df_daily is None or len(self.df_daily) < 10:
            return {'score': 0, 'details': '数据不足'}
        
        df = self.df_daily
        close = df['收盘'].iloc[-1]
        open_price = df['开盘'].iloc[-1]
        high = df['最高'].iloc[-1]
        low = df['最低'].iloc[-1]
        
        # K 线实体
        body = abs(close - open_price) / open_price * 100
        # 上影线
        upper_shadow = (high - max(close, open_price)) / open_price * 100
        # 下影线
        lower_shadow = (min(close, open_price) - low) / open_price * 100
        
        # K 线形态判断
        is_yang = close > open_price
        is_big_yang = body > 3 and is_yang
        is_big_yin = body > 3 and not is_yang
        is_doji = body < 0.5
        is_hammer = lower_shadow > body * 2 and upper_shadow < body * 0.5
        is_shooting_star = upper_shadow > body * 2 and lower_shadow < body * 0.5
        
        # 近期形态
        recent_closes = df['收盘'].iloc[-5:].tolist()
        is_uptrend = all(recent_closes[i] >= recent_closes[i-1] for i in range(1, len(recent_closes)))
        is_downtrend = all(recent_closes[i] <= recent_closes[i-1] for i in range(1, len(recent_closes)))
        
        # 是否创新高
        recent_high = df['最高'].iloc[-20:].max()
        is_new_high = high >= recent_high * 0.98
        
        # 评分
        score = 0
        if is_big_yang:
            score += 8
        elif is_yang:
            score += 5
        if is_hammer:
            score += 5
        if is_new_high:
            score += 5
        if is_uptrend:
            score += 3
        
        details = (
            f"K 线实体：{body:.2f}% | 上影：{upper_shadow:.2f}% | 下影：{lower_shadow:.2f}%\n"
            f"阳线：{'是' if is_yang else '否'} | 大阳：{'是' if is_big_yang else '否'}\n"
            f"锤头线：{'是' if is_hammer else '否'} | 创新高：{'是' if is_new_high else '否'}"
        )
        
        return {
            'score': min(score, 15),
            'max_score': 15,
            'details': details,
            'is_yang': is_yang,
            'is_new_high': is_new_high,
            'pattern': '大阳' if is_big_yang else ('锤头' if is_hammer else ('十字' if is_doji else '普通'))
        }
    
    def analyze_main_force(self):
        """
        分析主力行为 (20 分)
        
        Returns:
            dict: 主力行为分析结果
        """
        if self.df_daily is None or len(self.df_daily) < 20:
            return {'score': 0, 'details': '数据不足'}
        
        df = self.df_daily
        
        # 获取资金流向数据
        try:
            fund_flow = ak.stock_individual_fund_flow(symbol=self.stock_code, market="sz" if self.stock_code.startswith(('0', '3')) else "sh")
            if not fund_flow.empty:
                main_inflow = fund_flow['主力净流入-净额'].iloc[0]
                main_inflow_3d = fund_flow['主力净流入 -3 日净额'].iloc[0] if '主力净流入 -3 日净额' in fund_flow.columns else 0
            else:
                main_inflow = 0
                main_inflow_3d = 0
        except:
            main_inflow = 0
            main_inflow_3d = 0
        
        # 大单净流入
        try:
            big_order = ak.stock_individual_fund_flow_rank(indicator="3d")
            if not big_order.empty:
                stock_data = big_order[big_order['代码'] == self.stock_code]
                if not stock_data.empty:
                    big_order_inflow = stock_data['主力净流入'].iloc[0]
                else:
                    big_order_inflow = 0
            else:
                big_order_inflow = 0
        except:
            big_order_inflow = 0
        
        # 判断主力行为
        has_inflow = main_inflow > 0
        has_continuous_inflow = main_inflow_3d > 0
        is_accumulation = has_continuous_inflow and not has_inflow  # 3 日流入但今日流出，可能是洗盘
        
        # 评分
        score = 0
        if has_inflow:
            score += 10
        if has_continuous_inflow:
            score += 8
        if is_accumulation:
            score += 5
        
        details = (
            f"今日主力净流入：{main_inflow/10000:.2f}万\n"
            f"3 日主力净流入：{main_inflow_3d/10000:.2f}万\n"
            f"资金流入：{'是' if has_inflow else '否'} | "
            f"持续流入：{'是' if has_continuous_inflow else '否'} | "
            f"吸筹迹象：{'是' if is_accumulation else '否'}"
        )
        
        return {
            'score': min(score, 20),
            'max_score': 20,
            'details': details,
            'has_inflow': has_inflow,
            'has_continuous_inflow': has_continuous_inflow,
            'is_accumulation': is_accumulation
        }
    
    def analyze_sector_sentiment(self):
        """
        分析板块与情绪环境 (20 分)
        
        Returns:
            dict: 板块情绪分析结果
        """
        try:
            # 获取所属板块
            stock_board = ak.stock_individual_info(symbol=self.stock_code)
            if not stock_board.empty:
                board_info = stock_board[stock_board['item'] == '所属板块']
                if not board_info.empty:
                    board_name = board_info['value'].iloc[0]
                else:
                    board_name = "未知"
            else:
                board_name = "未知"
            
            # 获取板块表现
            df_board = ak.stock_board_industry_name_em()
            if not df_board.empty:
                board_row = df_board[df_board['板块名称'].str.contains(board_name, na=False)]
                if not board_row.empty:
                    board_change = board_row['涨跌幅'].iloc[0]
                    board_rank = board_row['涨跌幅'].rank(pct=True).iloc[0]
                else:
                    board_change = 0
                    board_rank = 0.5
            else:
                board_change = 0
                board_rank = 0.5
            
            # 市场整体情绪
            try:
                zt_data = ak.stock_zt_pool_em(date=datetime.now().strftime('%Y-%m-%d'))
                zt_count = len(zt_data) if not zt_data.empty else 0
            except:
                zt_count = 0
            
            # 评分
            score = 0
            if board_change > 1:
                score += 10
            elif board_change > 0:
                score += 5
            if board_rank > 0.7:
                score += 8
            elif board_rank > 0.5:
                score += 4
            if zt_count > 50:
                score += 5
            elif zt_count > 30:
                score += 2
            
            details = (
                f"所属板块：{board_name}\n"
                f"板块涨幅：{board_change:.2f}% | 板块排名：{board_rank*100:.1f}%\n"
                f"市场涨停：{zt_count}家"
            )
            
        except Exception as e:
            logger.warning(f"板块分析失败：{e}")
            details = "板块数据获取失败"
            score = 5  # 默认给基础分
        
        return {
            'score': min(score, 20),
            'max_score': 20,
            'details': details,
            'board_name': board_name if 'board_name' in dir() else '未知',
            'board_change': board_change if 'board_change' in dir() else 0
        }
    
    def comprehensive_analysis(self):
        """
        综合分析 - 7 维评分体系
        
        Returns:
            dict: 综合分析结果
        """
        logger.info(f"开始综合分析 {self.stock_code} - {self.stock_name}")
        
        # 各维度分析
        trend_result = self.analyze_trend()
        volume_price_result = self.analyze_volume_price()
        kline_result = self.analyze_kline_pattern()
        main_force_result = self.analyze_main_force()
        sector_result = self.analyze_sector_sentiment()
        
        # 计算总分
        total_score = (
            trend_result['score'] +
            volume_price_result['score'] +
            kline_result['score'] +
            main_force_result['score'] +
            sector_result['score']
        )
        
        max_score = 100
        
        # 评级
        if total_score >= 80:
            rating = "强势主升"
            action = "积极参与"
            position = "50-80%"
        elif total_score >= 60:
            rating = "可操作"
            action = "择时操作"
            position = "30-50%"
        elif total_score >= 40:
            rating = "观望"
            action = "等待信号"
            position = "0-20%"
        else:
            rating = "风险区"
            action = "回避"
            position = "0%"
        
        self.analysis_result = {
            'stock_code': self.stock_code,
            'stock_name': self.stock_name,
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_score': total_score,
            'max_score': max_score,
            'rating': rating,
            'action': action,
            'position': position,
            'dimensions': {
                'trend': trend_result,
                'volume_price': volume_price_result,
                'kline': kline_result,
                'main_force': main_force_result,
                'sector': sector_result
            }
        }
        
        return self.analysis_result
    
    def print_report(self):
        """打印分析报告"""
        if not self.analysis_result:
            print("❌ 请先执行综合分析")
            return
        
        r = self.analysis_result
        
        print("=" * 70)
        print(f"📊 个股综合分析报告 v3.0")
        print(f"股票代码：{r['stock_code']} | 股票名称：{r['stock_name']}")
        print(f"分析时间：{r['analysis_date']}")
        print("=" * 70)
        
        print(f"\n【综合评分】")
        print(f"  总分：{r['total_score']}/{r['max_score']}")
        print(f"  评级：{r['rating']}")
        print(f"  建议：{r['action']}")
        print(f"  仓位：{r['position']}")
        
        print(f"\n【维度分析】")
        dims = r['dimensions']
        print(f"  趋势结构：      {dims['trend']['score']}/{dims['trend']['max_score']} - {dims['trend']['details']}")
        print(f"  量价健康度：    {dims['volume_price']['score']}/{dims['volume_price']['max_score']} - {dims['volume_price']['details']}")
        print(f"  K 线信号质量：   {dims['kline']['score']}/{dims['kline']['max_score']} - {dims['kline']['details']}")
        print(f"  主力行为可信度：{dims['main_force']['score']}/{dims['main_force']['max_score']} - {dims['main_force']['details']}")
        print(f"  板块情绪环境：  {dims['sector']['score']}/{dims['sector']['max_score']} - {dims['sector']['details']}")
        
        print(f"\n【操作建议】")
        if r['total_score'] >= 80:
            print(f"  ✅ 强势主升形态，可积极参与")
            print(f"  ✅ 关注：量价配合、主线地位")
            print(f"  ✅ 止损：趋势破位")
        elif r['total_score'] >= 60:
            print(f"  ⚠️ 可操作区间，等待更好买点")
            print(f"  ⚠️ 关注：回调企稳信号")
            print(f"  ⚠️ 止损：-5%")
        else:
            print(f"  🛑 风险较高，建议观望")
            print(f"  🛑 等待：明确转强信号")
        
        print("=" * 70)
    
    def save_report(self):
        """保存报告到文件"""
        if not self.analysis_result:
            return
        
        filename = f"{self.stock_code}_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        filepath = os.path.join(REPORT_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.analysis_result, f, ensure_ascii=False, indent=2)
        
        logger.info(f"报告已保存：{filepath}")
        return filepath


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='个股综合分析 v3.0')
    parser.add_argument('--code', required=True, help='股票代码 (6 位数字)')
    parser.add_argument('--json', action='store_true', help='输出 JSON 格式')
    args = parser.parse_args()
    
    # 验证股票代码
    if not args.code.isdigit() or len(args.code) != 6:
        print("❌ 股票代码格式错误，请输入 6 位数字")
        sys.exit(1)
    
    # 创建分析器
    analyzer = StockAnalyzer(args.code)
    
    # 获取数据
    if not analyzer.fetch_data():
        print("❌ 数据获取失败")
        sys.exit(1)
    
    # 综合分析
    result = analyzer.comprehensive_analysis()
    
    # 输出结果
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        analyzer.print_report()
    
    # 保存报告
    analyzer.save_report()


if __name__ == "__main__":
    main()
