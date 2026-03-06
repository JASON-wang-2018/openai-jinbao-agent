#!/bin/bash
# 金宝启动脚本

echo "🚀 金宝启动中..."
echo "================"

# 1. 自动备份（重要！）
echo ""
echo "💾 执行自动备份..."
bash auto_backup.sh

# 2. 检查索引
echo ""
echo "📋 检查索引文件..."
if [ -f STOCK_MODEL_INDEX.md ]; then
    cat STOCK_MODEL_INDEX.md
else
    echo "⚠️ 索引文件不存在"
fi

# 3. 读取核心文档
echo ""
echo "📖 加载双系统模型..."
if [ -f knowledge_base/25-双系统模型分析.md ]; then
    echo "✅ 已加载: 25-双系统模型分析.md"
else
    echo "❌ 核心文档缺失"
fi

# 4. 检查脚本
echo ""
echo "⚙️ 检查分析脚本..."
if [ -f stock/scripts/stock_analysis_v2.py ]; then
    echo "✅ 脚本就绪: stock_analysis_v2.py (老股民警v2.0)"
fi
if [ -f stock/scripts/zhuangjia_detector.py ]; then
    echo "✅ 脚本就绪: zhuangjia_detector.py (庄家识别)"
fi
if [ -f stock/scripts/double_system_analysis.py ]; then
    echo "✅ 脚本就绪: double_system_analysis.py (双系统复盘)"
fi

echo ""
echo "✨ 启动完成"
