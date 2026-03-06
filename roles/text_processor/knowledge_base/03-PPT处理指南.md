# PowerPoint 演示文稿完全指南

> 版本: 2.0 | 适用于: 项目管理、产品设计、中层管理

---

## 一、核心技能

### 1.1 基础操作

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN

# 创建新演示文稿
prs = Presentation()

# 添加标题幻灯片
title_slide_layout = prs.slide_layouts[0]
slide = prs.slides.add_slide(title_slide_layout)
slide.shapes.title.text = "演示文稿标题"
slide.placeholders[1].text = "副标题或描述"

# 添加内容幻灯片
content_layout = prs.slide_layouts[1]
slide = prs.slides.add_slide(content_layout)
slide.shapes.title.text = "幻灯片标题"
slide.placeholders[1].text = "内容区域"

# 保存演示文稿
prs.save('演示文稿.pptx')
```

### 1.2 幻灯片布局

```python
from pptx import Presentation

prs = Presentation()

# 可用布局 (0-9)
layouts = {
    0: "标题幻灯片",
    1: "标题和内容",
    2: "节标题",
    3: "两栏内容",
    4: "比较",
    5: "仅标题",
    6: "空白",
    7: "图片与标题",
    8: "图片与题注"
}

# 使用不同布局
for i, layout_name in layouts.items():
    slide = prs.slides.add_slide(prs.slide_layouts[i])
    slide.shapes.title.text = f"{layout_name} 示例"
```

---

## 二、文本操作

### 2.1 添加文本框

```python
from pptx.util import Inches, Pt

# 添加文本框
left = Inches(1)
top = Inches(2)
width = Inches(8)
height = Inches(1)

txBox = slide.shapes.add_textbox(left, top, width, height)
tf = txBox.text_frame
tf.text = "这是文本框中的内容"

# 添加段落
p = tf.add_paragraph()
p.text = "这是第二个段落"
p.font.size = Pt(18)
p.font.bold = True
p.alignment = PP_ALIGN.CENTER
```

### 2.2 文本格式化

```python
from pptx.util import Pt
from pptx.dml.color import RGBColor

# 设置字体属性
text_frame.text = "格式化文本示例"

# 遍历所有段落设置样式
for paragraph in text_frame.paragraphs:
    paragraph.font.name = '微软雅黑'
    paragraph.font.size = Pt(20)
    paragraph.font.bold = True
    paragraph.font.italic = False
    
    # 设置颜色（RGB）
    paragraph.font.color.rgb = RGBColor(0, 51, 102)

# 只设置特定段落
if len(text_frame.paragraphs) > 1:
    text_frame.paragraphs[1].font.size = Pt(14)
    text_frame.paragraphs[1].font.color.rgb = RGBColor(128, 128, 128)
```

### 2.3 项目符号列表

```python
# 添加项目符号列表
tf = slide.shapes.placeholders[1].text_frame
tf.text = "主要要点"

# 添加子要点
p = tf.add_paragraph()
p.text = "第一个要点"
p.level = 0

p = tf.add_paragraph()
p.text = "子要点1"
p.level = 1

p = tf.add_paragraph()
p.text = "子要点2"
p.level = 1

p = tf.add_paragraph()
p.text = "第二个要点"
p.level = 0
```

---

## 三、图表操作

### 3.1 创建图表

```python
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE

# 定义图表数据
chart_data = CategoryChartData()
chart_data.categories = ['一月', '二月', '三月', '四月']
chart_data.add_series('产品A', (20, 35, 30, 25))
chart_data.add_series('产品B', (15, 25, 20, 30))

# 添加图表
x, y, cx, cy = Inches(2), Inches(2), Inches(6), Inches(4.5)
chart = slide.shapes.add_chart(
    XL_CHART_TYPE.COLUMN_CLUSTERED,
    x, y, cx, cy,
    chart_data
).chart

# 添加标题
chart.has_title = True
chart.chart_title.text_frame.text = "季度销售数据"
```

### 3.2 常见图表类型

```python
# 柱状图
chart = slide.shapes.add_chart(
    XL_CHART_TYPE.COLUMN_CLUSTERED,
    x, y, cx, cy, chart_data
).chart

# 折线图
chart = slide.shapes.add_chart(
    XL_CHART_TYPE.LINE,
    x, y, cx, cy, chart_data
).chart

# 饼图
chart = slide.shapes.add_chart(
    XL_CHART_TYPE.PIE,
    x, y, cx, cy, chart_data
).chart

# 条形图
chart = slide.shapes.add_chart(
    XL_CHART_TYPE.BAR_CLUSTERED,
    x, y, cx, cy, chart_data
).chart

