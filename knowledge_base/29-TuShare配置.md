# TuShare数据源配置

> TuShare是国内最专业的财经数据平台，数据质量高、更新及时。
> 需要注册使用，免费版有一定限制，付费版功能全面。

---

## 一、TuShare介绍

### 1.1 简介

```
TuShare - 专业的财经数据平台

特点：
├── 数据质量高
├── 更新及时
├── 接口丰富
├── 文档完善
├── 需要注册
├── 免费版有限制
└── 付费版功能全
```

### 1.2 官网

```
官网：https://tushare.pro
文档：https://tushare.pro/document
```

---

## 二、安装与配置

### 2.1 安装

```bash
# 安装
pip install tushare -U

# 或者使用清华源
pip install tushare -U -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 2.2 注册获取Token

```
步骤：
1. 访问 https://tushare.pro
2. 注册账号
3. 进入个人中心
4. 获取API Token
5. 设置到代码中
```

### 2.3 初始化

```python
import tushare as ts

# 初始化（使用你的Token）
pro = ts.pro_api('your_token_here')

# 测试连接
print(pro.query('trade_cal', start_date='20240101', end_date='20240131'))
```

---

## 三、常用数据接口

### 3.1 交易日历

```python
# 获取交易日历
df = pro.query('trade_cal', 
    start_date='20240101',
    end_date='20240131',
    is_open='1'  # 1=交易日, 0=非交易日
)
print(df)
```

### 3.2 股票列表

```python
# 获取所有A股
df = pro.query('stock_basic',
    exchange='',
    list_status='L',  # L=上市, D=退市, P=暂停上市
    fields='ts_code,symbol,name,area,industry,list_date'
)
print(df.head())
```

### 3.3 行情数据

```python
# 日线行情
df = pro.query('daily',
    ts_code='000001.SZ',
    start_date='20240101',
    end_date='20240131'
)
print(df)

# 字段说明：
# ts_code: 股票代码
# trade_date: 交易日期
# open: 开盘价
# high: 最高价
# low: 最低价
# close: 收盘价
# pre_close: 昨收价
# change: 涨跌额
# pct_chg: 涨跌幅
# vol: 成交量(手)
# amount: 成交额(千元)
```

### 3.4 分钟数据

```python
# 分钟数据（需要付费）
df = pro.query('min',
    ts_code='000001.SZ',
    start_time='20240102 09:30:00',
    end_time='20240102 15:00:00',
    freq='1min'  # 1min, 5min, 15min, 30min, 60min
)
```

### 3.5 复权数据

```python
# 后复权日线
df = pro.query('daily',
    ts_code='000001.SZ',
    start_date='20240101',
    end_date='20240131',
    adj='qfq'  # qfq=前复权, hfq=后复权, None=不复权
)
```

### 3.6 财务数据

```python
# 利润表
df = pro.query('income',
    ts_code='000001.SZ',
    start_date='20240101',
    end_date='20240131',
    report_type='1'  # 1=一季报, 2=中报, 3=三季报, 4=年报
)

# 资产负债表
df = pro.query('balance',
    ts_code='000001.SZ',
    start_date='20240101',
    end_date='20240131'
)

# 现金流量表
df = pro.query('cashflow',
    ts_code='000001.SZ',
    start_date='20240101',
    end_date='20240131'
)
```

### 3.7 财务指标

```python
# 财务指标
df = pro.query('fina_indicator',
    ts_code='000001.SZ',
    start_date='20240101',
    end_date='20240131'
)

# 字段：
# roe: 净资产收益率
# netprofit_margin: 净利率
# grossprofit_margin: 毛利率
# eps: 每股收益
# bvps: 每股净资产
# pe: 市盈率
# pb: 市净率
```

### 3.8 复因子数据

```python
# 估值指标
df = pro.query('daily_basic',
    ts_code='000001.SZ',
    start_date='20240101',
    end_date='20240131',
    fields='ts_code,trade_date,close,turnover_rate,pe,pb'
)
```

### 3.9 资金流向

```python
# 资金流向
df = pro.query('moneyflow_hsgt',
    ts_code='000001.SZ',
    start_date='20240101',
    end_date='20240131'
)

