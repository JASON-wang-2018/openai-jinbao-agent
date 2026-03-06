# 中层管理者知识库索引

> 本目录包含中层管理者所需的所有知识文档、模型和工具。

---

## 📁 目录结构

```
management/
├── database/                    # SQLite 数据库
│   └── management_knowledge.db # 主数据库
│
├── knowledge_base/              # 知识文档
│   ├── 01-角色定位/            # 角色认知
│   ├── 02-产品设计/             # 产品方法论
│   ├── 03-项目管理/             # 项目管理知识
│   ├── 04-团队管理/             # 团队建设与人才
│   ├── 05-向上管理/             # 向上协作
│   ├── 06-横向协作/             # 跨部门沟通
│   ├── 07-自我管理/             # 时间与精力
│   └── 08-职场软技能/           # 沟通与影响力
│
├── models/                      # 分析模型库
│   ├── 目标管理模型/            # SMART/OKR
│   ├── 项目管理模型/            # WBS/甘特图
│   ├── 团队管理模型/            # Tuckman/绩效
│   ├── 问题解决模型/            # 5W2H/PDCA
│   └── 战略分析模型/            # SWOT/波特五力
│
├── scripts/                     # 自动化脚本
│   ├── db_manager.py           # 数据库管理工具
│   ├── knowledge_search.py     # 知识搜索工具
│   ├── model_selector.py       # 模型选择助手
│   ├── template_generator.py   # 模板生成器
│   └── daily_check.py          # 每日检查清单
│
└── docs/                        # 文档与指南
    ├── 使用指南.md
    ├── 快速入门.md
    └── 常见问题FAQ.md
```

---

## 🚀 快速开始

### 1. 查询知识

```bash
# 搜索关键词
python scripts/knowledge_search.py "团队管理"

# 搜索模型
python scripts/model_selector.py --scenario "目标设定"

# 生成模板
python scripts/template_generator.py --type "周报"
```

### 2. 数据库操作

```bash
# 初始化数据库
python scripts/db_manager.py --init

# 查看统计
python scripts/db_manager.py --stats

# 备份数据
python scripts/db_manager.py --backup
```

---

## 📚 核心知识模块

### 1. 角色定位
- 中层管理者三大角色
- 一天工作节奏
- 能力进阶路径

### 2. 产品设计
- 需求分析流程
- KANO模型应用
- 产品迭代方法

### 3. 项目管理
- WBS工作分解
- 进度管控
- 风险管理

### 4. 团队管理
- 团队发展阶段
- OKR绩效管理
- 冲突解决方法

### 5. 向上管理
- 高效汇报技巧
- 资源争取策略
- 接受反馈方法

### 6. 横向协作
- 跨部门沟通原则
- 会议效率提升
- 资源协调方法

### 7. 自我管理
- 时间管理矩阵
- 精力管理策略
- 压力应对技巧

### 8. 职场软技能
- 沟通表达技巧
- 影响力建立
- 决策能力提升

---

## 🛠️ 常用工具

### 脚本工具

| 脚本 | 功能 |
|------|------|
| `db_manager.py` | 数据库管理 |
| `knowledge_search.py` | 知识搜索 |
| `model_selector.py` | 模型推荐 |
| `template_generator.py` | 模板生成 |
| `daily_check.py` | 每日检查 |

### 数据库表

| 表名 | 用途 |
|------|------|
| `knowledge_categories` | 知识分类 |
| `knowledge_points` | 知识点 |
| `management_models` | 管理模型 |
| `templates` | 模板库 |
| `cases` | 案例库 |
| `faqs` | 常见问题 |
| `skills` | 技能清单 |
| `action_items` | 行动清单 |

---

## 📊 使用统计

- **知识分类**: 8 大类，17 子类
- **管理模型**: 15+ 核心模型
- **工具模板**: 10+ 实用模板
- **案例库**: 持续更新中

---

## 💡 使用建议

1. **新手建议**: 从"角色定位"开始，建立整体认知
2. **解决问题**: 使用"模型选择器"找到合适的分析工具
3. **日常应用**: 使用"每日检查清单"形成习惯
4. **持续学习**: 利用"知识搜索"快速查找答案

---

*最后更新: 2026-02-20*