# 面积图
chart = slide.shapes.add_chart(
    XL_CHART_TYPE.AREA,
    x, y, cx, cy, chart_data
).chart
```

### 3.3 图表格式化

```python
# 设置图例
chart.has_legend = True
chart.legend.include_in_layout = False
chart.legend.font.size = Pt(10)

# 设置数据标签
plot = chart.plots[0]
plot.has_data_labels = True
data_labels = plot.data_labels
data_labels.font.size = Pt(9)
data_labels.number_format = '0%'

# 设置坐标轴
category_axis = chart.category_axis
category_axis.has_major_gridlines = False
value_axis = chart.value_axis
value_axis.has_major_gridlines = True
```

---

## 四、表格操作

### 4.1 创建表格

```python
from pptx.util import Inches

# 添加表格
rows, cols = 5, 3
left = Inches(1)
top = Inches(2)
width = Inches(8)
height = Inches(3)

table = slide.shapes.add_table(rows, cols, left, top, width, height).table

# 设置列宽
table.columns[0].width = Inches(2.0)  # 第一列宽
table.columns[1].width = Inches(3.0)  # 第二列宽
table.columns[2].width = Inches(3.0)  # 第三列宽

# 添加数据
data = [
    ['姓名', '部门', '职位'],
    ['张三', '技术部', '经理'],
    ['李四', '产品部', '主管'],
    ['王五', '设计部', '设计师']
]

for row_idx, row_data in enumerate(data):
    for col_idx, value in enumerate(row_data):
        table.cell(row_idx, col_idx).text = str(value)
```

### 4.2 表格格式化

```python
from pptx.dml.color import RGBColor

# 设置表格样式
table.style = "Table Grid"

# 设置表头样式
for col_idx in range(cols):
    cell = table.cell(0, col_idx)
    cell.fill.solid()
    cell.fill.fore_color.rgb = RGBColor(0, 51, 102)
    cell.text_frame.paragraphs[0].font.color.rgb = RGBColor(255, 255, 255)
    cell.text_frame.paragraphs[0].font.bold = True

# 设置字体
for row in table.rows:
    for cell in row.cells:
        cell.text_frame.paragraphs[0].font.name = '微软雅黑'
        cell.text_frame.paragraphs[0].font.size = Pt(11)
```

---

## 五、图片操作

### 5.1 添加图片

```python
from pptx.util import Inches

# 添加图片
left = Inches(1)
top = Inches(2)
width = Inches(5)

# 保持原始比例
slide.shapes.add_picture('image.png', left, top, width=width)

# 指定宽高
height = Inches(3)
slide.shapes.add_picture('image.jpg', left, top, width=width, height=height)
```

### 5.2 图片裁剪

```python
# 裁剪图片
picture = slide.shapes.add_picture('image.png', left, top, width=width)

# 注意：python-pptx 的裁剪功能有限
# 完整裁剪需要使用其他库处理图片后再插入
```

---

## 六、形状操作

### 6.1 添加形状

```python
from pptx.util import Inches
from pptx.enum.shapes import MSO_SHAPE

# 添加各种形状
shapes = [
    (MSO_SHAPE.RECTANGLE, "矩形"),
    (MSO_SHAPE.ROUNDED_RECTANGLE, "圆角矩形"),
    (MSO_SHAPE.OVAL, "椭圆"),
    (MSO_SHAPE.DIAMOND, "菱形"),
    (MSO_SHAPE.TRIANGLE, "三角形"),
    (MSO_SHAPE.PENTAGON, "五边形"),
    (MSO_SHAPE.STAR_5, "五角星"),
    (MSO_SHAPE.ARROW_RIGHT, "右箭头"),
    (MSO_SHAPE.SPEECH_BUBBLE, "对话框")
]

left = Inches(1)
top = Inches(2)
width = Inches(1.5)
height = Inches(1)

for i, (shape_type, name) in enumerate(shapes):
    shape = slide.shapes.add_shape(
        shape_type,
        left + i * 2, top, width, height
    )
    shape.text = name
```

### 6.2 形状格式化

```python
from pptx.dml.color import RGBColor
from pptx.util import Pt

# 设置填充颜色
shape.fill.solid()
shape.fill.fore_color.rgb = RGBColor(0, 102, 204)

# 设置边框
shape.line.color.rgb = RGBColor(0, 51, 102)
shape.line.width = Pt(2)

# 设置阴影
shape.shadow.type = MSO_SHADOW.OUTER_BOTTOM_RIGHT
shape.shadow.blur_radius = Pt(5)
shape.shadow.distance = Pt(3)
shape.shadow.direction = 225

