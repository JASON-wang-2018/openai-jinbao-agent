#!/usr/bin/env python3
"""
股票知识推送脚本
- 16:18 知识干货
- 20:18 收盘总结
"""

import os
import sys
import json
import random
import datetime
import subprocess

WEBHOOK_URL = os.environ.get("STOCK_WEBHOOK_URL", "")

# 知识干货库
KNOWLEDGE_TIPS = [
    "📈 【量价关系】放量上涨是健康的量价配合，说明有资金进场；放量下跌则需警惕，可能是出货信号。",
    "📊 【趋势识别】MA5>MA10>MA20>MA60是多头排列，每次回踩不破均线都是加仓机会。",
    "🔍 【龙头战法】做短线一定要做龙头，龙头股涨幅最大、回调最少、溢价最高。",
    "💎 【分歧转一致】个股首日分歧放量大长腿，次日高开缩量上板，是经典的分歧转一致信号。",
    "🎯 【止损纪律】止损是交易的保护伞，亏损超过7%必须止损，不能心存侥幸。",
    "📉 【反弹信号】连续缩量下跌后出现十字星，是变盘信号，可能迎来反弹。",
    "🧭 【主线思维】不做杂毛，只做主线。只有主线板块才有持续性，才有机会。",
    "⚡ 【情绪周期】冰点→修复→高潮→分化→退潮→冰点，循环往复。",
    "📌 【阻力支撑】前期高点是阻力位，突破需要放量；前期低点是支撑位，跌破可能加速下跌。",
    "🔔 【涨停信号】首板封板时间越早越好，尾盘封板多为偷鸡，次日溢价有限。",
    "🏃 【短线纪律】买入后3天内不涨就是错误，该走要走，不要死扛。",
    "📊 【板块轮动】资金是逐利的，涨多了会跌，跌多了会涨，轮动是常态。",
    "💰 【复利效应】本金50万，每年翻一倍，10年后是5个亿。稳定复利才是王道。",
    "🎪 【仓位管理】永远不要满仓一只票，分散风险才能活得久。",
    "🔎 【基本面】技术面选股，基本面选时。基本面向上的股票，技术面配合更容易走牛。",
]

def send_message(message):
    """发送到飞书"""
    if not WEBHOOK_URL:
        print("❌ 未配置 STOCK_WEBHOOK_URL")
        return False
    
    cmd = [
        "curl", "-X", "POST", "-H", "Content-Type: application/json",
        "-d", json.dumps({"msg_type": "text", "content": {"text": message}}),
        WEBHOOK_URL
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return "success" in result.stdout

def get_market_summary():
    """获取收盘总结"""
    try:
        # 尝试直接读取复盘报告
        from pathlib import Path
        report_dir = Path("/home/jason/.openclaw/workspace/stock/reports/daily")
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        report_path = report_dir / f"report_{today}.txt"
        
        if report_path.exists():
            with open(report_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            # 如果没有报告，生成一个简单的总结
            return "今日暂无详细复盘报告"
    except Exception as e:
        return f"获取收盘总结失败: {e}"

def main():
    if len(sys.argv) < 2:
        print("用法: python stock_push.py [knowledge|summary]")
        sys.exit(1)
    
    mode = sys.argv[1]
    
    if mode == "knowledge":
        # 知识干货
        tip = random.choice(KNOWLEDGE_TIPS)
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        message = f"📚 【股票知识干货】{date}\n\n{tip}\n\n💡 每天进步一点点！"
        print(message)
        send_message(message)
        
    elif mode == "summary":
        # 收盘总结
        summary = get_market_summary()
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        message = f"📊 【收盘总结】{date}\n\n{summary}"
        print(message)
        send_message(message)
    
    else:
        print("未知模式:", mode)
        sys.exit(1)

if __name__ == "__main__":
    main()
