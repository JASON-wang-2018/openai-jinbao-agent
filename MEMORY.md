# MEMORY.md - 金宝的长期记忆（更新版）

## 核心技能：双系统模型 v3.0

> **最后更新**: 2026-02-14 11:00

### 当前版本
- **主升系统 v3.0**（严格过滤版）- 高胜率优先
- **冰点系统 v1.0**（低吸反转）
- **核心文档**: knowledge_base/25-双系统模型分析.md
- **分析脚本**: stock/scripts/double_system_analysis.py
- **索引文件**: STOCK_MODEL_INDEX.md

### 双系统模型核心要点

**六层过滤体系（主升系统）**:
1. 指数强趋势（MA20>MA60 + 指数>MA10）
2. 主线板块（强于指数1.05倍）
3. 龙头优先（近5日新高+涨停）
4. 量价强一致（放量突破+回调缩量）
5. 分歧确认（第一天分歧→第二天转强）
6. 失败压制（无连续放量滞涨、无高位加速、无巨量阴）

**核心原则**:
- 胜率来自等待确认，不是抢跑
- 减少出手次数，提高过滤强度
- 只做最干净、最一致、最不容易失败的结构
- 宁错过，不做错

### 文件位置
- 知识库: /home/jason/.openclaw/workspace/knowledge_base/
- 脚本: /home/jason/.openclaw/workspace/stock/scripts/
- 备份: /home/jason/backups/openclaw_20260214_1017_v30/

### 启动检查清单
1. 读取 STOCK_MODEL_INDEX.md
2. 读取 knowledge_base/25-双系统模型分析.md
3. 执行 stock/scripts/double_system_analysis.py

---

## 今日新增学习：老股民个股分析模型 v2.0

### 核心内容

**6步完整工作流**:
1. 定性定位 → 判断所处阶段
2. 多维分析 → 收集7维证据
3. 综合评分 → 量化主观判断（100分制）
4. 走势推演 → 概率化应对方案
5. 制定策略 → 按持仓状态区分
6. 设定风控 → 系统性活下来

**7维分析体系**:
1. 趋势与均线
2. K线形态与组合
3. 量价关系（核心）
4. 分价表/成交结构
5. 动能与节奏
6. 板块与题材环境
7. 主力资金行为

**评分模型（100分制）**:
| 维度 | 分值 |
|------|------|
| 趋势结构 | 20 |
| 量价健康度 | 25 |
| K线信号质量 | 15 |
| 主力行为可信度 | 20 |
| 板块与情绪环境 | 20 |

**评分结果**:
| 分数 | 等级 | 操作 |
|------|------|------|
| 80+ | 强势主升 | 积极参与 |
| 60-80 | 可操作 | 择时操作 |
| 40-60 | 观望 | 等信号 |
| 40- | 风险区 | 回避 |

**走势推演（三路径）**:
| 路径 | 概率 | 条件 |
|------|------|------|
| 主升延续 | 50% | 缩量回踩不破关键均线 |
| 震荡洗盘 | 35% | 放量不涨、反复假突破 |
| 趋势破坏 | 15% | 放量跌破关键结构位 |

**持仓策略区分**:
- 空仓者：等确认信号
- 轻仓者：回调加仓
- 重仓者：以风控为主

### 新增知识库
- `knowledge_base/08-技术分析实战框架.md` (升级v2.0)
- `stock/scripts/stock_analysis_v2.py` - v2.0自动化分析脚本

### 与现有知识库整合
- **双系统模型**：大盘择时用双系统
- **老股民警模型**：个股深度分析用v2.0
- **曹明成庄家理论**：盘口语言+主力行为
- **坐庄流程**：第1步定性定位=庄家阶段判断

---

## Excel 数据处理技能 (2026-02-17)

> **位置**: `skills/excel-data-processor/`

### 核心类