# 设置透明度（百分比）
shape.fill.transparency = 0.2
```

---

## 七、主题和样式

### 7.1 应用主题

```python
from pptx import Presentation

# 创建带主题的演示文稿
prs = Presentation()

# 可用的主题布局
themes = [
    "Aspect", "Badge", "Berlin", "Circuit", "Damask",
    "Depth", "Equity", "Flow", "Founders", "Gallery",
    "Ion", "Madison", "Module", "Night", "Office",
    "Orbit", "Pixel", "Retreat", "Soho", "Sports",
    "Urban", "Vintage", "Wisp"
]

# 应用主题（需要主题文件）
# prs.themes.apply_theme('theme.xml')
```

### 7.2 自定义主题颜色

```python
from pptx.util import RGBColor

# 注意：主题颜色需要通过 XML 修改
# 这里演示如何手动设置颜色保持一致性

COLORS = {
    'primary': RGBColor(0, 51, 102),      # 主色（深蓝）
    'secondary': RGBColor(0, 102, 204),  # 辅色（亮蓝）
    'accent': RGBColor(255, 153, 0),     # 强调色（橙）
    'text': RGBColor(51, 51, 51),        # 正文色（深灰）
    'light': RGBColor(245, 245, 245)     # 背景色（浅灰）
}

def apply_theme_colors(shape, color_type='primary'):
    """应用主题颜色"""
    color = COLORS.get(color_type, COLORS['primary'])
    if hasattr(shape, 'fill'):
        shape.fill.solid()
        shape.fill.fore_color.rgb = color
    if hasattr(shape, 'text_frame'):
        shape.text_frame.paragraphs[0].font.color.rgb = color
```

---

## 八、动画效果

### 8.1 添加动画

```python
from pptx.enum.animation import XL_ANIMATION_TYPE, XL_ANIMATION_TRIGGER

# 获取形状
shape = slide.shapes[1]

# 添加进入动画
animation = shape.animation
animation.type = XL_ANIMATION_TYPE.FADE
animation.duration = 1.0
animation.trigger = XL_ANIMATION_TRIGGER.ON_CLICK

# 常用动画类型
anim_types = [
    ("进入", XL_ANIMATION_TYPE.FADE, "Fade"),
    ("出现", XL_ANIMATION_TYPE.APPEAR, "Appear"),
    ("飞入", XL_ANIMATION_TYPE.FLY_IN, "Fly In"),
    ("缩放", XL_ANIMATION_TYPE.ZOOM, "Zoom"),
    ("旋转", XL_ANIMATION_TYPE.SPIN, "Spin"),
    ("擦除", XL_ANIMATION_TYPE.WIPE, "Wipe"),
    ("滑入", XL_ANIMATION_TYPE.SLIDE_IN, "Slide In"),
    ("淡入", XL_ANIMATION_TYPE.FADE_IN, "Fade In")
]
```

### 8.2 动画序列

```python
# 多个元素动画序列
shapes_list = [shape1, shape2, shape3]

for i, shape in enumerate(shapes_list):
    anim = shape.animation
    anim.type = XL_ANIMATION_TYPE.FADE
    anim.duration = 0.5
    anim.delay = i * 0.3  # 延迟时间递增
    anim.trigger = XL_ANIMATION_TRIGGER.AFTER_PREVIOUS
