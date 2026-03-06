# 股票分析系统总索引 v4.0

> **最后更新**: 2026-02-28
> **版本**: v4.0 整合优化版

---

## 📁 目录结构

```
/home/jason/.openclaw/workspace/
├── knowledge_base/          # 知识库 (38个核心文档)
├── stock/
│   ├── scripts/            # 分析脚本
│   ├── models/             # 模型配置
│   ├── data/               # 数据缓存
│   ├── database/           # 数据库
│   └── reports/            # 报告输出
└── STOCK_MODEL_INDEX.md    # 本索引文件
```

---

## 🧠 核心模型体系

### 1. 双系统模型 v3.0（大盘择时）

**定位**: 大盘趋势判断 + 开仓信号

**核心文档**:
- `knowledge_base/25-双系统模型分析.md`

**核心脚本**:
- `stock/scripts/double_system_analysis.py`

**六层过滤**:
1. 指数强趋势（MA20>MA60 + 指数>MA10）
2. 主线板块（强于指数 1.05 倍）
3. 龙头优先（近 5 日新高 + 涨停）
4. 量价强一致（放量突破 + 回调缩量）
5. 分歧确认（第一天分歧→第二天转强）
6. 失败压制（无连续放量滞涨等）

**信号类型**:
- 🟢 主升系统触发 - 可开仓
- 🟡 冰点系统触发 - 轻仓试错
- 🔴 混沌期 - 空仓等待

---

### 2. 老股民警个股分析模型 v2.0

**定位**: 个股深度分析 + 评分量化

**核心文档**:
- `knowledge_base/08-技术分析实战框架.md`

**核心脚本**:
- `stock/scripts/stock_analysis_v2.py`

**7 维分析体系**:
1. 趋势与均线 (20 分)
2. 量价健康度 (25 分)
3. K 线信号质量 (15 分)
4. 主力行为可信度 (20 分)
5. 板块与情绪环境 (20 分)

**评分等级**:
| 分数 | 等级 | 操作 |
|------|------|------|
| 80+ | 强势主升 | 积极参与 |
| 60-80 | 可操作 | 择时操作 |
| 40-60 | 观望 | 等信号 |
| 40- | 风险区 | 回避 |

---

### 3. 曹明成庄家理论

**定位**: 主力行为识别 + 跟庄策略

**核心文档**:
- `knowledge_base/34-曹明成看透股市庄家.md`
- `knowledge_base/09-主力坐庄流程.md`
- `knowledge_base/35-主力洗盘手段.md`

**核心脚本**:
- `stock/scripts/zhuangjia_detector.py`
- `stock/scripts/zhuangjia_batch.py`

**坐庄六阶段**:
1. 吸筹阶段
2. 建仓阶段
3. 洗盘阶段
4. 拉升阶段
5. 出货阶段
6. 反弹出货

---

### 4. 游资情绪周期模型

**定位**: 短线情绪判断 + 热点追踪

**核心文档**:
- `knowledge_base/27-北京炒家情绪周期.md`
- `knowledge_base/21-赵老哥龙头战法.md`
- `knowledge_base/22-作手新一短线技巧.md`
- `knowledge_base/20-炒股养家心法.md`

**情绪周期**:
- 冰点期 → 启动期 → 发酵期 → 高潮期 → 分歧期 → 退潮期

---

## 📚 知识库分类索引

### 基础理论 (01-10)
| 编号 | 文档 | 核心内容 |
|------|------|----------|
| 01 | 基础概念.md | K 线、均线、成交量等基础 |
| 02 | 基本面分析.md | 财报、估值、行业分析 |
| 03 | 技术分析.md | 技术指标、形态分析 |
| 04 | 情绪与资金面.md | 市场情绪、资金流向 |
| 05 | 板块与热点.md | 板块轮动、热点追踪 |
| 06 | 风险管理.md | 仓位管理、止损策略 |
| 07 | 交易策略.md | 策略制定、执行纪律 |
| 08 | 技术分析实战框架.md | 老股民警 7 维分析 |
| 09 | 主力坐庄流程.md | 庄家六阶段 |
| 10 | 市场周期与板块轮动.md | 周期理论 |

### 实战技法 (11-20)
| 编号 | 文档 | 核心内容 |
|------|------|----------|
| 11 | 散户游资操作手法.md | 游资操盘手法 |
| 12 | 交易心理学.md | 心理控制 |
| 13 | 波段操作.md | 波段战法 |
| 14 | 市场大行情模型.md | 大行情识别 |
| 15 | 量价关系深入.md | 量价分析 |
| 16 | K 线组合形态.md | K 线形态 |
| 17 | AKShare 配置.md | 数据接口 |
| 18 | Baostock 配置.md | 数据接口 |
| 19 | 数据库搭建.md | 数据存储 |
| 20 | 炒股养家心法.md | 心法精髓 |

### 名家战法 (21-28)
| 编号 | 文档 | 核心内容 |
|------|------|----------|
| 21 | 赵老哥龙头战法.md | 龙头战法 |
| 22 | 作手新一短线技巧.md | 短线技巧 |
| 23 | 交易心理学.md | 心理控制 |
| 24 | 超级短线战法.md | 超短战法 |
| 25 | 双系统模型分析.md | 双系统 v3.0 |
| 26 | 徐翔操作模式.md | 徐翔模式 |
| 27 | 北京炒家情绪周期.md | 情绪周期 |
| 28 | 实时数据获取.md | 数据接口 |

