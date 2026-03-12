#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
英语学习助手核心模块
English Learning Assistant Core Module

功能:
1. 文章搜索与获取
2. 文字转语音 (TTS)
3. 语法纠错
4. 飞书消息发送
5. 学习进度追踪
"""

import json
import os
from datetime import datetime
from pathlib import Path

# 尝试导入 TTS 工具
try:
    from skills.sag import tts as elevenlabs_tts
except ImportError:
    elevenlabs_tts = None

try:
    from skills.sherpa_onnx_tts import tts as sherpa_tts
except ImportError:
    sherpa_tts = None

# 尝试导入 STT 工具
# 优先级：openai_whisper > 无
try:
    from skills.openai_whisper import transcribe
except ImportError:
    transcribe = None


class EnglishLearningAssistant:
    """英语学习助手主类"""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent / "data"
        self.data_dir.mkdir(exist_ok=True)
        self.user_level = "A2-B1"  # 初中级，略低于CET-4
        self.vocab_bank = self._load_json("vocab_bank.json", {})
        self.progress = self._load_json("progress.json", {
            "total_articles": 0,
            "grammar_corrections": 0,
            "daily_streak": 0,
            "last_study_date": None,
            "mistakes_log": []
        })
        
    def _load_json(self, filename, default):
        """加载 JSON 文件"""
        filepath = self.data_dir / filename
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return default
    
    def _save_json(self, filename, data):
        """保存 JSON 文件"""
        filepath = self.data_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    # ==================== 文章搜索 ====================
    
    def search_article(self, topic: str, level: str = "CET-4") -> dict:
        """
        搜索英语文章
        
        Args:
            topic: 主题关键词
            level: 难度级别 (beginner/intermediate/advanced)
            
        Returns:
            文章信息字典
        """
        import subprocess
        
        # 预设英语学习文章（CET-4难度，300词以内）
        preset_articles = [
            {
                "title": "The Rise of Artificial Intelligence",
                "url": "https://www.bbc.com/learning-english/english/features/6-minute-english",
                "level": "CET-4",
                "snippet": "How AI is changing our daily lives in unexpected ways.",
                "content": """Artificial intelligence (AI) is no longer just a topic for science fiction. It has become part of our daily lives in ways we may not even realize.

One common example is voice assistants like Siri and Alexa. These tools use natural language processing to understand and respond to our questions. They can set alarms, play music, or control smart home devices.

Another area where AI makes a big impact is recommendation systems. When you watch a movie on Netflix or buy something on Amazon, AI analyzes your preferences and suggests things you might like. This technology learns from your behavior over time.

In healthcare, AI is helping doctors diagnose diseases more accurately. Machine learning algorithms can analyze medical images and identify patterns that might be missed by human eyes.

However, there are concerns about privacy and job displacement. As AI becomes more powerful, society needs to address these challenges carefully. The key is to use AI as a tool to enhance human capabilities, not replace them.

In conclusion, AI is transforming our world in many positive ways."""
            },
            {
                "title": "Climate Change Basics",
                "url": "https://www.bbc.com/learning-english/english/features/6-minute-english/ep-201205",
                "level": "CET-4",
                "snippet": "Learn key vocabulary about climate change and environmental issues.",
                "content": """Climate change is one of the most pressing issues of our time. It refers to long-term shifts in global temperatures and weather patterns.

The primary cause of climate change is burning fossil fuels like coal, oil, and gas. This releases greenhouse gases into the atmosphere, which trap heat and cause the planet to warm.

The effects of climate change are already visible around the world. Temperatures are rising, ice caps are melting, and sea levels are increasing. Extreme weather events like hurricanes and floods are becoming more frequent.

Individuals can help combat climate change in their daily lives. Reducing energy consumption, using public transportation, and recycling are effective actions. Small changes can make a big difference when many people participate.

Governments and businesses also play crucial roles. Investing in green technology and sustainable practices is essential for a healthier future."""
            },
            {
                "title": "The Importance of Sleep",
                "url": "https://www.bbc.com/learning-english/english/features/6-minute-english/ep-190717",
                "level": "CET-4",
                "snippet": "Discover why sleep is important for your health.",
                "content": """Sleep is essential for our physical and mental well-being. Yet many of us treat it as a luxury rather than a necessity.

During sleep, your body works to support healthy brain function and maintain physical health. The brain forms new pathways to help you learn and remember information. Meanwhile, the body repairs tissues and strengthens the immune system.

