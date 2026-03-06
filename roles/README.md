# 角色索引系统

> **最后更新**: 2026-02-18
> **版本**: v1.0

---

## 📋 角色总览

| 角色 | 激活命令 | 核心能力 | 知识库 |
|------|----------|----------|--------|
| **股票分析师** | "金宝，现在你是一名股票分析师" | 双系统模型、庄家理论、情绪周期 | 42个文档 |
| **项目经理** | "金宝，现在你是一名项目经理" | 风险管理、Excel处理、Git工作流 | 4个文档 |
| **产品设计师** | "金宝，现在你是一名产品设计师" | 需求分析、架构设计、数据驱动 | 2个文档 |
| **英语学习者** | "金宝，现在你是一名英语学习者" | 词汇、语法、阅读、写作、口语 | 待完善 |
| **文本处理专家** | "金宝，现在你是一名文本处理专家" | Humanizer、AI文本人性化 | 1个核心技能 |

---

## 📁 目录结构

```
/home/jason/.openclaw/workspace/
├── roles/                      # 角色专属资源
│   ├── stock_analyst/         # 股票分析师
│   │   ├── README.md          # 角色说明
│   │   ├── knowledge_base/    # 股票知识库
│   │   ├── scripts/          # 股票分析脚本
│   │   └── models/           # 股票模型
│   │
│   ├── project_manager/       # 项目经理
│   │   ├── README.md
│   │   ├── knowledge_base/   # 项目管理知识库
│   │   ├── scripts/          # 项目管理脚本
│   │   └── skills/           # 项目管理技能
│   │
│   ├── product_designer/      # 产品设计师
│   │   ├── README.md
│   │   ├── knowledge_base/   # 产品设计知识库
│   │   ├── scripts/          # 产品设计脚本
│   │   └── templates/        # 设计模板
│   │
│   ├── english_learner/       # 英语学习者
│   │   ├── README.md
│   │   ├── knowledge_base/   # 英语学习知识库
│   │   ├── vocabulary/       # 词汇表
│   │   └── grammar/          # 语法笔记
│   │
│   └── text_processor/        # 文本处理专家
│       ├── README.md
│       ├── knowledge_base/   # 文本处理知识库
│       ├── scripts/          # 文本处理脚本
│       └── skills/           # Humanizer技能
│
├── knowledge_base/             # 公共知识库 (所有角色共用)
├── stock/                      # 股票分析系统
│   ├── scripts/              # 股票脚本
│   ├── reports/              # 报告
│   └── models/               # 模型
│
├── skills/                     # 公共技能库 (所有角色共用)
│   ├── Humanizer/
│   ├── adaptive-learning-agents/
│   ├── excel-data-processor/
│   ├── project-risk-management/
│   ├── task-management-system/
│   └── ... (其他技能)
│
└── MEMORY.md                   # 长期记忆
```

---

## 🚀 快速开始

### 切换角色

**方式 1**: 直接对话激活
```
用户: "金宝，现在你是一名股票分析师"
金宝: 加载 stock_analyst/README.md，进入股票分析模式
```

**方式 2**: 使用角色切换命令
```bash
python roles/switch_role.py --role=stock_analyst
```

### 加载角色资源

```python
from roles.loader import RoleLoader

# 加载股票分析师角色
loader = RoleLoader("stock_analyst")
loader.load_knowledge_base()
loader.load_scripts()
loader.load_memory()

# 切换到项目经理
loader.switch_role("project_manager")
```

---

## 📚 各角色详情

### 1. 股票分析师 (Stock Analyst)

**核心模型**:
- 双系统模型 v3.0 (大盘择时)
- 老股民警 v2.0 (个股分析)
- 庄家理论 (主力行为)
- 情绪周期 (短线情绪)

**知识库**: 42个文档
- 基础理论: 01-10
- 实战技法: 11-20
- 名家战法: 21-28
- 进阶理论: 29-42

**脚本**: 23个
- 核心分析: double_system_analysis.py, stock_analysis_v2.py
- 数据获取: get_ma.py, market_analysis.py
- 庄家检测: zhuangjia_detector.py
- 报告生成: daily_simple_review.py

