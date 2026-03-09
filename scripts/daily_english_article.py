#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日英语短文自动发送脚本
发送到飞书群聊
"""

import json
import random
from datetime import datetime
from pathlib import Path

# 预设英语文章库
ARTICLES = [
    {
        "title": "The Rise of Artificial Intelligence in Everyday Life",
        "snippet": "How AI is changing the way we live, work, and interact with technology in our daily lives.",
        "vocab": "artificial intelligence (AI) - 人工智能\npersonalized - 个性化的\nadaptive learning - 自适应学习"
    },
    {
        "title": "Climate Change: What You Need to Know",
        "snippet": "Learn key vocabulary about climate change and environmental issues affecting our planet.",
        "vocab": "climate change - 气候变化\nsustainable development - 可持续发展\ncarbon footprint - 碳足迹\nrenewable energy - 可再生能源"
    },
    {
        "title": "The Science of Sleep",
        "snippet": "Discover why sleep is important and how it affects our health and productivity.",
        "vocab": "productivity - 生产力\ncircadian rhythm - 昼夜节律\nREM sleep - 快速眼动睡眠\ninsomnia - 失眠"
    },
    {
        "title": "Business Innovation in the Digital Age",
        "snippet": "Learn about how companies are innovating and adapting to the digital economy.",
        "vocab": "innovation - 创新\ndigital transformation - 数字化转型\ndisruptive technology - 颠覆性技术\nstartup - 初创公司"
    },
    {
        "title": "The Future of Space Exploration",
        "snippet": "Explore new frontiers in space travel and the latest discoveries about our universe.",
        "vocab": "space exploration - 太空探索\nastronaut - 宇航员\nspacecraft - 宇宙飞船\norbit - 轨道"
    },
    {
        "title": "The Benefits of Reading Every Day",
        "snippet": "Reading daily can improve your mind, vocabulary, and emotional intelligence in surprising ways.",
        "vocab": "vocabulary - 词汇量\nemotional intelligence - 情商\ncognitive function - 认知功能\nliteracy - 识字"
    },
    {
        "title": "How to Stay Healthy While Working from Home",
        "snippet": "Tips for maintaining physical and mental health in a remote work environment.",
        "vocab": "remote work - 远程工作\nwork-life balance - 工作生活平衡\nergonomics - 人体工程学\nmental health - 心理健康"
    },
    {
        "title": "The Power of Positive Thinking",
        "snippet": "How your thoughts can shape your reality and influence your success.",
        "vocab": "positive thinking - 积极思考\nmindset - 心态\nself-efficacy - 自我效能\nresilience - 韧性"
    }
]


def get_daily_article():
    """获取今日文章（每天轮换）"""
    # 按日期选择，确保同一天显示相同文章
    day_of_year = datetime.now().timetuple().tm_yday
    index = day_of_year % len(ARTICLES)
    return ARTICLES[index]


def format_message():
    """格式化发送到群的消息"""
    article = get_daily_article()
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    message = f"""📚 每日英语短文 · {date_str}

📰 {article['title']}

📖 {article['snippet']}

💡 核心词汇:
{article['vocab']}

━━━━━━━━━━━━━━━
每天进步一点点，积累改变未来 🇺🇸"""

    return message


def main():
    """主函数"""
    message = format_message()
    
    # 使用 OpenClaw 的 message 工具发送
    from tools import message
    
    result = message(
        action="send",
        channel="feishu",
        target="oc_f84f0158693c8887be1bac624f143805",
        message=message
    )
    
    print(f"✅ 已发送英语短文到群")
    print(f"📝 内容: {message[:100]}...")


if __name__ == "__main__":
    main()
