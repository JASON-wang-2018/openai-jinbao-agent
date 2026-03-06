-- ============================================
-- 股票分析数据库初始化脚本
-- Database: SQLite (stock_analysis.db)
-- ============================================

-- 1. 股票基础信息表
CREATE TABLE IF NOT EXISTS stocks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts_code VARCHAR(20) UNIQUE NOT NULL,
    symbol VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(50) NOT NULL,
    area VARCHAR(20),
    industry VARCHAR(50),
    market VARCHAR(20),
    list_date DATE,
    delist_date DATE,
    status VARCHAR(10) DEFAULT '正常',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_stocks_symbol ON stocks(symbol);
CREATE INDEX IF NOT EXISTS idx_stocks_industry ON stocks(industry);

-- 2. 日线行情数据表
CREATE TABLE IF NOT EXISTS daily_data (
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
    vol BIGINT,
    amount DECIMAL(20, 4),
    adj_factor DECIMAL(20, 8),
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

CREATE INDEX IF NOT EXISTS idx_daily_tscode ON daily_data(ts_code);
CREATE INDEX IF NOT EXISTS idx_daily_trade_date ON daily_data(trade_date);
CREATE INDEX IF NOT EXISTS idx_daily_pct_chg ON daily_data(pct_chg DESC);

-- 3. 资金流向表
CREATE TABLE IF NOT EXISTS fund_flow (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts_code VARCHAR(20) NOT NULL,
    trade_date DATE NOT NULL,
    main_net_inflow DECIMAL(15, 2),
    main_buy DECIMAL(15, 2),
    main_sell DECIMAL(15, 2),
    super_net_inflow DECIMAL(15, 2),
    large_net_inflow DECIMAL(15, 2),
    medium_net_inflow DECIMAL(15, 2),
    small_net_inflow DECIMAL(15, 2),
    net_inflow_rate DECIMAL(10, 4),
    turnover_rate DECIMAL(10, 4),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(ts_code, trade_date)
);

CREATE INDEX IF NOT EXISTS idx_fund_tscode ON fund_flow(ts_code);
CREATE INDEX IF NOT EXISTS idx_fund_trade_date ON fund_flow(trade_date);

-- 4. 市场情绪表
CREATE TABLE IF NOT EXISTS market_sentiment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trade_date DATE UNIQUE NOT NULL,
    sh_index DECIMAL(10, 2),
    sz_index DECIMAL(10, 2),
    cy_index DECIMAL(10, 2),
    market_volume BIGINT,
    market_amount DECIMAL(20, 4),
    up_count INTEGER,
    down_count INTEGER,
    up_limit_count INTEGER,
    down_limit_count INTEGER,
    avg_turnover DECIMAL(10, 4),
    market_sentiment_score INTEGER,
    margin_balance DECIMAL(20, 2),
    north_money DECIMAL(20, 2),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_sentiment_date ON market_sentiment(trade_date);

-- 5. 板块数据表
CREATE TABLE IF NOT EXISTS sectors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sector_code VARCHAR(20) UNIQUE NOT NULL,
    sector_name VARCHAR(50) NOT NULL,
    parent_code VARCHAR(20),
    level INTEGER,
    member_count INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sector_daily (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sector_code VARCHAR(20) NOT NULL,
    trade_date DATE NOT NULL,
    open DECIMAL(10, 2),
    high DECIMAL(10, 2),
    low DECIMAL(10, 2),
    close DECIMAL(10, 2),
    pct_chg DECIMAL(10, 4),
    turnover_rate DECIMAL(10, 4),
    net_inflow DECIMAL(20, 2),
    up_count INTEGER,
    down_count INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(sector_code, trade_date)
);

CREATE INDEX IF NOT EXISTS idx_sector_tscode ON sector_daily(sector_code);
CREATE INDEX IF NOT EXISTS idx_sector_trade_date ON sector_daily(trade_date);

-- 6. 分析结果表
CREATE TABLE IF NOT EXISTS analysis_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts_code VARCHAR(20) NOT NULL,
    trade_date DATE NOT NULL,
    analysis_type VARCHAR(20),
    model_name VARCHAR(50),
    signal VARCHAR(20),
    confidence DECIMAL(10, 4),
    score DECIMAL(10, 4),
    indicators TEXT,
    reason TEXT,
    status VARCHAR(10) DEFAULT '待验证',
    pnl DECIMAL(10, 4),
    hold_days INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_analysis_tscode ON analysis_results(ts_code);
CREATE INDEX IF NOT EXISTS idx_analysis_date ON analysis_results(trade_date);
CREATE INDEX IF NOT EXISTS idx_analysis_type ON analysis_results(analysis_type);

-- 7. 交易记录表
CREATE TABLE IF NOT EXISTS trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts_code VARCHAR(20) NOT NULL,
    trade_date DATE NOT NULL,
    direction VARCHAR(10),
    price DECIMAL(10, 2),
    quantity INTEGER,
    amount DECIMAL(15, 2),
    strategy_id INTEGER,
    analysis_id INTEGER,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_trades_tscode ON trades(ts_code);
CREATE INDEX IF NOT EXISTS idx_trades_date ON trades(trade_date);

-- 8. 持仓表
CREATE TABLE IF NOT EXISTS positions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts_code VARCHAR(20) NOT NULL,
    quantity INTEGER NOT NULL,
    cost_price DECIMAL(10, 2),
    current_price DECIMAL(10, 2),
    market_value DECIMAL(15, 2),
    profit_loss DECIMAL(15, 2),
    profit_rate DECIMAL(10, 4),
    stop_loss_price DECIMAL(10, 2),
    target_price DECIMAL(10, 2),
    status VARCHAR(10) DEFAULT '持仓',
    position_ratio DECIMAL(10, 4),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 9. 两融数据表
CREATE TABLE IF NOT EXISTS margin_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts_code VARCHAR(20) NOT NULL,
    trade_date DATE NOT NULL,
    rzye DECIMAL(20, 2),      -- 融资余额
    rzmre DECIMAL(20, 2),      -- 融资买入额
    rzche DECIMAL(20, 2),       -- 融资偿还额
    rqye DECIMAL(20, 2),       -- 融券余额
    rqmcl DECIMAL(20, 2),       -- 融券卖出量
    rqchl DECIMAL(20, 2),       -- 融券偿还量
    rzrqye DECIMAL(20, 2),      -- 融资融券余额
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(ts_code, trade_date)
);

