#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股交易模式自动识别系统
中国股市特有模式识别

使用方法:
    from stock.analysis.patterns.pattern_detector import PatternDetector
    
    detector = PatternDetector()
    result = detector.analyze(df)
    print(result)
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional


class PatternDetector:
    """A股模式识别器"""

    def analyze(self, df: pd.DataFrame) -> Dict:
        """综合分析"""
        if df is None or len(df) < 20:
            return {"error": "数据不足，至少需要20日数据"}
        
        result = {
            "分析时间": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "当前价格": round(df['close'].iloc[-1], 2),
            "趋势": self._detect_trend(df),
            "资金流": self._detect_fund_flow(df),
            "动量": self._detect_momentum(df),
            "技术形态": self._detect_patterns(df),
            "综合评分": self._calc_score(df),
            "A股模式": self._detect_china_patterns(df)
        }
        
        return result
    
    def _detect_trend(self, df: pd.DataFrame) -> Dict:
        """趋势识别"""
        close = df['close']
        ma5 = close.rolling(5).mean().iloc[-1]
        ma20 = close.rolling(20).mean().iloc[-1]
        ma60 = close.rolling(60).mean().iloc[-1] if len(df) >= 60 else ma20
        
        if ma5 > ma20 > ma60:
            trend = "多头排列"
            signal = "买入"
        elif ma5 < ma20 < ma60:
            trend = "空头排列"
            signal = "卖出"
        else:
            trend = "横盘整理"
            signal = "观望"
        
        change20 = (close.iloc[-1] - close.iloc[-20]) / close.iloc[-20] * 100 if len(df) >= 20 else 0
        
        return {
            "趋势": trend,
            "MA5/MA20/MA60": f"{ma5:.2f}/{ma20:.2f}/{ma60:.2f}",
            "近20日涨跌幅": f"{change20:+.1f}%",
            "信号": signal
        }
    
    def _detect_fund_flow(self, df: pd.DataFrame) -> Dict:
        """资金流识别"""
        close = df['close']
        volume = df['volume']
        
        vol_ma10 = volume.rolling(10).mean()
        vol_now = volume.iloc[-1]
        vol_ratio = vol_now / vol_ma10.iloc[-1] if vol_ma10.iloc[-1] > 0 else 1
        
        change5d = (close.iloc[-1] - close.iloc[-5]) / close.iloc[-5] * 100 if len(df) >= 5 else 0
        
        if vol_ratio > 1.5 and change5d > 3:
            flow_type = "资金流入"
            desc = "量价齐升"
        elif vol_ratio > 1.5 and change5d < -3:
            flow_type = "资金流出"
            desc = "放量下跌"
        elif vol_ratio < 0.8 and change5d > 0:
            flow_type = "缩量上涨"
            desc = "量能不足"
        else:
            flow_type = "资金平衡"
            desc = "观望为主"
        
        return {
            "类型": flow_type,
            "描述": desc,
            "量比": round(vol_ratio, 2),
            "近5日涨跌": f"{change5d:+.1f}%"
        }
    
    def _detect_momentum(self, df: pd.DataFrame) -> Dict:
        """动量信号"""
        close = df['close']
        
        # RSI
        delta = close.diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs)) if loss.iloc[-1] > 0 else 50
        rsi_val = rsi.iloc[-1] if hasattr(rsi, 'iloc') else 50
        
        # MACD
        ema12 = close.ewm(span=12).mean().iloc[-1]
        ema26 = close.ewm(span=26).mean().iloc[-1]
        dif = ema12 - ema26
        dea = (ema12 - ema26) * 0.9
        macd = 2 * (dif - dea)
        
        if rsi_val > 70:
            rsi_status = "超买"
        elif rsi_val < 30:
            rsi_status = "超卖"
        else:
            rsi_status = "中性"
        
        return {
            "RSI(14)": round(rsi_val, 2),
            "RSI状态": rsi_status,
            "MACD": round(macd, 4),
            "MACD信号": "多头" if macd > 0 else "空头"
        }
    
    def _detect_patterns(self, df: pd.DataFrame) -> Dict:
        """技术形态"""
        close = df['close']
        high = df['high']
        low = df['low']
        volume = df['volume']
        
        patterns = []
        
        # 突破
        ma20 = close.rolling(20).mean().iloc[-1]
        high20 = high.rolling(20).max().iloc[-1]
        if close.iloc[-1] > high20:
            patterns.append(f"突破{high20:.2f}元高点")
        
        # 回踩
        ma10 = close.rolling(10).mean().iloc[-1]
        if abs(close.iloc[-1] - ma10) / ma10 < 0.02:
            patterns.append(f"回踩MA10({ma10:.2f})支撑")
        
        # 连阳
        consec = 0
        for i in range(min(5, len(close))):
            if close.iloc[-1-i] > close.iloc[-2-i]:
                consec += 1
            else:
                break
        if consec >= 3:
            patterns.append(f"连阳{consec}日")
        
        return {
            "识别的形态": patterns if patterns else ["无明显形态"],
            "当前价格": close.iloc[-1],
            "20日高点": high20,
            "MA10": round(ma10, 2)
        }
    
    def _calc_score(self, df: pd.DataFrame) -> Dict:
        """综合评分"""
        close = df['close']
        volume = df['volume']
        
        score = 50
        ma5 = close.rolling(5).mean().iloc[-1]
        ma20 = close.rolling(20).mean().iloc[-1]
        
        # 趋势加分
        if ma5 > ma20:
            score += 20
        else:
            score -= 20
        
        # 资金加分
        vol_ma10 = volume.rolling(10).mean().iloc[-1]
        if volume.iloc[-1] > vol_ma10 * 1.5:
            score += 15
        
        # 限制分数
        score = max(0, min(100, score))
        
        if score >= 80:
            level = "【强势】"
            action = "积极参与"
        elif score >= 60:
            level = "【偏强】"
            action = "回调买入"
        elif score >= 40:
            level = "【中性】"
            action = "观望"
        else:
            level = "【弱势】"
            action = "回避"
        
        return {"评分": score, "等级": level, "建议": action}
    
    def _detect_china_patterns(self, df: pd.DataFrame) -> Dict:
        """A股特有模式"""
        close = df['close']
        high = df['high']
        volume = df['volume']
        
        patterns = {"机会": [], "风险": []}
        
        # 涨停候选
        if len(df) >= 2:
            today_change = (close.iloc[-1] - close.iloc[-2]) / close.iloc[-2] * 100
            if today_change > 7:
                patterns["机会"].append(f"涨停候选(+{today_change:.1f}%)")
        
        # 高换手
        vol_ma20 = volume.rolling(20).mean().iloc[-1]
        if volume.iloc[-1] > vol_ma20 * 3:
            patterns["风险"].append("异常高换手")
        
        # 量价齐升
        vol5d = volume.iloc[-5:].mean()
        price5d = (close.iloc[-1] - close.iloc[-5]) / close.iloc[-5] * 100 if len(df) >= 5 else 0
        if vol5d > vol_ma20 * 1.5 and price5d > 10:
            patterns["机会"].append("量价齐升")
        
        return patterns


