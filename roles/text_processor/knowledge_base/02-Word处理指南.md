# Word 文档处理完全指南

> 版本: 2.0 | 适用于: 项目管理、产品设计、中层管理

---

## 一、核心技能

### 1.1 文档创建与保存

```python
from docx import Document

# 创建新文档
doc = Document()

# 添加内容
doc.add_heading('文档标题', 0)           # 标题级别 0
doc.add_heading('一级标题', 1)          # 标题级别 1
doc.add_heading('二级标题', 2)          # 标题级别 2

# 添加段落
doc.add_paragraph('这是一个段落')
doc.add_paragraph('这是另一个段落', style='Heading 1')

# 保存文档
doc.save('output.docx')
```

### 1.2 文本格式化

```python
from docx.shared import Pt, Inches
from docx.oxml.ns import qn

# 添加段落并设置样式
para = doc.add_paragraph('格式化文本示例')

# 添加不同格式的文本
run = para.add_run('加粗文本')
run.bold = True

run = para.add_run('斜体文本')
run.italic = True

run = para.add_run('下划线文本')
run.underline = True

# 设置字体
run.font.name = '微软雅黑'
run.font.size = Pt(12)
run.font.bold = True

# 中文字体设置
doc.styles['Normal'].font.name = '微软雅黑'
doc.styles['Normal']._element.rPr.rFonts.set(qn('w:eastAsia'), '微软雅黑')
```

### 1.3 列表

```python
# 无序列表
doc.add_paragraph('第一项', style='List Bullet')
doc.add_paragraph('第二项', style='List Bullet')
doc.add_paragraph('第三项', style='List Bullet')

# 有序列表
doc.add_paragraph('第一步', style='List Number')
doc.add_paragraph('第二步', style='List Number')
doc.add_paragraph('第三步', style='List Number')

# 多级列表
doc.add_paragraph('一级项目', style='List Number')
doc.add_paragraph('    二级项目', style='List Number 2')
doc.add_paragraph('        三级项目', style='List Number 3')
```

---

## 二、表格操作

### 2.1 创建表格

```python
# 创建表格（行数，列数）
table = doc.add_table(rows=5, cols=3)

# 设置表格样式
table.style = 'Table Grid'

# 添加表头
hdr_cells = table.rows[0].cells
hdr_cells[0].text = '姓名'
hdr_cells[1].text = '部门'
hdr_cells[2].text = '职位'

# 添加数据行
data = [
    ('张三', '技术部', '经理'),
    ('李四', '产品部', '主管'),
    ('王五', '设计部', '设计师')
]

for row_idx, row_data in enumerate(data, start=1):
    row_cells = table.rows[row_idx].cells
    for col_idx, value in enumerate(row_data):
        row_cells[col_idx].text = value
```

### 2.2 表格格式化

```python
from docx.shared import Pt

# 设置表格列宽
for cell in table.columns[0].cells:
    cell.width = Inches(1.5)
for cell in table.columns[1].cells:
    cell.width = Inches(2.0)

# 设置单元格字体
for row in table.rows:
    for cell in row.cells:
        cell.paragraphs[0].runs[0].font.size = Pt(11)
        cell.paragraphs[0].runs[0].font.name = '微软雅黑'

# 表格自动调整
from docx.table import Table
from docx.oxml.ns import nsdecls
from docx.oxml import parse_xml

# 表格斑马纹
for i, row in enumerate(table.rows):
    if i % 2 == 1:
        for cell in row.cells:
            cell_shading = parse_xml(
                r'<w:shd {} w:fill="F0F0F0"/>'.format(
                    nsdecls('w')
                )
            )
            cell._tc.get_or_add_tcPr().append(cell_shading)
```

### 2.3 复杂表格

```python
def create_project_table(doc, project_data):
    """创建项目信息表格"""
    table = doc.add_table(rows=len(project_data)+1, cols=2)
    table.style = 'Table Grid'
    
    # 表头
    table.rows[0].cells[0].text = '项目属性'
    table.rows[0].cells[1].text = '内容'
    
    # 数据
    for i, (key, value) in enumerate(project_data.items()):
        table.rows[i+1].cells[0].text = key
        table.rows[i+1].cells[1].text = str(value)
    
    return table

# 使用
project_info = {
    '项目名称': 'XX系统升级',
    '项目经理': '张三',
    '开始日期': '2024-01-01',
    '结束日期': '2024-06-30',
    '预算': '100万',
    '状态': '进行中'
}
create_project_table(doc, project_info)
```