-- 10. 股票列表缓存表
CREATE TABLE IF NOT EXISTS stock_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts_code VARCHAR(20) UNIQUE NOT NULL,
    symbol VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(50) NOT NULL,
    latest_price DECIMAL(10, 2),
    change_pct DECIMAL(10, 4),
    turnover_rate DECIMAL(10, 4),
    pe DECIMAL(10, 4),
    pb DECIMAL(10, 4),
    market_cap DECIMAL(20, 2),
    list_date DATE,
    industry VARCHAR(50),
    area VARCHAR(20),
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 11. 数据更新日志
CREATE TABLE IF NOT EXISTS update_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data_type VARCHAR(30) NOT NULL,
    update_date DATE NOT NULL,
    records_updated INTEGER,
    status VARCHAR(20) DEFAULT 'success',
    error_message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 创建视图：每日涨跌停统计
CREATE VIEW IF NOT EXISTS daily_limit_stats AS
SELECT 
    trade_date,
    COUNT(CASE WHEN pct_chg >= 9.5 THEN 1 END) as up_limit_count,
    COUNT(CASE WHEN pct_chg <= -9.5 THEN 1 END) as down_limit_count,
    AVG(pct_chg) as avg_pct_chg,
    SUM(vol) as total_volume
FROM daily_data
WHERE trade_date >= date('now', '-1 year')
GROUP BY trade_date
ORDER BY trade_date DESC;

-- 创建视图：板块涨幅排行
CREATE VIEW IF NOT EXISTS sector_rank AS
SELECT 
    s.sector_name,
    sd.trade_date,
    sd.close,
    sd.pct_chg,
    sd.net_inflow,
    sd.up_count,
    sd.down_count
FROM sector_daily sd
JOIN sectors s ON sd.sector_code = s.sector_code
ORDER BY sd.trade_date DESC, sd.pct_chg DESC;
