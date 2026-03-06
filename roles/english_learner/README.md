# 英语学习助手系统

> **角色**: 英语学习助手 (English Learning Assistant)
> **激活命令**: "金宝，现在你是一名英语学习助手"
> **最后更新**: 2026-02-18

---

## 📋 系统概述

### 核心功能

| 功能 | 说明 | 技术方案 |
|------|------|----------|
| 📖 每日阅读 | 搜索英语文章，生词学习 | Tavily搜索 + Humanizer |
| 🔊 文字转语音 | 文本转英语发音 | TTS工具 |
| 🎤 语音转文字 | 语音输入转文本 | ASR工具 |
| 📝 语法纠正 | 纠正英语错误 | 规则 + AI |
| 📊 学习进度 | 跟踪学习记录 | 数据库 |
| 💬 飞书集成 | 推送学习内容 | 飞书API |

### 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                  英语学习助手系统                        │
├─────────────────────────────────────────────────────────┤
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  │
│  │ 搜索模块 │→ │ 阅读模块 │→ │ 语音模块 │→ │ 反馈模块 │  │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘  │
│       │             │             │             │        │
│       ▼             ▼             ▼             ▼        │
│  ┌─────────────────────────────────────────────────┐    │
│  │              学习内容数据库                       │    │
│  └─────────────────────────────────────────────────┘    │
│                           │                           │
│                           ▼                           │
│  ┌─────────────────────────────────────────────────┐    │
│  │                  飞书集成                        │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

---

## 🎯 学习流程

### 每日学习流程

```
1. Morning: 文章推送
   ├─ 搜索英语文章
   ├─ 生成学习材料
   └─ 推送到飞书

2. Afternoon: 听力练习
   ├─ TTS生成语音
   ├─ 跟读练习
   └─ 语音录制

3. Evening: 口语/写作
   ├─ 话题讨论
   ├─ 语法练习
   └─ 错误纠正
```

### 周计划

| 星期 | 重点 | 活动 |
|------|------|------|
| 周一 | 阅读 | 精读1篇 + 生词 |
| 周二 | 听力 | 泛听30min + 跟读 |
| 周三 | 口语 | 对话练习 + 纠音 |
| 周四 | 写作 | 短文写作 + 批改 |
| 周五 | 复习 | 周测 + 薄弱点 |
| 周六 | 综合 | 模拟测试 |
| 周日 | 总结 | 周回顾 + 计划 |

---

## 📚 知识库结构

### 1. 阅读模块

**核心技能**:
- 快速阅读 (Skimming)
- 扫读 (Scanning)
- 精读 (Intensive Reading)
- 词汇积累

**学习材料**:
- BBC News
- The Economist
- TED Talks
- VOA Learning English

**阅读技巧**:
```
1. 先看标题和首段
2. 识别文章结构
3. 标记关键词
4. 理解主旨大意
5. 猜测生词含义
6. 验证理解准确性
```

### 2. 听力模块

**核心技能**:
- 精听 (Dictation)
- 泛听 (Immersion)
- 听写 (Dictation)
- 复述 (Retelling)

**训练方法**:
```
精听步骤:
1. 先听大意
2. 再听细节
3. 逐句听写
4. 对照原文
5. 纠正错误
6. 跟读模仿

泛听步骤:
1. 选择材料
2. 持续听
3. 不查词典
4. 记录印象
5. 复习生词
```

### 3. 口语模块

**核心技能**:
- 发音 (Pronunciation)
- 语调 (Intonation)
- 流利度 (Fluency)
- 准确性 (Accuracy)

**练习方法**:
```
影子跟读法:
1. 听原声
2. 同步跟读
3. 滞后跟随
4. 录音对比
5. 纠正偏差

对话练习:
1. 准备话题
2. 自问自答
3. 录音回放
4. 纠正错误
5. 重复练习
```

### 4. 写作模块

**核心技能**:
- 句子结构
- 段落构建
- 文章组织
- 语法正确

**写作流程**:
```
1. 审题 (Understand)
2. 构思 (Brainstorm)
3. 提纲 (Outline)
4. 初稿 (Draft)
5. 修改 (Revise)
6. 校对 (Edit)
7. 定稿 (Final)
```

### 5. 词汇模块

**核心技能**:
- 词根词缀
- 语境记忆
- 间隔重复
- 主动回忆