```

---

## 九、PPTProcessor 类

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE
from pptx.dml.color import RGBColor

class PPTProcessor:
    """PowerPoint 演示文稿处理器"""
    
    def __init__(self):
        self.prs = None
        self.slide = None
    
    def create_presentation(self):
        """创建新演示文稿"""
        self.prs = Presentation()
        return self
    
    def load_presentation(self, filepath):
        """加载现有演示文稿"""
        self.prs = Presentation(filepath)
        return self
    
    def add_title_slide(self, title, subtitle=""):
        """添加标题幻灯片"""
        slide_layout = self.prs.slide_layouts[0]
        slide = self.prs.slides.add_slide(slide_layout)
        slide.shapes.title.text = title
        if subtitle:
            slide.placeholders[1].text = subtitle
        self.slide = slide
        return slide
    
    def add_content_slide(self, title, content=""):
        """添加内容幻灯片"""
        slide_layout = self.prs.slide_layouts[1]
        slide = self.prs.slides.add_slide(slide_layout)
        slide.shapes.title.text = title
        if content:
            slide.placeholders[1].text = content
        self.slide = slide
        return slide
    
    def add_text_slide(self, title, bullets):
        """添加项目符号幻灯片"""
        slide_layout = self.prs.slide_layouts[1]
        slide = self.prs.slides.add_slide(slide_layout)
        slide.shapes.title.text = title
        
        tf = slide.placeholders[1].text_frame
        tf.text = bullets[0]
        
        for bullet in bullets[1:]:
            p = tf.add_paragraph()
            p.text = bullet
        
        self.slide = slide
        return slide
    
    def add_chart(self, title, chart_type, data):
        """添加图表"""
        chart_data = CategoryChartData()
        chart_data.categories = data['categories']
        for series_name, series_data in data['series'].items():
            chart_data.add_series(series_name, series_data)
        
        x, y, cx, cy = Inches(1), Inches(2), Inches(8), Inches(4.5)
        chart = self.slide.shapes.add_chart(
            chart_type, x, y, cx, cy, chart_data
        ).chart
        
        chart.has_title = True
        chart.chart_title.text_frame.text = title
        
        return chart
    
    def add_table(self, data, title=""):
        """添加表格"""
        rows = len(data)
        cols = len(data[0]) if data else 0
        
        left = Inches(1)
        top = Inches(2) if title else Inches(1)
        width = Inches(8)
        height = Inches(0.8) * rows
        
        table = self.slide.shapes.add_table(rows, cols, left, top, width, height).table
        
        for row_idx, row_data in enumerate(data):
            for col_idx, value in enumerate(row_data):
                table.cell(row_idx, col_idx).text = str(value)
        
        return table
    
    def add_picture(self, image_path, width=None, height=None, left=None, top=None):
        """添加图片"""
        if left is None:
            left = Inches(1)
        if top is None:
            top = Inches(2)
        
        if width:
            self.slide.shapes.add_picture(image_path, left, top, width=Inches(width))
        elif height:
            self.slide.shapes.add_picture(image_path, left, top, height=Inches(height))
        else:
            self.slide.shapes.add_picture(image_path, left, top)
    
    def save(self, filepath):
        """保存演示文稿"""
        self.prs.save(filepath)
        print(f"✅ 演示文稿已保存: {filepath}")
    
    def create_project_report(self, project_info):
        """创建项目报告演示文稿"""
        
        # 封面
        self.add_title_slide(
            project_info['title'],
            f"项目经理: {project_info['manager']}\n日期: {project_info['date']}"
        )
        
        # 目录
        self.add_content_slide("目录")
        self.slide.placeholders[1].text = "\n".join([
            f"{i+1}. {section}" for i, section in enumerate(project_info['sections'])
        ])
        
        # 各章节
        for section in project_info['sections']:
            if section == '项目概览':
                self.add_text_slide(section, [
                    f"项目名称: {project_info['name']}",
                    f"当前阶段: {project_info['phase']}",
                    f"整体进度: {project_info['progress']}%",
                    f"团队规模: {project_info['team_size']}人"
                ])
            elif section == '进度统计':
                self.add_chart('任务完成情况', {
                    'categories': ['已完成', '进行中', '待开始'],
                    'series': {'任务数': [10, 5, 3]}
                })
        
        # 总结页
        self.add_content_slide("总结与展望")
        self.slide.placeholders[1].text = project_info.get('summary', '感谢关注！')
```

---

## 十、模板库

### 10.1 项目状态周报模板

```python
def create_weekly_report(prs, week_info):
    """创建项目周报"""
    
    # 封面
    slide = prs.slides.add_slide(prs.slide_layouts[0])
    slide.shapes.title.text = f"{week_info['project_name']} - 周报"
    slide.placeholders[1].text = f"第 {week_info['week']} 周 | {week_info['date_range']}"
    
    # 本周完成
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "本周完成"
    tf = slide.placeholders[1].text_frame
    for task in week_info['completed']:
        p = tf.add_paragraph()
        p.text = f"✅ {task}"
    
    # 进行中
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "进行中"
    tf = slide.placeholders[1].text_frame
    for task in week_info['in_progress']:
        p = tf.add_paragraph()
        p.text = f"🔄 {task} ({week_info['progress']}%)"
    
    # 下周计划
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "下周计划"
    tf = slide.placeholders[1].text_frame
    for task in week_info['next_week']:
        p = tf.add_paragraph()
        p.text = f"📋 {task}"
    
    # 问题与风险
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "问题与风险"
    tf = slide.placeholders[1].text_frame
    for risk in week_info['risks']:
        p = tf.add_paragraph()
        p.text = f"⚠️ {risk}"
```

### 10.2 产品演示模板