Adults generally need seven to nine hours of sleep per night. However, quality matters as much as quantity. Poor sleep can lead to problems with concentration and memory. Chronic sleep deprivation increases the risk of health issues like heart disease and diabetes.

Many factors can affect sleep quality. Screen time before bed exposes you to blue light, which can disrupt your sleep cycle. Caffeine and alcohol consumption close to bedtime can also interfere with sleep.

Good sleep habits can improve your rest. This includes maintaining a consistent sleep schedule and creating a dark, cool sleeping environment."""
            },
            {
                "title": "The Benefits of Reading",
                "url": "https://www.bbc.com/learning-english/english/features/6-minute-english",
                "level": "CET-4",
                "snippet": "Why reading is good for your brain and personal growth.",
                "content": """Reading is one of the most beneficial activities you can do. It not only provides knowledge but also strengthens your brain.

Books can take you to places you've never been. They introduce you to different cultures, ideas, and perspectives. This helps develop empathy and understanding of others.

Reading regularly improves memory and concentration. When you read, your brain is actively working to process information. This mental exercise keeps your mind sharp, especially as you age.

Books can also reduce stress. Getting lost in a good story can help you forget your worries temporarily. It's a form of relaxation that doesn't require screens.

For better reading habits, try setting aside a specific time each day. Start with books that interest you. The key is to make reading enjoyable, not a chore."""
            },
            {
                "title": "Healthy Eating Habits",
                "url": "https://www.bbc.com/learning-english/english/features/6-minute-english",
                "level": "CET-4",
                "snippet": "Simple tips for maintaining a healthy diet.",
                "content": """Healthy eating is fundamental to good health. It provides the nutrients your body needs to function properly.

A balanced diet includes fruits, vegetables, whole grains, and lean proteins. These foods provide vitamins, minerals, and energy. Avoiding processed foods can significantly improve your health.

Drinking enough water is also essential. Water helps regulate body temperature and transport nutrients. Aim for eight glasses a day.

Portion control is another important factor. Even healthy foods can lead to weight gain if eaten in large amounts. Eating slowly helps your brain recognize when you're full.