def format_report(result: Dict) -> str:
    """格式化报告"""
    if "error" in result:
        return f"分析失败: {result['error']}"
    
    return f"""
{'='*70}
【A股模式识别报告】 - {result['分析时间']}
{'='*70

当前价格: {result['当前价格']:.2f}元

─────────────────────────────────────────────────────────────────────
【趋势分析】
─────────────────────────────────────────────────────────────────────
  {result['趋势']['趋势']}
  MA5/MA20/MA60: {result['趋势']['MA5/MA20/MA60']}
  近20日涨跌: {result['趋势']['近20日涨跌幅']}
  信号: {result['趋势']['信号']}

─────────────────────────────────────────────────────────────────────
【资金流】
─────────────────────────────────────────────────────────────────────
  {result['资金流']['类型']} - {result['资金流']['描述']}
  量比: {result['资金流']['量比']} | 近5日涨跌: {result['资金流']['近5日涨跌']}

─────────────────────────────────────────────────────────────────────
【动量信号】
─────────────────────────────────────────────────────────────────────
  RSI(14): {result['动量']['RSI(14)']:.1f} - {result['动量']['RSI状态']}
  MACD: {result['动量']['MACD']:.4f} - {result['动量']['MACD信号']}

─────────────────────────────────────────────────────────────────────
【技术形态】
─────────────────────────────────────────────────────────────────────
  {' / '.join(result['技术形态']['识别的形态'])}

─────────────────────────────────────────────────────────────────────
【A股特有模式】
─────────────────────────────────────────────────────────────────────
  机会信号: {', '.join(result['A股模式']['机会']) if result['A股模式']['机会'] else '无'}
  风险提示: {', '.join(result['A股模式']['风险']) if result['A股模式']['风险'] else '无'}

─────────────────────────────────────────────────────────────────────
【综合评分】{result['综合评分']['评分']}分 - {result['综合评分']['等级']}
  建议: {result['综合评分']['建议']}
{'='*70}
"""


# ========== 测试 ==========
if __name__ == '__main__':
    import random
    
    dates = pd.date_range(end=datetime.now(), periods=60)
    base = 10
    close = [base + i * 0.05 + random.uniform(-0.2, 0.2) for i in range(60)]
    
    df = pd.DataFrame({
        'close': close,
        'open': close,
        'high': [c + random.uniform(0, 0.3) for c in close],
        'low': [c - random.uniform(0, 0.3) for c in close],
        'volume': [1000000 + random.randint(-200000, 400000) for _ in range(60)]
    })
    
    detector = PatternDetector()
    result = detector.analyze(df)
    print(format_report(result))
