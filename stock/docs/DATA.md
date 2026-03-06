# 中国股票实时交易数据信息库

> 金宝的股票数据系统 - 支持 AKShare / BaoStock

---

## 📁 数据目录

```
data/
├── stock_analysis.db       # SQLite主数据库
├── raw/daily/              # 日线原始数据
│   └── stock_list.csv     # 股票列表
├── raw/fundflow/           # 资金流向数据
│   └── fundflow_YYYY-MM-DD.csv
└── raw/market/             # 市场情绪数据
```

## 📊 数据库表结构

| 表名 | 说明 | 更新频率 |
|------|------|---------|
| stocks | 股票基础信息 | 每日 |
| daily_data | 日线行情 | 每日 |
| fund_flow | 资金流向 | 每日 |
| market_sentiment | 市场情绪 | 每日 |
| sectors | 板块信息 | 每日 |
| sector_daily | 板块行情 | 每日 |
| top_list | 龙虎榜 | 每日 |
| margin_data | 两融数据 | 每日 |
| analysis_results | 分析结果 | 手动 |
| trades | 交易记录 | 手动 |
| positions | 持仓管理 | 手动 |

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install akshare baostock requests beautifulsoup4 lxml pandas numpy
```

### 2. 初始化数据

```bash
# 获取股票列表
python scripts/stock_data_manager.py --mode stock

# 全量更新（首次运行）
python scripts/stock_data_manager.py --mode all --days 90

# 每日更新
python scripts/stock_data_manager.py --mode daily
```

### 3. 查询数据

```python
from scripts.stock_data_utils import StockDataUtils

utils = StockDataUtils()

# 获取股票列表
stocks = utils.get_stock_list()

# 获取个股行情
df = utils.get_stock_price('000001', days=30)

# 技术信号
signal = utils.get_technical_signal('000001')

# 涨幅榜
rising = utils.get_rising_stocks(5)
```

---

## 📈 数据获取命令

| 命令 | 功能 |
|------|------|
| `--mode stock` | 获取股票列表 |
| `--mode daily` | 每日更新（资金/情绪/龙虎榜） |
| `--mode all` | 全量更新 |
| `--mode fundflow` | 资金流向 |
| `--mode market` | 市场情绪 |
| `--mode lhb` | 龙虎榜 |
| `--mode sector` | 板块数据 |
| `--days N` | 指定天数（默认30） |
| `--symbol 000001` | 指定股票 |

### 示例

```bash
# 获取近90天数据（AKShare）
python scripts/stock_data_manager.py --mode all --days 90

# 新浪财经获取实时行情
python scripts/stock_data_web.py --source sina --action quote --symbol 000001

# 东方财富获取K线
python scripts/stock_data_web.py --source eastmoney --action kline --symbol 000001

# 腾讯财经获取实时报价
python scripts/stock_data_web.py --source tencent --action quote --symbol 600000

# 获取市场热点（东方财富）
python scripts/stock_data_web.py --source eastmoney --action hot
```

---

## 📊 常用分析

### 筛选股票

```python
# 低PE股票
utils.filter_by_pe(low=0, high=15)

# 高换手率
utils.filter_by_turnover(min_rate=3)

# 今日涨幅>5%
utils.filter_by_change(min_change=5, max_change=100)
```

### 排行榜

```python
# 5日涨幅榜
utils.get_rising_stocks(days=5, limit=20)

# 3日资金流入榜
utils.get_fundflow_leaders(days=3, limit=20)
```

### 技术分析

```python
# 技术面信号
signal = utils.get_technical_signal('000001')
# 返回: 趋势、均线排列、5日/20日涨跌幅

# 计算均线
ma = utils.calc_ma('000001', periods=[5,10,20,60])
```

---

## 🔧 数据源配置

### AKShare（默认）

```python
import akshare as ak
df = ak.stock_zh_a_hist(symbol="000001", ...)
```

特点：
- 无需注册
- 稳定可靠
- 适合日常使用

### 网页数据源（新增）

```bash
# 新浪财经实时行情
python scripts/stock_data_web.py --source sina --action quote

# 东方财富K线数据
python scripts/stock_data_web.py --source eastmoney --action kline --symbol 000001

# 腾讯财经实时行情
python scripts/stock_data_web.py --source tencent --action quote --symbol 600000
```

| 数据源 | 特点 | 支持数据 |
|-------|------|---------|
| 新浪财经 | 实时性强 | 实时行情、所属板块 |
| 东方财富 | 数据全面 | 股票列表、K线、资金流向、热点 |
| 腾讯财经 | 实时行情 | 实时报价 |

```python
# 直接调用
from scripts.stock_data_web import SinaFinance, EastMoney, TencentFinance

# 新浪实时行情
quote = SinaFinance.get_stock_quote('000001')

# 东方财富K线
df = EastMoney.get_daily_kline('000001', days=250)

# 腾讯实时行情
quote = TencentFinance.get_stock_quote('600000')
```

### BaoStock

```python
import baostock as bs
lg = bs.login()
rs = bs.query_history_k_data_plus(...)
```

特点：
- 历史数据更完整
- 适合回测
- 需登录

---

## 📡 网页数据源使用

### 新浪财经

```python
from scripts.stock_data_web import SinaFinance

# 实时行情
quote = SinaFinance.get_stock_quote('000001')
print(f"当前价: {quote['close']}, 涨跌: {quote['pct_chg']}%")

# 所属板块
plates = SinaFinance.get_plate_data('000001')
print(f"板块: {plates}")
```

### 东方财富

```python
from scripts.stock_data_web import EastMoney

# K线数据
df = EastMoney.get_daily_kline('000001', days=250)
print(df.head())

# 资金流向
flow_data = EastMoney.get_fund_flow('000001')

# 市场热点
hot_df = EastMoney.get_market_hot()
print(hot_df.head())
```

### 腾讯财经

```python
from scripts.stock_data_web import TencentFinance

# 实时报价
quote = TencentFinance.get_stock_quote('600000')
print(f"最新价: {quote['close']}, 涨跌幅: {quote['pct_chg']}%")
```

---

## ⚠️ 注意事项

1. **请求频率**：避免过高请求，脚本已内置延迟
2. **数据完整性**：首次全量更新可能需要数小时
3. **实时性**：数据为收盘后更新，非真正实时
4. **历史范围**：从2025-01-01至今

---

## 📝 更新日志

- 2026-02-13: 初始化数据系统
- 支持AKShare/BaoStock双数据源
- 添加资金流向、市场情绪、龙虎榜
- 添加数据查询工具类
