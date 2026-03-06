# 股票分析数据库设计

> 金宝的股票分析数据存储方案

---

## 📁 数据库结构

```
database/
├── schema.md              # 数据库设计文档
└── sql/
    ├── 00-init.sql        # 初始化脚本
    ├── 01-stocks.sql      # 股票基础表
    ├── 02-daily.sql       # 日线数据表
    ├── 03-fundflow.sql    # 资金流向表
    ├── 04-news.sql        # 新闻公告表
    └── 05-analysis.sql    # 分析结果表
```

---

## 一、数据库选择

### 1.1 轻量级方案（推荐起步）
- **SQLite**：单文件，零配置
- **适合**：个人学习、策略回测

### 1.2 中等规模
- **MySQL/PostgreSQL**：关系型，支持复杂查询
- **适合**：多数据源、多策略

### 1.3 大规模数据
- **ClickHouse**：列式存储，OLAP优化
- **适合**：高频数据、实时分析

---

## 二、表结构设计

### 2.1 股票基础信息表 (stocks)

```sql
CREATE TABLE stocks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts_code VARCHAR(20) UNIQUE NOT NULL,      -- 股票代码（TS格式）
    symbol VARCHAR(10) UNIQUE NOT NULL,      -- 股票代码（6位）
    name VARCHAR(50) NOT NULL,               -- 股票名称
    area VARCHAR(20),                        -- 所在地域
    industry VARCHAR(50),                     -- 所属行业
    market VARCHAR(20),                      -- 市场类型（主板/创业板/科创板）
    list_date DATE,                          -- 上市日期
    delist_date DATE,                        -- 退市日期
    status VARCHAR(10) DEFAULT '正常',        -- 状态
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_stocks_symbol ON stocks(symbol);
CREATE INDEX idx_stocks_industry ON stocks(industry);
```

### 2.2 日线行情数据表 (daily_data)

```sql
CREATE TABLE daily_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts_code VARCHAR(20) NOT NULL,
    trade_date DATE NOT NULL,
    open DECIMAL(10, 2),
    high DECIMAL(10, 2),
    low DECIMAL(10, 2),
    close DECIMAL(10, 2),
    pre_close DECIMAL(10, 2),
    change DECIMAL(10, 2),
    pct_chg DECIMAL(10, 4),
    vol BIGINT,                               -- 成交量（手）
    amount DECIMAL(20, 4),                   -- 成交额（万元）
    adj_factor DECIMAL(20, 8),               -- 复权因子
    
    -- 技术指标缓存
    ma5 DECIMAL(10, 2),
    ma10 DECIMAL(10, 2),
    ma20 DECIMAL(10, 2),
    ma60 DECIMAL(10, 2),
    macd DECIMAL(10, 4),
    kdj_k DECIMAL(10, 4),
    kdj_d DECIMAL(10, 4),
    kdj_j DECIMAL(10, 4),
    rsi DECIMAL(10, 4),
    boll_upper DECIMAL(10, 2),
    boll_lower DECIMAL(10, 2),
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(ts_code, trade_date)
);

CREATE INDEX idx_daily_tscode ON daily_data(ts_code);
CREATE INDEX idx_daily_trade_date ON daily_data(trade_date);
CREATE INDEX idx_daily_pct_chg ON daily_data(pct_chg DESC);
```

### 2.3 资金流向表 (fund_flow)

```sql
CREATE TABLE fund_flow (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts_code VARCHAR(20) NOT NULL,
    trade_date DATE NOT NULL,
    
    -- 主力资金（万元）
    main_net_inflow DECIMAL(15, 2),
    main_buy DECIMAL(15, 2),
    main_sell DECIMAL(15, 2),
    
    -- 超大单
    super_net_inflow DECIMAL(15, 2),
    super_buy DECIMAL(15, 2),
    super_sell DECIMAL(15, 2),
    
    -- 大单
    large_net_inflow DECIMAL(15, 2),
    large_buy DECIMAL(15, 2),
    large_sell DECIMAL(15, 2),
    
    -- 中单
    medium_net_inflow DECIMAL(15, 2),
    
    -- 小单
    small_net_inflow DECIMAL(15, 2),
    
    -- 资金流向
    net_inflow_rate DECIMAL(10, 4),
    turnover_rate DECIMAL(10, 4),
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(ts_code, trade_date)
);

CREATE INDEX idx_fund_tscode ON fund_flow(ts_code);
CREATE INDEX idx_fund_trade_date ON fund_flow(trade_date);
```

### 2.4 市场情绪表 (market_sentiment)

```sql
CREATE TABLE market_sentiment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trade_date DATE UNIQUE NOT NULL,
    
    -- 指数数据
    sh_index DECIMAL(10, 2),          -- 上证指数
    sz_index DECIMAL(10, 2),          -- 深证成指
    cy_index DECIMAL(10, 2),          -- 创业板指
    ch_index DECIMAL(10, 2),          -- 科创50
    
    -- 成交量
    market_volume BIGINT,             -- 市场总成交量
    market_amount DECIMAL(20, 4),    -- 市场总成交额
    
    -- 涨跌统计
    up_count INTEGER,                 -- 上涨家数
    down_count INTEGER,               -- 下跌家数
    up_limit_count INTEGER,           -- 涨停家数
    down_limit_count INTEGER,         -- 跌停家数
    
    -- 情绪指标
    avg_turnover DECIMAL(10, 4),     -- 平均换手率
    market_sentiment_score INTEGER,  -- 情绪评分(0-100)
    
    -- 两融数据
    margin_balance DECIMAL(20, 2),   -- 融资余额
    securities_balance DECIMAL(20, 2),-- 融券余额
    margin_rate DECIMAL(10, 4),       -- 杠杆率
    
    -- 外资
    north_money DECIMAL(20, 2),      -- 北向资金净流入
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sentiment_date ON market_sentiment(trade_date);
```

