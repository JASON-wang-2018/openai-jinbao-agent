#!/bin/bash

# OpenClaw 心跳检查脚本（精简版）
# 仅保留核心功能，减少token消耗

WORKSPACE="/home/jason/.openclaw/workspace"
MEMORY_DIR="${WORKSPACE}/memory"
TODAY=$(date +%Y-%m-%d)

# 1. 检查记忆文件（自动创建）
MEMORY_FILE="${MEMORY_DIR}/${TODAY}.md"
[ ! -f "$MEMORY_FILE" ] && cat > "$MEMORY_FILE" << EOF
# ${TODAY} 工作日志

## 日期：${TODAY} $(date +%A)

## 今日完成

## 待办

## 系统状态
EOF

# 2. 快速检查备份状态
[ -L "/home/jason/backups/openclaw_latest" ] && echo "✅ 备份正常" || echo "⚠️ 备份异常"

# 精简版检查完成
