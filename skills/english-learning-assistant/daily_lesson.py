#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日英语课程脚本
Daily English Lesson Script

功能:
1. 搜索英语文章
2. 生成语音版本
3. 发送到飞书
4. 记录学习进度
"""

from english_learning import EnglishLearningAssistant
from datetime import datetime
import json


def generate_daily_lesson():
    """生成每日英语课程"""
    
    print("📚 生成每日英语课程...")
    
    assistant = EnglishLearningAssistant()
    
    # 1. 搜索文章
    print("🔍 搜索英语文章...")
    topics = [
        "artificial intelligence",
        "climate change", 
        "space exploration",
        "healthy lifestyle",
        "business innovation"
    ]
    
    import random
    topic = random.choice(topics)
    article = assistant.search_article(topic=topic, level="intermediate")
    
    print(f"✅ 找到文章: {article['title']}")
    
    # 1.5 获取完整文章内容
    print("📄 获取完整文章内容...")
    full_content = assistant.fetch_article_content(article.get('url', ''))
    if full_content:
        article['content'] = full_content
        print(f"✅ 获取到 {len(full_content)} 字符的文章内容")
    else:
        print("⚠️ 无法获取完整内容，使用摘要")
    
    # 2. 生成词汇表 (CET-4难度)
    vocab_list = f"""
• artificial intelligence - 人工智能
• recommendation system - 推荐系统
• natural language processing - 自然语言处理
• healthcare - 医疗保健
• diagnose - 诊断
• algorithm - 算法
• privacy - 隐私
• greenhouse gas - 温室气体
• fossil fuels - 化石燃料
• renewable energy - 可再生能源
• chronic - 慢性的
• deprivation - 匮乏
• portion control - 分量控制
• balanced diet - 均衡饮食
• essential - 必要的
• beneficial - 有益的
"""
    
    # 3. 发送到飞书
    print("📱 发送到飞书...")
    lesson_data = {
        "title": article['title'],
        "url": article['url'],
        "level": article['level'],
        "vocab": vocab_list,
        "summary": article['snippet'],
        "content": article.get('content', ''),  # 完整文章内容
        "date": datetime.now().strftime("%Y-%m-%d")
    }
    
    assistant.send_lesson_to_feishu(lesson_data)
    
    # 4. 更新学习记录
    assistant.update_streak()
    progress = assistant.get_progress()
    
    print("✅ 课程发送完成!")
    print(f"📊 学习进度: {progress['total_articles']} 篇文章, {progress['daily_streak']} 天连续学习")
    
    return lesson_data


if __name__ == "__main__":
    generate_daily_lesson()
