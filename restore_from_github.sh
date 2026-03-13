#!/bin/bash
# OpenClaw 从GitHub恢复脚本
# 用法: bash restore_from_github.sh

set -e

WORKSPACE="/home/jason/.openclaw/workspace"
BACKUP_BASE="/home/jason/backups"

echo "========================================"
echo "🔄 OpenClaw 从GitHub恢复"
echo "========================================"
echo "恢复时间：$(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 检查Git仓库
if [ ! -d "$WORKSPACE/.git" ]; then
    echo "❌ 当前目录不是Git仓库"
    echo "请先克隆仓库: git clone <your-repo-url> $WORKSPACE"
    exit 1
fi

# 拉取最新
echo "📥 从GitHub拉取最新代码..."
cd "$WORKSPACE"
git fetch origin
git reset --hard origin/main

echo ""
echo "✅ 代码恢复完成！"
echo ""

# ===== 第2步：恢复Cron配置 =====
if [ -d "$WORKSPACE/.openclaw/cron" ]; then
    echo "⏰ 恢复Cron配置..."
    mkdir -p /home/jason/.openclaw
    cp -r "$WORKSPACE/.openclaw/cron" /home/jason/.openclaw/
    echo "  ✓ Cron配置已恢复"
fi

echo ""
echo "========================================"
echo "✅ 恢复完成！"
echo "========================================"
echo ""
echo "下一步："
echo "1. 重启OpenClaw: openclaw gateway restart"
echo "2. 检查Cron: openclaw cron list"
