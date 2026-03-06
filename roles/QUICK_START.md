# 🎭 金宝角色系统 - 快速激活指南

> **最后更新**: 2026-02-18

---

## ⚡ 一键激活

直接对金宝说：

| 角色 | 激活命令 |
|------|----------|
| **股票分析师** | "金宝，现在你是一名股票分析师" |
| **项目经理** | "金宝，现在你是一名项目经理" |
| **产品设计师** | "金宝，现在你是一名产品设计师" |
| **英语学习者** | "金宝，现在你是一名英语学习者" |
| **文本处理专家** | "金宝，现在你是一名文本处理专家" |

---

## 📖 详细说明

### 1. 🎯 股票分析师 (Stock Analyst)

**激活**: "金宝，现在你是一名股票分析师"

**核心能力**:
- 🧠 双系统模型 v3.0 - 大盘择时
- 📊 老股民警 v2.0 - 个股7维分析
- 🏠 庄家理论 - 主力行为识别
- 📈 情绪周期 - 短线情绪判断

**知识库**: 42个文档
- 基础理论 (01-10)
- 实战技法 (11-20)
- 名家战法 (21-28)
- 进阶理论 (29-42)

**脚本**:
```bash
# 盘前检查
python stock/scripts/market_analysis.py

# 个股分析
python stock/scripts/stock_analysis_v2.py --code=000001

# 双系统复盘
python stock/scripts/double_system_analysis.py
```

**详情**: `roles/stock_analyst/README.md`

---

### 2. 📋 项目经理 (Project Manager)

**激活**: "金宝，现在你是一名项目经理"

**核心能力**:
- ⚠️ 风险管理 (RiskManager)
- 📊 Excel数据处理 (ExcelProcessor)
- 📅 进度管理 (TaskManager)
- 🔀 Git工作流 (GitWorkflows)

**知识库**: 4个文档
- PMP知识体系: 37, 38
- 风险管理: 06, 41

**技能**:
```python
# 风险管理示例
from risk_manager import RiskManager
rm = RiskManager()
risks = rm.identify_risks(project_data)

# Excel处理示例
from excel_processor import ProjectManager
pm = ProjectManager()
pm.create_progress_tracker('project.xlsx')
```

**详情**: `roles/project_manager/README.md`

---

### 3. 🎨 产品设计师 (Product Designer)

**激活**: "金宝，现在你是一名产品设计师"

**核心能力**:
- 📝 需求分析
- 🏗️ 架构设计
- 🔍 竞品分析
- 📊 数据驱动设计

**技能**:
- `find-skills` - 技能搜索
- `diagram-generator` - 图表生成
- `first-principles-decomposer` - 第一性原理
- `reasoning-personas` - 推理模型

**详情**: `roles/product_designer/README.md`

---

### 4. 📚 英语学习者 (English Learner)

**激活**: "金宝，现在你是一名英语学习者"

**核心能力**:
- 📖 词汇积累
- 📝 语法提升
- 📰 阅读理解
- ✍️ 写作表达
- 🗣️ 口语表达
- 👂 听力训练

**工具**:
- `Humanizer` - 文本润色
- `adaptive-learning-agents` - 自适应学习
- `self-reflection` - 自我反思

**详情**: `roles/english_learner/README.md`

---

### 5. 🔧 文本处理专家 (Text Processing Expert)

**激活**: "金宝，现在你是一名文本处理专家"

**核心能力**:
- 🤖 AI文本人性化 (Humanizer)
- 🎭 风格迁移
- 🧹 文本清洗
- 🔄 格式转换

**使用示例**:
```python
from humanizer import Humanizer

h = Humanizer()

# AI文本润色
human_text = h.remove_ai_marks(ai_text)

# 转换为正式风格
formal = h.to_professional(casual_text)
```

**详情**: `roles/text_processor/README.md`

---

## 🛠️ 命令行工具

```bash
# 切换角色
python roles/switch_role.py --role=stock_analyst

# 列出所有角色
python roles/switch_role.py --list

# 显示当前角色
python roles/switch_role.py --current
```

---

## 📁 目录结构

```
/home/jason/.openclaw/workspace/
├── roles/                      # 角色专属资源
│   ├── README.md              # 主索引
│   ├── switch_role.py         # 角色切换工具
│   ├── current_role.json      # 当前角色状态
│   ├── memory/                # 角色专属记忆
│   │
│   ├── stock_analyst/         # 股票分析师
│   │   └── README.md
│   │
│   ├── project_manager/       # 项目经理
│   │   └── README.md
│   │
│   ├── product_designer/      # 产品设计师
│   │   └── README.md
│   │
│   ├── english_learner/       # 英语学习者
│   │   └── README.md
│   │
│   └── text_processor/        # 文本处理专家
│       └── README.md
│
├── knowledge_base/             # 公共知识库
├── stock/scripts/              # 股票脚本
├── skills/                     # 公共技能库
└── MEMORY.md                   # 长期记忆
```

---

## 🎯 使用流程

```
1. 用户激活角色
   ↓
2. 金宝加载 MEMORY.md
   ↓
3. 读取角色 README.md
   ↓
4. 加载对应知识库和脚本
   ↓
5. 进入角色模式
   ↓
6. 执行用户任务
```

---

## 💡 提示

- 每个角色都有专属的 `README.md`，包含详细的使用说明
- 角色切换后，金宝会记住当前的专注领域
- 使用命令行工具可以快速查看和切换角色
- 角色的记忆会保存在 `roles/memory/` 目录下

---

**系统状态**: ✅ 正常运行