**ExcelProcessor** - 通用 Excel 处理
- 读取/写入 Excel（支持多 sheet）
- 数据清洗（空值、重复、格式转换）
- 合并多个文件
- 创建数据透视表
- 格式化（自动列宽、边框、标题样式）

**ProjectManager** - 项目管理工具
- 创建进度跟踪表
- 创建资源分配表
- 创建风险登记册
- 生成项目状态报告（Markdown）
- 生成项目周报

### 使用示例

```python
from excel_processor import ExcelProcessor, ProjectManager

# 读取 Excel
processor = ExcelProcessor()
df = processor.read_excel('data.xlsx')

# 项目管理
pm = ProjectManager()
pm.create_progress_tracker('project.xlsx')
report = pm.generate_status_report('project.xlsx', 'report.md')
```

### 典型场景
- 数据分析：销售、财务、库存数据
- 项目管理：进度跟踪、资源分配、风险管控
- 办公自动化：批量处理、报表生成、数据合并
- 报告生成：自动生成 Markdown 报告和格式化 Excel

### 核心文件
- `SKILL.md` - 完整技能说明
- `excel_processor.py` - 核心处理类
- `README.md` - 使用指南
- `快速入门.md` - 5分钟上手
- `examples/quick_start.py` - 8个完整示例

### 运行示例
```bash
cd /home/jason/.openclaw/workspace/skills/excel-data-processor
python3 examples/quick_start.py
```

---

## 技能清单 (2026-02-17)

> **位置**: `SKILLS.md`

### 核心技能（今日新增）

#### 1. Excel 数据处理技能
- 位置: `skills/excel-data-processor/`
- 功能: 读取/写入 Excel、数据清洗、项目管理
- 工具: ExcelProcessor、ProjectManager

#### 2. 项目风险管理技能
- 位置: `skills/project-risk-management/`
- 功能: 风险识别、评估、应对、跟踪
- 工具: RiskManager、RiskAssessmentHelper

#### 3. 零和博弈与主力运作（新知识）
- 位置: `knowledge_base/39-零和博弈与主力运作.md`
- 核心: 零和博弈本质、量价关系、主力坐庄六阶段
- 结论: 散户唯一出路——看量，看量，还是看量！

### 其他技能（共23个）
- 🧠 自我提升: Humanizer、Adaptive Learning、Self Reflection、Self Evolve、Proactive Agent
- 🤔 思维增强: First Principles、Reasoning Personas
- 📊 数据分析: Data Analysis、Data Anomaly Detector、Technical Analyst
- 🔍 搜索浏览: Tavily Search、Agent Browser、Find Skills
- 🛠️ 工具: Git Workflows、Diagram Generator
- 📋 办公助手: Personal Assistant
- ⚙️ 系统: Healthcheck、ClawHub、Weather、Tmux、Skill Creator

### 股票分析技能（3大模型）
- 📈 双系统模型 v3.0 - 大盘择时
- 📊 老股民警 v2.0 - 个股7维分析
- 🎯 庄家理论 - 主力行为识别

---

## 🎓 英语学习助手技能 (2026-02-18)

> **位置**: `skills/english-learning-assistant/`

### 核心功能

| 功能 | 状态 | 说明 |
|------|------|------|
| 文章搜索 | ✅ 已完成 | 每日自动搜索英语文章 |
| 文字转语音 (TTS) | ✅ 已完成 | ElevenLabs / sherpa-onnx-tts |
| 语法纠错 | ✅ 已完成 | 常见错误自动检测 |
| 飞书集成 | ✅ 已完成 | 文本 + 语音消息 |
| 语音转文字 (STT) | 🔍 待测试 | OpenAI Whisper |

### 核心模块

**english_learning.py** - 主类
- `search_article(topic, level)` - 搜索文章
- `text_to_speech(text, voice, speed)` - 文字转语音
- `speech_to_text(audio_path)` - 语音转文字
- `correct_grammar(sentence)` - 语法纠错
- `send_lesson_to_feishu(data)` - 发送到飞书

