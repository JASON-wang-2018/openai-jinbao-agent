# 股票分析模型库

> 金宝的股票分析模型集合 - 可直接使用的策略代码

---

## 📁 模型分类

```
models/
├── 技术指标模型/     # MACD、RSI、KDJ、布林带等
├── 选股模型/         # 基本面选股、技术选股
├── 择时模型/         # 买入卖出时机判断
├── 组合模型/         # 多因子、资产配置
└── 情绪模型/         # 市场情绪、资金流向
```

---

## 📊 技术指标模型

### 1. MACD模型

```python
# 计算MACD
def calc_macd(close, fast=12, slow=26, signal=9):
    ema_fast = close.ewm(span=fast, adjust=False).mean()
    ema_slow = close.ewm(span=slow, adjust=False).mean()
    dif = ema_fast - ema_slow
    dea = dif.ewm(span=signal, adjust=False).mean()
    macd = 2 * (dif - dea)
    return dif, dea, macd

# 交易信号
def macd_signal(dif, dea):
    if dif.iloc[-1] > dea.iloc[-1] and dif.iloc[-2] <= dea.iloc[-2]:
        return "金叉-买入"
    elif dif.iloc[-1] < dea.iloc[-1] and dif.iloc[-2] >= dea.iloc[-2]:
        return "死叉-卖出"
    else:
        return "持有"
```

### 2. RSI模型

```python
# 计算RSI
def calc_rsi(close, period=14):
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# 交易信号
def rsi_signal(rsi):
    if rsi.iloc[-1] > 70:
        return "超买-可能回落"
    elif rsi.iloc[-1] < 30:
        return "超卖-可能反弹"
    else:
        return "中性"
```

### 3. 布林带模型

```python
# 计算布林带
def calc_bollinger(close, period=20, std_dev=2):
    middle = close.rolling(window=period).mean()
    std = close.rolling(window=period).std()
    upper = middle + (std_dev * std)
    lower = middle - (std_dev * std)
    return upper, middle, lower

# 交易信号
def boll_signal(close, upper, lower):
    if close.iloc[-1] > upper.iloc[-1]:
        return "突破上轨-超买"
    elif close.iloc[-1] < lower.iloc[-1]:
        return "跌破下轨-超卖"
    else:
        return "震荡区间内"
```

### 4. KDJ模型

```python
# 计算KDJ
def calc_kdj(high, low, close, n=9, m1=3, m2=3):
    lowest_low = low.rolling(window=n).min()
    highest_high = high.rolling(window=n).max()
    rsv = (close - lowest_low) / (highest_high - lowest_low) * 100
    k = rsv.ewm(alpha=1/m1, adjust=False).mean()
    d = k.ewm(alpha=1/m2, adjust=False).mean()
    j = 3 * k - 2 * d
    return k, d, j

# 交易信号
def kdj_signal(k, d, j):
    if k.iloc[-1] > d.iloc[-1] and k.iloc[-2] <= d.iloc[-2]:
        return "金叉-买入"
    elif k.iloc[-1] < d.iloc[-1] and k.iloc[-2] >= d.iloc[-2]:
        return "死叉-卖出"
    elif j.iloc[-1] > 100:
        return "超买-警惕"
    elif j.iloc[-1] < 0:
        return "超卖-机会"
    else:
        return "中性"
```

---

## 🎯 选股模型

### 1. 均线多头排列

```python
def ma多头排列选股(df, periods=[5, 10, 20, 60]):
    """选择均线多头排列的股票"""
    result = {}
    for period in periods:
        result[f'ma{period}'] = df['close'].rolling(period).mean()
    
    # 条件：短期均线 > 长期均线，且都在上升
    cond = all([
        result['ma5'] > result['ma10'],
        result['ma10'] > result['ma20'],
        result['ma20'] > result['ma60'],
        result['ma5'] > result['ma5'].shift(5),  # 5日均线在上升
    ])
    return cond
```

### 2. 量价齐升

```python
def 量价齐升选股(df, days=5):
    """量价关系选股"""
    volume_ma = df['volume'].rolling(days).mean()
    price_change = df['close'].pct_change(days)
    
    cond = all([
        df['volume'] > volume_ma * 1.5,  # 放量
        price_change > 0.05,             # 涨幅>5%
        df['close'] > df['close'].shift(1),  # 连涨
    ])
    return cond
```

### 3. 突破形态

```python
def 突破选股(df, lookback=20):
    """突破前期高点选股"""
    recent_high = df['high'].rolling(lookback).max().iloc[-1]
    current_close = df['close'].iloc[-1]
    
    cond = current_close > recent_high * 1.02  # 突破2%以上确认
    return cond
```

---

## ⏰ 择时模型

### 1. 趋势跟随

```python
def 趋势跟随择时(df, short=5, long=20):
    """均线金叉死叉择时"""
    ma_short = df['close'].rolling(short).mean()
    ma_long = df['close'].rolling(long).mean()
    
    # 当前状态
    golden = ma_short.iloc[-1] > ma_long.iloc[-1]
    # 前一状态
    golden_prev = ma_short.iloc[-2] > ma_long.iloc[-2]
    
    if golden and not golden_prev:
        return "买入信号-均线金叉"
    elif not golden and golden_prev:
        return "卖出信号-均线死叉"
    else:
        return "持有"
```

### 2. 情绪择时

```python
def 情绪择时(vix, margin_balance, turnover_rate):
    """综合情绪指标择时"""
    score = 0
    
    # VIX < 15 恐慌（买入机会）
    if vix < 15:
        score += 2
    elif vix > 30:
        score -= 2
    
    # 融资余额上升
    if margin_balance > 0:
        score += 1
    
    # 换手率适中
    if 1 < turnover_rate < 5:
        score += 1
    elif turnover_rate > 8:
        score -= 1
    
    # 综合信号
    if score >= 3:
        return "乐观-可加仓"
    elif score <= -2:
        return "悲观-宜减仓"
    else:
        return "中性-持仓观望"
```

---

## 📈 多因子模型

### 1. 价值因子

```python
def 价值因子选股(stocks):
    """PE、PB、股息率综合选股"""
    candidates = []
    for stock in stocks:
        if stock.pe < 20 and stock.pe > 0:
            if stock.pb < 3:
                if stock.dividend_yield > 2:
                    candidates.append(stock)
    return candidates
```

### 2. 成长因子

```python
def 成长因子选股(stocks):
    """营收、利润增长选股"""
    candidates = []
    for stock in stocks:
        if stock.revenue_growth > 20:
            if stock.profit_growth > 15:
                if stock.roe > 10:
                    candidates.append(stock)
    return candidates
```

### 3. 技术因子

```python
def 技术因子选股(stocks):
    """技术指标综合选股"""
    candidates = []
    for stock in stocks:
        if stock.rsi < 70:       # 不超买
            if stock.macd > 0:    # 上升趋势
                if stock.ma20 > stock.ma60:  # 中期上升
                    candidates.append(stock)
    return candidates
```

---

## 🔧 模型使用说明

### 1. 导入模型
```python
from models.技术指标模型 import calc_macd, calc_rsi
from models.选股模型 import 均线多头排列选股
```

### 2. 获取数据
```python
import akshare as ak
stock_df = ak.stock_zh_a_hist(symbol="000001", period="daily")
```

### 3. 运行模型
```python
dif, dea, macd = calc_macd(stock_df['close'])
signal = macd_signal(dif, dea)
print(signal)
```

---

## 📝 模型更新日志

- 2026-02-13: 初始化模型库框架
- 添加基础技术指标模型
- 添加选股模型模板
- 添加择时模型模板
