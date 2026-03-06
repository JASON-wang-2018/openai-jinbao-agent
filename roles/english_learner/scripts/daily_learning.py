#!/usr/bin/env python3
"""
英语学习助手 - 每日学习任务生成器

功能:
1. 搜索英语文章
2. 生成学习材料
3. 推送飞书消息
4. 跟踪学习进度

使用方式:
    python3 daily_learning.py --mode=full      # 完整流程
    python3 daily_learning.py --mode=article    # 仅生成文章
    python3 daily_learning.py --mode=tts       # 仅生成语音
    python3 daily_learning.py --mode=progress  # 显示进度
"""

import argparse
import json
import os
from datetime import datetime
from pathlib import Path
import random

# 导入TTS工具
try:
    from tts import TTS
    HAS_TTS = True
except ImportError:
    HAS_TTS = False
    print("⚠️ TTS工具不可用，将跳过语音生成")


# ==================== 配置 ====================

BASE_PATH = Path(__file__).parent.parent
DATA_PATH = BASE_PATH / "data"
ARTICLES_PATH = DATA_PATH / "articles"
PROGRESS_FILE = DATA_PATH / "progress.json"

# 学习话题库
TOPICS = [
    "Technology and AI",
    "Education and Learning",
    "Environment and Climate",
    "Health and Wellness",
    "Career and Work",
    "Travel and Culture",
    "Science and Space",
    "Business and Economy",
    "Art and Music",
    "Food and Cooking",
]

# 难度级别
LEVELS = {
    "beginner": {"name": "初级", "vocab_range": (500, 2000)},
    "intermediate": {"name": "中级", "vocab_range": (2000, 5000)},
    "advanced": {"name": "高级", "vocab_range": (5000, 10000)}
}


# ==================== 文章生成器 ====================

class ArticleGenerator:
    """英语文章生成器"""
    
    ARTICLE_TEMPLATES = {
        "technology": {
            "title": "The Future of {topic}",
            "vocabulary": ["innovation", "disruption", "transformation", "advancement"]
        },
        "environment": {
            "title": "Protecting Our Planet: {topic}",
            "vocabulary": ["sustainability", "conservation", "ecosystem", "climate"]
        },
        "education": {
            "title": "The Evolution of {topic}",
            "vocabulary": ["pedagogy", "curriculum", "digital learning", "skills"]
        },
        "business": {
            "title": "{topic} in Modern Business",
            "vocabulary": ["strategy", "innovation", "competition", "growth"]
        }
    }
    
    @classmethod
    def generate_article(cls, topic: str = None, level: str = "intermediate") -> dict:
        """生成学习文章"""
        if topic is None:
            topic = random.choice(TOPICS)
        
        topic_lower = topic.lower()
        if "tech" in topic_lower or "ai" in topic_lower:
            template = cls.ARTICLE_TEMPLATES["technology"]
        elif "env" in topic_lower or "climate" in topic_lower:
            template = cls.ARTICLE_TEMPLATES["environment"]
        elif "educ" in topic_lower or "learn" in topic_lower:
            template = cls.ARTICLE_TEMPLATES["education"]
        else:
            template = cls.ARTICLE_TEMPLATES["business"]
        
        title = template["title"].format(topic=topic)
        vocab = template["vocabulary"] + ["important", "significant", "development"]
        
        article = {
            "title": title,
            "topic": topic,
            "level": level,
            "vocabulary": vocab,
            "created_at": datetime.now().isoformat(),
            "content": cls._generate_content(title, level)
        }
        
        return article
    
    @classmethod
    def _generate_content(cls, title: str, level: str) -> str:
        """生成文章内容"""
        intro_templates = {
            "beginner": f"Today, I want to talk about {title}. It is very important because it affects our daily life.",
            "intermediate": f"In recent years, {title} has become increasingly significant. This article explores its various aspects and implications.",
            "advanced": f"The contemporary discourse surrounding {title} necessitates a comprehensive examination of its multifaceted implications for society."
        }
        
        body_templates = {
            "beginner": "First, we need to understand this topic. For example, many people are interested in this. Also, there are many benefits.",
            "intermediate": "Several factors contribute to this phenomenon. Primarily, technological advancement plays a crucial role. Additionally, economic considerations influence outcomes. Research indicates significant potential for growth.",
            "advanced": "Empirical evidence suggests that multiple factors converge to create this paradigm. The interplay between technological innovation and socioeconomic dynamics presents both opportunities and challenges."
        }
        
        conclusion_templates = {
            "beginner": f"In conclusion, {title} is very important. We should learn more about it. Thank you for reading.",
            "intermediate": "In conclusion, this analysis reveals that the topic presents both opportunities and challenges. Future research should focus on sustainable development and practical applications.",
            "advanced": "In summation, the analysis demonstrates the necessity for strategic interventions. Future investigations should address identified gaps while practitioners ought to consider comprehensive implementations."
        }
        
        return f"## Introduction\n\n{intro_templates[level]}\n\n## Main Points\n\n{body_templates[level]}\n\n## Conclusion\n\n{conclusion_templates[level]}"