```python
def create_product_demo(prs, product_info):
    """创建产品演示"""
    
    # 封面
    slide = prs.slides.add_slide(prs.slide_layouts[0])
    slide.shapes.title.text = product_info['name']
    slide.placeholders[1].text = product_info['tagline']
    
    # 问题与解决方案
    for i, feature in enumerate(product_info['features']):
        slide = prs.slides.add_slide(prs.slide_layouts[1])
        slide.shapes.title.text = f"特性 {i+1}: {feature['title']}"
        tf = slide.placeholders[1].text_frame
        tf.text = feature['description']
        
        # 添加特性图
        if 'image' in feature:
            prs.slides.add_picture(feature['image'], 
                                   Inches(1), Inches(3), width=Inches(8))
    
    # 总结
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "总结"
    tf = slide.placeholders[1].text_frame
    for benefit in product_info['benefits']:
        p = tf.add_paragraph()
        p.text = f"✓ {benefit}"
```

---

## 十一、最佳实践

### 11.1 设计原则

1. **简洁为主**: 每页不超过 6 个要点
2. **一致风格**: 字体、颜色、对齐保持一致
3. **突出重点**: 使用粗体、颜色、图标强调关键信息
4. **图文并茂**: 适当使用图表和图片增强表达
5. **留白合理**: 保持页面呼吸感

### 11.2 制作技巧

```python
# 1. 统一字体
TITLE_FONT = '微软雅黑'
BODY_FONT = '微软雅黑'
TITLE_SIZE = Pt(36)
BODY_SIZE = Pt(18)

# 2. 统一配色
COLORS = {
    'primary': RGBColor(0, 51, 102),
    'secondary': RGBColor(0, 102, 204),
    'accent': RGBColor(255, 153, 0),
    'text': RGBColor(51, 51, 51),
    'bg': RGBColor(255, 255, 255)
}

# 3. 合理布局
LAYOUT_GUIDE = {
    'title_y': Inches(0.5),
    'content_top': Inches(1.5),
    'content_margin': Inches(1),
    'footer_y': Inches(6.8)
}
```

---

## 十二、常见问题

### Q1: 如何设置默认字体？
```python
# 遍历所有幻灯片设置字体
for slide in prs.slides:
    for shape in slide.shapes:
        if hasattr(shape, "text_frame"):
            for paragraph in shape.text_frame.paragraphs:
                paragraph.font.name = '微软雅黑'
```

### Q2: 如何添加页码？
```python
# 只能在母版视图中添加页码
# 这里使用 VBA 宏添加：
# Sub AddPageNumbers()
#     Dim sld As Slide
#     For Each sld In ActivePresentation.Slides
#         sld.Shapes.AddTextbox(msoTextOrientationHorizontal, _
#             Inches(6), Inches(7), Inches(2), Inches(0.5) _
#         ).TextFrame.TextRange.Text = sld.SlideNumber & " / " & ActivePresentation.Slides.Count
#     Next sld
# End Sub
```

### Q3: 如何导出为 PDF？
```python
# 保存为 PDF
prs.save('演示文稿.pdf')

# 注意：需要安装 Microsoft PowerPoint 或使用在线转换服务
```

### Q4: 如何压缩图片减小文件大小？
```python
# 图片压缩需要使用图片处理库
from PIL import Image

def compress_image(input_path, output_path, quality=85):
    img = Image.open(input_path)
    img.save(output_path, 'JPEG', quality=quality)
```

---

## 十三、常用资源

### 13.1 动画类型

| 类型 | XL_ANIMATION_TYPE | 说明 |
|------|-------------------|------|
| 出现 | APPEAR | 立即出现 |
| 淡入 | FADE_IN | 淡入效果 |
| 擦除 | WIPE | 从方向擦除 |
| 飞入 | FLY_IN | 飞入效果 |
| 缩放 | ZOOM | 缩放效果 |
| 旋转 | SPIN | 旋转效果 |

### 13.2 图表类型

| 类型 | XL_CHART_TYPE | 适用场景 |
|------|---------------|----------|
| 柱状图 | COLUMN_CLUSTERED | 比较不同类别 |
| 折线图 | LINE | 趋势变化 |
| 饼图 | PIE | 占比分布 |
| 条形图 | BAR_CLUSTERED | 横向比较 |
| 面积图 | AREA | 累计趋势 |
| 散点图 | XY_SCORTER | 相关性分析 |

### 13.3 形状类型

| 类型 | MSO_SHAPE | 说明 |
|------|-----------|------|
| 矩形 | RECTANGLE | 基础形状 |
| 椭圆 | OVAL | 圆形/椭圆 |
| 箭头 | ARROW_RIGHT | 指示方向 |
| 星星 | STAR_5 | 五角星 |
| 对话框 | SPEECH_BUBBLE | 标注说明 |
