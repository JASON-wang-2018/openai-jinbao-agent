#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
老股民警个股分析模型 v3.0
新增：心理层面分析、历史定位、均线拐头、RSI指标

7维 + 4大新增 = 11维分析体系
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Tuple, Optional

class StockAnalyzerV3:
    """老股民警个股分析器 v3.0"""
    
    def __init__(self, data_path: str):
        """初始化分析器"""
        self.df = self._load_data(data_path)
        self.latest = self.df.iloc[-1]
        self.prev = self.df.iloc[-2] if len(self.df) > 1 else self.latest
        
        # 计算常用指标
        self._calculate_indicators()
    
    def _load_data(self, path: str) -> pd.DataFrame:
        """加载数据"""
        try:
            # 尝试GBK编码（A股数据常用）
            with open(path, 'r', encoding='gbk') as f:
                content = f.read()
        except:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
        
        lines = content.strip().split('\n')
        data_lines = [l for l in lines if l.strip() and '/' in l]
        
        data = []
        for line in data_lines:
            parts = line.split()
            if len(parts) >= 6:
                try:
                    date = parts[0]
                    o, h, l, c = float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4])
                    v = int(parts[5])
                    data.append({
                        'date': date, 'open': o, 'high': h, 
                        'low': l, 'close': c, 'volume': v
                    })
                except:
                    pass
        
        df = pd.DataFrame(data)
        df = df.sort_values('date').reset_index(drop=True)
        return df
    
    def _calculate_indicators(self):
        """计算技术指标"""
        # 均线
        for period in [5, 10, 20, 60, 120]:
            if len(self.df) >= period:
                self.df[f'ma{period}'] = self.df['close'].rolling(period).mean()
        
        # RSI
        for period in [6, 12, 24]:
            if len(self.df) >= period:
                delta = self.df['close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(period).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
                rs = gain / loss
                self.df[f'rsi{period}'] = 100 - (100 / (1 + rs))
        
        # VOL均线
        for period in [5, 10, 20, 60, 120]:
            if len(self.df) >= period:
                self.df[f'vol{period}'] = self.df['volume'].rolling(period).mean()
        
        # 涨跌幅
        self.df['pct_change'] = self.df['close'].pct_change() * 100
    
    # ==================== 维度1: 趋势与均线 ====================
    def analyze_trend(self) -> Dict:
        """趋势与均线分析"""
        df_20 = self.df.tail(20)
        df_60 = self.df.tail(60) if len(self.df) >= 60 else df_20
        df_120 = self.df.tail(120) if len(self.df) >= 120 else df_60
        
        ma5 = df_20['close'].tail(5).mean()
        ma10 = df_20['close'].tail(10).mean()
        ma20 = df_20['close'].tail(20).mean()
        ma60 = df_60['close'].tail(60).mean() if len(df_60) >= 60 else ma20
        ma120 = df_120['close'].tail(120).mean() if len(df_120) >= 120 else ma60
        
        # 均线排列
        if ma5 > ma10 > ma20 > ma60 > ma120:
            arrangement = "多头排列"
            score = 20
        elif ma5 < ma10 < ma20 < ma60 < ma120:
            arrangement = "空头排列"
            score = 5
        elif ma5 > ma20 and ma20 > ma60:
            arrangement = "短期多头"
            score = 12
        elif ma5 < ma20 and ma20 < ma60:
            arrangement = "短期回调"
            score = 8
        else:
            arrangement = "均线缠绕"
            score = 10
        
        # 均线拐头判断（新增）
        ma5_prev = self.df['close'].tail(6).head(5).mean()
        ma5_now = ma5
        ma10_prev = self.df['close'].tail(11).head(10).mean()
        ma10_now = ma10
        
        拐头 = "向上" if ma5_now > ma5_prev else ("向下" if ma5_now < ma5_prev else "走平")
        
        return {
            "ma5": round(ma5, 2),
            "ma10": round(ma10, 2),
            "ma20": round(ma20, 2),
            "ma60": round(ma60, 2),
            "ma120": round(ma120, 2),
            "arrangement": arrangement,
            "拐头方向": 拐头,
            "score": score
        }
    
    # ==================== 维度2: K线形态 ====================
    def analyze_kline(self) -> Dict:
        """K线形态分析"""
        latest = self.latest
        body = latest['close'] - latest['open']
        body_pct = body / latest['open'] * 100
        upper_shadow = latest['high'] - max(latest['open'], latest['close'])
        lower_shadow = min(latest['open'], latest['close']) - latest['low']
        total_range = latest['high'] - latest['low']
        
        # 形态识别
        if upper_shadow > total_range * 0.6 and body_pct < 1:
            pattern = "射击之星"
            signal = "🔴"
            score = 5
        elif lower_shadow > total_range * 0.6 and body_pct < 1:
            pattern = "锤子线"
            signal = "🟢"
            score = 12
        elif body_pct > 5:
            pattern = "大阳线"
            signal = "🟢"
            score = 15
        elif body_pct < -5:
            pattern = "大阴线"
            signal = "🔴"
            score = 5
        else:
            pattern = "小阴小阳"
            signal = "⚪"
            score = 8
        
        return {
            "pattern": pattern,
            "signal": signal,
            "涨跌幅": round(body_pct, 2),
            "上影线": round(upper_shadow, 2),
            "下影线": round(lower_shadow, 2),
            "score": score
        }
    
    # ==================== 维度3: 量价关系 ====================
    def analyze_volume_price(self) -> Dict:
        """量价关系分析"""
        df_20 = self.df.tail(20)
        avg_vol = df_20['volume'].mean()
        vol_ratio = self.latest['volume'] / avg_vol
        vol_change = (self.latest['volume'] - self.prev['volume']) / self.prev['volume'] * 100
        
        # 量价健康度
        if vol_ratio > 1.5 and self.latest['close'] > self.latest['open']:
            status = "价涨量增（健康）"
            score = 25
        elif vol_ratio > 1.5 and self.latest['close'] < self.latest['open']:
            status = "价跌量增（危险）"
            score = 8
        elif vol_ratio < 0.5:
            status = "缩量观望"
            score = 10
        else:
            status = "量价平稳"
            score = 15
        
        return {
            "成交量万": round(self.latest['volume'] / 10000, 1),
            "量比": round(vol_ratio, 2),
            "较昨日变化": round(vol_change, 1),
            "status": status,
            "score": score
        }
    
    # ==================== 维度4: 成交结构 ====================
    def analyze_structure(self) -> Dict:
        """成交结构分析"""
        df_60 = self.df.tail(60) if len(self.df) >= 60 else self.df
        
        high_60 = df_60['high'].max()
        low_60 = df_60['low'].min()
        avg_price = df_60['close'].mean()
        
        position = (self.latest['close'] - low_60) / (high_60 - low_60) * 100
        
        if position > 70:
            status = "高位风险大"
            score = 8
        elif position < 30:
            status = "低位有机会"
            score = 15
        else:
            status = "中性位置"
            score = 15
        
        return {
            "60日最高": round(high_60, 2),
            "60日最低": round(low_60, 2),
            "60日均价": round(avg_price, 2),
            "当前位置": round(position, 1),
            "status": status,
            "score": score
        }
    
    # ==================== 维度5: 动能节奏 ====================
    def analyze_momentum(self) -> Dict:
        """动能与节奏分析"""
        df_20 = self.df.tail(20)
        volatility = df_20['close'].std() / df_20['close'].mean() * 100
        
        df_60 = self.df.tail(60) if len(self.df) >= 60 else df_20
        limit_up = (df_60['pct_change'] > 9).sum()
        limit_down = (df_60['pct_change'] < -9).sum()
        
        if volatility > 20:
            status = "波动较大"
            score = 10
        else:
            status = "平稳运行"
            score = 12
        
        return {
            "波动率": round(volatility, 2),
            "60日涨停": limit_up,
            "60日跌停": limit_down,
            "status": status,
            "score": score
        }
    
    # ==================== 维度6: 板块题材 ====================
    def analyze_sector(self) -> Dict:
        """板块题材分析（需手动补充）"""
        return {
            "所属板块": "待查询",
            "题材概念": "待查询",
            "score": 10
        }
    
    # ==================== 维度7: 主力资金 ====================
    def analyze_money(self) -> Dict:
        """主力资金分析"""
        body = self.latest['close'] - self.latest['open']
        vol_ratio = self.latest['volume'] / self.df.tail(20)['volume'].mean()
        
        if body > 0 and vol_ratio > 1.2:
            status = "主力可能介入"
            score = 18
        elif body < 0 and vol_ratio > 1.2:
            status = "主力可能出货"
            score = 6
        elif vol_ratio < 0.5:
            status = "观望情绪浓厚"
            score = 10
        else:
            status = "多空平衡"
            score = 12
        
        return {
            "status": status,
            "score": score
        }
    
    # ==================== 新增维度8: 历史定位 ====================
    def analyze_history_position(self) -> Dict:
        """历史定位分析（新增）"""
        df_all = self.df
        
        all_time_high = df_all['high'].max()
        all_time_low = df_all['low'].min()
        
        # 获取数据对应的历史区间
        dates = df_all['date'].tolist()
        if len(dates) > 250:  # 约一年数据
            year_high = df_all.tail(250)['high'].max()
            year_low = df_all.tail(250)['low'].min()
        else:
            year_high, year_low = all_time_high, all_time_low
        
        current = self.latest['close']
        
        # 距离高点的跌幅
        from_high = (current - all_time_high) / all_time_high * 100
        
        # 距离低点的涨幅
        from_low = (current - all_time_low) / all_time_low * 100
        
        if from_high > -20:
            position = "接近历史高点"
            score = 8
        elif from_high > -50:
            position = "高位回落"
            score = 10
        elif from_low < 20:
            position = "接近历史低点"
            score = 15
        else:
            position = "中间位置"
            score = 12
        
        return {
            "历史最高": round(all_time_high, 2),
            "历史最低": round(all_time_low, 2),
            "距高点跌幅": round(from_high, 1),
            "距低点涨幅": round(from_low, 1),
            "当前位置": position,
            "score": score
        }
    
    # ==================== 新增维度9: 均线拐头 ====================
    def analyze_ma_direction(self) -> Dict:
        """均线方向分析（新增）"""
        df_20 = self.df.tail(20)
        
        # 计算均线变化方向
        ma5_now = df_20['close'].tail(5).mean()
        ma5_5d_ago = self.df['close'].tail(10).head(5).mean()
        
        ma10_now = df_20['close'].tail(10).mean()
        ma10_5d_ago = self.df['close'].tail(15).head(10).mean()
        
        ma20_now = df_20['close'].mean()
        ma20_5d_ago = self.df.tail(25).head(20)['close'].mean() if len(self.df) >= 25 else ma20_now
        
        direction5 = "上升" if ma5_now > ma5_5d_ago else ("下降" if ma5_now < ma5_5d_ago else "走平")
        direction10 = "上升" if ma10_now > ma10_5d_ago else ("下降" if ma10_now < ma10_5d_ago else "走平")
        direction20 = "上升" if ma20_now > ma20_5d_ago else ("下降" if ma20_now < ma20_5d_ago else "走平")
        
        # 判断是否有金叉/死叉可能
        if direction5 == "上升" and direction10 == "上升" and ma5_now > ma10_now:
            cross = "均线金叉在即"
            score = 15
        elif direction5 == "下降" and direction10 == "下降" and ma5_now < ma10_now:
            cross = "均线死叉在即"
            score = 5
        else:
            cross = "均线整理"
            score = 10
        
        return {
            "MA5方向": direction5,
            "MA10方向": direction10,
            "MA20方向": direction20,
            "均线交叉": cross,
            "score": score
        }
    
    # ==================== 新增维度10: RSI指标 ====================
    def analyze_rsi(self) -> Dict:
        """RSI指标分析（新增）"""
        # 取最新的RSI值
        rsi_cols = [c for c in self.df.columns if c.startswith('rsi')]
        
        if not rsi_cols:
            return {"status": "数据不足", "score": 8}
        
        rsi_values = {}
        for col in rsi_cols:
            rsi_values[col] = self.df[col].iloc[-1]
        
        rsi1 = rsi_values.get('rsi6', 50)
        
        # RSI判断
        if rsi1 > 80:
            status = "超买区"
            score = 5
        elif rsi1 > 70:
            status = "强势区"
            score = 10
        elif rsi1 < 20:
            status = "超卖区"
            score = 15
        elif rsi1 < 30:
            status = "弱势区"
            score = 12
        else:
            status = "中性区"
            score = 10
        
        return {
            "RSI1": round(rsi1, 1),
            "RSI2": round(rsi_values.get('rsi12', 50), 1),
            "RSI3": round(rsi_values.get('rsi24', 50), 1),
            "status": status,
            "score": score
        }
    
    # ==================== 新增维度11: 心理层面 ====================
    def analyze_psychology(self) -> Dict:
        """心理层面分析（新增 - 核心价值）"""
        df_5 = self.df.tail(5)
        
        # 近期量价特征
        vol_trend = "放量" if df_5['volume'].iloc[-1] > df_5['volume'].iloc[0] else "缩量"
        price_trend = "上涨" if df_5['close'].iloc[-1] > df_5['close'].iloc[0] else "下跌"
        
        # 恐慌/贪婪判断
        df_10 = self.df.tail(10)
        
        # 近期最大跌幅
        max_drop = (df_10['close'].min() - df_10['close'].max()) / df_10['close'].max() * 100
        
        if max_drop > 15:
            phase = "恐慌出清期"
            description = "近期跌幅超过15%，可能出现恐慌盘"
            score = 15
        elif max_drop > 8:
            phase = "调整期"
            description = "有一定跌幅，但未到恐慌程度"
            score = 12
        else:
            phase = "稳定期"
            description = "近期波动较小，市场情绪稳定"
            score = 10
        
        # 放量涨/缩量跌判断
        latest_vol = self.latest['volume']
        avg_vol = df_10['volume'].mean()
        
        if latest_vol > avg_vol * 1.5 and self.latest['close'] > self.latest['open']:
            emotion = "贪婪积极"
        elif latest_vol > avg_vol * 1.5 and self.latest['close'] < self.latest['open']:
            emotion = "恐慌抛售"
        elif latest_vol < avg_vol * 0.7:
            emotion = "观望谨慎"
        else:
            emotion = "多空平衡"
        
        return {
            "量价趋势": f"{vol_trend}{price_trend}",
            "近期跌幅": round(max_drop, 1),
            "所处阶段": phase,
            "市场情绪": emotion,
            "description": description,
            "score": score
        }
    
    # ==================== 综合分析 ====================
    def full_analysis(self) -> str:
        """完整分析报告"""
        trend = self.analyze_trend()
        kline = self.analyze_kline()
        vp = self.analyze_volume_price()
        struct = self.analyze_structure()
        momentum = self.analyze_momentum()
        sector = self.analyze_sector()
        money = self.analyze_money()
        history = self.analyze_history_position()
        ma_dir = self.analyze_ma_direction()
        rsi = self.analyze_rsi()
        psychology = self.analyze_psychology()
        
        # 计算总分
        total = (trend['score'] + kline['score'] + vp['score'] + 
                struct['score'] + momentum['score'] + sector['score'] + 
                money['score'] + history['score'] + ma_dir['score'] + 
                rsi['score'] + psychology['score'])
        
        # 评级
        if total >= 140:
            rating = "强势主升"
            action = "积极参与"
        elif total >= 110:
            rating = "可操作"
            action = "择时操作"
        elif total >= 80:
            rating = "观望"
            action = "等待信号"
        else:
            rating = "风险区"
            action = "建议回避"
        
        # 生成报告
        report = f"""
======================================================================
📊 {self._get_stock_name()} 个股分析报告 v3.0
======================================================================

【一、趋势与均线】得分: {trend['score']}/20
  MA5: {trend['ma5']} | MA10: {trend['ma10']} | MA20: {trend['ma20']}
  MA60: {trend['ma60']} | MA120: {trend['ma120']}
  均线排列: {trend['arrangement']}
  短期方向: {trend['拐头方向']}

【二、K线形态】得分: {kline['score']}/15
  形态: {kline['pattern']} {kline['signal']}
  涨跌幅: {kline['涨跌幅']:+.2f}%

【三、量价关系】得分: {vp['score']}/25
  成交量: {vp['成交量万']}万手
  量比: {vp['量比']} | 较昨日: {vp['较昨日变化']:+.1f}%
  状态: {vp['status']}

【四、成交结构】得分: {struct['score']}/20
  60日区间: {struct['60日最低']} ~ {struct['60日最高']}
  当前位置: {struct['当前位置']} ({struct['当前位置']}%)

【五、动能节奏】得分: {momentum['score']}/15
  波动率: {momentum['波动率']}%

【六、板块题材】得分: {sector['score']}/20
  所属板块: {sector['所属板块']}

【七、主力资金】得分: {money['score']}/20
  状态: {money['status']}

【八、历史定位】得分: {history['score']}/20 【新增】
  历史高低: {history['历史最低']} ~ {history['历史最高']}
  距高点: {history['距高点跌幅']:+.1f}% | 距低点: {history['距低点涨幅']:+.1f}%
  当前位置: {history['当前位置']}

【九、均线方向】得分: {ma_dir['score']}/15 【新增】
  MA5: {ma_dir['MA5方向']} | MA10: {ma_dir['MA10方向']} | MA20: {ma_dir['MA20方向']}
  {ma_dir['均线交叉']}

【十、RSI指标】得分: {rsi['score']}/15 【新增】
  RSI1: {rsi['RSI1']} | RSI2: {rsi['RSI2']} | RSI3: {rsi['RSI3']}
  状态: {rsi['status']}

【十一、心理层面】得分: {psychology['score']}/15 【新增-核心】
  市场情绪: {psychology['市场情绪']}
  所处阶段: {psychology['所处阶段']}
  {psychology['description']}

======================================================================
【综合评分】{total}/195
【评级】{rating}
【操作建议】{action}
======================================================================
"""
        return report
    
    def _get_stock_name(self) -> str:
        """获取股票名称（从数据推断）"""
        # 尝试从文件获取
        return "个股"


def analyze_stock(data_path: str) -> str:
    """分析个股"""
    analyzer = StockAnalyzerV3(data_path)
    return analyzer.full_analysis()


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        report = analyze_stock(sys.argv[1])
        print(report)
    else:
        print("用法: python3 stock_analyzer_v3.py <数据文件路径>")
