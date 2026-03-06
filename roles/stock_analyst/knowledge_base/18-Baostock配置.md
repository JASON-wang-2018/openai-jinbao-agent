# Baostock数据源配置

> Baostock是另一个开源的证券数据接口，与AKShare互补。

---

## 一、安装与配置

### 1.1 安装Baostock

```bash
pip install baostock -U
```

### 1.2 基本使用

```python
import baostock as bs
import pandas as pd

# 登录
lg = bs.login()

# 显示登录信息
print('login respond error_code: ' + lg.error_code)
print('login respond error_msg: ' + lg.error_msg)

# 获取数据后退出
bs.logout()
```

---

## 二、常用数据接口

### 2.1 股票基础信息

```python
import baostock as bs

# 登录
lg = bs.login()
print(lg.error_msg)

# 获取股票列表
rs = bs.query_stock_list()
print('query_stock_list respond error_code:' + rs.error_code)
print('query_stock_list respond error_msg:' + rs.error_msg)

# 转换为DataFrame
data_list = []
while (rs.error_code == '0') & rs.next():
    data_list.append(rs.get_row_data())
df = pd.DataFrame(data_list, columns=rs.fields)
print(df)

# 退出
bs.logout()
```

### 2.2 股票历史数据

```python
import baostock as bs
import pandas as pd

# 登录
lg = bs.login()

# 获取日线数据
rs = bs.query_history_k_data_plus(
    "sh.600000",    # 股票代码
    "date,code,open,high,low,close,volume,amount",  # 字段
    start_date='2024-01-01',
    end_date='2024-06-30',
    frequency="d",   # 日线
    adjustflag="2"   # 前复权
)

# 转换为DataFrame
data_list = []
while (rs.error_code == '0') & rs.next():
    data_list.append(rs.get_row_data())
df = pd.DataFrame(data_list, columns=rs.fields)
print(df)

# 退出
bs.logout()
```

### 2.3 复权因子

```python
# 获取复权因子
rs = bs.query_adjust_factor(code="sh.600000", start_date='2024-01-01', end_date='2024-06-30')
```

### 2.4 财务数据

```python
# 季频盈利能力
rs = bs.query_profit_data(code="sh.600000", year=2023, quarter=4)

# 季频成长能力
rs = bs.query_growth_data(code="sh.600000", year=2023, quarter=4)

# 季频偿债能力
rs = bs.query_debtpay_data(code="sh.600000", year=2023, quarter=4)

# 季频现金流
rs = bs.query_cashflow_data(code="sh.600000", year=2023, quarter=4)
```

### 2.5 季频估值指标

```python
rs = bs.query_valuation_data(code="sh.600000", year=2023, quarter=4)
```

---

## 三、AKShare与Baostock对比

| 对比项 | AKShare | Baostock |
|--------|---------|----------|
| 安装 | pip install akshare | pip install baostock |
| 登录 | 无需登录 | 需要login/logout |
| 更新频率 | 实时/日频 | 盘后更新 |
| 数据质量 | 较好 | 很好 |
| 接口数量 | 多 | 较少 |
| 文档 | 完善 | 一般 |
| 免费 | 是 | 是 |
| 商业使用 | 建议咨询 | 建议咨询 |

---

## 四、最佳使用方式

```python
"""
建议：
1. 日常数据：AKShare（更新快）
2. 财务数据：Baostock（质量高）
3. 量化因子：两者结合
"""

import akshare as ak
import baostock pandas as pd

 as bs
importclass StockDataSystem:
    """股票数据系统"""
    
    def __init__(self):
        pass
    
    def get_realtime(self, code):
        """实时数据 - 用AKShare"""
        try:
            df = ak.stock_zh_a_spot_em()
            return df[df['代码'] == code]
        except:
            return None
    
    def get_history(self, code, start, end):
        """历史数据 - AKShare"""
        try:
            df = ak.stock_zh_a_hist(
                symbol=code,
                period="daily",
                start_date=start,
                end_date=end,
                adjust="qfq"
            )
            return df
        except:
            return None
    
    def get_fundament(self, code, year, quarter):
        """财务数据 - 用Baostock"""
        bs.login()
        try:
            rs = bs.query_profit_data(code=code, year=year, quarter=quarter)
            data_list = []
            while (rs.error_code == '0') & rs.next():
                data_list.append(rs.get_row_data())
            return pd.DataFrame(data_list, columns=rs.fields)
        finally:
            bs.logout()
    
    def get_valuation(self, code):
        """估值数据 - Baostock"""
        bs.login()
        try:
            rs = bs.query_valuation_data(code=code)
            data_list = []
            while (rs.error_code == '0') & rs.next():
                data_list.append(rs.get_row_data())
            return pd.DataFrame(data_list, columns=rs.fields)
        finally:
            bs.logout()
```

---

## 五、数据字段说明

### 5.1 日线数据字段

| 字段 | 含义 |
|------|------|
| date | 日期 |
| code | 股票代码 |
| open | 开盘价 |
| high | 最高价 |
| low | 最低价 |
| close | 收盘价 |
| volume | 成交量 |
| amount | 成交额 |
| adjustflag | 复权类型 |

### 5.2 财务数据字段

| 字段 | 含义 |
|------|------|
| roe | 净资产收益率 |
| netprofit_margin | 净利率 |
| grossprofit_margin | 毛利率 |
| netprofit_ratio | 净利润率 |
| operationprofit_ratio | 营业利润率 |
| eps | 每股收益 |
| bvps | 每股净资产 |

---

## 六、常见问题

### Q1: Baostock登录失败

```python
# 检查网络连接
# 多次尝试登录
import baostock as bs
for i in range(3):
    lg = bs.login()
    if lg.error_code == '0':
        print("登录成功")
        break
```

### Q2: 数据延迟

```python
# Baostock数据是盘后更新的
# 实时数据用AKShare
# 历史数据用Baostock
```

### Q3: 数据格式

```python
# 转换为数值类型
df['close'] = pd.to_numeric(df['close'], errors='coerce')
```

---

## 七、学习资源

- 官方文档: http://baostock.com/baostock/index
- GitHub: https://github.com/finmind/baostock
- QQ群: 531253136