### 进阶理论 (29-38)
| 编号 | 文档 | 核心内容 |
|------|------|----------|
| 29 | TuShare 配置.md | 数据接口 |
| 30 | 最省 Token 数据获取.md | 优化方案 |
| 31 | 题材概念分类.md | 题材分类 |
| 32 | 缠论核心解析.md | 缠论 |
| 33 | 波浪理论.md | 波浪理论 |
| 34 | 曹明成看透股市庄家.md | 庄家理论 |
| 35 | 主力洗盘手段.md | 洗盘识别 |
| 36 | (待补充) | |
| 37 | PMP 项目管理知识体系.md | 项目管理 |
| 38 | PMP 跨行业案例分析.md | 案例分析 |

---

## 🛠️ 脚本工具清单

### 数据分析类
| 脚本 | 功能 | 状态 |
|------|------|------|
| `double_system_analysis.py` | 双系统复盘 | ✅ v3.0 |
| `stock_analysis_v2.py` | 个股深度分析 | ✅ v2.0 |
| `stock_analysis_old_trader.py` | 老股民警模型 | ✅ v1.0 |
| `market_analysis.py` | 市场分析 | ✅ |
| `market_analysis_baostock.py` | 市场分析 (Baostock) | ✅ |

### 庄家检测类
| 脚本 | 功能 | 状态 |
|------|------|------|
| `zhuangjia_detector.py` | 庄家阶段识别 | ✅ |
| `zhuangjia_batch.py` | 批量庄家分析 | ✅ |

### 数据获取类
| 脚本 | 功能 | 状态 |
|------|------|------|
| `get_ma.py` | 获取均线数据 | ✅ |
| `stock_data_utils.py` | 数据工具 | ✅ |
| `stock_data_manager.py` | 数据管理 | ✅ |
| `stock_data_web.py` | 网页数据抓取 | ✅ |

### 报告生成类
| 脚本 | 功能 | 状态 |
|------|------|------|
| `daily_simple_review.py` | 晚间复盘 (低 Token) | ✅ |
| `daily_market_report.py` | 日报生成 | ✅ |

### 工具类
| 脚本 | 功能 | 状态 |
|------|------|------|
| `analyze_stock.py` | 个股分析 | ✅ |
| `analyze_pattern.py` | 形态分析 | ✅ |
| `baostock_test.py` | Baostock 测试 | ✅ |
| `get_daily_data.py` | 日线数据 | ✅ |

---

## 🚀 标准工作流程

### 盘前准备 (9:00-9:25)
```bash
# 1. 查看隔夜外盘
# 2. 查看消息面
# 3. 查看昨日复盘报告
cat stock/reports/daily/report_YYYY-MM-DD.txt
```

### 盘中监控 (9:30-15:00)
```bash
# 1. 实时监控指数
python stock/scripts/get_ma.py

# 2. 监控主线板块
python stock/scripts/market_analysis.py

# 3. 个股分析
python stock/scripts/stock_analysis_v2.py --code=000001
```

### 盘后复盘 (15:00-20:00)
```bash
# 1. 双系统复盘
python stock/scripts/double_system_analysis.py

# 2. 晚间复盘 (自动 20:00)
python stock/scripts/daily_simple_review.py

# 3. 庄家检测
python stock/scripts/zhuangjia_batch.py
```

---

## 📊 数据接口配置

### AKShare (推荐)
- 免费、无需注册
- 数据全面、更新及时
- 配置：`knowledge_base/17-AKShare 配置.md`

### Baostock
- 免费、需登录
- 历史数据完整
- 配置：`knowledge_base/18-Baostock 配置.md`

### TuShare
- 部分免费、高级需付费
- 数据质量高
- 配置：`knowledge_base/29-TuShare 配置.md`

---

## ⚙️ 自动化任务

### Cron 任务
| 时间 | 任务 | 脚本 |
|------|------|------|
| 每日 20:00 | 晚间复盘 | `daily_simple_review.py` |
| 每小时 | 自动备份 | `auto_backup.sh` |

### 心跳检查
- 每 60 分钟检查一次市场状态
- 重大事件即时通知

---

## 📈 版本历史

| 版本 | 日期 | 更新内容 |
|------|------|----------|
| v4.0 | 2026-02-16 | 整合优化版，统一索引 |
| v3.0 | 2026-02-14 | 双系统严格过滤版 |
| v2.0 | 2026-02-14 | 老股民警模型 + 庄家理论 |
| v1.0 | 2026-02-13 | 初始版本 |

---

## 🎯 下一步优化计划

- [ ] 添加实时预警系统
- [ ] 整合选股策略
- [ ] 优化数据缓存机制
- [ ] 添加回测功能
- [ ] 完善文档注释

---

**系统状态**: ✅ 正常运行
**最后备份**: `/home/jason/backups/openclaw_latest/`

---

## 搜索系统 (新增)

### 整合搜索脚本
- `stock/scripts/unified_search.py` - 统一搜索入口

### 支持的搜索源
| 源 | 状态 | 额度 |
|----|------|------|
| Serper.dev | ✅ 可用 | 有限 |
| Tavily | ✅ 可用 | 每月 1000 次 |
| DuckDuckGo | 需安装 ddgr | 无限 |

### 使用方法
```bash
# 默认搜索 (自动选择)
python stock/scripts/unified_search.py --query "A股走势"

# 指定搜索源
python stock/scripts/unified_search.py --query "荣联科技" --source serper

# JSON 输出
python stock/scripts/unified_search.py --query "热点" --json
```


---

## 股票数据接口 (新增)

### 知识库
- `knowledge_base/42-股票数据接口整合.md` - AKShare/BaoStock/TuShare 整合

### 测试结果
- ✅ AKShare: 上证指数 4082.073
- ✅ BaoStock: 登录成功

### 推荐组合
- **AKShare**: 实时行情、板块、资金流向
- **BaoStock**: 历史数据、财务数据、复权因子