# 沪深港通
df = pro.query('hsgt_top10',
    ts_code='000001.SZ',
    start_date='20240101',
    end_date='20240131'
)
```

### 3.10 龙虎榜

```python
# 龙虎榜
df = pro.query('top_list',
    trade_date='20240102'
)

# 龙虎榜明细
df = pro.query('top_inst',
    trade_date='20240102',
    ts_code='000001.SZ'
)
```

### 3.11 涨跌停

```python
# 涨跌停
df = pro.query('limit_list',
    trade_date='20240102',
    limit_status='U'  # U=涨停, D=跌停
)
```

### 3.12 热点概念

```python
# 概念列表
df = pro.query('concept',
    fields='code,name'
)

# 概念详情
df = pro.query('concept_detail',
    code='C2022101'  # 概念代码
)

# 概念成员
df = pro.query('concept_member',
    ts_code='000001.SZ'
)
```

---

## 四、数据获取示例

### 4.1 批量获取多只股票

```python
import tushare as ts
import pandas as pd

pro = ts.pro_api('your_token')

# 股票列表
stocks = pro.query('stock_basic',
    exchange='',
    list_status='L',
    fields='ts_code,name'
)

# 批量获取日线
all_data = []
for i, row in stocks.iterrows():
    try:
        df = pro.query('daily',
            ts_code=row['ts_code'],
            start_date='20240101',
            end_date='20240131'
        )
        if len(df) > 0:
            df['name'] = row['name']
            all_data.append(df)
    except Exception as e:
        print(f"获取{row['ts_code']}失败: {e}")

# 合并数据
if all_data:
    result = pd.concat(all_data, ignore_index=True)
    result.to_csv('stock_data.csv', index=False)
```

### 4.2 获取大盘指数

```python
# 上证指数
sh = pro.query('daily',
    ts_code='000001.SH',
    start_date='20240101',
    end_date='20240131'
)

# 深证成指
sz = pro.query('daily',
    ts_code='399001.SZ',
    start_date='20240101',
    end_date='20240131'
)

# 创业板
cy = pro.query('daily',
    ts_code='399006.SZ',
    start_date='20240101',
    end_date='20240131'
)
```

### 4.3 实时数据（需要付费）

```python
# 需要开通实时行情权限
df = pro.query(' realtime',
    ts_code='000001.SZ'
)

# 字段：
# ts_code: 股票代码
# price: 当前价
# change: 涨跌额
# pct_chg: 涨跌幅
# vol: 成交量
# amount: 成交额
# time: 时间
```

---

## 五、积分与权限

### 5.1 积分说明

```
TuShare使用积分制：
├── 注册送100积分
├── 每日签到送积分
├── 邀请用户送积分
├── 社区贡献送积分
└── 充值购买积分

不同数据需要不同积分：
├── 基础行情：免费
├── 财务数据：需要积分
├── 分钟数据：需要较多积分
└── 实时数据：需要付费
```

### 5.2 常用积分获取

```python
# 签到（在网页端或APP）
# 1. 访问 https://tushare.pro
# 2. 点击签到
# 3. 每日可获得积分

# 邀请用户
# 1. 获取邀请链接
# 2. 分享给好友
# 3. 好友注册后获得积分
```

---

## 六、错误处理

### 6.1 常见错误

```python
import tushare as ts

pro = ts.pro_api('your_token')

try:
    df = pro.query('daily',
        ts_code='000001.SZ',
        start_date='20240101',
        end_date='20240131'
    )
    print(df)
except Exception as e:
    print(f"错误: {e}")
```

### 6.2 错误代码

| 错误码 | 说明 | 解决方案 |
|--------|------|---------|
| 40001 | Token无效 | 检查Token是否正确 |
| 40002 | 请求次数超限 | 升级积分 |
| 40003 | 无权限 | 开通相应权限 |
| 40004 | 参数错误 | 检查参数格式 |
| 40005 | 服务繁忙 | 稍后重试 |

---

## 七、数据保存

```python
import tushare as ts
import pandas as pd
from datetime import datetime

pro = ts.pro_api('your_token')

