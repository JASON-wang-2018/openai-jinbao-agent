#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票实时预警系统 v1.0

功能:
- 价格突破预警
- 成交量异常预警
- 涨跌幅预警
- 资金流向预警
- 支持多股票监控

使用方法:
    python stock/scripts/stock_alert_system.py --watchlist=watchlist.txt
    python stock/scripts/stock_alert_system.py --code=000001,000002 --interval=60
"""

import akshare as ak
import pandas as pd
import time
import os
import sys
import argparse
import logging
from datetime import datetime
from typing import Dict, List, Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/tmp/stock_alert.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


class StockAlert:
    """股票预警"""
    
    def __init__(self, code: str, name: str, alert_type: str, message: str, price: float):
        self.code = code
        self.name = name
        self.alert_type = alert_type
        self.message = message
        self.price = price
        self.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def __str__(self):
        return f"[{self.timestamp}] {self.alert_type} - {self.code} {self.name}: {self.message}"


class AlertSystem:
    """预警系统"""
    
    def __init__(self, watchlist_file: Optional[str] = None):
        """
        初始化预警系统
        
        Args:
            watchlist_file: 自选股文件路径
        """
        self.watchlist: List[Dict] = []
        self.alert_history: List[StockAlert] = []
        self.last_data: Dict[str, Dict] = {}
        
        # 预警阈值配置
        self.config = {
            'price_breakthrough': 0.05,  # 价格突破 5%
            'volume_abnormal': 2.0,  # 成交量异常 2 倍
            'price_change_alert': 0.07,  # 涨跌幅预警 7%
            'fund_flow_alert': 10000000,  # 资金流入预警 1000 万
        }
        
        # 加载自选股
        if watchlist_file:
            self.load_watchlist(watchlist_file)
    
    def load_watchlist(self, filepath: str):
        """
        加载自选股列表
        
        Args:
            filepath: 自选股文件路径
        """
        if not os.path.exists(filepath):
            logger.warning(f"自选股文件不存在：{filepath}")
            return
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            self.watchlist = []
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                parts = line.split(',')
                if len(parts) >= 1:
                    code = parts[0].strip()
                    name = parts[1].strip() if len(parts) > 1 else ''
                    notes = parts[2].strip() if len(parts) > 2 else ''
                    
                    if code.isdigit() and len(code) == 6:
                        self.watchlist.append({
                            'code': code,
                            'name': name,
                            'notes': notes
                        })
            
            logger.info(f"加载 {len(self.watchlist)} 只自选股")
            
        except Exception as e:
            logger.error(f"加载自选股失败：{e}")
    
    def add_stock(self, code: str, name: str = '', notes: str = ''):
        """添加股票到自选列表"""
        if code not in [s['code'] for s in self.watchlist]:
            self.watchlist.append({
                'code': code,
                'name': name,
                'notes': notes
            })
            logger.info(f"添加股票：{code} {name}")
    
    def remove_stock(self, code: str):
        """从自选列表移除股票"""
        self.watchlist = [s for s in self.watchlist if s['code'] != code]
        logger.info(f"移除股票：{code}")
    
    def get_realtime_data(self, code: str) -> Optional[Dict]:
        """
        获取实时行情数据
        
        Args:
            code: 股票代码
        
        Returns:
            dict: 行情数据
        """
        try:
            df = ak.stock_zh_a_spot_em()
            if df.empty:
                return None
            
            stock_data = df[df['代码'] == code]
            if stock_data.empty:
                return None
            
            row = stock_data.iloc[0]
            
            data = {
                'code': code,
                'name': row.get('名称', ''),
                'price': row.get('最新价', 0),
                'change_pct': row.get('涨跌幅', 0),
                'change': row.get('涨跌额', 0),
                'volume': row.get('成交量', 0),
                'amount': row.get('成交额', 0),
                'high': row.get('最高', 0),
                'low': row.get('最低', 0),
                'open': row.get('今开', 0),
                'prev_close': row.get('昨收', 0),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            return data
            
        except Exception as e:
            logger.error(f"获取 {code} 行情失败：{e}")
            return None
    
    def check_price_breakthrough(self, code: str, current_data: Dict) -> Optional[StockAlert]:
        """检查价格突破预警"""
        if code not in self.last_data:
            return None
        
        last_price = self.last_data[code].get('price', 0)
        current_price = current_data.get('price', 0)
        
        if last_price == 0:
            return None
        
        change_pct = abs(current_price - last_price) / last_price
        
        if change_pct >= self.config['price_breakthrough']:
            direction = "突破" if current_price > last_price else "跌破"
            return StockAlert(
                code=code,
                name=current_data.get('name', ''),
                alert_type="价格突破",
                message=f"{direction} {change_pct*100:.2f}% (现价：{current_price:.2f})",
                price=current_price
            )
        
        return None
    
    def check_volume_abnormal(self, code: str, current_data: Dict) -> Optional[StockAlert]:
        """检查成交量异常预警"""
        if code not in self.last_data:
            return None
        
        last_volume = self.last_data[code].get('volume', 0)
        current_volume = current_data.get('volume', 0)
        
        if last_volume == 0:
            return None
        
        volume_ratio = current_volume / last_volume
        
        if volume_ratio >= self.config['volume_abnormal']:
            return StockAlert(
                code=code,
                name=current_data.get('name', ''),
                alert_type="成交量异常",
                message=f"放量 {volume_ratio:.2f}倍 (现量：{current_volume/10000:.1f}万手)",
                price=current_data.get('price', 0)
            )
        
        return None
    
    def check_price_change(self, current_data: Dict) -> Optional[StockAlert]:
        """检查涨跌幅预警"""
        change_pct = abs(current_data.get('change_pct', 0))
        
        if change_pct >= self.config['price_change_alert']:
            direction = "大涨" if current_data.get('change_pct', 0) > 0 else "大跌"
            return StockAlert(
                code=current_data.get('code', ''),
                name=current_data.get('name', ''),
                alert_type="涨跌幅预警",
                message=f"{direction} {change_pct:.2f}% (现价：{current_data.get('price', 0):.2f})",
                price=current_data.get('price', 0)
            )
        
        return None
    
    def check_fund_flow(self, code: str, current_data: Dict) -> Optional[StockAlert]:
        """检查资金流向预警"""
        try:
            # 获取资金流向
            fund_flow = ak.stock_individual_fund_flow(
                symbol=code,
                market="sz" if code.startswith(('0', '3')) else "sh"
            )
            
            if fund_flow.empty:
                return None
            
            main_inflow = fund_flow['主力净流入 - 净额'].iloc[0]
            
            if abs(main_inflow) >= self.config['fund_flow_alert']:
                direction = "大幅流入" if main_inflow > 0 else "大幅流出"
                return StockAlert(
                    code=code,
                    name=current_data.get('name', ''),
                    alert_type="资金流向",
                    message=f"{direction} {main_inflow/10000:.1f}万",
                    price=current_data.get('price', 0)
                )
            
        except Exception as e:
            logger.debug(f"获取 {code} 资金流向失败：{e}")
        
        return None
    
    def run_checks(self, code: str) -> List[StockAlert]:
        """
        对单只股票执行所有预警检查
        
        Args:
            code: 股票代码
        
        Returns:
            list: 触发的预警列表
        """
        alerts = []
        
        # 获取实时数据
        current_data = self.get_realtime_data(code)
        if not current_data:
            return alerts
        
        # 执行各项检查
        alert = self.check_price_breakthrough(code, current_data)
        if alert:
            alerts.append(alert)
        
        alert = self.check_volume_abnormal(code, current_data)
        if alert:
            alerts.append(alert)
        
        alert = self.check_price_change(current_data)
        if alert:
            alerts.append(alert)
        
        alert = self.check_fund_flow(code, current_data)
        if alert:
            alerts.append(alert)
        
        # 更新最后数据
        self.last_data[code] = current_data
        
        # 记录预警历史
        self.alert_history.extend(alerts)
        
        return alerts
    
    def monitor_loop(self, interval: int = 60, max_iterations: Optional[int] = None):
        """
        监控循环
        
        Args:
            interval: 检查间隔 (秒)
            max_iterations: 最大迭代次数 (None 为无限)
        """
        logger.info(f"开始监控，间隔：{interval}秒")
        logger.info(f"监控股票：{len(self.watchlist)}只")
        
        iteration = 0
        try:
            while max_iterations is None or iteration < max_iterations:
                iteration += 1
                start_time = time.time()
                
                logger.info(f"\n=== 第 {iteration} 次检查 ===")
                
                # 检查所有股票
                for stock in self.watchlist:
                    code = stock['code']
                    name = stock['name']
                    
                    logger.info(f"检查：{code} {name}")
                    alerts = self.run_checks(code)
                    
                    # 输出预警
                    for alert in alerts:
                        print(f"\n🚨 {alert}")
                        logger.warning(f"预警：{alert}")
                
                # 等待下次检查
                elapsed = time.time() - start_time
                sleep_time = max(0, interval - elapsed)
                
                if sleep_time > 0 and (max_iterations is None or iteration < max_iterations):
                    logger.info(f"等待 {sleep_time:.1f}秒...")
                    time.sleep(sleep_time)
        
        except KeyboardInterrupt:
            logger.info("用户中断监控")
        
        # 输出总结
        print(f"\n{'='*60}")
        print(f"监控结束")
        print(f"总检查次数：{iteration}")
        print(f"触发预警：{len(self.alert_history)}次")
        print(f"{'='*60}")
    
    def save_alerts(self, filepath: str = '/tmp/stock_alerts.log'):
        """保存预警历史"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                for alert in self.alert_history:
                    f.write(f"{alert}\n")
            logger.info(f"预警历史已保存：{filepath}")
        except Exception as e:
            logger.error(f"保存预警历史失败：{e}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='股票实时预警系统 v1.0')
    parser.add_argument('--watchlist', type=str, help='自选股文件路径')
    parser.add_argument('--code', type=str, help='股票代码 (多个用逗号分隔)')
    parser.add_argument('--interval', type=int, default=60, help='检查间隔 (秒)')
    parser.add_argument('--iterations', type=int, help='最大迭代次数')
    parser.add_argument('--config', type=str, help='配置文件路径')
    args = parser.parse_args()
    
    # 创建预警系统
    alert_system = AlertSystem(watchlist_file=args.watchlist)
    
    # 添加命令行指定的股票
    if args.code:
        codes = [c.strip() for c in args.code.split(',')]
        for code in codes:
            if code.isdigit() and len(code) == 6:
                alert_system.add_stock(code)
    
    # 检查是否有监控目标
    if not alert_system.watchlist:
        print("❌ 没有监控目标，请使用 --watchlist 或 --code 指定")
        sys.exit(1)
    
    # 开始监控
    max_iter = args.iterations
    alert_system.monitor_loop(interval=args.interval, max_iterations=max_iter)
    
    # 保存预警历史
    alert_system.save_alerts()


if __name__ == "__main__":
    main()
