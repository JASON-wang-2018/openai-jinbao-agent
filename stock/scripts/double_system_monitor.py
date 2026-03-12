#!/usr/bin/env python3
"""
双系统股票监控脚本
每30分钟扫描市场，符合双系统条件的股票推送到飞书群
"""
import baostock as bs
import pandas as pd
from datetime import datetime, timedelta
import json
import os

# 缓存文件
CACHE_FILE = "/home/jason/.openclaw/workspace/stock/data/double_system_cache.json"
LOG_FILE = "/home/jason/.openclaw/workspace/logs/double_system_monitor.log"

def log(msg):
    """日志"""
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, 'a') as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {msg}\n")

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

def login_bs():
    """登录Baostock"""
    lg = bs.login()
    if lg.error_code != '0':
        log(f"登录失败: {lg.error_msg}")
        return None
    return True

def get_index_data():
    """获取指数数据"""
    # 获取上证指数
    rs = bs.query_history_k_data_plus(
        "sh.000001",
        "date,code,open,high,low,close,volume,amount",
        start_date=(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
        end_date=datetime.now().strftime('%Y-%m-%d'),
        frequency="d"
    )
    
    data = []
    while rs.next():
        data.append(rs.get_row_data())
    df = pd.DataFrame(data, columns=rs.fields)
    
    for col in ['open', 'high', 'low', 'close', 'volume']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df

def check_double_system(df):
    """检查双系统条件"""
    if len(df) < 20:
        return None, "数据不足"
    
    latest = df.iloc[-1]
    prev = df.iloc[-1]
    
    # 计算均线
    df['MA10'] = df['close'].rolling(10).mean()
    df['MA20'] = df['close'].rolling(20).mean()
    df['MA60'] = df['close'].rolling(60).mean()
    
    latest_ma10 = df['MA10'].iloc[-1]
    latest_ma20 = df['MA20'].iloc[-1]
    latest_ma60 = df['MA60'].iloc[-1]
    close = latest['close']
    
    # 主升系统条件
    signals = []
    
    # 1. 指数强趋势
    if latest_ma20 > latest_ma60 and close > latest_ma10:
        signals.append("指数强趋势")
    
    # 2. 计算涨跌幅
    if len(df) >= 5:
        pct5 = (df['close'].iloc[-1] - df['close'].iloc[-5]) / df['close'].iloc[-5] * 100
        if pct5 > 5:
            signals.append(f"5日涨幅{pct5:.1f}%")
    
    # 获取创业板指
    rs = bs.query_history_k_data_plus(
        "sz.399006",
        "date,close",
        start_date=(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
        end_date=datetime.now().strftime('%Y-%m-%d'),
        frequency="d"
    )
    
    cyb_data = []
    while rs.next():
        cyb_data.append(rs.get_row_data())
    
    if cyb_data:
        cyb_df = pd.DataFrame(cyb_data, columns=rs.fields)
        cyb_df['close'] = pd.to_numeric(cyb_df['close'], errors='coerce')
        cyb_df['MA20'] = cyb_df['close'].rolling(20).mean()
        
        if len(cyb_df) >= 20:
            cyb_ma20 = cyb_df['MA20'].iloc[-1]
            cyb_close = cyb_df['close'].iloc[-1]
            
            # 创业板强趋势
            if cyb_close > cyb_ma20:
                signals.append("创业板强趋势")
    
    return signals if signals else None, "无信号"

def get_limit_up_stocks():
    """获取涨停板股票"""
    # 获取当天涨停的股票（通过涨跌幅排序）
    rs = bs.query_history_k_data_plus(
        "sh.000001",
        "date,code,open,high,low,close,volume,amount,pctChg",
        start_date=datetime.now().strftime('%Y-%m-%d'),
        end_date=datetime.now().strftime('%Y-%m-%d'),
        frequency="d"
    )
    
    return []

def main():
    """主函数"""
    log("=== 双系统监控开始 ===")
    
    if not login_bs():
        return
    
    try:
        # 获取指数数据
        df = get_index_data()
        if df is None or len(df) == 0:
            log("获取数据失败")
            return
        
        # 检查双系统
        signals, status = check_double_system(df)
        
        log(f"状态: {status}, 信号: {signals}")
        
        # 获取缓存
        cache = get_cache()
        today = datetime.now().strftime('%Y-%m-%d')
        
        # 如果有信号且今天还没推送过
        if signals:
            if cache.get('last_signal_date') != today or cache.get('last_signals') != signals:
                # 发送通知
                msg = f"📊 双系统监控 {datetime.now().strftime('%H:%M')}\n\n"
                msg += f"状态: {status}\n"
                msg += f"信号: {', '.join(signals)}\n\n"
                msg += f"上证: {df['close'].iloc[-1]:.2f}\n"
                
                if len(df) >= 20:
                    msg += f"MA20: {df['MA20'].iloc[-1]:.2f}\n"
                    msg += f"MA60: {df['MA60'].iloc[-1]:.2f}\n"
                
                # 推送到飞书（使用已保存的群ID）
                send_to_feishu(msg)
                
                # 更新缓存
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
    finally:
        bs.logout()

def send_to_feishu(msg):
    """发送到飞书"""
    try:
        import subprocess
        # 使用 openclaw message 发送到群
        cmd = [
            "openclaw", "message", "send",
            "--channel", "feishu", 
            "--target", "chat:oc_f84f0158693c8887be1bac624f143805"
            "--message", msg
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            log("飞书消息发送成功")
        else:
            log(f"飞书消息发送失败: {result.stderr}")
    except Exception as e:
        log(f"发送飞书出错: {e}")

if __name__ == "__main__":
    main()
