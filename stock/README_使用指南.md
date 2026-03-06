# 股票系统使用指南

> **版本**: v4.0  
> **最后更新**: 2026-02-17  
> **状态**: ✅ 已配置开机自启

---

## 🚀 快速开始

### 开机检查
每次开机后运行一次（确保系统正常）：
```bash
bash /home/jason/.openclaw/workspace/startup_check.sh
```

### 查看 Cron 任务
```bash
crontab -l
```

---

## 📊 核心脚本

### 1. 双系统复盘 (盘后使用)
```bash
# 标准输出
python /home/jason/.openclaw/workspace/stock/scripts/double_system_analysis.py

# JSON 格式 (便于程序处理)
python /home/jason/.openclaw/workspace/stock/scripts/double_system_analysis.py --json

# 静默模式
python /home/jason/.openclaw/workspace/stock/scripts/double_system_analysis.py --quiet
```

**输出位置**: `stock/reports/report_YYYY-MM-DD.txt`

---

### 2. 个股综合分析
```bash
# 分析单只股票
python /home/jason/.openclaw/workspace/stock/scripts/stock_analysis_comprehensive.py --code=000001

# 输出 JSON
python /home/jason/.openclaw/workspace/stock/scripts/stock_analysis_comprehensive.py --code=000001 --json

# 批量分析 (自行编写循环)
for code in 000001 600519 300750; do
    python stock/scripts/stock_analysis_comprehensive.py --code=$code
done
```

**输出位置**: `stock/reports/stocks/`

---

### 3. 晚间复盘 (自动执行)
```bash
# 手动执行
python /home/jason/.openclaw/workspace/stock/scripts/daily_simple_review.py
```

**自动执行**: 每日 20:00  
**输出位置**: `stock/reports/daily/report_YYYY-MM-DD.txt`

---

### 4. 实时预警系统
```bash
# 监控自选股文件
python /home/jason/.openclaw/workspace/stock/scripts/stock_alert_system.py \
    --watchlist=/home/jason/.openclaw/workspace/stock/scripts/watchlist.txt \
    --interval=60

# 监控指定股票 (60 秒检查一次)
python /home/jason/.openclaw/workspace/stock/scripts/stock_alert_system.py \
    --code=000001,600519,300750 \
    --interval=60

# 监控 10 次后停止
python /home/jason/.openclaw/workspace/stock/scripts/stock_alert_system.py \
    --code=000001 \
    --interval=60 \
    --iterations=10
```

**预警类型**:
- 价格突破 (±5%)
- 成交量异常 (2 倍)
- 涨跌幅 (±7%)
- 资金流向 (±1000 万)

---

### 5. 自动备份
```bash
# 手动备份
bash /home/jason/.openclaw/workspace/auto_backup.sh

# 查看备份
ls -la /home/jason/backups/

# 查看最新备份
ls -la /home/jason/backups/openclaw_latest/
```

**自动执行**: 每小时整点  
**备份位置**: `/home/jason/backups/openclaw_YYYYMMDD_HHMM/`

---

## ⏰ 定时任务配置

| 时间 | 任务 | 脚本 |
|------|------|------|
| 每小时 | 自动备份 | `auto_backup.sh` |
| 每日 20:00 | 晚间复盘 | `daily_simple_review.py` |
| 交易日 15:30 | 双系统复盘 | `double_system_analysis.py` |
| 交易日 08:30 | 盘前检查 | `get_ma.py` |

**查看日志**:
```bash
# 备份日志
tail -f /tmp/cron_backup.log

# 复盘日志
tail -f /tmp/cron_review.log

# 开机检查日志
cat /tmp/openclaw_startup.log
```

---

## 📁 文件结构

```
/home/jason/.openclaw/workspace/
├── STOCK_MODEL_INDEX.md          # 总索引
├── auto_backup.sh                # 备份脚本
├── startup_check.sh              # 开机检查
├── knowledge_base/               # 知识库 (38 个文档)
├── stock/
│   ├── scripts/                  # 分析脚本
│   │   ├── double_system_analysis.py      # 双系统 v4.0
│   │   ├── stock_analysis_comprehensive.py # 个股分析 v3.0
│   │   ├── stock_alert_system.py          # 预警系统 v1.0
│   │   ├── daily_simple_review.py         # 晚间复盘
│   │   └── ... (其他脚本)
│   ├── reports/                  # 报告输出
│   │   ├── report_*.txt          # 双系统报告
│   │   ├── daily/                # 每日复盘
│   │   └── stocks/               # 个股报告
│   └── data/cache/               # 数据缓存
└── memory/                       # 记忆文件
```

---

## 🎯 评分体系说明

### 双系统模型 (大盘择时)
| 信号 | 条件 | 操作 |
|------|------|------|
| 🟢 主升系统 | 六层过滤通过≥3 层 | 可开仓 50-80% |
| 🟡 冰点系统 | 四要素满足≥2 条 | 轻仓试错≤30% |
| 🔴 混沌期 | 无信号 | 空仓等待 |

### 个股分析 (7 维评分)
| 分数 | 评级 | 操作 | 仓位 |
|------|------|------|------|
| 80+ | 强势主升 | 积极参与 | 50-80% |
| 60-80 | 可操作 | 择时操作 | 30-50% |
| 40-60 | 观望 | 等待信号 | 0-20% |
| 40- | 风险区 | 回避 | 0% |

---

## 🔧 常见问题

### Q: 数据获取失败？
**A**: 检查网络连接，AKShare 需要访问东方财富网站。

### Q: 脚本报错？
**A**: 查看日志 `/tmp/stock_alert.log` 或运行 `python -m py_compile 脚本名.py` 检查语法。

### Q: 备份太多占空间？
**A**: 自动保留最近 10 个备份，也可手动清理：
```bash
cd /home/jason/backups
ls -dt openclaw_*/ | tail -n +11 | xargs rm -rf
```

### Q: 如何修改预警阈值？
**A**: 编辑 `stock_alert_system.py` 中的 `self.config` 字典。

---

## 📞 系统状态检查

```bash
# 一键检查
bash /home/jason/.openclaw/workspace/startup_check.sh

# 查看 cron 状态
crontab -l

# 查看备份状态
ls -lh /home/jason/backups/

# 查看最新报告
cat /home/jason/.openclaw/workspace/stock/reports/daily/report_$(date +%Y-%m-%d).txt
```

---

## ✅ 开机即用清单

- [x] Python 环境检查
- [x] 依赖包检查 (akshare, pandas, numpy)
- [x] cron 服务运行
- [x] 定时任务配置
- [x] 核心脚本就绪
- [x] 备份机制正常
- [x] 开机自动备份

**系统状态**: ✅ 正常运行

---

**最后更新**: 2026-02-17 00:06  
**备份位置**: `/home/jason/backups/openclaw_latest/`