---

## 三、插入对象

### 3.1 插入图片

```python
from docx.shared import Inches

# 添加图片（路径，宽度）
doc.add_picture('chart.png', width=Inches(5))

# 添加图片并设置高度
doc.add_picture('logo.png', height=Inches(1.5))
```

### 3.2 插入分页符

```python
doc.add_page_break()
```

### 3.3 插入超链接

```python
from docx.oxml.shared import OxmlElement
from docx.oxml import ns

def add_hyperlink(paragraph, text, url):
    """添加超链接"""
    hyperlink = OxmlElement('w:hyperlink')
    hyperlink.set(ns.rId('rId' + str(len(paragraph.part.rels))))
    
    new_run = OxmlElement('w:r')
    rPr = OxmlElement('w:rPr')
    
    rStyle = OxmlElement('w:rStyle')
    rStyle.set(ns.w('val'), 'Hyperlink')
    
    rPr.append(rStyle)
    new_run.append(rPr)
    
    text_element = OxmlElement('w:t')
    text_element.text = text
    new_run.append(text_element)
    
    hyperlink.append(new_run)
    paragraph._element.append(hyperlink)
    
    # 添加关系
    paragraph.part.rels.add(
        paragraph.part.rels.get_or_add_target_ref(url)
    )

# 使用
para = doc.add_paragraph()
run = para.add_run('访问网站')
run.hyperlink = 'https://example.com'
```

---

## 四、样式管理

### 4.1 使用内置样式

```python
# 标题样式
doc.add_heading('使用内置标题', 1)

# 引用样式
doc.add_paragraph('这是一段引用', style='Quote')

# 代码样式
doc.add_paragraph('print("Hello")', style='Code')

# 强调样式
doc.add_paragraph('重要文本', style='Emphasis')
```

### 4.2 自定义样式

```python
from docx.enum.style import WD_STYLE_TYPE

# 创建新样式
style = doc.styles.add_style('MyHeading', WD_STYLE_TYPE.PARAGRAPH)

# 设置样式属性
style.font.name = '微软雅黑'
style.font.size = Pt(14)
style.font.bold = True
style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
style.paragraph_format.space_before = Pt(12)
style.paragraph_format.space_after = Pt(6)
```

---

## 五、文档模板

### 5.1 项目报告模板

```python
def create_project_report(doc, project_info, progress_data):
    """创建项目报告"""
    
    # 标题
    doc.add_heading(f"{project_info['项目名称']} - 项目报告", 0)
    
    # 项目概述
    doc.add_heading('项目概述', 1)
    doc.add_paragraph(f"项目经理：{project_info['项目经理']}")
    doc.add_paragraph(f"报告周期：{project_info['报告周期']}")
    doc.add_paragraph(f"当前状态：{project_info['状态']}")
    
    # 进度摘要
    doc.add_heading('进度摘要', 1)
    table = doc.add_table(rows=len(progress_data)+1, cols=3)
    table.style = 'Table Grid'
    
    # 表头
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = '任务'
    hdr_cells[1].text = '进度'
    hdr_cells[2].text = '状态'
    
    # 数据
    for i, task in enumerate(progress_data):
        row_cells = table.rows[i+1].cells
        row_cells[0].text = task['name']
        row_cells[1].text = str(task['progress']) + '%'
        row_cells[2].text = task['status']
    
    # 问题与风险
    doc.add_heading('问题与风险', 1)
    for risk in project_info['风险列表']:
        doc.add_paragraph(f"⚠️ {risk}", style='List Bullet')
    
    # 下一步计划
    doc.add_heading('下一步计划', 1)
    for plan in project_info['计划']:
        doc.add_paragraph(f"→ {plan}", style='List Number')
```

### 5.2 PRD 文档模板

