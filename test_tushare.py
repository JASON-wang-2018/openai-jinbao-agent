#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tushare as ts
import pandas as pd

def test_tushare_connection():
    """测试tushare连接"""
    print("🔗 测试tushare连接...")
    
    # 设置token
    token = "4bbf1cb7035329312ffd8404ba1488e1150654f1b4437a7eb6b882b8"
    ts.set_token(token)
    
    # 初始化pro接口
    pro = ts.pro_api()
    
    try:
        # 测试获取股票数据 - 获取上证指数数据
        print("📊 获取上证指数数据...")
        df = pro.index_daily(ts_code='000001.SH', start_date='20240101', end_date='20240131')
        
        if not df.empty:
            print("✅ 连接成功！")
            print(f"📈 获取到 {len(df)} 条数据")
            print("📋 数据预览：")
            print(df.head())
            
            # 保存数据到CSV
            df.to_csv('shanghai_index_data.csv', index=False)
            print(f"💾 数据已保存到: shanghai_index_data.csv")
            
            return True
        else:
            print("⚠️ 获取数据为空")
            return False
            
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False

if __name__ == "__main__":
    test_tushare_connection()