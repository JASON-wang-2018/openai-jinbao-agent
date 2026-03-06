# Excel 数据处理完全指南

> 版本: 2.0 | 适用于: 项目管理、产品设计、中层管理

---

## 一、核心技能

### 1.1 数据读取

```python
import pandas as pd

# 基本读取
df = pd.read_excel('file.xlsx')

# 指定工作表
df = pd.read_excel('file.xlsx', sheet_name='Sheet1')

# 指定行列
df = pd.read_excel('file.xlsx', sheet_name='Sheet1', 
                   header=0,        # 表头行
                   usecols='A:C',   # 指定列
                   skiprows=2)      # 跳过前2行

# 读取多个工作表
xlsx = pd.ExcelFile('file.xlsx')
dfs = {name: pd.read_excel(xlsx, sheet_name=name) for name in xlsx.sheet_names}
```

### 1.2 数据分析

```python
# 数据概览
df.head()           # 前5行
df.info()           # 数据类型和空值
df.describe()       # 统计摘要
df.shape            # (行数, 列数)

# 数据筛选
df[df['列名'] > 100]                           # 条件筛选
df[(df['列1'] > 100) & (df['列2'] == 'A')]    # 多条件
df[df['列名'].isin(['值1', '值2'])]            # 包含筛选

# 数据排序
df.sort_values('列名', ascending=False)        # 降序
df.sort_values(['列1', '列2'])                 # 多列排序

# 分组统计
df.groupby('类别列')['数值列'].sum()           # 求和
df.groupby('类别列')['数值列'].mean()          # 平均
df.groupby('类别列').size()                     # 计数
df.pivot_table(index='行', columns='列', 
               values='值', aggfunc='sum')    # 透视表
```

### 1.3 数据清洗

```python
# 处理空值
df.dropna()                                    # 删除空值行
df.fillna(0)                                   # 填充为0
df['列名'].fillna(df['列名'].mean())          # 填充平均值

# 处理重复值
df.drop_duplicates()

# 数据类型转换
df['日期'] = pd.to_datetime(df['日期'])
df['数值'] = pd.to_numeric(df['数值'], errors='coerce')

# 字符串处理
df['列名'] = df['列名'].str.strip()           # 去空格
df['列名'] = df['列名'].str.upper()           # 大写
df['列名'] = df['列名'].str.replace('旧', '新')  # 替换
```

### 1.4 Excel 写入

```python
# 写入 Excel
df.to_excel('output.xlsx', index=False, sheet_name='数据')

# 多个 sheet 写入
with pd.ExcelWriter('output.xlsx') as writer:
    df1.to_excel(writer, sheet_name='Sheet1', index=False)
    df2.to_excel(writer, sheet_name='Sheet2', index=False)

# 格式化写入
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment

book = load_workbook('output.xlsx')
sheet = book['数据']
sheet['A1'].font = Font(bold=True, size=14)
sheet['A1'].fill = PatternFill(start_color='366092', end_color='366092', fill_type='solid')
book.save('output.xlsx')
```

---

## 二、项目管理模板

### 2.1 项目进度跟踪表

```python
import pandas as pd
from datetime import datetime, timedelta

def create_progress_tracker():
    data = {
        '任务ID': ['T001', 'T002', 'T003', 'T004', 'T005'],
        '任务名称': ['需求分析', '系统设计', '开发实施', '测试验证', '部署上线'],
        '负责人': ['张三', '李四', '王五', '赵六', '张三'],
        '开始日期': [datetime.now().date() - timedelta(days=5)] * 5,
        '计划完成': [datetime.now().date() + timedelta(days=i*5+5) for i in range(5)],
        '实际完成': [None, None, None, None, None],
        '状态': ['进行中', '待开始', '待开始', '待开始', '待开始'],
        '进度(%)': [30, 0, 0, 0, 0],
        '优先级': ['高', '高', '中', '中', '高'],
        '备注': ['', '', '', '', '']
    }
    return pd.DataFrame(data)
```

### 2.2 资源分配表

```python
def create_resource_allocation():
    data = {
        '资源ID': ['R001', 'R002', 'R003', 'R004', 'R005'],
        '资源名称': ['开发工程师A', '开发工程师B', '测试工程师', 'UI设计师', '项目经理'],
        '技能': ['Python', 'Java', '自动化测试', 'Figma', '敏捷管理'],
        '可用性(%)': [80, 100, 60, 70, 90],
        '当前项目': ['项目A', '项目A', '项目B', '项目A', '项目A,项目B'],
        '成本/小时': [200, 180, 150, 220, 300],
        '联系方式': ['email1@', 'email2@', 'email3@', 'email4@', 'email5@']
    }
    return pd.DataFrame(data)
```