```python
def create_prd(doc, prd_info):
    """创建产品需求文档"""
    
    # 封面
    doc.add_heading(prd_info['产品名称'], 0)
    doc.add_paragraph(f"版本：{prd_info['版本号']}")
    doc.add_paragraph(f"作者：{prd_info['作者']}")
    doc.add_paragraph(f"日期：{prd_info['日期']}")
    
    doc.add_page_break()
    
    # 目录
    doc.add_heading('目录', 1)
    # ... 添加目录内容
    
    # 需求概述
    doc.add_heading('1. 需求概述', 1)
    doc.add_paragraph(prd_info['概述'])
    
    # 用户故事
    doc.add_heading('2. 用户故事', 1)
    for story in prd_info['用户故事']:
        doc.add_heading(story['标题'], 2)
        doc.add_paragraph(f"作为 {story['角色']}，我希望 {story['功能']}，以便 {story['价值']}")
        
        # 验收标准
        doc.add_paragraph('验收标准：', style='Quote')
        for criteria in story['验收标准']:
            doc.add_paragraph(f"✓ {criteria}", style='List Bullet')
```

---

## 六、WordProcessor 类

```python
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

class WordProcessor:
    """Word 文档处理器"""
    
    def __init__(self):
        self.doc = None
        self.save_path = None
    
    def create_document(self):
        """创建新文档"""
        self.doc = Document()
        return self
    
    def load_document(self, filepath):
        """加载现有文档"""
        self.doc = Document(filepath)
        self.save_path = filepath
        return self
    
    def add_heading(self, text, level=0):
        """添加标题"""
        self.doc.add_heading(text, level)
    
    def add_paragraph(self, text, style=None):
        """添加段落"""
        return self.doc.add_paragraph(text, style)
    
    def add_table(self, rows, cols, data=None):
        """创建表格"""
        table = self.doc.add_table(rows=rows, cols=cols)
        table.style = 'Table Grid'
        
        if data:
            for i, row_data in enumerate(data):
                for j, value in enumerate(row_data):
                    table.rows[i].cells[j].text = str(value)
        
        return table
    
    def add_picture(self, path, width=None, height=None):
        """添加图片"""
        if width:
            self.doc.add_picture(path, width=Inches(width))
        elif height:
            self.doc.add_picture(path, height=Inches(height))
        else:
            self.doc.add_picture(path)
    
    def save(self, filepath=None):
        """保存文档"""
        save_path = filepath or self.save_path
        if save_path:
            self.doc.save(save_path)
            print(f"✅ 文档已保存: {save_path}")
        else:
            print("⚠️ 未指定保存路径")
    
    def create_project_report(self, title, sections):
        """创建项目报告"""
        self.doc.add_heading(title, 0)
        
        for section in sections:
            self.doc.add_heading(section['title'], 1)
            
            if section['type'] == 'paragraph':
                self.doc.add_paragraph(section['content'])
            elif section['type'] == 'table':
                self.add_table(section['rows'], section['cols'], section['data'])
            elif section['type'] == 'list':
                for item in section['items']:
                    self.doc.add_paragraph(item, style='List Bullet')
```

---

## 七、最佳实践

1. **样式统一**: 使用统一的样式，避免直接设置字体
2. **图片路径**: 使用相对路径，便于文档共享
3. **表格样式**: 使用 `Table Grid` 或自定义表格样式
4. **分节处理**: 长文档使用分节符分隔不同部分
5. **目录自动**: 使用域插入自动目录
6. **版本控制**: 重要文档保存多个版本

---

## 八、常见问题

### Q1: 如何删除文档中的空白页？
```python
# 找到并删除空白段落
for paragraph in doc.paragraphs:
    if paragraph.text.strip() == '' and paragraph.runs:
        # 检查是否为分页符导致的空白页
        pass
```

### Q2: 如何复制样式到另一个文档？
```python
# 复制整个样式
from docx import Document
from docx.oxml import parse_xml

source_doc = Document('source.docx')
target_doc = Document('target.docx')

# 复制样式
for style in source_doc.styles:
    if style.name not in target_doc.styles:
        # 创建新样式
        new_style = target_doc.styles.add_style(style.name, style.type)
        # 复制属性
        new_style.font.size = style.font.size
```

### Q3: 如何添加页眉页脚？
```python
from docx.shared import Pt

# 页眉
header = doc.sections[0].header
header_para = header.paragraphs[0]
header_para.text = "文档标题 | 公司名称"
header_para.style = doc.styles['Header']

# 页脚
footer = doc.sections[0].footer
footer_para = footer.paragraphs[0]
footer_para.text = f"第 {doc.sections[0].footer.paragraphs[0].runs[0].add_field('PAGE')} 页"
```