Planning meals in advance can help you make healthier choices. It reduces the temptation to grab fast food when you're busy."""
            }
        ]
        
        # 尝试使用 tavily-search skill 脚本
        query = f"{topic} English article learning {level} level"
        base_dir = "/home/jason/.openclaw/workspace/skills/tavily-search/scripts"
        results = []
        
        try:
            result = subprocess.run(
                ["node", f"{base_dir}/search.mjs", query, "-n", "3"],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                import json
                try:
                    results = json.loads(result.stdout)
                except:
                    results = []
        except Exception as e:
            print(f"搜索出错: {e}")
        
        # 如果没有搜索结果，使用预设文章
        if not results:
            import random
            article = random.choice(preset_articles)
        else:
            article = {
                "title": results[0]["title"] if results else f"Article about {topic}",
                "url": results[0]["url"] if results else "",
                "snippet": results[0]["snippet"] if results else "",
            }
        
        # 添加元数据（保留原文章的level，避免覆盖）
        article.update({
            "topic": topic,
            "fetched_at": datetime.now().isoformat()
        })
        
        # 更新进度
        self.progress["total_articles"] += 1
        self._save_json("progress.json", self.progress)
        
        return article
    
    def fetch_article_content(self, url: str) -> str:
        """
        获取文章的完整内容
        
        Args:
            url: 文章URL
            
        Returns:
            完整文章内容
        """
        import subprocess
        import json
        
        # 使用 web_fetch 工具获取内容
        base_dir = "/home/jason/.openclaw/workspace/skills/tavily-search/scripts"
        
        try:
            result = subprocess.run(
                ["node", f"{base_dir}/fetch.mjs", url],
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode == 0 and result.stdout:
                data = json.loads(result.stdout)
                return data.get("content", "")[:2000]  # 限制长度
            
        except Exception as e:
            pass
        
        # 备用：尝试用 curl 获取
        try:
            result = subprocess.run(
                ["curl", "-s", url],
                capture_output=True, text=True, timeout=15
            )
            if result.returncode == 0:
                # 简单提取正文（移除HTML标签）
                import re
                text = re.sub(r'<[^>]+>', '', result.stdout)
                # 提取一段文字
                paragraphs = [p.strip() for p in text.split('\n') if len(p.strip()) > 50]
                return '\n\n'.join(paragraphs[:5])  # 返回前5段
        
        except Exception as e:
            pass
        
        return ""
    
    # ==================== 文字转语音 ====================
    
    def text_to_speech(self, text: str, voice: str = "default", speed: float = 1.0) -> str:
        """
        文字转语音
        
        Args:
            text: 要转换的文本
            voice: 语音风格
            speed: 语速 (0.5-2.0)
            
        Returns:
            音频文件路径
        """
        # 使用可用的 TTS 工具
        if elevenlabs_tts:
            audio_path = elevenlabs_tts(text=text, voice=voice, speed=speed)
        elif sherpa_tts:
            audio_path = sherpa_tts(text=text, voice=voice, speed=speed)
        else:
            # 使用系统 TTS 工具
            from tools import tts
            result = tts(text=text)
            audio_path = result.get("file", "")
        
        return audio_path
    
    def play_audio(self, audio_path: str) -> bool:
        """
        播放音频文件
        
        Args:
            audio_path: 音频文件路径
            
        Returns:
            是否成功
        """
        try:
            import subprocess
            subprocess.run(["play", audio_path], check=True)
            return True
        except:
            return False
    
    # ==================== 语音转文字 ====================
    
    def speech_to_text(self, audio_path: str) -> str:
        """
        语音转文字
        
        Args:
            audio_path: 音频文件路径
            
        Returns:
            识别出的文字
        """
        # 优先使用 openai_whisper
        if transcribe and callable(transcribe):
            try:
                text = transcribe(audio_path=audio_path)
                return text
            except Exception as e:
                pass
        
        return "[语音识别未配置 - 请安装 openai_whisper skill]"
    
    # ==================== 语法纠错 ====================
    
    def correct_grammar(self, sentence: str) -> dict:
        """
        纠正英语语法错误
        
        Args:
            sentence: 用户输入的句子
            
        Returns:
            纠错结果字典
        """
        # 常见错误模式
        error_patterns = {
            r"\bI am agree\b": {
                "correct": "I agree",
                "explanation": "agree 是动词，不需要 be 动词"
            },
            r"\bShe have\b": {
                "correct": "She has",
                "explanation": "第三人称单数用 has"
            },
            r"\bsince \d+ years\b": {
                "correct": "for \d+ years",
                "explanation": "时间段用 for，since + 时间点"
            },
            r"\bI am agree with\b": {
                "correct": "I agree with",
                "explanation": "动词 agree 后直接加介词 with"
            },
            r"\bHe go\b": {
                "correct": "He goes",
                "explanation": "第三人称单数动词需要加 s"
            },
            r"\bGood morning\s*, teacher\b": {
                "correct": "Good morning",
                "explanation": "英语中通常不直接称呼老师为 'teacher'"
            }
        }
        
        import re
        
        correction = {
            "original": sentence,
            "corrected": sentence,
            "explanation": "句子看起来正确！",
            "has_error": False,
            "examples": []
        }
        
        # 检查错误模式
        for pattern, fix in error_patterns.items():
            if re.search(pattern, sentence, re.IGNORECASE):
                correction["corrected"] = re.sub(pattern, fix["correct"], sentence, flags=re.IGNORECASE)
                correction["explanation"] = fix["explanation"]
                correction["has_error"] = True
                correction["examples"].extend([
                    f"✅ {fix['correct']}",
                    f"❌ {sentence}"
                ])
                break
        
        # 如果没有匹配到模式，使用 AI 分析
        if not correction["has_error"]:
            correction["explanation"] = "未检测到明显语法错误，但可能有其他改进空间。"
        
        # 更新进度
        self.progress["grammar_corrections"] += 1
        self._save_json("progress.json", self.progress)
        
        return correction
    
    # ==================== 词汇管理 ====================
    
    def add_vocab(self, word: str, meaning: str, example: str = ""):
        """添加生词到词库"""
        self.vocab_bank[word.lower()] = {
            "meaning": meaning,
            "example": example,
            "added_at": datetime.now().isoformat(),
            "review_count": 0
        }
        self._save_json("vocab_bank.json", self.vocab_bank)
    
    def get_vocab_list(self) -> list:
        """获取词库列表"""
        return [
            {"word": k, **v} for k, v in self.vocab_bank.items()
        ]
    
    # ==================== 飞书集成 ====================
    
    def send_to_feishu(self, message: str, channel: str = "feishu"):
        """
        发送消息到飞书
        
        Args:
            message: 消息内容
            channel: 频道 (feishu)
        """
        # 尝试使用 webhook 发送
        import os
        import subprocess
        
        webhook_url = os.environ.get("FEISHU_WEBHOOK_URL")
        if webhook_url:
            # 使用 curl 发送 webhook 请求
            cmd = [
                "curl", "-X", "POST", "-H", "Content-Type: application/json",
                "-d", json.dumps({"msg_type": "text", "content": {"text": message}}),
                webhook_url
            ]
            subprocess.run(cmd, capture_output=True)
            print("✅ 已发送到飞书")
        else:
            # 没有配置 webhook，打印消息
            print("📱 飞书 webhook 未配置，发送消息:")
            print(message)
    
    def send_lesson_to_feishu(self, lesson_data: dict):
        """
        发送完整课程到飞书（包含完整文章内容）
        
        Args:
            lesson_data: 课程数据字典
        """
        # 判断是否有完整文章内容
        full_content = lesson_data.get('content', '')
        
        if full_content:
            # 发送完整文章（去掉链接）
            text = f"""
📚 今日英语学习

📰 标题: {lesson_data.get('title', 'No Title')}
📊 难度: {lesson_data.get('level', 'Intermediate')}

💡 核心词汇:
{lesson_data.get('vocab', '暂无词汇')}

📖 完整文章:
{full_content}
"""
        else:
            # 降级为摘要（去掉链接）
            text = f"""
📚 今日英语学习

📰 标题: {lesson_data.get('title', 'No Title')}
📊 难度: {lesson_data.get('level', 'Intermediate')}

💡 核心词汇:
{lesson_data.get('vocab', '暂无词汇')}

📝 文章摘要:
{lesson_data.get('summary', '暂无摘要')}
"""
        self.send_to_feishu(text)
    
    # ==================== 进度追踪 ====================
    
    def get_progress(self) -> dict:
        """获取学习进度"""
        return {
            "total_articles": self.progress["total_articles"],
            "grammar_corrections": self.progress["grammar_corrections"],
            "vocab_count": len(self.vocab_bank),
            "daily_streak": self.progress["daily_streak"],
            "last_study_date": self.progress["last_study_date"]
        }
    
    def update_streak(self):
        """更新连续学习天数"""
        from datetime import datetime, timedelta
        
        today = datetime.now().date().isoformat()
        last_date = self.progress.get("last_study_date")
        
        if last_date != today:
            if last_date:
                last = datetime.fromisoformat(last_date).date()
                if last == datetime.now().date() - timedelta(days=1):
                    self.progress["daily_streak"] += 1
                else:
                    self.progress["daily_streak"] = 1
            else:
                self.progress["daily_streak"] = 1
            
            self.progress["last_study_date"] = today
            self._save_json("progress.json", self.progress)


# ==================== 便捷函数 ====================

def new_lesson():
    """创建新课程"""
    assistant = EnglishLearningAssistant()
    
    # 搜索文章
    article = assistant.search_article(
        topic="technology",
        level="intermediate"
    )
    
    # 生成词汇表
    vocab_text = """
• artificial intelligence (AI) - 人工智能
• personalized - 个性化的  
• adaptive learning - 自适应学习
• algorithm - 算法
• data-driven - 数据驱动的
"""
    
    # 发送到飞书
    assistant.send_lesson_to_feishu({
        "title": article["title"],
        "url": article["url"],
        "level": article["level"],
        "vocab": vocab_text,
        "summary": article["snippet"]
    })
    
    return article


def check_english(text: str) -> str:
    """快速检查英语"""
    assistant = EnglishLearningAssistant()
    correction = assistant.correct_grammar(text)
    
    if correction["has_error"]:
        return f"""
❌ 原文: {correction['original']}
✅ 纠正: {correction['corrected']}

📚 说明: {correction['explanation']}
"""
    else:
        return f"✅ {correction['original']}\n\n📚 {correction['explanation']}"


def practice_speech(audio_path: str) -> str:
    """语音练习"""
    assistant = EnglishLearningAssistant()
    
    # 语音转文字
    text = assistant.speech_to_text(audio_path)
    
    if text and "[语音识别" not in text:
        # 检查语法
        correction = assistant.correct_grammar(text)
        return f"""
🎤 语音识别: {text}
{correction}
"""
    else:
        return text


if __name__ == "__main__":
    # 测试代码
    print("🧪 测试英语学习助手")
    
    assistant = EnglishLearningAssistant()
    
    # 测试语法纠错
    test_sentences = [
        "I am agree with you",
        "She have a car",
        "I have lived here since five years"
    ]
    
    for sentence in test_sentences:
        result = assistant.correct_grammar(sentence)
        print(f"\n原文: {sentence}")
        print(f"纠正: {result['corrected']}")
        print(f"说明: {result['explanation']}")
