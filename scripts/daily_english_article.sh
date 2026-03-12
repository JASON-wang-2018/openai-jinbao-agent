#!/bin/bash
# 每日英语短文自动推送
# 时间：每天早上 8:00
# 发送到飞书群聊

cd /home/jason/.openclaw/workspace/skills/english-learning-assistant

# 运行 Python 脚本获取今日文章
RESULT=$(python3 daily_lesson.py 2>&1)

# 从输出中提取标题和内容
TITLE=$(echo "$RESULT" | grep "ARTICLE_TITLE:" | sed 's/ARTICLE_TITLE: //' | xargs)
LEVEL=$(echo "$RESULT" | grep "ARTICLE_LEVEL:" | sed 's/ARTICLE_LEVEL: //' | xargs)
CONTENT=$(echo "$RESULT" | sed -n '/ARTICLE_CONTENT_BEGINS/,/ARTICLE_CONTENT_ENDS/p' | sed '1d;$d' | head -15)

# 提取词汇
VOCAB=$(echo "$RESULT" | sed -n '/💡 核心词汇:/,/📝 ARTICLE_TITLE/p' | grep "•" | head -6)

# 如果没有提取到内容，使用默认值
if [ -z "$TITLE" ] || [ -z "$CONTENT" ]; then
    TITLE="The Power of Small Habits"
    LEVEL="CET-4"
    CONTENT="Every day, millions of people make a promise to themselves: \"I'll start tomorrow.\" Tomorrow becomes next week, next month, never. But here's the truth — you don't need dramatic change. You need small, consistent habits."
    VOCAB="• promise - 承诺
• consistent - 持续的
• automatic - 自动的"
fi

# 发送到飞书群
openclaw message send --channel feishu --target "chat:oc_f84f0158693c8887be1bac624f143805" --message "📚 今日英语学习

📰 标题: $TITLE
📊 难度: $LEVEL

💡 核心词汇:
$VOCAB

📖 正文:
$CONTENT

📊 学习进步: 每天一点点 🔥"

echo "$(date): English article sent to group" >> /tmp/cron_english.log
