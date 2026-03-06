# 📦 系统备份清单
# 日期：2026-02-17

---

## ✅ 备份完成

- **备份时间**: 2026-02-17 01:03:41
- **备份位置**: `/home/jason/backups/openclaw_20260217_0103/`
- **备份大小**: 97M
- **文件数量**: 121 个
- **最新链接**: `/home/jason/backups/openclaw_latest/`

---

## 📋 核心配置 (11 个)

| 文件 | 说明 |
|------|------|
| `AGENTS.md` | Agent 行为规则 |
| `SOUL.md` | 身份人格 |
| `USER.md` | 用户信息 |
| `IDENTITY.md` | 身份标识 |
| `MEMORY.md` | 长期记忆 |
| `HEARTBEAT.md` | 心跳任务 |
| `TOOLS.md` | 工具配置 |
| `STOCK_MODEL_INDEX.md` | 股票系统索引 |
| `BOOTSTRAP.md` | 初始化 |
| `MEMORY_SYSTEM.md` | 记忆系统 |
| `SESSION-STATE.md` | 会话状态 |

---

## 🧠 Skills (17 个)

| # | 技能 | 版本 | 功能 |
|---|------|------|------|
| 1 | proactive-agent | v3.1.0 | 主动型 agent 架构 |
| 2 | self-evolve | v1.0.0 | 自主进化 |
| 3 | self-reflection | v1.1.1 | 自我反思 |
| 4 | adaptive-learning-agents | v1.0.0 | 自适应学习 |
| 5 | find-skills | v0.1.0 | 发现技能 |
| 6 | reasoning-personas | v1.0.0 | 推理人格 |
| 7 | personal-assistant | - | 个人助理 |
| 8 | first-principles-decomposer | - | 第一性原理 |
| 9 | tavily-search | v1.0.0 | AI 搜索 |
| 10 | technical-analyst | - | 技术分析 |
| 11 | data-analysis | - | 数据分析 |
| 12 | data-anomaly-detector | - | 异常检测 |
| 13 | diagram-generator | - | 图表生成 |
| 14 | git-workflows | - | Git 高级操作 |
| 15 | humanizer | - | 去除 AI 痕迹 |
| 16 | agent-browser | - | 浏览器自动化 |
| 17 | healthcheck | - | 安全检查 |

---

## 📊 股票系统 (16 个脚本)

| # | 脚本 | 功能 |
|---|------|------|
| 1 | `double_system_analysis.py` | 双系统复盘 v4.0 |
| 2 | `stock_analysis_comprehensive.py` | 个股综合分析 v3.0 |
| 3 | `stock_alert_system.py` | 实时预警系统 v1.0 |
| 4 | `daily_simple_review.py` | 晚间复盘 |
| 5 | `stock_analysis_v2.py` | 个股分析 v2.0 |
| 6 | `stock_analysis_old_trader.py` | 老股民警模型 |
| 7 | `zhuangjia_detector.py` | 庄家检测 |
| 8 | `zhuangjia_batch.py` | 批量庄家分析 |
| 9 | `market_analysis.py` | 市场分析 |
| 10 | `market_analysis_baostock.py` | 市场分析 (Baostock) |
| 11 | `get_ma.py` | 均线获取 |
| 12 | `stock_data_manager.py` | 数据管理 |
| 13 | `stock_data_utils.py` | 数据工具 |
| 14 | `analyze_stock.py` | 个股分析 |
| 15 | `analyze_pattern.py` | 形态分析 |
| 16 | `daily_market_report.py` | 日报生成 |

---

## 📚 知识库 (38 个文档)

位置：`knowledge_base/`

| 编号 | 文档 | 核心内容 |
|------|------|----------|
| 01 | 基础概念.md | K线、均线、成交量 |
| 02 | 基本面分析.md | 财报、估值 |
| 03 | 技术分析.md | 技术指标 |
| 04 | 情绪与资金面.md | 市场情绪 |
| 05 | 板块与热点.md | 板块轮动 |
| 06 | 风险管理.md | 仓位管理 |
| 07 | 交易策略.md | 策略制定 |
| 08 | 技术分析实战框架.md | 老股民警 7 维 |
| 09 | 主力坐庄流程.md | 庄家六阶段 |
| 10 | 市场周期与板块轮动.md | 周期理论 |
| 11-38 | ... | 其他 |

---

## ⚙️ 定时任务 (Cron)

| 时间 | 任务 | 状态 |
|------|------|------|
| 每小时 | 自动备份 | ✅ 已配置 |
| 每日 20:00 | 晚间复盘 | ✅ 已配置 |
| 交易日 15:30 | 双系统复盘 | ✅ 已配置 |
| 交易日 08:30 | 盘前检查 | ✅ 已配置 |

---

## 🔧 备份脚本

| 脚本 | 功能 |
|------|------|
| `auto_backup.sh` | 自动备份 |
| `startup_check.sh` | 开机检查 |

---

## 📁 目录结构总览

```
/home/jason/.openclaw/workspace/
├── AGENTS.md              # Agent 规则
├── SOUL.md                # 人格
├── USER.md                # 用户
├── MEMORY.md              # 长期记忆
├── HEARTBEAT.md           # 心跳任务
├── STOCK_MODEL_INDEX.md    # 股票索引
│
├── knowledge_base/         # 38 个知识文档
│
├── stock/                 # 股票系统
│   ├── scripts/           # 16 个分析脚本
│   ├── reports/           # 报告输出
│   └── data/              # 数据缓存
│
├── skills/                # 17 个技能
│   ├── self-evolve/
│   ├── self-reflection/
│   ├── proactive-agent/
│   └── ...
│
└── memory/                # 每日记忆
    ├── 2026-02-13.md
    ├── 2026-02-14.md
    └── 2026-02-16.md
```

---

## 🔄 备份位置

- **最新**: `/home/jason/backups/openclaw_latest/`
- **历史**: `/home/jason/backups/openclaw_YYYYMMDD_HHMM/`

---

**备份状态**: ✅ 完成
**备份时间**: 2026-02-17 01:03
**文件总数**: 121 个
**总大小**: 97M
