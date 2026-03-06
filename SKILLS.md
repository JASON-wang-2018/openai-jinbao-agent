# SKILLS.md - 金宝的技能清单（更新版）

> **最后更新**: 2026-02-17 23:30
> **位置**: `/home/jason/.openclaw/workspace/skills/`

---

## 📦 已安装技能清单

### 💼 核心技能（今日新增）

#### 1. Excel 数据处理技能
**位置**: `excel-data-processor/`
**创建时间**: 2026-02-17 08:04

**核心功能**:
- ✅ 读取/写入 Excel（支持多 sheet）
- ✅ 数据清洗（空值、重复、格式）
- ✅ 合并多个文件
- ✅ 创建数据透视表
- ✅ 格式化 Excel（自动列宽、边框、标题）

**项目管理工具**:
- 📊 创建进度跟踪表
- 👥 创建资源分配表
- ⚠️ 创建风险登记册
- 📄 生成项目状态报告（Markdown）
- 📅 生成项目周报

#### 2. 项目风险管理技能
**位置**: `project-risk-management/`
**创建时间**: 2026-02-17 08:11

**核心功能**:
- 🔍 风险识别（6大类别：技术、资源、时间、范围、质量、外部）
- 📊 风险评估（9分制矩阵：可能性×影响程度）
- 🛡️ 风险应对（4大策略：规避、缓解、转移、接受）
- 📈 风险跟踪（定期检查、状态更新）
- 📄 风险报告（自动生成）

#### 3. Task Management System（任务管理与预警）✅ 新增
**位置**: `task-management-system/`
**创建时间**: 2026-02-17 22:26

**核心功能**:
- ✅ 任务管理（创建、编辑、删除、标记完成）
- 📅 计划规划（每日、每周、每月、季度）
- 🔥 重点提醒（Top 3 高优先级任务）
- ⏰ 预警系统（截止日期预警、逾期提醒、优先级提醒）

**核心类**:
- Task（任务类）
- TaskManager（任务管理器）
- ReminderManager（提醒管理器）

**文档**:
- `SKILL.md` - 完整技能文档
- `task_manager.py` - 核心类
- `README.md` - 使用指南
- `examples/integration_examples.py` - 8个完整示例

---

### 📋 办公助手

#### 4. Personal Assistant（个人助手）✅ 今日学习
**位置**: `personal-assistant/`
**功能**: 个人日常简报和生产力助手
- 🌅 每日简报生成（早安、天气、今日重点、习惯追踪、自我关怀、晚间复盘）
- ✅ 习惯追踪
- 💚 自我关怀提醒
- 🌙 晚间复盘

**使用方法**:
```bash
python3 skills/personal-assistant/scripts/daily_briefing.py --location "上海" --summary
```

---

### 🧠 自我提升技能

#### 5. Humanizer（文本人性化）
**位置**: `Humanizer/`
**功能**: 去除AI写作痕迹，让文本更自然

#### 6. Adaptive Learning（自适应学习）
**位置**: `adaptive-learning-agents/`
**功能**: 记录错误和成功经验，持续改进

#### 7. Self Reflection（自我反思）
**位置**: `self-reflection/`
**功能**: 定期反思，持续自我改进

#### 8. Self Evolve（自我进化）
**位置**: `self-evolve/`
**功能**: 自主修改配置、技能、文档，持续优化

#### 9. Proactive Agent（主动代理）
**位置**: `proactive-agent/`
**功能**: 主动发现问题、持续改进、记忆管理
- **主动** - 预期需求
- **持久** - WAL Protocol、Working Buffer
- **自我改进** - Self-healing、Relentless Resourcefulness

---

### 🤔 思维增强技能

#### 10. First Principles Decomposer（第一性原理）
**位置**: `first-principles-decomposer/`
**功能**: 将问题分解到基本事实，从原子级别重建解决方案

**三阶段流程**:
1. **识别假设** - "我假设为真但可能不对的是什么？"
2. **分解到原子** - 不断问"为什么"直到触及基本事实
3. **从真理重建** - 只从已验证的基本事实构建解决方案

#### 11. Reasoning Personas（推理人设）
**位置**: `reasoning-personas/`
**功能**: 激活不同高阶思维模式

**四种人设**:
- **Gonzo Truth-Seeker** - 找到缺口、挑战假设
- **Devil's Advocate** - 找到弱点、失败模式
- **Pattern Hunter** - 寻找连接、先例、模式
- **Integrator** - 确保系统连贯性

---

### 📊 数据分析技能

#### 12. Data Analysis（数据分析）
**位置**: `data-analysis/`
**功能**: 用统计严谨性、适当方法论和分析陷阱意识将原始数据转化为决策

#### 13. Data Anomaly Detector（数据异常检测）
**位置**: `data-anomaly-detector/`
**功能**: 检测建筑数据中的异常和离群值

#### 14. Technical Analyst（技术分析师）
**位置**: `technical-analyst/`
**功能**: 分析股票、股指、加密货币或外汇对的周K线图

---

### 🔍 搜索与浏览技能

#### 15. Tavily Search（Tavily搜索）
**位置**: `tavily-search/`
**功能**: AI优化的网络搜索，返回简洁相关结果

#### 16. Agent Browser（代理浏览器）
**位置**: `agent-browser/`
**功能**: 快速的基于 Rust 的无头浏览器自动化 CLI

#### 17. Find Skills（技能发现）
**位置**: `find-skills/`
**功能**: 帮助用户发现和安装代理技能

