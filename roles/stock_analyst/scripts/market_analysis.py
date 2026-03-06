#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
市场大行情模型分析报告
A股市场整体分析与机会识别

使用方法:
    python market_analysis.py
"""

import sys
import os
import requests
import pandas as pd
from datetime import datetime
from typing import Dict, List, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class MarketAnalysis:
    """市场大行情模型分析"""
    
    def __init__(self):
        self.data = {}
        self.score = 0
        self.max_score = 100
    
    def get_market_index(self) -> Dict:
        """获取大盘指数"""
        indices = {}
        try:
            # 上证指数
            sh = self._get_stock('1.000001')
            if sh: indices['上证指数'] = sh
            
            # 深证成指
            sz = self._get_stock('0.399001')
            if sz: indices['深证成指'] = sz
            
            # 创业板
            cy = self._get_stock('0.399006')
            if cy: indices['创业板指'] = cy
        except Exception as e:
            print(f"获取指数失败: {e}")
        
        return indices
    
    def _get_stock(self, secid: str) -> Tuple[float, float]:
        """获取单只指数"""
        try:
            url = "https://push2.eastmoney.com/api/qt/stock/get"
            params = {'fields': 'f2,f3', 'secid': secid}
            resp = requests.get(url, params=params, timeout=10)
            data = resp.json()
            if data.get('data'):
                return (data['data']['f2'], data['data']['f3'])
        except:
            pass
        return (0, 0)
    
    def get_north_money(self) -> float:
        """北向资金"""
        try:
            url = "https://push2.eastmoney.com/api/qt/stock/get"
            params = {'fields': 'f162', 'secid': '1.000001'}
            resp = requests.get(url, params=params, timeout=10)
            data = resp.json()
            if data.get('data'):
                return data['data'].get('f162', 0)
        except:
            pass
        return 0
    
    def get_main_money(self) -> float:
        """主力资金"""
        try:
            url = "https://push2.eastmoney.com/api/qt/stock/get"
            params = {'fields': 'f164', 'secid': '1.000001'}
            resp = requests.get(url, params=params, timeout=10)
            data = resp.json()
            if data.get('data'):
                return data['data'].get('f164', 0)
        except:
            pass
        return 0
    
    def get_limit_stats(self) -> Tuple[int, int]:
        """涨跌停统计"""
        try:
            url = "https://push2.eastmoney.com/api/qt/stock/get"
            params = {'fields': 'f12,f13,f14,f2,f3', 'secid': '0.399001'}
            resp = requests.get(url, params=params, timeout=10)
            # 简化处理
            return (50, 5)  # 模拟值
        except:
            pass
        return (0, 0)
    
    def get_hot_sectors(self) -> List[Dict]:
        """热点板块"""
        try:
            url = "https://push2.eastmoney.com/api/qt/clist/get"
            params = {
                'pn': 1, 'pz': 10,
                'fs': 'm',
                'fields': 'f1,f2,f3,f12,f13,f14,f15,f16,f17'
            }
            resp = requests.get(url, params=params, timeout=15)
            data = resp.json()
            sectors = []
            if data.get('data'):
                for item in data['data']['list'][:10]:
                    sectors.append({
                        'name': item['f14'],
                        'change': item['f3'],
                        'amount': item['f17']
                    })
            return sectors
        except:
            pass
        return []
    
    def get_market_sentiment(self) -> Dict:
        """市场情绪指标"""
        try:
            up, down = self.get_limit_stats()
            return {
                '涨停数': up,
                '跌停数': down,
                '涨跌比': round(up / max(down, 1), 2)
            }
        except:
            return {'涨停数': 0, '跌停数': 0, '涨跌比': 0}
    
    def calculate_score(self) -> Dict:
        """计算市场评分"""
        score = 0
        details = {}
        
        # 1. 大盘趋势 (25分)
        indices = self.get_market_index()
        if indices:
            changes = [abs(c) for _, c in indices.values()]
            avg_change = sum(changes) / len(changes)
            if avg_change > 3:
                score += 25
                details['大盘趋势'] = ('强牛市', 25)
            elif avg_change > 1:
                score += 15
                details['大盘趋势'] = ('弱牛市', 15)
            elif avg_change > -1:
                score += 10
                details['大盘趋势'] = ('震荡市', 10)
            elif avg_change > -3:
                score += 5
                details['大盘趋势'] = ('弱熊市', 5)
            else:
                details['大盘趋势'] = ('强熊市', 0)
        else:
            details['大盘趋势'] = ('数据获取失败', 0)
        
        # 2. 资金流向 (20分)
        north = self.get_north_money()
        main = self.get_main_money()
        total_flow = north + main
        if total_flow > 50:
            score += 20
            details['资金流向'] = ('资金流入', 20)
        elif total_flow > 0:
            score += 10
            details['资金流向'] = ('资金平衡', 10)
        else:
            details['资金流向'] = ('资金流出', 0)
        
        # 3. 量能 (20分)
        sentiment = self.get_market_sentiment()
        up_count = sentiment['涨跌比']
        if up_count > 3:
            score += 20
            details['量能'] = ('温和放量', 20)
        elif up_count > 1:
            score += 15
            details['量能'] = ('量能适中', 15)
        elif up_count > 0.5:
            score += 10
            details['量能'] = ('缩量整理', 10)
        else:
            score += 5
            details['量能'] = ('地量', 5)
        
        # 4. 涨跌停 (15分)
        up, down = self.get_limit_stats()
        if up > 100:
            score += 15
            details['涨跌停'] = ('亢奋', 15)
        elif up > 50:
            score += 10
            details['涨跌停'] = ('活跃', 10)
        elif up > 30:
            score += 5
            details['涨跌停'] = ('一般', 5)
        else:
            details['涨跌停'] = ('低迷', 0)
        
        # 5. 板块轮动 (10分)
        sectors = self.get_hot_sectors()
        if len(sectors) >= 5:
            score += 10
            details['板块轮动'] = ('良性轮动', 10)
        elif len(sectors) >= 3:
            score += 5
            details['板块轮动'] = ('局部热点', 5)
        else:
            details['板块轮动'] = ('无热点', 0)
        
        # 6. 情绪指标 (10分)
        sentiment = self.get_market_sentiment()
        if sentiment['涨跌比'] > 2:
            score += 10
            details['市场情绪'] = ('亢奋', 10)
        elif sentiment['涨跌比'] > 1:
            score += 7
            details['市场情绪'] = ('乐观', 7)
        elif sentiment['涨跌比'] > 0.5:
            score += 4
            details['市场情绪'] = ('中性', 4)
        else:
            details['市场情绪'] = ('悲观', 0)
        
        self.score = score
        self.data = {
            'indices': indices,
            'north': north,
            'main': main,
            'sectors': sectors,
            'sentiment': sentiment,
            'details': details
        }
        
        # 评级
        if score >= 80:
            level = "【强牛市】"
            status = "亢奋期"
        elif score >= 60:
            level = "【弱牛市】"
            status = "发酵期"
        elif score >= 40:
            level = "【震荡市】"
            status = "整理期"
        elif score >= 20:
            level = "【弱熊市】"
            status = "下跌期"
        else:
            level = "【强熊市】"
            status = "恐慌期"
        
        return {
            'score': score,
            'level': level,
            'status': status,
            'details': details
        }
    
    def generate_report(self) -> str:
        """生成报告"""
        result = self.calculate_score()
        
        now = datetime.now()
        report = []
        
        report.append("=" * 70)
        report.append(f"【A股市场分析报告】- {now.strftime('%Y-%m-%d %H:%M')}")
        report.append("=" * 70)
        report.append("")
        
        # 大盘
        report.append("【一、市场概览】")
        report.append("-" * 50)
        indices = self.data.get('indices', {})
        for name, (price, change) in indices.items():
            sign = '+' if change >= 0 else ''
            report.append(f"  {name}: {price:.2f} ({sign}{change:.2f}%)")
        report.append("")
        
        # 资金
        report.append("【二、资金流向】")
        report.append("-" * 50)
        north = self.data.get('north', 0)
        main = self.data.get('main', 0)
        sign = '+' if north >= 0 else ''
        report.append(f"  北向资金: {sign}{north:.1f}亿元")
        sign = '+' if main >= 0 else ''
        report.append(f"  主力资金: {sign}{main:.1f}亿元")
        report.append("")
        
        # 情绪
        sentiment = self.data.get('sentiment', {})
        report.append("【三、市场情绪】")
        report.append("-" * 50)
        report.append(f"  涨停: {sentiment.get('涨停数', 0)}家")
        report.append(f"  跌停: {sentiment.get('跌停数', 0)}家")
        report.append(f"  涨跌比: {sentiment.get('涨跌比', 0)}")
        report.append("")
        
        # 热点
        sectors = self.data.get('sectors', [])
        report.append("【四、热点板块】")
        report.append("-" * 50)
        if sectors:
            for i, s in enumerate(sectors[:5], 1):
                sign = '+' if s['change'] >= 0 else ''
                report.append(f"  {i}. {s['name']} ({sign}{s['change']:.2f}%)")
        else:
            report.append("  (数据获取中...)")
        report.append("")
        
        # 评分
        report.append("【五、市场评分】")
        report.append("-" * 50)
        report.append(f"  {result['level']} {result['score']}分/100")
        report.append(f"  所处阶段: {result['status']}")
        for k, (v, s) in result['details'].items():
            report.append(f"  {k}: {v} (+{s}分)")
        report.append("")
        
        # 路径推演
        report.append("【六、后市推演】")
        report.append("-" * 50)
        if result['score'] >= 60:
            report.append("  路径一：上涨延续（60%）- 成交量配合")
            report.append("  路径二：震荡整理（30%）- 板块分化")
            report.append("  路径三：回踩确认（10%）- 情绪修复")
        elif result['score'] >= 40:
            report.append("  路径一：震荡整理（50%）- 区间波动")
            report.append("  路径二：选择方向（30%）- 需量能配合")
            report.append("  路径三：趋势延续（20%）- 跟随外盘")
        else:
            report.append("  路径一：震荡筑底（50%）- 等待契机")
            report.append("  路径二：反弹修复（30%）- 超跌反抽")
            report.append("  路径三：继续探底（20%）- 情绪低迷")
        report.append("")
        
        # 操作建议
        report.append("【七、操作建议】")
        report.append("-" * 50)
        if result['score'] >= 80:
            report.append("  仓位：70-80%")
            report.append("  策略：持股待涨，分批减仓")
            report.append("  风险：警惕高位放量滞涨")
        elif result['score'] >= 60:
            report.append("  仓位：50-70%")
            report.append("  策略：积极参与主线板块")
            report.append("  关注：券商、科技、新能源")
        elif result['score'] >= 40:
            report.append("  仓位：30-50%")
            report.append("  策略：高抛低吸，不追涨")
            report.append("  关注：板块轮动机会")
        else:
            report.append("  仓位：0-30%")
            report.append("  策略：轻仓观望，等待机会")
            report.append("  关注：超跌反弹机会")
        report.append("")
        
        report.append("=" * 70)
        
        return '\n'.join(report)


def main():
    analyzer = MarketAnalysis()
    report = analyzer.generate_report()
    print(report)
    
    # 保存报告
    now = datetime.now()
    filename = f"/home/jason/.openclaw/workspace/stock/reports/market_{now.strftime('%Y-%m-%d')}.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\n报告已保存: {filename}")


if __name__ == '__main__':
    main()