### 2.5 板块数据表 (sectors)

```sql
CREATE TABLE sectors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sector_code VARCHAR(20) UNIQUE NOT NULL,
    sector_name VARCHAR(50) NOT NULL,
    parent_code VARCHAR(20),          -- 父板块代码
    level INTEGER,                     -- 层级(1/2/3)
    member_count INTEGER,              -- 成分股数量
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sector_daily (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sector_code VARCHAR(20) NOT NULL,
    trade_date DATE NOT NULL,
    open DECIMAL(10, 2),
    high DECIMAL(10, 2),
    low DECIMAL(10, 2),
    close DECIMAL(10, 2),
    pct_chg DECIMAL(10, 4),
    turnover_rate DECIMAL(10, 4),
    net_inflow DECIMAL(20, 2),         -- 板块净流入
    up_count INTEGER,                  -- 上涨家数
    down_count INTEGER,                -- 下跌家数
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(sector_code, trade_date)
);

CREATE INDEX idx_sector_tscode ON sector_daily(sector_code);
CREATE INDEX idx_sector_trade_date ON sector_daily(trade_date);
```

### 2.6 龙虎榜数据表 (top_list)

```sql
CREATE TABLE top_list (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts_code VARCHAR(20) NOT NULL,
    trade_date DATE NOT NULL,
    
    -- 买入营业部
    buyer营业部 VARCHAR(100),
    buyer_rank INTEGER,               -- 买入排名
    buyer_amount DECIMAL(15, 2),      -- 买入金额(万)
    buyer_count INTEGER,              -- 买入次数
    
    -- 卖出营业部
    seller营业部 VARCHAR(100),
    seller_rank INTEGER,              -- 卖出排名
    seller_amount DECIMAL(15, 2),    -- 卖出金额(万)
    
    -- 净买入
    net_amount DECIMAL(15, 2),       -- 净买入额
    
    -- 席位类型
    buyer_type VARCHAR(20),          -- 买入方类型
    seller_type VARCHAR(20),         -- 卖出方类型
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_toplist_tscode ON top_list(ts_code);
CREATE INDEX idx_toplist_trade_date ON top_list(trade_date);
```

### 2.7 分析结果表 (analysis_results)

```sql
CREATE TABLE analysis_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts_code VARCHAR(20) NOT NULL,
    trade_date DATE NOT NULL,
    
    -- 分析类型
    analysis_type VARCHAR(20),       -- '选股/择时/风控/策略'
    model_name VARCHAR(50),          -- 使用的模型名称
    
    -- 分析结果
    signal VARCHAR(20),              -- 信号('买入/卖出/持有')
    confidence DECIMAL(10, 4),      -- 置信度(0-1)
    score DECIMAL(10, 4),            -- 综合评分
    
    -- 指标数据（JSON存储）
    indicators TEXT,                 -- 关键指标JSON
    reason TEXT,                     -- 分析理由
    
    -- 后续跟踪
    status VARCHAR(10) DEFAULT '待验证',  -- 待验证/正确/错误
    pnl DECIMAL(10, 4),              -- 收益率
    hold_days INTEGER,               -- 持仓天数
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_analysis_tscode ON analysis_results(ts_code);
CREATE INDEX idx_analysis_date ON analysis_results(trade_date);
CREATE INDEX idx_analysis_type ON analysis_results(analysis_type);
```

### 2.8 交易记录表 (trades)

```sql
CREATE TABLE trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts_code VARCHAR(20) NOT NULL,
    trade_date DATE NOT NULL,
    
    -- 交易信息
    direction VARCHAR(10),           -- '买入/卖出'
    price DECIMAL(10, 2),
    quantity INTEGER,               -- 股数
    amount DECIMAL(15, 2),          -- 成交金额
    
    -- 策略关联
    strategy_id INTEGER,             -- 对应策略ID
    analysis_id INTEGER,            -- 对应分析ID
    
    -- 备注
    notes TEXT,
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_trades_tscode ON trades(ts_code);
CREATE INDEX idx_trades_date ON trades(trade_date);
```

### 2.9 持仓表 (positions)

```sql
CREATE TABLE positions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts_code VARCHAR(20) NOT NULL,
    
    -- 持仓信息
    quantity INTEGER NOT NULL,       -- 持股数量
    cost_price DECIMAL(10, 2),      -- 成本价
    current_price DECIMAL(10, 2),   -- 当前价
    market_value DECIMAL(15, 2),    -- 市值
    
    -- 盈亏
    profit_loss DECIMAL(15, 2),     -- 盈亏金额
    profit_rate DECIMAL(10, 4),     -- 盈亏比例
    
    -- 风控
    stop_loss_price DECIMAL(10, 2), -- 止损价
    target_price DECIMAL(10, 2),   -- 目标价
    
    -- 状态
    status VARCHAR(10) DEFAULT '持仓',  -- 持仓/清仓
    position_ratio DECIMAL(10, 4),  -- 仓位占比
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## 三、数据更新策略

### 3.1 更新频率

| 数据类型 | 更新频率 | 数据源 |
|---------|---------|--------|
| 股票基础信息 | 每日 | 交易所公告 |
| 日线行情 | 每日收盘后 | A股接口 |
| 资金流向 | 每日收盘后 | 东方财富 |
| 龙虎榜 | 每日收盘后 | 同花顺 |
| 市场情绪 | 每日收盘后 | 聚合数据 |
| 板块数据 | 每日收盘后 | 东方财富 |

### 3.2 数据清洗

- 处理停牌日期
- 处理复权因子
- 处理分红送股
- 处理停牌退市
