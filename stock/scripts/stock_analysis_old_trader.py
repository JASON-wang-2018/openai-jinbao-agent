#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
老股民警模型
专注于识别"主力可持续推升阶段"

严格遵循7步分析流程，证据一致性原则

使用方法:
    python stock_analysis.py --code 002642
"""

import sys
import os
import argparse
import pandas as pd
import numpy as np
import akshare as ak
from datetime import datetime
from typing import Dict, List, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class OldTraderAnalysis:
    """老股民警模型"""
    
    def __init__(self, stock_code: str):
        self.code = stock_code
        self.df = None
        self.name = ""
        self.close = 0
        self.score = 0
        self.max_score = 100
        
        # 计算指标缓存
        self.ma5 = self.ma10 = self.ma20 = self.ma60 = 0
        self.ma5_ago = self.ma10_ago = self.ma20_ago = 0
        self.close_ago5 = self.close_ago20 = 0
        self.high_252 = self.low_252 = 0
        self.vol_now = self.vol_ma20 = 0
        self.rsi = 50
        self.macd = 0
        self.position = 50
        
    def get_data(self) -> bool:
        """获取数据"""
        try:
            self.df = ak.stock_zh_a_hist(
                symbol=self.code,
                period="daily",
                start_date="20250101",
                end_date=datetime.now().strftime('%Y%m%d'),
                adjust="qfq"
            )
            
            if self.df is None or len(self.df) < 60:
                return False
            
            # 基础数据
            self.close = float(self.df['收盘'].iloc[-1])
            self.name = self._get_name()
            
            # 计算均线
            close = pd.to_numeric(self.df['收盘'], errors='coerce')
            self.ma5 = close.rolling(5).mean().iloc[-1]
            self.ma10 = close.rolling(10).mean().iloc[-1]
            self.ma20 = close.rolling(20).mean().iloc[-1]
            self.ma60 = close.rolling(60).mean().iloc[-1]
            
            self.ma5_ago = close.rolling(5).mean().iloc[-20] if len(self.df) >= 20 else self.ma5
            self.ma10_ago = close.rolling(10).mean().iloc[-20] if len(self.df) >= 20 else self.ma10
            
            self.close_ago5 = close.iloc[-5]
            self.close_ago20 = close.iloc[-20]
            
            # 价格区间
            self.high_252 = close.max()
            self.low_252 = close.min()
            self.position = (self.close - self.low_252) / (self.high_252 - self.low_252) * 100
            
            # 量能
            volume = pd.to_numeric(self.df['成交量'], errors='coerce')
            self.vol_now = volume.iloc[-1]
            self.vol_ma20 = volume.rolling(20).mean().iloc[-1]
            
            # RSI
            delta = close.diff()
            gain = delta.where(delta > 0, 0).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss
            self.rsi = 100 - (100 / (1 + rs.iloc[-1])) if loss.iloc[-1] > 0 else 50
            
            # MACD
            ema12 = close.ewm(span=12).mean().iloc[-1]
            ema26 = close.ewm(span=26).mean().iloc[-1]
            dif = ema12 - ema26
            dea = dif.ewm(span=9).mean().iloc[-1]
            self.macd = 2 * (dif - dea)
            
            return True
        except Exception as e:
            print(f"数据获取失败: {e}")
            return False
    
    def _get_name(self) -> str:
        """获取股票名称"""
        try:
            url = f"https://hq.sinajs.cn/list=sz{self.code}" if not self.code.startswith('6') else f"https://hq.sinajs.cn/list=sh{self.code}"
            resp = requests.get(url, headers={'Referer':'https://finance.sina.com.cn'}, timeout=10)
            return resp.text.split('"')[1].split(',')[0]
        except:
            return self.code
    
    # ========== 一、趋势与生命周期判断 ==========
    
    def step1_trend_analysis(self) -> Dict:
        """趋势与生命周期判断"""
        # 1. 均线结构
        if self.ma5 > self.ma10 > self.ma20 > self.ma60:
            ma_structure = "多头发散"
            ma_score = 20
        elif self.ma5 < self.ma10 < self.ma20 < self.ma60:
            ma_structure = "空头下压"
            ma_score = 0
        elif abs(self.ma5 - self.ma10) < 0.02 * self.ma20 and abs(self.ma10 - self.ma20) < 0.02 * self.ma20:
            ma_structure = "震荡缠绕"
            ma_score = 10
        elif self.ma5 > self.ma10 > self.ma20:
            ma_structure = "多头初期"
            ma_score = 15
        elif self.ma5 < self.ma10 < self.ma20:
            ma_structure = "空头初期"
            ma_score = 5
        else:
            ma_structure = "震荡整理"
            ma_score = 10
        
        # 2. 股价位置
        if self.position < 30:
            price_position = "阶段低位"
            pos_score = 10
        elif self.position < 70:
            price_position = "中位"
            pos_score = 7
        else:
            price_position = "高位"
            pos_score = 3
        
        # 3. 趋势阶段判断
        change_20d = (self.close - self.close_ago20) / self.close_ago20 * 100
        
        if ma_structure == "多头发散" and change_20d > 20:
            trend_stage = "主升阶段"
        elif ma_structure == "多头发散" and change_20d > 0:
            trend_stage = "启动阶段"
        elif ma_structure == "震荡缠绕" and change_20d > 0:
            trend_stage = "洗盘整理"
        elif ma_structure == "空头下压" and change_20d < -20:
            trend_stage = "派发出货"
        elif ma_structure == "空头下压":
            trend_stage = "下跌趋势"
        else:
            trend_stage = "震荡筑底"
        
        return {
            'ma_structure': ma_structure,
            'ma_structure_score': ma_score,
            'price_position': price_position,
            'position_score': pos_score,
            'trend_stage': trend_stage,
            'change_20d': change_20d
        }
    
    # ========== 二、多维技术与行为证据 ==========
    
    def step2_multidimensional_analysis(self) -> Dict:
        """多维技术分析"""
        result = {}
        
        # 4. 趋势与均线
        vol_now = self.vol_now
        vol_ma20 = self.vol_ma20
        vol_ratio = vol_now / vol_ma20
        
        change_5d = (self.close - self.close_ago5) / self.close_ago5 * 100
        
        # 回踩关键均线
        if self.close > self.ma20 * 0.98:
            ma_support = True
            ma_support_desc = f"收盘>{self.ma20:.2f}元（MA20支撑）"
        elif self.close > self.ma60 * 0.98:
            ma_support = True
            ma_support_desc = f"收盘>{self.ma60:.2f}元（MA60支撑）"
        else:
            ma_support = False
            ma_support_desc = "跌破关键均线"
        
        # 回踩缩量
        if vol_ratio < 0.8:
            vol_shrink = True
            vol_shrink_desc = "回踩缩量，惜售明显"
        elif vol_ratio < 1:
            vol_shrink = True
            vol_shrink_desc = "回踩略有缩量"
        else:
            vol_shrink = False
            vol_shrink_desc = "回踩放量，需警惕"
        
        # 均线斜率
        if self.ma5 > self.ma5_ago * 1.01:
            ma_slope = "上行"
            ma_slope_desc = "MA5斜率向上"
        elif self.ma5 < self.ma5_ago * 0.99:
            ma_slope = "下行"
            ma_slope_desc = "MA5斜率向下"
        else:
            ma_slope = "走平"
            ma_slope_desc = "MA5走平"
        
        result['ma'] = {
            'support': (ma_support, ma_support_desc),
            'shrink': (vol_shrink, vol_shrink_desc),
            'slope': (ma_slope, ma_slope_desc)
        }
        
        # 5. K线形态
        recent = self.df.tail(10)
        close = pd.to_numeric(recent['收盘'], errors='coerce')
        high = pd.to_numeric(recent['最高'], errors='coerce')
        low = pd.to_numeric(recent['最低'], errors='coerce')
        
        # 试盘线
        test_line = False
        if high.iloc[-1] > high.rolling(5).max().iloc[-1] * 0.99:
            test_line = True
        
        # 洗盘线
        wash_line = False
        if close.iloc[-1] < close.iloc[-2] and vol_ratio < 0.8:
            wash_line = True
        
        # 启动线
        start_line = False
        if change_5d > 5 and vol_ratio > 1.5:
            start_line = True
        
        result['kline'] = {
            'test_line': (test_line, "试盘线" if test_line else "无"),
            'wash_line': (wash_line, "洗盘线" if wash_line else "无"),
            'start_line': (start_line, "启动线" if start_line else "无")
        }
        
        # 6. 量价关系（核心）
        if change_5d > 0 and vol_ratio > 1.2:
            vp_type = "价涨量增"
            vp_score = 20
            vp_desc = "量价齐升，健康上涨"
        elif change_5d > 0 and vol_ratio < 0.8:
            vp_type = "价涨量缩"
            vp_score = 12
            vp_desc = "量能不足，警惕诱多"
        elif change_5d < 0 and vol_ratio < 0.8:
            vp_type = "价跌量缩"
            vp_score = 10
            vp_desc = "惜售，可能见底"
        elif change_5d < 0 and vol_ratio > 1.2:
            vp_type = "价跌量增"
            vp_score = 8
            vp_desc = "放量下跌，恐慌抛售"
        else:
            vp_type = "量价平衡"
            vp_score = 12
            vp_desc = "震荡整理"
        
        result['volume_price'] = {
            'type': vp_type,
            'score': vp_score,
            'desc': vp_desc,
            'change_5d': change_5d,
            'vol_ratio': vol_ratio
        }
        
        # 7. 成交结构
        vol_ma60 = pd.to_numeric(self.df['成交量'], errors='coerce').rolling(60).mean().iloc[-1]
        
        if vol_now > vol_ma60 * 1.5:
            structure = "放量突破"
            structure_score = 10
            structure_desc = "量能放大，资金关注"
        elif vol_now > vol_ma60 * 0.8:
            structure = "量能适中"
            structure_score = 7
            structure_desc = "交投正常"
        else:
            structure = "缩量整理"
            structure_score = 5
            structure_desc = "交投清淡"
        
        result['structure'] = {
            'type': structure,
            'score': structure_score,
            'desc': structure_desc
        }
        
        # 8. 板块与情绪（简化）
        result['sector'] = {
            'sector': "科技-软件服务",
            'activity': "一般",
            'score': 10
        }
        
        return result
    
    # ========== 三、主力行为模型判定 ==========
    
    def step3_main_force_judgment(self, trend: Dict, multi: Dict) -> Dict:
        """主力行为模型判定"""
        vp = multi['volume_price']
        
        # 综合判断
        if vp['type'] == "价涨量增" and trend['change_20d'] > 10:
            main_force = "拉升推升"
            main_desc = "量价齐升，主力做多"
        elif vp['type'] == "价跌量缩" and self.position < 40:
            main_force = "吸筹"
            main_desc = "缩量回调，主力吸筹"
        elif vp['type'] == "价涨量缩":
            main_force = "洗盘"
            main_desc = "缩量上涨，主力洗盘"
        elif vp['type'] == "价跌量增":
            main_force = "派发"
            main_desc = "放量下跌，主力派发"
        else:
            main_force = "震荡整理"
            main_desc = "量价平衡，震荡整理"
        
        return {
            'stage': main_force,
            'desc': main_desc
        }
    
    # ========== 四、综合评分 ==========
    
    def step4_scoring(self, trend: Dict, multi: Dict, main: Dict) -> Dict:
        """综合评分"""
        score = 0
        
        # 均线结构 (20)
        score += trend['ma_structure_score']
        
        # 股价位置 (10)
        score += trend['position_score']
        
        # K线信号 (15)
        kline = multi['kline']
        if kline['test_line'][0]:
            score += 8
        if kline['start_line'][0]:
            score += 10
        if kline['wash_line'][0]:
            score += 5
        score = min(score, 15)
        
        # 量价健康度 (20)
        score += multi['volume_price']['score']
        
        # 成交结构 (10)
        score += multi['structure']['score']
        
        # 板块情绪 (15)
        score += multi['sector']['score']
        
        # 额外加分
        if self.macd > 0:
            score += 5
        if 40 < self.rsi < 70:
            score += 3
        
        self.score = min(score, 100)
        
        if self.score >= 80:
            level = "【主升候选】"
            qualified = True
        elif self.score >= 60:
            level = "【观察】"
            qualified = True
        else:
            level = "【不合格】"
            qualified = False
        
        # 不合格判定
        unqualified_reasons = []
        if vp_type := multi['volume_price']['type'] == "价跌量增":
            unqualified_reasons.append("放量跌破关键位")
        if self.position > 80:
            unqualified_reasons.append("股价处于高位")
        if vp_type := multi['volume_price']['type'] == "价涨量缩" and self.close > self.ma20 * 1.1:
            unqualified_reasons.append("高位放量滞涨")
        
        return {
            'score': self.score,
            'level': level,
            'qualified': qualified and not unqualified_reasons,
            'unqualified_reasons': unqualified_reasons
        }
    
    # ========== 五、走势概率推演 ==========
    
    def step5_probability(self, score: int, main: Dict) -> Dict:
        """走势概率推演"""
        if score >= 60:
            return {
                'path1': ("主升延续", 45, "放量突破或缩量回踩不破"),
                'path2': ("震荡洗盘", 40, "区间震荡，消化浮筹"),
                'path3': ("趋势破坏", 15, "跌破关键支撑位")
            }
        else:
            return {
                'path1': ("震荡筑底", 40, "缩量整理，企稳回升"),
                'path2': ("弱势反弹", 35, "超跌反抽，空间有限"),
                'path3': ("继续探底", 25, "破位下行")
            }
    
    # ========== 六、策略与风控 ==========
    
    def step6_strategy(self, trend: Dict, main: Dict, prob: Dict) -> Dict:
        """策略与风控"""
        stage = main['stage']
        
        if stage == "拉升推升":
            return {
                'empty': "回调至MA5/MA10企稳后买入",
                'light': "回调加仓至50%",
                'heavy': "以MA10为止损，不加仓",
                'stop_loss': round(self.ma10, 2),
                'alert': "放量滞涨、板块退潮"
            }
        elif stage == "吸筹":
            return {
                'empty': "分批建仓30%",
                'light': "回落至MA60加仓至50%",
                'heavy': "以MA60为止损",
                'stop_loss': round(self.ma60, 2),
                'alert': "放量跌破MA60"
            }
        elif stage == "洗盘":
            return {
                'empty': "等待洗盘结束信号",
                'light': "保持现有仓位",
                'heavy': "持股不动",
                'stop_loss': round(self.low_252, 2),
                'alert': "破位下跌"
            }
        else:
            return {
                'empty': "观望为主",
                'light': "轻仓观望",
                'heavy': "减仓至30%",
                'stop_loss': round(self.close * 0.95, 2),
                'alert': "趋势走弱"
            }
    
    # ========== 七、最终输出 ==========
    
    def generate_report(self) -> str:
        """生成完整报告"""
        if not self.get_data():
            return "数据获取失败"
        
        # 执行7步分析
        trend = self.step1_trend_analysis()
        multi = self.step2_multidimensional_analysis()
        main = self.step3_main_force_judgment(trend, multi)
        scoring = self.step4_scoring(trend, multi, main)
        prob = self.step5_probability(scoring['score'], main)
        strategy = self.step6_strategy(trend, main, prob)
        
        # 生成报告
        report = []
        report.append("=" * 70)
        report.append(f"【{self.code}】{self.name} - 老股民警模型分析报告")
        report.append(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        report.append("=" * 70)
        report.append("")
        report.append(f"当前价格: {self.close:.2f}元  位置: {self.position:.0f}%")
        report.append("")
        
        # 一、趋势与生命周期
        report.append("-" * 70)
        report.append("【一、趋势与生命周期判断】")
        report.append("-" * 70)
        report.append(f"均线结构: {trend['ma_structure']} ({trend['ma_structure_score']}分)")
        report.append(f"MA5/10/20/60: {self.ma5:.2f}/{self.ma10:.2f}/{self.ma20:.2f}/{self.ma60:.2f}")
        report.append(f"股价位置: {trend['price_position']} ({trend['position_score']}分)")
        report.append(f"20日涨跌幅: {trend['change_20d']:+.1f}%")
        report.append(f"趋势阶段: 【{trend['trend_stage']}】")
        report.append("")
        
        # 二、多维证据
        report.append("-" * 70)
        report.append("【二、多维技术与行为证据分析】")
        report.append("-" * 70)
        
        # 趋势均线
        ma = multi['ma']
        report.append("4. 趋势与均线:")
        report.append(f"   回踩支撑: {'是' if ma['support'][0] else '否'} - {ma['support'][1]}")
        report.append(f"   回踩缩量: {'是' if ma['shrink'][0] else '否'} - {ma['shrink'][1]}")
        report.append(f"   均线斜率: {ma['slope'][0]} - {ma['slope'][1]}")
        
        # K线形态
        kline = multi['kline']
        report.append("5. K线形态:")
        report.append(f"   试盘线: {kline['test_line'][1]}")
        report.append(f"   洗盘线: {kline['wash_line'][1]}")
        report.append(f"   启动线: {kline['start_line'][1]}")
        
        # 量价
        vp = multi['volume_price']
        report.append("6. 量价关系（核心）:")
        report.append(f"   当前状态: {vp['type']} - {vp['desc']}")
        report.append(f"   5日涨幅: {vp['change_5d']:+.1f}%  量比: {vp['vol_ratio']:.2f}")
        
        # 成交结构
        st = multi['structure']
        report.append("7. 成交结构:")
        report.append(f"   类型: {st['type']} - {st['desc']}")
        
        # 板块
        sc = multi['sector']
        report.append("8. 板块环境:")
        report.append(f"   所属: {sc['sector']} - 活跃度: {sc['activity']}")
        report.append("")
        
        # 三、主力行为
        report.append("-" * 70)
        report.append("【三、主力行为模型判定】")
        report.append("-" * 70)
        report.append(f"主力阶段: 【{main['stage']}】")
        report.append(f"判断理由: {main['desc']}")
        report.append("")
        
        # 四、综合评分
        report.append("-" * 70)
        report.append("【四、80分主升评分】")
        report.append("-" * 70)
        report.append(f"综合评分: {scoring['score']}分/100 → {scoring['level']}")
        
        if scoring['unqualified_reasons']:
            report.append("不合格原因:")
            for r in scoring['unqualified_reasons']:
                report.append(f"  - {r}")
        
        report.append("评分明细:")
        report.append(f"  均线结构: {trend['ma_structure_score']}分")
        report.append(f"  股价位置: {trend['position_score']}分")
        report.append(f"  K线信号: {min(15, (8 if kline['test_line'][0] else 0) + (10 if kline['start_line'][0] else 0) + (5 if kline['wash_line'][0] else 0)}分")
        report.append(f"  量价健康: {vp['score']}分")
        report.append(f"  成交结构: {st['score']}分")
        report.append(f"  板块情绪: {sc['score']}分")
        report.append(f"  MACD加分: {'+5' if self.macd > 0 else '0'}分")
        report.append(f"  RSI加分: {'+3' if 40 < self.rsi < 70 else '0'}分")
        report.append("")
        
        # 五、走势推演
        report.append("-" * 70)
        report.append("【五、走势概率推演】")
        report.append("-" * 70)
        report.append(f"  路径一: {prob['path1'][0]}（{prob['path1'][1]}%）- {prob['path1'][2]}")
        report.append(f"  路径二: {prob['path2'][0]}（{prob['path2'][1]}%）- {prob['path2'][2]}")
        report.append(f"  路径三: {prob['path3'][0]}（{prob['path3'][1]}%）- {prob['path3'][2]}")
        report.append("")
        
        # 六、策略
        report.append("-" * 70)
        report.append("【六、策略与风控建议】")
        report.append("-" * 70)
        report.append("空仓者:")
        report.append(f"  {strategy['empty']}")
        report.append("持仓者:")
        report.append(f"  {strategy['light']}")
        report.append("重仓者:")
        report.append(f"  {strategy['heavy']}")
        report.append(f"止损位: {strategy['stop_loss']:.2f}元")
        report.append(f"警惕信号: {strategy['alert']}")
        report.append("")
        
        report.append("=" * 70)
        
        return '\n'.join(report)


def main():
    parser = argparse.ArgumentParser(description='老股民警模型')
    parser.add_argument('--code', required=True, help='股票代码')
    args = parser.parse_args()
    
    analyzer = OldTraderAnalysis(args.code)
    report = analyzer.generate_report()
    print(report)
    
    # 保存
    now = datetime.now()
    filename = f"/home/jason/.openclaw/workspace/stock/reports/stock_{args.code}_{now.strftime('%Y-%m-%d')}.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\n报告已保存: {filename}")


if __name__ == '__main__':
    main()
