# 股票分析工具箱使用指南

> 金宝的股票分析系统 - 快速上手

---

## 📁 目录结构

```
stock/
├── knowledge_base/    # 知识库（学习用）
├── models/            # 分析模型（直接调用）
├── database/          # 数据库设计
├── data/              # 数据存储
├── scripts/           # 自动化脚本
└── docs/              # 文档
```

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install akshare pandas numpy
```

### 2. 获取股票数据

```python
import akshare as ak
import pandas as pd

# 获取日线数据
stock_df = ak.stock_zh_a_hist(
    symbol="000001",  # 平安银行
    period="daily",
    start_date="20250101",
    end_date="20250213"
)
print(stock_df.head())
```

### 3. 运行技术分析

```python
import sys
sys.path.append('stock/models')

from 技术指标模型 import calc_macd, calc_rsi

# 计算MACD
dif, dea, macd = calc_macd(stock_df['close'])
rsi = calc_rsi(stock_df['close'])

print(f"MACD: {macd.iloc[-1]:.4f}")
print(f"RSI: {rsi.iloc[-1]:.2f}")
```

### 4. 使用数据库

```bash
# 初始化数据库
sqlite3 stock_analysis.db < database/sql/00-init.sql

# 查看数据
sqlite3 stock_analysis.db "SELECT * FROM stocks LIMIT 5;"
```

---

## 📊 常用分析流程

### 流程一：选股分析

```
1. 获取股票池 → 2. 运行选股模型 → 3. 筛选结果 → 4. 人工复审
```

```python
from models.选股模型 import 均线多头排列选股, 量价齐升选股

# 均线多头排列
ma_signal = 均线多头排列选股(stock_df)

# 量价齐升
vol_signal = 量价齐升选股(stock_df)

if ma_signal and vol_signal:
    print("符合选股条件")
```

### 流程二：择时判断

```
1. 读取行情 → 2. 计算指标 → 3. 信号判断 → 4. 决策
```

```python
from models.择时模型 import 趋势跟随择时, 情绪择时

# 技术择时
tech_signal = 趋势跟随择时(stock_df)

# 情绪择时（需要额外数据）
emotion_signal = 情绪择时(vix=18, margin_balance=18000, turnover_rate=2.5)

print(f"技术信号: {tech_signal}")
print(f"情绪信号: {emotion_signal}")
```

### 流程三：回测验证

```
1. 定义策略 → 2. 历史数据 → 3. 运行回测 → 4. 评估指标
```

```python
from scripts.backtest import backtest

# 回测均线策略
result = backtest(
    data=stock_df,
    strategy='ma_cross',
    params={'short': 5, 'long': 20}
)

print(f"收益率: {result['total_return']:.2%}")
print(f"最大回撤: {result['max_drawdown']:.2%}")
print(f"夏普比率: {result['sharpe_ratio']:.2f}")
```

---

## 🔧 脚本使用

### 数据获取

```bash
# 每日收盘后运行
python scripts/get_daily_data.py

# 获取资金流向
python scripts/get_fundflow.py

# 更新市场情绪
python scripts/update_sentiment.py
```

### 分析报告

```bash
# 生成日报
python scripts/generate_report.py --type daily

# 生成周报
python scripts/generate_report.py --type weekly

# 生成选股报告
python scripts/generate_report.py --type stock_pick
```

---

## 📈 模型列表

| 模型 | 类型 | 适用场景 |
|------|------|---------|
| MACD | 技术指标 | 趋势判断、金叉死叉 |
| RSI | 技术指标 | 超买超卖 |
| KDJ | 技术指标 | 短线交易 |
| 布林带 | 技术指标 | 震荡、突破 |
| 均线多头 | 选股 | 中线趋势股 |
| 量价齐升 | 选股 | 强势股 |
| 趋势跟随 | 择时 | 中线操作 |
| 情绪择时 | 择时 | 大方向判断 |

---

## 💾 数据源

| 数据 | 来源 | 更新频率 |
|------|------|---------|
| 股票行情 | akshare | 每日 |
| 资金流向 | 东方财富 | 每日 |
| 龙虎榜 | 同花顺 | 每日 |
| 市场情绪 | 聚合 | 每日 |

---

## ⚠️ 风险提示

1. **模型仅供参考** - 不构成投资建议
2. **历史业绩不代表未来**
3. **请控制仓位、设止损**
4. **盈亏自负**

---

## 📝 更新日志

- 2026-02-13: 初始化系统
- 添加技术指标模型
- 添加选股/择时模型
- 完成数据库设计
