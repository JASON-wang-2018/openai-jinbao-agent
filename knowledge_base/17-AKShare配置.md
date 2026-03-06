# AKShare数据源配置

> AKShare是Python开源财经数据接口，是目前最好用的A股数据获取工具。

---

## 一、安装与配置

### 1.1 安装AKShare

```bash
pip install akshare -U
```

### 1.2 基本使用

```python
import akshare as ak

# 查看版本
print(ak.__version__)
```

---

## 二、常用数据接口

### 2.1 大盘指数

```python
import akshare as ak

# 上证指数实时行情
sh = ak.stock_zh_index_spot_em(symbol="sh000001")
print(sh)

# 获取字段：
# 最新价、涨跌幅、涨跌额、成交量、成交额等
```

### 2.2 个股行情

```python
# 个股历史数据
stock_df = ak.stock_zh_a_hist(
    symbol="000001",      # 股票代码
    period="daily",       # 日线
    start_date="20230101", 
    end_date="20231231",
    adjust="qfq"          # 前复权
)

# 实时行情
stock_quote = ak.stock_zh_a_spot_em()
print(stock_quote.head())
```

### 2.3 财务数据

```python
# 财务报表
income = ak.stock_income_statement_new(symbol="000001")  # 利润表
balance = ak.stock_balance_sheet_new(symbol="000001")     # 资产负债表
cashflow = ak.stock_cashflow_statement_new(symbol="000001")  # 现金流量表

# 财务指标
indicator = ak.stock_indicator(symbol="000001")
print(indicator)
```

### 2.4 资金流向

```python
# 主力资金
money_flow = ak.stock_market_fund_flow(symbol="000001")

# 北向资金
north_money = ak.stock_hsgt_north_a_hist(symbol="sh000001")

# 沪深港通
hsgt = ak.stock_hsgt_top10(symbol="sh000001")
```

### 2.5 龙虎榜

```python
# 每日龙虎榜
lion_list = ak.stock_em_lg_jg(symbol="sh000001")

# 龙虎榜详情
lion_detail = ak.stock_em_lg_jg_detail(symbol="000001")
```

### 2.6 涨跌停

```python
# 涨跌停数据
limit_list = ak.stock_em_analyst()
print(limit_list[limit_list['涨跌幅'] >= 9.5])  # 涨停股
```

---

## 三、板块数据

### 3.1 行业板块

```python
# 行业板块
industry = ak.stock_board_industry_name_em()

# 行业板块行情
industry_cons = ak.stock_board_industry_cons_em(symbol="BK0001")  # 券商
```

### 3.2 概念板块

```python
# 概念板块
concept = ak.stock_board_concept_name_em()

# 概念板块成员
concept_detail = ak.stock_board_concept_detail_em(symbol="BK0801")  # AI
```

### 3.3 热点板块

```python
# 热点板块排行
hot_sector = ak.stock_em_hsgt_new()
print(hot_sector.head(10))
```

---

## 四、量化因子

### 4.1 技术指标

```python
# MACD
macd = ak.stock_zh_macd(symbol="000001", adjust="qfq")

# KDJ
kdj = ak.stock_zh_kdj(symbol="000001", adjust="qfq")

# RSI
rsi = ak.stock_zh_rsi(symbol="000001", adjust="qfq")
```

### 4.2 估值指标

```python
# PE、PB
pe_pb = ak.stock_a_indicator_lg(symbol="000001")

# 基本面
fundament = ak.stock_fundament(symbol="000001")
```

---

## 五、数据保存示例

```python
import akshare as ak
import pandas as pd
from datetime import datetime

def save_stock_data(stock_code, start_date, end_date):
    """保存股票数据"""
    
    # 获取日线数据
    df = ak.stock_zh_a_hist(
        symbol=stock_code,
        period="daily",
        start_date=start_date,
        end_date=end_date,
        adjust="qfq"
    )
    
    # 保存
    filename = f"data/{stock_code}.csv"
    df.to_csv(filename, index=False)
    
    print(f"{stock_code} 数据已保存: {filename}")
    return df

# 使用
df = save_stock_data("000001", "20240101", "20240630")
```

---

## 六、常见问题

### Q1: 数据获取失败

```python
# 解决方案：
# 1. 检查网络
# 2. 添加超时
# 3. 添加重试
import time

def get_with_retry(func, max_retry=3):
    for i in range(max_retry):
        try:
            return func()
        except Exception as e:
            print(f"第{i+1}次失败: {e}")
            time.sleep(2)
    return None
```

### Q2: 数据更新延迟

```python
# AKShare数据有一定延迟
# 实时数据：延迟约1-5分钟
# 财务数据：财报公布后1-2天更新
```

### Q3: 复权问题

```python
# adjust参数：
# "qfq" = 前复权（推荐）
# "hfq" = 后复权
# "" = 不复权
```

---

## 七、最佳实践

```python
"""
数据获取最佳实践：
1. 设置合理超时
2. 添加错误处理
3. 定期更新数据
4. 保存原始数据
5. 本地缓存
"""

import akshare as ak
import pandas as pd
import os

class StockData:
    def __init__(self, cache_dir="cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def get_history(self, code, start, end):
        """获取历史数据"""
        cache_file = f"{self.cache_dir}/{code}.csv"
        
        # 检查缓存
        if os.path.exists(cache_file):
            df = pd.read_csv(cache_file)
            df['日期'] = pd.to_datetime(df['日期'])
            return df
        
        # 获取新数据
        df = ak.stock_zh_a_hist(
            symbol=code,
            period="daily",
            start_date=start,
            end_date=end,
            adjust="qfq"
        )
        
        # 保存缓存
        df.to_csv(cache_file, index=False)
        return df
```

---

## 八、接口速查

| 数据类型 | 接口 | 常用字段 |
|---------|------|---------|
| 实时行情 | stock_zh_a_spot_em() | 代码、名称、现价、涨跌幅 |
| 涨跌幅榜 | stock_zh_a_lg_fh_sct() | 代码、涨跌幅、成交量 |
| 资金流向 | stock_market_fund_flow() | 净流入、流入额 |
| 龙虎榜 | stock_em_lg_jg() | 代码、买入营业部 |
| 北向资金 | stock_hsgt_north_a_hist() | 净流入、成交额 |
| 融资融券 | stock_margin_sse() | 融资余额、融券余额 |
| 新股申购 | stock_ipo_speculative() | 发行价、中签率 |

---

## 九、学习资源

- 官方文档: https://akfamily.readthedocs.io
- GitHub: https://github.com/akfamily/akshare
- 教程: https://www.akshare.xyz
