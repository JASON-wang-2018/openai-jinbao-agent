#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中层管理者知识库数据库初始化脚本
初始化 SQLite 数据库并导入初始数据
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), '../data/management_knowledge.db')

def init_database():
    """初始化数据库"""
    
    # 创建数据库连接
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 启用外键约束
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # 创建表
    tables = [
        # 知识分类表
        """
        CREATE TABLE IF NOT EXISTS knowledge_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            parent_id INTEGER DEFAULT 0,
            description TEXT,
            icon TEXT,
            sort_order INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        # 知识点表
        """
        CREATE TABLE IF NOT EXISTS knowledge_points (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            content TEXT,
            key_takeaways TEXT,
            examples TEXT,
            tags TEXT,
            importance INTEGER DEFAULT 3,
            difficulty INTEGER DEFAULT 2,
            read_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES knowledge_categories(id)
        )
        """,
        # 管理模型表
        """
        CREATE TABLE IF NOT EXISTS management_models (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            category TEXT NOT NULL,
            description TEXT,
            formula TEXT,
            application_scenario TEXT,
            steps TEXT,
            examples TEXT,
            limitations TEXT,
            resources TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        # 工具模板表
        """
        CREATE TABLE IF NOT EXISTS templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            category TEXT,
            description TEXT,
            content_template TEXT,
            fields TEXT,
            usage_guide TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        # 案例库表
        """
        CREATE TABLE IF NOT EXISTS cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            problem TEXT,
            analysis TEXT,
            solution TEXT,
            result TEXT,
            lessons TEXT,
            tags TEXT,
            views INTEGER DEFAULT 0,
            rating INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        # 常见问题表
        """
        CREATE TABLE IF NOT EXISTS faqs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            category TEXT NOT NULL,
            keywords TEXT,
            views INTEGER DEFAULT 0,
            useful_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        # 学习进度表
        """
        CREATE TABLE IF NOT EXISTS learning_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            item_type TEXT NOT NULL,
            item_id INTEGER NOT NULL,
            status TEXT DEFAULT 'not_started',
            progress_percent INTEGER DEFAULT 0,
            notes TEXT,
            last_accessed TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, item_type, item_id)
        )
        """,
        # 收藏夹表
        """
        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            item_type TEXT NOT NULL,
            item_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, item_type, item_id)
        )
        """,
        # 技能清单表
        """
        CREATE TABLE IF NOT EXISTS skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            category TEXT NOT NULL,
            description TEXT,
            level_required INTEGER,
            sub_skills TEXT,
            related_resources TEXT,
            practice_methods TEXT,
            assessment_criteria TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        # 行动清单表
        """
        CREATE TABLE IF NOT EXISTS action_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            category TEXT,
            priority INTEGER DEFAULT 3,
            due_date DATE,
            status TEXT DEFAULT 'pending',
            completed_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    ]
    
    for table_sql in tables:
        cursor.execute(table_sql)
    
    # 创建索引
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_knowledge_category ON knowledge_points(category_id)",
        "CREATE INDEX IF NOT EXISTS idx_knowledge_tags ON knowledge_points(tags)",
        "CREATE INDEX IF NOT EXISTS idx_cases_category ON cases(category)",
        "CREATE INDEX IF NOT EXISTS idx_faqs_category ON faqs(category)",
        "CREATE INDEX IF NOT EXISTS idx_progress_user ON learning_progress(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_actions_user_status ON action_items(user_id, status)"
    ]
    
    for index_sql in indexes:
        cursor.execute(index_sql)
    
    # 插入初始数据
    insert_initial_data(cursor)
    
    # 提交并关闭
    conn.commit()
    conn.close()
    
    print(f"✅ 数据库初始化完成: {DB_PATH}")
    print(f"📊 数据库大小: {os.path.getsize(DB_PATH) / 1024:.2f} KB")


def insert_initial_data(cursor):
    """插入初始数据"""
    
    # 分类数据
    categories = [
        (1, '角色定位', 0, '中层管理者的角色认知', '🎯', 1),
        (2, '产品设计', 0, '产品思维与方法论', '📦', 2),
        (3, '项目管理', 0, '项目规划与执行', '📊', 3),
        (4, '团队管理', 0, '团队建设与人才发展', '👥', 4),
        (5, '向上管理', 0, '与上级有效协作', '📈', 5),
        (6, '横向协作', 0, '跨部门沟通与合作', '🔗', 6),
        (7, '自我管理', 0, '时间与精力管理', '🧘', 7),
        (8, '职场软技能', 0, '沟通、影响力与决策', '🛠️', 8),
        # 子分类
        (9, '核心角色', 1, '三大核心角色解析', None, 1),
        (10, '工作节奏', 1, '日常工作节奏规划', None, 2),
        (11, '需求分析', 2, '需求收集与筛选', None, 1),
        (12, '产品迭代', 2, '产品迭代方法论', None, 2),
        (13, '项目规划', 3, 'WBS与里程碑', None, 1),
        (14, '进度管控', 3, '进度跟踪与风险管理', None, 2),
        (15, '团队建设', 4, '团队发展阶段管理', None, 1),
        (16, '绩效管理', 4, 'OKR与绩效面谈', None, 2),
        (17, '高效汇报', 5, '汇报技巧与结构', None, 1),
        (18, '资源争取', 5, '向上争取资源', None, 2),
        (19, '跨部门沟通', 6, '跨部门协作方法', None, 1),
        (20, '会议效率', 6, '高效会议技巧', None, 2),
        (21, '时间管理', 7, '优先级与时间分配', None, 1),
        (22, '压力管理', 7, '压力应对与调节', None, 2),
        (23, '沟通技巧', 8, '表达与倾听', None, 1),
        (24, '影响力', 8, '建立个人影响力', None, 2),
        (25, '决策能力', 8, '决策流程与方法', None, 3)
    ]
    
    cursor.executemany(
        """INSERT OR IGNORE INTO knowledge_categories 
           (id, name, parent_id, description, icon, sort_order) 
           VALUES (?, ?, ?, ?, ?, ?)""",
        categories
    )
    
    # 核心管理模型
    models = [
        ('SMART目标', '目标管理', '制定清晰可执行的目标', 
         'S+M+A+R+T', '目标设定',
         '["明确具体(Specific)","可衡量(Measurable)","可达成(Achievable)","相关性(Relevant)","有时限(Time-bound)"]',
         '本季度将用户留存率从60%提升至70%'),
        
        ('OKR目标', '目标管理', '目标与关键结果框架',
         'Objective + Key Results', '季度规划',
         '["设定目标(Objective)","分解关键结果(Key Results)","对齐公司目标","定期review","评分复盘"]',
         'Objective: 提升团队交付质量; KR1: 缺陷率降低30%'),
         
        ('WBS分解', '项目管理', '工作分解结构',
         '项目→阶段→任务→活动', '项目规划',
         '["明确项目目标","识别主要阶段","分解为工作包","分解为具体任务","分配责任和资源"]',
         '上线项目→需求阶段→用户调研→访谈10个用户'),
         
        ('KANO模型', '产品设计', '需求分类与优先级',
         '基本型→期望型→兴奋型', '需求分析',
         '["收集用户反馈","分类需求类型","确定优先级","差异化竞争"]',
         '基本型：登录功能; 期望型：快速登录; 兴奋型：AI推荐'),
         
        ('5W2H分析', '问题解决', '系统化问题分析工具',
         'What+Why+Who+When+Where+How+How much', '问题分析',
         '["What: 做什么?","Why: 为什么?","Who: 谁来做?","When: 何时?","Where: 何地?","How: 怎么做?","How much: 多少?"]',
         '团队执行力差→分析原因→制定对策'),
         
        ('STAR法则', '沟通表达', '结构化表达框架',
         'Situation+Task+Action+Result', '汇报与面试',
         '["描述背景(S)","说明任务(T)","阐述行动(A)","展示结果(R)"]',
         '在XX项目中担任项目经理，带领5人团队，3个月完成XX功能上线'),
         
        ('艾森豪威尔矩阵', '时间管理', '优先级分类工具',
         '重要性×紧急性', '日常工作安排',
         '["区分重要与紧急","按象限安排工作","聚焦第二象限","减少第四象限"]',
         '重要紧急: 立即处理; 重要不紧急: 计划执行'),
         
        ('PDCA循环', '持续改进', '质量管理循环',
         'Plan→Do→Check→Act', '持续改进',
         '["制定计划(Plan)","执行计划(Do)","检查结果(Check)","改进优化(Act)"]',
         '质量问题→分析原因→制定对策→验证效果→标准化'),
         
        ('SWOT分析', '战略分析', '战略分析工具',
         'Strengths+Weaknesses+Opportunities+Threats', '战略制定',
         '["分析优势(S)","识别劣势(W)","发现机会(O)","警惕威胁(T)","制定策略"]',
         '团队能力SWOT分析'),
         
        ('六顶思考帽', '团队决策', '多角度思考工具',
         '白+红+黑+黄+绿+蓝', '团队决策',
         '["白帽: 事实数据","红帽: 直觉感受","黑帽: 风险问题","黄帽: 积极价值","绿帽: 创新方案","蓝帽: 总结控制"]',
         '重大决策讨论')
    ]
    
    cursor.executemany(
        """INSERT OR IGNORE INTO management_models 
           (name, category, description, formula, application_scenario, steps, examples) 
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        models
    )
    
    # 常见问题
    faqs = [
        ('团队成员执行力差怎么办？', 
         '诊断思路：\n1. 能力问题 → 培训赋能\n2. 意愿问题 → 激励沟通\n3. 资源问题 → 提供支持\n4. 流程问题 → 优化流程\n\n解决措施：\n1. 明确目标（SMART）\n2. 提供方法（培训/工具）\n3. 跟进检查（定期review）\n4. 正向激励（认可/奖励）\n5. 负向约束（绩效考核）',
         '团队管理', '执行力 团队 管理', 0, 0),
         
        ('跨部门协作困难怎么办？',
         '根本原因：\n1. 目标不一致\n2. 考核不统一\n3. 沟通不顺畅\n4. 利益不匹配\n\n解决策略：\n1. 上升到共同目标\n2. 建立联合项目组\n3. 明确责任边界\n4. 定期同步机制\n5. 高层领导背书\n6. 利益共享机制',
         '横向协作', '跨部门 协作 沟通', 0, 0),
         
        ('上级决策不合理怎么办？',
         '应对原则：\n1. 先执行，后反馈（除非有重大风险）\n2. 理解背景（可能有你不知道的信息）\n3. 提供数据（用事实说话）\n4. 提出方案（不要只抱怨）\n5. 适时坚持（专业判断要坚守）\n6. 服从大局（最终要执行）',
         '向上管理', '向上管理 汇报 决策', 0, 0),
         
        ('团队士气低落怎么办？',
         '诊断士气来源：\n1. 任务压力 → 调整节奏\n2. 发展前景 → 明确晋升\n3. 人际关系 → 化解矛盾\n4. 工作价值 → 赋予意义\n5. 领导方式 → 改进管理\n\n激励措施：\n1. 认可表扬（及时、正面）\n2. 成长机会（挑战性任务）\n3. 团队活动（增强凝聚力）\n4. 授权赋能（信任下属）\n5. 公平公正（透明规则）',
         '团队管理', '士气 激励 团队建设', 0, 0),
         
        ('如何平衡业务与管理？',
         '核心原则：\n1. 业务是基础（不能脱离业务）\n2. 管理是杠杆（放大团队效能）\n3. 逐步放手（从亲力亲为到授权）\n4. 抓大放小（聚焦关键事项）\n\n时间配比建议：\n1. 业务（40%）：保持专业敏感度\n2. 管理（40%）：团队建设、目标达成\n3. 沟通（15%）：上下左右协调\n4. 学习（5%）：持续提升',
         '自我管理', '时间管理 平衡 业务 管理', 0, 0)
    ]
    
    cursor.executemany(
        """INSERT OR IGNORE INTO faqs 
           (question, answer, category, keywords, views, useful_count) 
           VALUES (?, ?, ?, ?, ?, ?)""",
        faqs
    )
    
    # 技能清单
    skills = [
        ('目标管理', '自我管理', '设定和分解目标的能力',
         2, '["SMART原则","OKR","KPI制定"]', 'SKILL.md目标管理章节', '["定期制定目标","分解到团队","跟踪反馈"]', '目标达成率'),
         
        ('项目管理', '项目管理', '规划、执行和控制项目的能力',
         3, '["WBS分解","进度管理","风险管理"]', 'SKILL.md项目管理章节', '["使用项目管理工具","定期项目复盘","风险预判"]', '项目按时交付率'),
         
        ('团队管理', '团队管理', '建设和领导团队的能力',
         3, '["团队建设","绩效管理","冲突解决"]', 'SKILL.md团队管理章节', '["定期一对一","团队活动","及时反馈"]', '团队满意度、员工留存率'),
         
        ('沟通表达', '职场软技能', '清晰表达观点的能力',
         2, '["金字塔原理","STAR法则","倾听技巧"]', 'SKILL.md沟通技巧章节', '["结构化表达练习","主动倾听","反馈练习"]', '沟通效率、误解次数'),
         
        ('决策能力', '职场软技能', '分析和做出决策的能力',
         3, '["数据分析","方案评估","风险判断"]', 'SKILL.md决策能力章节', '["案例分析练习","决策复盘","风险评估"]', '决策质量、决策速度'),
         
        ('时间管理', '自我管理', '有效利用时间的能力',
         2, '["优先级矩阵","精力管理","番茄工作法"]', 'SKILL.md时间管理章节', '["每日规划","时间追踪","定期复盘"]', '任务完成率、效率提升'),
         
        ('向上管理', '向上管理', '与上级有效协作的能力',
         2, '["高效汇报","资源争取","接受反馈"]', 'SKILL.md向上管理章节', '["定期汇报练习","主动沟通","数据支撑"]', '上级满意度、资源获取率'),
         
        ('跨部门协作', '横向协作', '跨部门有效合作的能力',
         2, '["利益分析","共识建立","资源整合"]', 'SKILL.md横向协作章节', '["定期跨部门会议","建立协作机制","利益共享"]', '协作效率、冲突次数')
    ]
    
    cursor.executemany(
        """INSERT OR IGNORE INTO skills 
           (name, category, description, level_required, sub_skills, related_resources, practice_methods, assessment_criteria) 
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        skills
    )
    
    print("✅ 初始数据插入完成")


if __name__ == "__main__":
    print("🚀 初始化中层管理者知识库数据库...")
    print(f"📁 数据库路径: {DB_PATH}")
    print("-" * 50)
    init_database()
    print("-" * 50)
    print("✨ 数据库初始化成功！")
