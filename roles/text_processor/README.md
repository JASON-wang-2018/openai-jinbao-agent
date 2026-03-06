# 文本处理专家

> 专业的 Office 文档处理助手
> 
> 支持 Word、Excel、PPT 等办公文档的创建、编辑、分析和格式转换

## 核心能力

### 📊 Excel 数据处理
- 数据读取、清洗、分析
- 数据透视表和图表生成
- 项目管理模板（进度表、资源表、风险表）
- 报告自动生成

### 📝 Word 文档处理
- 文档创建和格式化
- 表格和图表插入
- 目录和样式管理
- 多文档合并

### 📑 PowerPoint 制作
- 幻灯片创建和排版
- 图表和表格插入
- 主题和动画设置
- 批量生成模板

### 🔄 格式转换
- Excel ↔ CSV ↔ JSON
- Word ↔ PDF
- PPT ↔ PDF
- 多格式导出

## 适用场景

### 项目管理
- 项目计划书编写
- 进度跟踪表管理
- 项目状态报告生成
- 风险登记册维护

### 产品设计
- 需求文档编写
- PRD 文档生成
- 产品说明书制作
- 原型文档整理

### 中层管理
- 工作周报/月报
- 绩效考核表格
- 团队资源分配
- 管理决策报告

## 快速开始

### 处理 Excel
```python
# 读取并分析
df = pd.read_excel('项目进度.xlsx')
df.groupby('负责人')['进度'].mean()
```

### 生成报告
```python
# 从数据生成 Word 报告
from docx import Document
doc = Document()
doc.add_heading('项目报告', 0)
doc.add_paragraph('报告内容...')
doc.save('报告.docx')
```

### 创建 PPT
```python
# 从数据生成演示文稿
from pptx import Presentation
prs = Presentation()
slide = prs.slides.add_slide(prs.slide_layouts[0])
slide.shapes.title.text = '标题'
prs.save('演示文稿.pptx')
```

## 目录结构

```
text_processor/
├── README.md              # 本文件
├── knowledge_base/        # 知识库
│   ├── excel处理指南.md
│   ├── word处理指南.md
│   └── ppt处理指南.md
├── models/                # 模板库
│   ├── 项目管理模板
│   ├── 产品设计模板
│   └── 中层管理模板
├── scripts/               # 处理脚本
│   ├── excel_processor.py
│   ├── word_processor.py
│   ├── ppt_processor.py
│   └── document_converter.py
└── data/                  # 数据存储
```

## 常用工具

| 任务 | Python 库 |
|------|-----------|
| Excel | pandas, openpyxl, xlrd |
| Word | python-docx, docx2txt |
| PPT | python-pptx |
| PDF | PyPDF2, pdfplumber |
| 格式转换 | pandoc, pypandoc |

## 最佳实践

1. **数据备份**: 处理前备份原文件
2. **分步操作**: 复杂任务拆分成多步
3. **格式规范**: 统一命名和格式标准
4. **自动化**: 重复任务尽量脚本化
5. **文档记录**: 重要流程记录文档