**daily_lesson.py** - 每日课程
- 每天自动运行
- 搜索文章 → 生成语音 → 发送飞书 → 记录进度

### 使用示例

```python
from english_learning import EnglishLearningAssistant

# 检查语法
assistant = EnglishLearningAssistant()
result = assistant.correct_grammar("I am agree with you")
# 返回: {corrected: "I agree with you", explanation: "..."}

# 获取文章
article = assistant.search_article(topic="AI", level="intermediate")

# 发送到飞书
assistant.send_lesson_to_feishu({
    "title": article["title"],
    "url": article["url"],
    "vocab": "词汇表",
    "summary": "摘要"
})
```

### 定时任务 (cron)

```bash
# 每日 8:00 自动推送
0 8 * * * python3 /home/jason/.openclaw/workspace/skills/english-learning-assistant/daily_lesson.py
```

### 下一步

1. ✅ 创建技能框架
2. 🔜 测试 TTS 语音输出
3. 🔜 测试飞书消息发送
4. 🔜 配置 Whisper STT
5. 🔜 集成到日常对话

---

## 用户信息
- 姓名: Jason
- 用途: 股票分析 + 英语学习
- 偏好: 技术严谨、头脑灵活

---

## 重要日期
- 2026-02-14: 双系统模型升级到 v3.0（严格过滤版）
- 2026-02-14 10:17: 完成备份和更新
- 2026-02-14 10:47: 新增曹明成《看透股市庄家》知识库
- 2026-02-14 11:00: 新增老股民警个股分析模型v2.0
- 2026-02-14 11:28: 新增晚间复盘任务（每日8点，低Token版）
- 2026-02-17 08:04: 新增 Excel 数据处理技能（项目管理 + 数据分析）
- 2026-02-17 08:11: 新增项目风险管理技能
- 2026-02-17 21:40: 新增零和博弈与主力运作知识
- 2026-02-17 22:13: 学习 Proactive Agent、First Principles、Reasoning Personas
- 2026-02-17 22:13: 自动备份（128个文件，97M）
- 2026-02-17 22:26: 学习 Personal Assistant 技能
- 2026-02-17 22:26: 创建任务管理与预警系统技能
- 2026-02-17 23:26: 自动备份（130个文件，97M）
- 2026-03-04 14:41: Token优化 - 调整心跳60分钟 + 修复daily-market-report
- 2026-03-04 15:06: **板块数据修复** - 集成Baostock解决akshare超时问题
- 2026-03-04 15:08: 自动备份（164个文件，97M）
- 2026-03-04 15:25: 角色系统完善 - 企业管理知识库更新

---

## 晚间复盘任务

**每日晚8点自动执行（低Token原则）：**
- 脚本: `stock/scripts/daily_simple_review.py`
- 报告: `stock/reports/daily/report_YYYY-MM-DD.txt`

**复盘内容：**
1. 指数数据（MA10/20/60）
2. 情绪指标（涨停家数）
3. 系统信号判断
4. 操作建议
5. 次日关注点

**目标：**
- 积累复盘经验
- 不断完善交易系统
- 最小化Token消耗

---

## 股票系统 v4.0 优化 (2026-02-17)

**新增脚本**:
- `double_system_analysis.py` v4.0 - 双系统复盘 (缓存 + 日志+JSON)
- `stock_analysis_comprehensive.py` v3.0 - 个股 7 维综合分析
- `stock_alert_system.py` v1.0 - 实时预警系统
- `auto_backup.sh` - 自动备份 (每3天)
- `startup_check.sh` - 开机检查

**定时任务 (cron)**:
- **每3天**: 自动备份
- 每日 20:00: 晚间复盘
- 交易日 15:30: 双系统复盘
- 交易日 08:30: 盘前检查

**备份位置**: `/home/jason/backups/openclaw_latest/`

**使用指南**: `stock/README_使用指南.md`