# ==================== 语音生成器 ====================

class SpeechGenerator:
    """语音生成器"""
    
    @classmethod
    def generate_speech(cls, text: str, output_file: str = None, accent: str = "us"):
        """生成语音"""
        if not HAS_TTS:
            print("⚠️ TTS工具不可用，跳过语音生成")
            return None
        
        try:
            tts = TTS()
            if output_file is None:
                output_file = f"speech_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
            
            full_path = ARTICLES_PATH / output_file
            tts.save(str(full_path), text, accent=accent)
            
            print(f"✅ 语音已保存: {full_path}")
            return str(full_path)
        except Exception as e:
            print(f"❌ 语音生成失败: {e}")
            return None


# ==================== 学习进度跟踪器 ====================

class ProgressTracker:
    """学习进度跟踪器"""
    
    def __init__(self):
        self.data = self._load_data()
    
    def _load_data(self) -> dict:
        """加载数据"""
        if PROGRESS_FILE.exists():
            with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "daily_goal": {
                "reading_minutes": 15,
                "listening_minutes": 30,
                "speaking_minutes": 15,
                "writing_words": 100,
                "vocabulary": 20
            },
            "records": []
        }
    
    def _save_data(self):
        """保存数据"""
        PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def log_activity(self, activity_type: str, duration: int, details: str = ""):
        """记录学习活动"""
        record = {
            "date": datetime.now().isoformat(),
            "type": activity_type,
            "duration": duration,
            "details": details
        }
        self.data["records"].append(record)
        self._save_data()
        print(f"✅ 已记录: {activity_type} - {duration}分钟")
    
    def get_daily_summary(self) -> dict:
        """获取今日摘要"""
        today = datetime.now().strftime("%Y-%m-%d")
        today_records = [r for r in self.data["records"] if r["date"][:10] == today]
        
        summary = {
            "date": today,
            "activities": len(today_records),
            "reading_minutes": 0,
            "listening_minutes": 0,
            "speaking_minutes": 0
        }
        
        for r in today_records:
            if r["type"] == "reading":
                summary["reading_minutes"] += r["duration"]
            elif r["type"] == "listening":
                summary["listening_minutes"] += r["duration"]
            elif r["type"] == "speaking":
                summary["speaking_minutes"] += r["duration"]
        
        return summary
    
    def show_progress(self):
        """显示进度"""
        summary = self.get_daily_summary()
        
        print(f"\n📊 {summary['date']} 学习进度")
        print("=" * 50)
        
        goals = self.data["daily_goal"]
        
        reading_bar = "█" * int(min(summary["reading_minutes"] / 5, 15)) + "░" * (15 - int(min(summary["reading_minutes"] / 5, 15)))
        print(f"📖 阅读: {summary['reading_minutes']}/{goals['reading_minutes']}分钟 [{reading_bar}]")
        
        listening_bar = "█" * int(min(summary["listening_minutes"] / 2, 30)) + "░" * (30 - int(min(summary["listening_minutes"] / 2, 30)))
        print(f"🎧 听力: {summary['listening_minutes']}/{goals['listening_minutes']}分钟 [{listening_bar}]")
        
        speaking_bar = "█" * int(min(summary["speaking_minutes"], 15)) + "░" * (15 - int(min(summary["speaking_minutes"], 15)))
        print(f"🗣️ 口语: {summary['speaking_minutes']}/{goals['speaking_minutes']}分钟 [{speaking_bar}]")
        
        print("=" * 50)


# ==================== 每日任务生成 ====================