---

### 🛠️ 工具技能

#### 18. Git Workflows（Git工作流）
**位置**: `git-workflows/`
**功能**: 高级 Git 操作（rebase、bisect、worktrees等）

#### 19. Diagram Generator（图表生成器）
**位置**: `diagram-generator/`
**功能**: 生成各种图表

---

### ⚙️ 系统技能

#### 20. Healthcheck（健康检查）
**位置**: `/home/jason/.npm-global/lib/node_modules/openclaw/skills/healthcheck/`
**功能**: OpenClaw部署的主机安全加固和风险容忍度配置

#### 21. ClawHub（技能中心）
**位置**: `/home/jason/.npm-global/lib/node_modules/openclaw/skills/clawhub/`
**功能**: 使用 ClawHub CLI 从 clawhub.com 搜索、安装、更新和发布代理技能

#### 22. Weather（天气）
**位置**: `/home/jason/.npm-global/lib/node_modules/openclaw/skills/weather/`
**功能**: 获取当前天气和预报（无需 API 密钥）

#### 23. Tmux（Tmux控制）
**位置**: `/home/jason/.npm-global/lib/node_modules/openclaw/skills/tmux/`
**功能**: 通过发送击键和抓取窗格输出来远程控制 tmux 会话

#### 24. Skill Creator（技能创建器）
**位置**: `/home/jason/.npm-global/lib/node_modules/openclaw/skills/skill-creator/`
**功能**: 创建或更新 AgentSkills

---

## 📈 股票分析系统（3大模型）

### 1. 双系统模型 v3.0
**定位**: 大盘择时（严格过滤版）
**核心文档**: `knowledge_base/25-双系统模型分析.md`
**分析脚本**: `stock/scripts/double_system_analysis.py`

### 2. 老股民警个股分析模型 v2.0
**定位**: 个股7维分析（100分制）
**核心文档**: `knowledge_base/08-技术分析实战框架.md`
**分析脚本**: `stock/scripts/stock_analysis_v2.py`

### 3. 曹明成庄家理论
**定位**: 主力行为识别（六阶段）
**核心文档**: `knowledge_base/34-曹明成看透股市庄家.md`

---

## 🎯 技能快速查找

| 需求 | 技能 | 位置 |
|------|------|------|
| 任务管理 | Task Management | `task-management-system/` |
| 每日简报 | Personal Assistant | `personal-assistant/` |
| 处理Excel | Excel 数据处理 | `excel-data-processor/` |
| 项目管理 | ProjectManager | 见 SKILL.md |
| 风险管理 | RiskManager | `project-risk-management/` |
| 去除AI痕迹 | Humanizer | `Humanizer/` |
| 拆解问题 | 第一性原理 | `first-principles-decomposer/` |
| 头脑风暴 | 推理人设 | `reasoning-personas/` |
| 大盘分析 | 双系统模型 | `stock/scripts/double_system_analysis.py` |
| 个股分析 | 老股民警 v2.0 | `stock/scripts/stock_analysis_v2.py` |
| 主力行为 | 庄家理论 | `stock/scripts/zhuangjia_detector.py` |

---

## 💡 技能组合建议

### 组合1：日常生产全流程
```
1. Personal Assistant → 生成每日简报
2. Task Management → 管理今日任务
3. First Principles → 拆解复杂问题
4. Reasoning Personas → 多角度思考
5. Excel 数据处理 → 记录和分析数据
6. Adaptive Learning → 记录经验教训
```

### 组合2：项目开发全流程
```
1. First Principles → 拆解项目需求
2. Task Management → 创建项目任务
3. RiskManager → 识别和评估风险
4. Excel 数据处理 → 创建项目表单
5. Personal Assistant → 每日简报和提醒
6. Self Reflection → 项目复盘总结
```

### 组合3：股票投资全流程
```
1. 双系统模型 → 判断大盘趋势
2. 老股民警 v2.0 → 个股深度分析
3. 庄家理论 → 识别主力行为
4. First Principles → 拆解市场逻辑
5. Task Management → 跟踪交易任务
6. Adaptive Learning → 记录交易经验
```

---

## 📊 技能统计

### 今日新增（2026-02-17）
1. ✅ Excel 数据处理技能（08:04）
2. ✅ 项目风险管理技能（08:11）
3. ✅ 零和博弈与主力运作知识（21:40）
4. ✅ Proactive Agent v3.1.0（22:13）
5. ✅ First Principles Decomposer（22:13）
6. ✅ Reasoning Personas（22:13）
7. ✅ Personal Assistant（22:26）
8. ✅ Task Management System（22:26）

### 总计
- **技能总数**: 24 个
- **核心技能**: 3 个（Excel + 风险管理 + 任务管理）
- **自我提升**: 5 个（Humanizer + Adaptive + Reflection + Evolve + Proactive）
- **思维增强**: 2 个（First Principles + Reasoning Personas）
- **数据分析**: 3 个（Data Analysis + Anomaly Detector + Technical Analyst）
- **搜索浏览**: 3 个（Tavily + Browser + Find Skills）
- **工具类**: 2 个（Git Workflows + Diagram Generator）
- **办公助手**: 2 个（Personal Assistant + Task Management）
- **系统类**: 4 个（Healthcheck + ClawHub + Weather + Tmux + Skill Creator）

---

**最后更新**: 2026-02-17 23:30
**自动备份**: `/home/jason/backups/openclaw_latest/` (130个文件，97M）