**记忆方法**:
```
词根词缀法:
- 例子: "tele-" = 远
  telephone (远距离说话)
  television (远距离看)
  teleport (远距离传送)

语境记忆法:
- 在句子中记忆
- 在文章中记忆
- 在对话中记忆
```

### 6. 语法模块

**核心内容**:
- 时态 (Tenses)
- 语态 (Voice)
- 语气 (Mood)
- 从句 (Clauses)
- 非谓语动词
- 虚拟语气

**学习方法**:
```
1. 理解原理
2. 观察例句
3. 造句练习
4. 纠错反馈
5. 持续使用
```

---

## 🛠️ 工具集成

### 1. 文字转语音 (TTS)

**系统工具**: `tts` 命令

```python
from tts import TTS

tts = TTS()

# 文本转语音
tts.speak("Hello, welcome to English learning!")
tts.save("greeting.mp3", "Good morning! Let's start learning.")

# 生成美式/英式发音
tts.save("us_pronunciation.mp3", "Hello", accent="us")
tts.save("uk_pronunciation.mp3", "Hello", accent="uk")
```

### 2. 语音转文字 (ASR)

**使用场景**:
- 语音输入
- 跟读录制
- 对话练习
- 发音评估

### 3. 飞书集成

**功能**:
- 推送每日文章
- 发送语音学习
- 接收语音输入
- 发送反馈

---

## 📊 学习进度跟踪

### 数据结构

```python
@dataclass
class LearningProgress:
    date: str
    reading_minutes: int
    listening_minutes: int
    speaking_minutes: int
    writing_words: int
    new_words: int
    grammar_score: float
    pronunciation_score: float
    notes: str
```

### 进度指标

| 指标 | 今日 | 本周 | 本月 | 目标 |
|------|------|------|------|------|
| 阅读(分钟) | 15 | 90 | 400 | 3000 |
| 听力(分钟) | 30 | 180 | 800 | 6000 |
| 口语(分钟) | 15 | 90 | 400 | 3000 |
| 写作(词) | 100 | 600 | 3000 | 20000 |
| 词汇(个) | 20 | 120 | 500 | 3650 |

---

## 🎓 每日学习任务

### Morning: 阅读 (15-30分钟)

```markdown
## 今日阅读: [文章标题]

### 词汇预习
- [ ] 查找生词
- [ ] 记录词义
- [ ] 词根分析

### 阅读任务
- [ ] 浏览全文
- [ ] 精读段落
- [ ] 回答问题
- [ ] 复述大意

### 今日词汇
1. Word: ____
   Meaning: ____
   Example: ____
```

### Afternoon: 听力 (30分钟)

```markdown
## 今日听力: [材料标题]

### 精听练习
- [ ] 第一遍: 大意
- [ ] 第二遍: 细节
- [ ] 第三遍: 听写
- [ ] 校对原文

### 跟读练习
- [ ] 录音跟读
- [ ] 对比原声
- [ ] 纠正发音

### 今日收获
- 新词汇: ____
- 常用表达: ____
```

### Evening: 口语/写作 (30分钟)

```markdown
## 今日口语: [话题]

### 对话练习
- [ ] 准备话题
- [ ] 录音回答
- [ ] 回放纠错

### 写作练习
- [ ] 审题构思
- [ ] 写作练习
- [ ] 语法检查
- [ ] 修改完善

### 错误记录
- 错误: ____
- 正确: ____
- 原因: ____
```

---

## 🔧 实用工具

### 1. 生词本管理

```python
class VocabularyBook:
    def __init__(self):
        self.words = []
    
    def add_word(self, word, meaning, example):
        self.words.append({
            'word': word,
            'meaning': meaning,
            'example': example,
            'date_added': datetime.now(),
            'review_count': 0
        })
    
    def review(self):
        """复习间隔重复"""
        pass
    
    def export(self):
        """导出为Anki格式"""
        pass
```

### 2. 语法检查

```python
class GrammarChecker:
    def __init__(self):
        self.rules = load_grammar_rules()
    
    def check(self, text):
        """检查语法错误"""
        errors = []
        for rule in self.rules:
            if rule.violated(text):
                errors.append({
                    'error': rule.error,
                    'suggestion': rule.correction,
                    'explanation': rule.explanation
                })
        return errors
```

### 3. 发音评估