def save_daily_data(stocks, start_date, end_date):
    """保存日线数据"""
    all_data = []
    
    for code in stocks:
        try:
            df = pro.query('daily',
                ts_code=code,
                start_date=start_date,
                end_date=end_date
            )
            if len(df) > 0:
                df['save_time'] = datetime.now()
                all_data.append(df)
                print(f"保存{code}: {len(df)}条")
        except Exception as e:
            print(f"{code}失败: {e}")
    
    if all_data:
        result = pd.concat(all_data, ignore_index=True)
        filename = f"data/daily_{start_date}_{end_date}.csv"
        result.to_csv(filename, index=False)
        print(f"保存完成: {filename}")
        return result
    return None
```

---

## 八、AKShare vs TuShare vs Baostock对比

| 对比项 | AKShare | TuShare | Baostock |
|--------|---------|---------|----------|
| **费用** | 免费 | 积分制 | 免费 |
| **数据质量** | 较好 | 很好 | 很好 |
| **更新频率** | 实时 | 实时/盘后 | 盘后 |
| **接口数量** | 多 | 多 | 较少 |
| **文档** | 完善 | 非常完善 | 一般 |
| **使用门槛** | 低 | 中 | 低 |
| **商业使用** | 建议咨询 | 建议咨询 | 建议咨询 |

---

## 九、使用建议

```
使用建议：
1. 日常数据 → AKShare（免费、稳定）
2. 高质量数据 → TuShare（付费、稳定）
3. 历史数据 → Baostock（免费、稳定）
4. 实时数据 → 新浪/东方财富（免费）
5. 财务数据 → TuShare（质量高）
6. 批量数据 → 结合使用

最佳方案：
├── 实时数据：新浪/东方财富
├── 日线数据：AKShare + Baostock
├── 财务数据：TuShare
└── 研究数据：TuShare
```

---

## 十、完整示例代码

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TuShare数据获取示例
"""

import tushare as ts
import pandas as pd
from datetime import datetime

# 初始化（替换为你的Token）
TOKEN = 'your_token_here'
pro = ts.pro_api(TOKEN)

def get_index_data(ts_code, start_date, end_date):
    """获取指数数据"""
    try:
        df = pro.query('daily',
            ts_code=ts_code,
            start_date=start_date,
            end_date=end_date
        )
        return df
    except Exception as e:
        print(f"获取{ts_code}失败: {e}")
        return None

def get_market_overview():
    """获取市场概览"""
    indices = [
        ('000001.SH', '上证指数'),
        ('399001.SZ', '深证成指'),
        ('399006.SZ', '创业板指')
    ]
    
    result = {}
    today = datetime.now().strftime('%Y%m%d')
    
    for code, name in indices:
        df = get_index_data(code, today, today)
        if df is not None and len(df) > 0:
            result[name] = df.iloc[0]
    
    return result

def main():
    print("=" * 60)
    print("TuShare 数据获取测试")
    print("=" * 60)
    
    # 测试获取指数
    data = get_market_overview()
    
    if data:
        print("\n市场概览：")
        for name, row in data.items():
            change = row['pct_chg']
            sign = '+' if change >= 0 else ''
            print(f"{name}: {row['close']:.2f} ({sign}{change:.2f}%)")
    else:
        print("获取数据失败")
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    main()
```

---

## 十一、学习资源

```
官方资源：
├── 官网：https://tushare.pro
├── 文档：https://tushare.pro/document
├── 社区：https://tushare.pro/社区
├── 论坛：https://tushare.pro/forum
└── GitHub：https://github.com/tushare

使用教程：
├── 入门教程：https://tushare.pro/document/1
├── API文档：https://tushare.pro/document/2
├── 示例代码：https://tushare.pro/document/3
└── FAQ：https://tushare.pro/faq
```

---

## 十二、注意事项

```
注意事项：
1. Token不要泄露
2. 注意积分使用
3. 遵守使用条款
4. 商业使用需授权
5. 数据仅供参考
6. 投资有风险
```

---

## 十三、总结

```
TuShare总结：
1. 数据质量高
2. 更新及时
3. 接口丰富
4. 需要注册
5. 积分制
6. 适合专业用户
7. 适合研究分析
```

---

*TuShare，专业财经数据平台。*
