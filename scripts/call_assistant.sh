#!/bin/bash
# 直接调用指定助手分析股票

AGENT=$1
TASK=${2:-"分析今天的大盘"}

if [ -z "$AGENT" ]; then
    echo "用法: ./call_assistant.sh <助手ID> <任务>"
    echo "示例: ./call_assistant.sh assistant_stock '分析今天大盘'"
    exit 1
fi

# 通过Gateway API调用
openclaw agent --agent $AGENT --message "$TASK" --deliver 2>&1