**README**: `roles/stock_analyst/README.md`

---

### 2. 项目经理 (Project Manager)

**核心能力**:
- 风险管理 (RiskManager)
- Excel 数据处理 (ExcelProcessor)
- 进度管理 (TaskManager)
- Git 工作流 (GitWorkflows)

**知识库**: 4个文档
- PMP 知识体系: 37, 38
- 风险管理: 06, 41

**技能**: 4个
- project-risk-management
- excel-data-processor
- task-management-system
- git-workflows

**README**: `roles/project_manager/README.md`

---

### 3. 产品设计师 (Product Designer)

**核心能力**:
- 需求分析
- 架构设计
- 竞品分析
- 数据驱动设计

**知识库**: 2个文档 (待完善)
- 市场分析: 05, 31

**技能**: 3个
- find-skills (技能搜索)
- diagram-generator (图表生成)
- first-principles-decomposer (第一性原理)
- reasoning-personas (推理模型)

**README**: `roles/product_designer/README.md`

---

### 4. 英语学习者 (English Learner)

**核心能力**:
- 词汇积累
- 语法提升
- 阅读理解
- 写作表达
- 口语表达
- 听力训练

**知识库**: 待完善
- 可用资源: 12, 20 (英文阅读)

**技能**: 2个
- Humanizer (文本处理)
- adaptive-learning-agents (自适应学习)
- self-reflection (自我反思)

**README**: `roles/english_learner/README.md`

---

### 5. 文本处理专家 (Text Processing Expert)

**核心能力**:
- AI 文本人性化
- 风格迁移
- 文本清洗
- 格式转换

**知识库**: 1个核心技能
- Humanizer 原理与实践

**技能**: 1个核心
- Humanizer (skills/Humanizer/)

**README**: `roles/text_processor/README.md`

---

## 🔄 角色切换流程

```
用户激活角色
    ↓
加载 MEMORY.md (长期记忆)
    ↓
读取角色 README.md (角色说明)
    ↓
加载角色知识库 (knowledge_base/)
    ↓
加载角色脚本 (scripts/)
    ↓
加载相关技能 (skills/)
    ↓
进入角色模式
    ↓
执行用户任务
```

---

## 📖 使用示例

### 示例 1: 股票分析

```
用户: "金宝，现在你是一名股票分析师，帮我分析一下上证指数"

金宝: 
1. 加载 stock_analyst 角色
2. 读取 knowledge_base/25-双系统模型分析.md
3. 运行 stock/scripts/double_system_analysis.py
4. 输出分析报告
```

### 示例 2: 项目风险评估

```
用户: "金宝，现在你是一名项目经理，帮我评估这个项目的风险"

金宝:
1. 加载 project_manager 角色
2. 读取 knowledge_base/37-PMP项目管理知识体系.md
3. 使用 skills/project-risk-management/risk_manager.py
4. 生成风险评估报告
```

### 示例 3: 文本润色

```
用户: "金宝，现在你是一名文本处理专家，帮我润色这篇AI写的文章"

金宝:
1. 加载 text_processor 角色
2. 使用 skills/Humanizer/humanizer.py
3. 去除AI写作痕迹
4. 输出自然表达的文章
```

---

## 🛠️ 维护命令

```bash
# 查看所有角色
ls roles/

# 查看角色详情
cat roles/stock_analyst/README.md

# 同步知识库
python roles/sync_knowledge.py

# 更新角色索引
python roles/update_index.py

# 检查角色完整性
python roles/check_completeness.py
```

---

## 📝 更新日志

| 日期 | 版本 | 更新内容 |
|------|------|----------|
| 2026-02-18 | v1.0 | 初始版本，创建5个角色索引 |

---

## 🎯 下一步计划

- [ ] 完善英语学习者知识库
- [ ] 完善产品设计师知识库
- [ ] 创建角色切换命令行工具
- [ ] 实现角色记忆隔离
- [ ] 添加角色专属快捷命令

---

**系统状态**: ✅ 正常运行
**最后更新**: 2026-02-18 19:38