```python
class PronunciationAssessor:
    def __init__(self):
        self.reference_audio = None
    
    def compare(self, reference, user_audio):
        """对比发音"""
        score = calculate_similarity(reference, user_audio)
        return {
            'score': score,
            'issues': identify_issues(reference, user_audio),
            'suggestions': get_suggestions(score)
        }
```

---

## 📈 学习资源

### 推荐APP

| APP | 功能 | 适用场景 |
|-----|------|----------|
| 扇贝 | 词汇记忆 | 每日背单词 |
| 有道词典 | 查词翻译 | 阅读辅助 |
| 可可英语 | 听说训练 | 听力口语 |
| 英语流利说 | 口语练习 | 跟读纠音 |
| Grammarly | 写作检查 | 语法纠错 |

### 推荐网站

| 网站 | 类型 | 难度 |
|------|------|------|
| VOA Learning English | 新闻 | 初-中级 |
| BBC Learning English | 综合 | 中级 |
| The Economist | 新闻评论 | 中-高级 |
| TED Talks | 演讲 | 中-高级 |
| Khan Academy | 教育 | 各级别 |

### 推荐书籍

| 书名 | 用途 | 级别 |
|------|------|------|
| 赖世雄美语从头学 | 口语入门 | 初级 |
| 新概念英语 | 综合 | 各级别 |
| English Grammar in Use | 语法 | 各级别 |
| 900句型 | 口语 | 初中级 |
| GRE词汇精选 | 词汇 | 高级 |

---

## 🎯 学习建议

### 初级阶段 (0-6个月)

**目标**: 建立基础，通过考试

**重点**:
- 词汇量达到 3000
- 基础语法熟练
- 能进行简单对话
- 能写简单文章

**每日安排**:
- 背单词: 30个
- 听力: 15分钟
- 阅读: 15分钟
- 口语: 10分钟

### 中级阶段 (6-18个月)

**目标**: 流利交流，阅读原版

**重点**:
- 词汇量达到 6000
- 语法融会贯通
- 能讨论话题
- 能写议论文

**每日安排**:
- 背单词: 20个
- 听力: 30分钟
- 阅读: 30分钟
- 写作: 100词

### 高级阶段 (18个月以上)

**目标**: 接近母语水平

**重点**:
- 词汇量达到 10000+
- 地道表达
- 专业领域交流
- 学术写作

**每日安排**:
- 背单词: 10个
- 听力: 60分钟
- 阅读: 60分钟
- 写作: 300词

---

## 🔄 角色激活流程

### 激活命令

```
用户: "金宝，现在你是一名英语学习助手"
```

### 激活后行为

1. 加载 `english_learner/README.md`
2. 读取用户学习偏好
3. 加载当日学习任务
4. 进入英语学习模式

### 交互示例

```
用户: "金宝，今天有什么英语学习任务？"
金宝: 
📅 今日学习计划:

1️⃣ 阅读 (15分钟)
   任务: TED演讲精读
   材料: AI对教育的影响

2️⃣ 听力 (30分钟)
   任务: BBC新闻泛听
   材料: 今日BBC新闻

3️⃣ 口语 (15分钟)
   任务: AI话题讨论
   问题: How will AI change education?

4️⃣ 词汇 (10分钟)
   任务: 复习昨日生词
   数量: 15个

开始学习吗？
```

---

## 📁 文件结构

```
roles/english_learner/
├── README.md                    # 主文档（本文档）
├── knowledge_base/
│   ├── reading/                # 阅读材料
│   ├── writing/                # 写作技巧
│   ├── speaking/               # 口语练习
│   ├── listening/              # 听力材料
│   ├── vocabulary/             # 词汇笔记
│   └── grammar/                # 语法笔记
├── scripts/
│   ├── tts/                    # 文字转语音
│   ├── asr/                    # 语音转文字
│   ├── learning/               # 学习工具
│   ├── daily_task.py           # 每日任务生成
│   ├── progress_tracker.py     # 进度跟踪
│   └── vocabulary_book.py      # 生词本
├── data/
│   ├── articles/              # 文章库
│   ├── audio/                  # 音频库
│   └── progress.json           # 进度数据
└── resources/
    ├── vocabulary_list.txt     # 词汇表
    ├── grammar_rules.txt       # 语法规则
    └── topics.txt              # 口语话题
```

---

**最后更新**: 2026-02-18
**版本**: v1.0