class DailyLearningManager:
    """每日学习管理器"""
    
    def __init__(self):
        self.tracker = ProgressTracker()
    
    def generate_daily_plan(self, level: str = "intermediate") -> dict:
        """生成每日学习计划"""
        today = datetime.now().strftime("%Y-%m-%d")
        topic = random.choice(TOPICS)
        
        article = ArticleGenerator.generate_article(topic, level)
        
        plan = {
            "date": today,
            "level": level,
            "topic": topic,
            "reading": {
                "title": article["title"],
                "duration": 15,
                "vocabulary": article["vocabulary"],
                "content": article["content"]
            },
            "listening": {
                "title": f"Podcast about {topic}",
                "duration": 30
            },
            "speaking": {
                "topic": topic,
                "question": f"What is your opinion on {topic}?",
                "duration": 15
            }
        }
        
        return plan
    
    def display_daily_plan(self, plan: dict):
        """显示每日计划"""
        print(f"\n📅 {plan['date']} 英语学习计划")
        print(f"📚 难度: {LEVELS.get(plan['level'], {}).get('name', '中级')}")
        print(f"🎯 话题: {plan['topic']}")
        print("=" * 60)
        
        print(f"\n📖 阅读 (15分钟)")
        print(f"   标题: {plan['reading']['title']}")
        print(f"   词汇: {', '.join(plan['reading']['vocabulary'][:3])}")
        
        print(f"\n🎧 听力 (30分钟)")
        print(f"   标题: {plan['listening']['title']}")
        print("   任务: 泛听→精听→跟读")
        
        print(f"\n🗣️ 口语 (15分钟)")
        print(f"   话题: {plan['speaking']['topic']}")
        print(f"   问题: {plan['speaking']['question']}")
        
        print("=" * 60)
    
    def run_full_session(self, level: str = "intermediate"):
        """运行完整学习流程"""
        print("\n🚀 启动英语学习助手")
        print("=" * 60)
        
        # 1. 生成学习计划
        plan = self.generate_daily_plan(level)
        self.display_daily_plan(plan)
        
        # 2. 保存文章
        articles_dir = ARTICLES_PATH
        articles_dir.mkdir(parents=True, exist_ok=True)
        
        article_file = articles_dir / f"article_{plan['date']}.json"
        with open(article_file, 'w', encoding='utf-8') as f:
            json.dump(plan, f, ensure_ascii=False, indent=2)
        print(f"✅ 文章已保存: {article_file}")
        
        # 3. 生成语音
        if HAS_TTS:
            print("\n🔊 生成语音...")
            speech_gen = SpeechGenerator()
            
            # 词汇发音
            speech_gen.generate_speech(
                " ".join(plan["reading"]["vocabulary"][:3]),
                "vocabulary.mp3"
            )
        
        # 4. 显示进度
        self.tracker.show_progress()
        
        print("\n💡 提示: 使用 --mode=log 记录学习活动")
        
        return plan


# ==================== 主程序 ====================

def main():
    parser = argparse.ArgumentParser(
        description="英语学习助手 - 每日学习任务生成器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python3 daily_learning.py --mode=full           # 完整流程
    python3 daily_learning.py --mode=article       # 仅生成文章
    python3 daily_learning.py --mode=tts --text="Hello"  # 生成语音
    python3 daily_learning.py --mode=progress       # 显示进度
    python3 daily_learning.py --mode=log --type=reading --time=15
        """
    )
    
    parser.add_argument(
        "--mode", "-m",
        type=str,
        default="full",
        choices=["full", "article", "tts", "progress", "log"],
        help="运行模式"
    )
    
    parser.add_argument(
        "--level", "-l",
        type=str,
        default="intermediate",
        choices=["beginner", "intermediate", "advanced"],
        help="难度级别"
    )
    
    parser.add_argument(
        "--topic", "-t",
        type=str,
        default=None,
        help="指定话题"
    )
    
    parser.add_argument(
        "--text", "-s",
        type=str,
        help="要转语音的文本"
    )
    
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="语音输出文件"
    )
    
    parser.add_argument(
        "--type", "-y",
        type=str,
        default="reading",
        choices=["reading", "listening", "speaking", "writing"],
        help="学习活动类型"
    )
    
    parser.add_argument(
        "--time", "-i",
        type=int,
        default=15,
        help="学习时长"
    )
    
    parser.add_argument(
        "--details", "-d",
        type=str,
        default="",
        help="学习详情"
    )
    
    args = parser.parse_args()
    
    if args.mode == "full":
        manager = DailyLearningManager()
        manager.run_full_session(args.level)
    
    elif args.mode == "article":
        article = ArticleGenerator.generate_article(args.topic, args.level)
        print(f"\n📖 文章标题: {article['title']}")
        print(f"📚 词汇: {', '.join(article['vocabulary'])}")
        print(f"\n{article['content']}")
    
    elif args.mode == "tts":
        if not args.text:
            parser.error("--tts 模式需要 --text 参数")
        
        speech_gen = SpeechGenerator()
        speech_gen.generate_speech(args.text, args.output)
    
    elif args.mode == "progress":
        tracker = ProgressTracker()
        tracker.show_progress()
    
    elif args.mode == "log":
        tracker = ProgressTracker()
        tracker.log_activity(args.type, args.time, args.details)


if __name__ == "__main__":
    main()
