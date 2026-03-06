#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Baostock 数据获取测试
"""

import sys

def get_market_data():
    """获取市场数据"""
    try:
        import baostock as bs
        
        # 登录
        lg = bs.login()
        print(f"登录: {lg.error_msg}")
        
        if lg.error_code != '0':
            return None
        
        # 获取上证指数 - 使用更简单的查询
        print("\n获取上证指数...")
        rs = bs.query_history_k_data_plus(
            "sh.000001",
            "date,code,open,high,low,close,volume,amount",
            start_date='2026-02-13',
            end_date='2026-02-14',
            frequency="d",
            adjustflag="2"
        )
        
        data_list = []
        while (rs.error_code == '0') & rs.next():
            data_list.append(rs.get_row_data())
            print(f"获取到数据: {data_list[-1]}")
        
        if not data_list:
            print("无数据")
        
        # 登出
        bs.logout()
        return data_list
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    print("=" * 60)
    print("Baostock 测试")
    print("=" * 60)
    get_market_data()
