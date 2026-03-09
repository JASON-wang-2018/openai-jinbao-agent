#!/bin/bash
# 自动备份脚本
# 功能：备份知识库、脚本、模型配置等关键文件
# 流程：1. GitHub推送 2. 本地备份

set -e

# 配置
WORKSPACE="/home/jason/.openclaw/workspace"
BACKUP_BASE="/home/jason/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M)
LATEST_LINK="$BACKUP_BASE/openclaw_latest"

# 备份目录
BACKUP_DIR="$BACKUP_BASE/openclaw_$TIMESTAMP"

echo "========================================"
echo "📦 OpenClaw 自动备份"
echo "========================================"
echo "备份时间：$(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# ===== 第1步：GitHub推送 =====
echo "📤 推送到GitHub..."
cd "$WORKSPACE"
# 检查是否有未提交的更改
if git diff --quiet && git diff --cached --quiet; then
    echo "  ✓ 无新更改，无需推送"
else
    git add -A
    git commit -m "backup: $(date '+%Y-%m-%d %H:%M')" || true
    if git push origin master 2>/dev/null; then
        echo "  ✓ GitHub推送成功"
    else
        echo "  ⚠ GitHub推送失败（可能需要认证），跳过"
    fi
fi
echo ""

# ===== 第2步：本地备份 =====

# 备份知识库
echo "📚 备份知识库..."
if [ -d "$WORKSPACE/knowledge_base" ]; then
    cp -r "$WORKSPACE/knowledge_base" "$BACKUP_DIR/"
    echo "  ✓ knowledge_base/"
else
    echo "  ⚠ knowledge_base 不存在"
fi

# 备份股票相关
echo "📊 备份股票系统..."
if [ -d "$WORKSPACE/stock" ]; then
    cp -r "$WORKSPACE/stock" "$BACKUP_DIR/"
    echo "  ✓ stock/"
else
    echo "  ⚠ stock 不存在"
fi

# 备份核心配置文件
echo "📋 备份核心配置..."
for file in STOCK_MODEL_INDEX.md MEMORY.md SOUL.md USER.md IDENTITY.md; do
    if [ -f "$WORKSPACE/$file" ]; then
        cp "$WORKSPACE/$file" "$BACKUP_DIR/"
        echo "  ✓ $file"
    fi
done

# 备份记忆文件
if [ -d "$WORKSPACE/memory" ]; then
    cp -r "$WORKSPACE/memory" "$BACKUP_DIR/"
    echo "  ✓ memory/"
fi

# 创建最新备份软链接
echo ""
echo "🔗 更新最新备份链接..."
rm -rf "$LATEST_LINK"
ln -s "$BACKUP_DIR" "$LATEST_LINK"
echo "  ✓ $LATEST_LINK -> $BACKUP_DIR"

# 清理旧备份 (保留最近 10 个)
echo ""
echo "🧹 清理旧备份..."
cd "$BACKUP_BASE"
ls -dt openclaw_*/ 2>/dev/null | tail -n +11 | xargs rm -rf 2>/dev/null || true
echo "  ✓ 保留最近 10 个备份"

# 显示备份信息
echo ""
echo "========================================"
echo "✅ 备份完成"
echo "========================================"
echo "备份位置：$BACKUP_DIR"
echo "备份大小：$(du -sh "$BACKUP_DIR" | cut -f1)"
echo "文件数量：$(find "$BACKUP_DIR" -type f | wc -l)"
echo ""

# 输出备份清单
echo "📝 备份清单:"
find "$BACKUP_DIR" -type f | wc -l
echo "个文件"

echo ""
echo "========================================"
