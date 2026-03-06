#!/bin/bash
# 开机自启检查脚本
# 功能：确保 OpenClaw 股票系统开机即可用

set -e

WORKSPACE="/home/jason/.openclaw/workspace"
LOG_FILE="/tmp/openclaw_startup.log"

echo "========================================" | tee -a "$LOG_FILE"
echo "🚀 OpenClaw 开机检查" | tee -a "$LOG_FILE"
echo "时间：$(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"

# 1. 检查 Python 环境
echo "" | tee -a "$LOG_FILE"
echo "【1】检查 Python 环境..." | tee -a "$LOG_FILE"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "  ✓ $PYTHON_VERSION" | tee -a "$LOG_FILE"
else
    echo "  ❌ Python3 未安装" | tee -a "$LOG_FILE"
fi

# 2. 检查依赖包
echo "" | tee -a "$LOG_FILE"
echo "【2】检查 Python 依赖..." | tee -a "$LOG_FILE"
REQUIRED_PACKAGES="akshare pandas numpy"
for pkg in $REQUIRED_PACKAGES; do
    if python3 -c "import $pkg" 2>/dev/null; then
        echo "  ✓ $pkg" | tee -a "$LOG_FILE"
    else
        echo "  ⚠ $pkg 未安装 (运行：pip3 install $pkg)" | tee -a "$LOG_FILE"
    fi
done

# 3. 检查 cron 服务
echo "" | tee -a "$LOG_FILE"
echo "【3】检查 cron 服务..." | tee -a "$LOG_FILE"
if pgrep -x "cron" > /dev/null; then
    echo "  ✓ cron 服务运行中" | tee -a "$LOG_FILE"
else
    echo "  ⚠ cron 服务未运行" | tee -a "$LOG_FILE"
    # 尝试启动 (需要 sudo)
    # sudo service cron start
fi

# 4. 检查 cron 任务
echo "" | tee -a "$LOG_FILE"
echo "【4】检查 cron 任务..." | tee -a "$LOG_FILE"
CRON_COUNT=$(crontab -l 2>/dev/null | grep -v "^#" | grep -v "^$" | wc -l)
echo "  ✓ 已配置 $CRON_COUNT 个定时任务" | tee -a "$LOG_FILE"

# 5. 检查工作区文件
echo "" | tee -a "$LOG_FILE"
echo "【5】检查工作区文件..." | tee -a "$LOG_FILE"
ESSENTIAL_FILES=(
    "STOCK_MODEL_INDEX.md"
    "stock/scripts/double_system_analysis.py"
    "stock/scripts/stock_analysis_comprehensive.py"
    "stock/scripts/daily_simple_review.py"
    "auto_backup.sh"
)

for file in "${ESSENTIAL_FILES[@]}"; do
    if [ -f "$WORKSPACE/$file" ]; then
        echo "  ✓ $file" | tee -a "$LOG_FILE"
    else
        echo "  ❌ $file 缺失" | tee -a "$LOG_FILE"
    fi
done

# 6. 检查备份目录
echo "" | tee -a "$LOG_FILE"
echo "【6】检查备份..." | tee -a "$LOG_FILE"
if [ -d "/home/jason/backups" ]; then
    BACKUP_COUNT=$(ls -d /home/jason/backups/openclaw_*/ 2>/dev/null | wc -l)
    echo "  ✓ 备份目录存在 ($BACKUP_COUNT 个备份)" | tee -a "$LOG_FILE"
    
    if [ -L "/home/jason/backups/openclaw_latest" ]; then
        LATEST_PATH=$(readlink /home/jason/backups/openclaw_latest)
        echo "  ✓ 最新备份链接：$LATEST_PATH" | tee -a "$LOG_FILE"
    else
        echo "  ⚠ 最新备份链接不存在" | tee -a "$LOG_FILE"
    fi
else
    echo "  ⚠ 备份目录不存在" | tee -a "$LOG_FILE"
fi

# 7. 执行一次快速备份
echo "" | tee -a "$LOG_FILE"
echo "【7】执行开机备份..." | tee -a "$LOG_FILE"
cd "$WORKSPACE" && bash auto_backup.sh >> "$LOG_FILE" 2>&1
echo "  ✓ 备份完成" | tee -a "$LOG_FILE"

# 8. 测试脚本可执行性
echo "" | tee -a "$LOG_FILE"
echo "【8】测试脚本..." | tee -a "$LOG_FILE"
if [ -x "$WORKSPACE/stock/scripts/double_system_analysis.py" ] || python3 -m py_compile "$WORKSPACE/stock/scripts/double_system_analysis.py" 2>/dev/null; then
    echo "  ✓ 双系统脚本正常" | tee -a "$LOG_FILE"
else
    echo "  ⚠ 双系统脚本可能有误" | tee -a "$LOG_FILE"
fi

if [ -x "$WORKSPACE/stock/scripts/stock_analysis_comprehensive.py" ] || python3 -m py_compile "$WORKSPACE/stock/scripts/stock_analysis_comprehensive.py" 2>/dev/null; then
    echo "  ✓ 个股分析脚本正常" | tee -a "$LOG_FILE"
else
    echo "  ⚠ 个股分析脚本可能有误" | tee -a "$LOG_FILE"
fi

echo "" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
echo "✅ 开机检查完成" | tee -a "$LOG_FILE"
echo "日志：$LOG_FILE" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