### 2.3 风险登记册

```python
def create_risk_register():
    data = {
        '风险ID': ['RISK001', 'RISK002', 'RISK003'],
        '风险描述': ['技术选型不成熟', '关键人员离职', '需求变更频繁'],
        '风险类别': ['技术风险', '人员风险', '需求风险'],
        '可能性': [3, 2, 4],
        '影响程度': [4, 5, 3],
        '风险等级': ['高', '中', '高'],
        '应对策略': ['增加技术调研', '加强文档建设', '建立变更流程'],
        '责任人': ['技术总监', '项目经理', '产品经理'],
        '状态': ['监控中', '已缓解', '监控中'],
        '更新日期': [datetime.now().date()] * 3
    }
    df = pd.DataFrame(data)
    df['风险等级'] = df['风险等级'].map({'高': '🔴 高', '中': '🟡 中', '低': '🟢 低'})
    return df
```

---

## 三、报告生成

### 3.1 项目状态报告

```python
def generate_project_report(progress_file, output_file):
    df = pd.read_excel(progress_file)
    
    report = []
    report.append("# 项目状态报告")
    report.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    
    # 项目概览
    total_tasks = len(df)
    completed = len(df[df['状态'] == '已完成'])
    in_progress = len(df[df['状态'] == '进行中'])
    avg_progress = df['进度(%)'].mean()
    
    report.append("## 项目概览")
    report.append(f"- 总任务数: {total_tasks}")
    report.append(f"- 已完成: {completed} ({completed/total_tasks*100:.1f}%)")
    report.append(f"- 进行中: {in_progress}")
    report.append(f"- 整体进度: {avg_progress:.1f}%\n")
    
    # 保存报告
    report_text = '\n'.join(report)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report_text)
    
    return report_text
```

---

## 四、ExcelProcessor 类

```python
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

class ExcelProcessor:
    def __init__(self):
        pass
    
    def read_excel(self, filepath, sheet_name=0):
        """读取 Excel 文件"""
        return pd.read_excel(filepath, sheet_name=sheet_name)
    
    def write_excel(self, df, filepath, sheet_name='Sheet1', index=False):
        """写入 Excel 文件"""
        df.to_excel(filepath, sheet_name=sheet_name, index=index)
    
    def format_excel(self, filepath, sheet_name='Sheet1'):
        """格式化 Excel 表格"""
        book = load_workbook(filepath)
        sheet = book[sheet_name]
        
        # 设置标题样式
        for cell in sheet[1]:
            cell.font = Font(bold=True, color='FFFFFF')
            cell.fill = PatternFill(start_color='366092', end_color='366092', fill_type='solid')
            cell.alignment = Alignment(horizontal='center', vertical='center')
        
        # 自动列宽
        for col in sheet.columns:
            max_length = 0
            column = col[0].column_letter
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = (max_length + 2) * 1.2
            sheet.column_dimensions[column].width = adjusted_width
        
        book.save(filepath)
    
    def merge_excels(self, file_list, output_file):
        """合并多个 Excel 文件"""
        all_dfs = []
        for file in file_list:
            df = pd.read_excel(file)
            df['来源文件'] = file
            all_dfs.append(df)
        
        merged = pd.concat(all_dfs, ignore_index=True)
        merged.to_excel(output_file, index=False)
        return merged
    
    def export_multiple_sheets(self, data_dict, output_file):
        """导出多个 sheet 到一个 Excel"""
        with pd.ExcelWriter(output_file) as writer:
            for sheet_name, df in data_dict.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)
```

---

## 五、最佳实践

1. **数据验证**: 读取后先用 `df.info()` 检查数据类型和空值
2. **备份原文件**: 处理前备份原始文件
3. **分步处理**: 复杂操作拆分成多步，每步保存中间结果
4. **异常处理**: 用 try-except 包裹文件操作
5. **日期处理**: 统一使用 pandas 的 datetime 格式
6. **列名规范**: 使用英文列名，避免空格和特殊字符
7. **文档记录**: 重要脚本添加注释和使用说明

---

## 六、常见问题

### Q1: 读取大文件很慢？
```python
# 使用分块读取
chunksize = 10000
for chunk in pd.read_excel('large_file.xlsx', chunksize=chunksize):
    process(chunk)
```

### Q2: 中文字符显示乱码？
```python
# 指定编码
df = pd.read_excel('file.xlsx', encoding='utf-8-sig')
```

### Q3: 如何处理合并单元格？
```python
# 使用 openpyxl 读取合并单元格
from openpyxl import load_workbook
book = load_workbook('file.xlsx')
sheet = book.active
# 获取合并单元格范围
for merged_range in sheet.merged_cells.ranges:
    print(merged_range)
```
