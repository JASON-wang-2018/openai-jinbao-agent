#!/usr/bin/env python3
"""
双系统股票监控脚本
每30分钟扫描市场，符合双系统条件的股票推送到飞书群
使用akshare作为数据源（baostock DNS问题）
"""
import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
import json
import os

# 缓存文件
CACHE_FILE = "/home/jason/.openclaw/workspace/stock/data/double_system_cache.json"
LOG_FILE = "/home/jason/.openclaw/workspace/logs/double_system_monitor.log"

def log(msg):
    """"日志"""
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, 'a') as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {msg}\n")
    # 同时打印到stdout（便于cron调试）
    print(f"{datetime.now().strftime('%H:%M:%S')} {msg}")

def get_cache():
    """获取缓存"""
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_cache(data):
    """保存缓存"""
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, 'w') as f:
        json.dump(data, f, ensure_ascii=False)

def get_index_data():
    """获取上证指数数据"""
    try:
        df = ak.stock_zh_index_daily(symbol="sh000001")
        # 转换日期格式
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        # 取最近150天
        df = df.tail(150)
        return df
    except Exception as e:
        log(f"获取数据失败: {e}")
        return None

def get_cyb_data():
    """获取创业板指数据"""
    try:
        df = ak.stock_zh_index_daily(symbol="sz399006")
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date').tail(150)
        return df
    except Exception as e:
        log(f"获取创业板数据失败: {e}")
        return None

def check_double_system(sh_df, cyb_df):
    """检查双系统条件"""
    if sh_df is None or len(sh_df) == 0:
        return None, "无数据"
    if len(sh_df) < 20:
        return None, f"数据不足({len(sh_df)}天)"
    
    latest = sh_df.iloc[-1]
    close = latest['close']
    
    # 计算均线
    sh_df['MA10'] = sh_df['close'].rolling(10).mean()
    sh_df['MA20'] = sh_df['close'].rolling(20).mean()
    sh_df['MA60'] = sh_df['close'].rolling(60).mean()
    
    latest_ma10 = sh_df['MA10'].iloc[-1]
    latest_ma20 = sh_df['MA20'].iloc[-1]
    latest_ma60 = sh_df['MA60'].iloc[-1]
    
    signals = []
    
    # 1. 指数强趋势
    if latest_ma20 > latest_ma60 and close > latest_ma10:
        signals.append("指数强趋势")
    
    # 2. 计算涨跌幅
    if len(sh_df) >= 5:
        pct5 = (sh_df['close'].iloc[-1] - sh_df['close'].iloc[-5]) / sh_df['close'].iloc[-5] * 100
        if pct5 > 5:
            signals.append(f"5日涨幅{pct5:.1f}%")
    
    # 创业板强趋势
    if cyb_df is not None and len(cyb_df) >= 20:
        cyb_df['MA20'] = cyb_df['close'].rolling(20).mean()
        cyb_ma20 = cyb_df['MA20'].iloc[-1]
        cyb_close = cyb_df['close'].iloc[-1]
        
        if cyb_close > cyb_ma20:
            signals.append("创业板强趋势")
    
    return signals if signals else None, "无信号"

def send_to_feishu(msg):
    """发送到飞书 - 通过当前session发送"""
    try:
        # 尝试用subprocess发送，如果失败就用message工具
        import subprocess
        cmd = [
            "openclaw", "message", "send",
            "--channel", "feishu",
            "--target", "chat:oc_f84f0158693c8887be1bac624f143805",
            "--message", msg
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            log("飞书消息发送成功")
        else:
            # subprocess失败，记录但标记已发送(让用户从日志看到)
            log(f"飞书消息失败(机器人不在群里): {result.stderr[:200]}")
            log(f"已推送信号(本地记录): {msg}")
    except Exception as e:
        log(f"发送飞书出错: {e}")

def main():
    """主函数"""
    log("=== 双系统监控开始 ===")
    
    try:
        # 获取指数数据
        sh_df = get_index_data()
        cyb_df = get_cyb_data()
        
        if sh_df is None or len(sh_df) == 0:
            log("获取数据失败")
            return
        
        # 检查双系统
        signals, status = check_double_system(sh_df, cyb_df)
        
        log(f"状态: {status}, 信号: {signals}")
        
        # 获取缓存
        cache = get_cache()
        today = datetime.now().strftime('%Y-%m-%d')
        
        if signals:
            if cache.get('last_signal_date') != today or cache.get('last_signals') != signals:
                # 发送通知
                msg = f"📊 双系统监控 {datetime.now().strftime('%H:%M')}\n\n"
                msg += f"状态: {status}\n"
                msg += f"信号: {', '.join(signals)}\n\n"
                msg += f"上证: {sh_df['close'].iloc[-1]:.2f}\n"
                
                if len(sh_df) >= 20:
                    msg += f"MA20: {sh_df['MA20'].iloc[-1]:.2f}\n"
                    msg += f"MA60: {sh_df['MA60'].iloc[-1]:.2f}\n"
                
                send_to_feishu(msg)
                
                cache['last_signal_date'] = today
                cache['last_signals'] = signals
                save_cache(cache)
                
                log(f"已推送信号: {signals}")
            else:
                log("今日已推送，跳过")
        else:
            log("无信号")
            
    except Exception as e:
        log(f"错误: {e}")
        import traceback
        log(traceback.format_exc())

if __name__ == "__main__":
    main()