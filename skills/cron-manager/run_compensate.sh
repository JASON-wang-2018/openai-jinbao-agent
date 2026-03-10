#!/bin/bash
# Cron Manager 自动补偿脚本
# 每5分钟执行一次，检查并补偿错过的关键任务
# 不消耗LLM token

cd /home/jason/.openclaw/workspace
python3 skills/cron-manager/auto_compensate.py >> /tmp/cron_compensate.log 2>&1
