# Cron Manager Skill 🕐

> 定时任务管理技能 - 确保任务不被错过

**版本**: 1.1.0  
**功能**: 定时任务添加/管理、监控、可靠性保障、自动修复  
**场景**: 定时提醒、定时推送、定时执行

**依赖**: 整合 task-scheduler（系统级 cron 管理）

---

## 核心能力

| 能力 | 说明 |
|------|------|
| 任务添加 | 通过 task-scheduler 添加 cron 任务 |
| 任务管理 | 列出、删除定时任务 |
| 任务监控 | 追踪所有定时任务执行状态 |
| 失败重试 | 任务失败时自动重试 |
| 延迟补偿 | 错过时间后尽快执行 |
| 状态告警 | 任务失败时通知 |

---

## 可靠性设计

### 三层保障

1. **主任务层** - 原生 cron 定时触发
2. **监控层** - 检查任务是否按时执行
3. **补偿层** - 错过则立即补偿执行

### 任务分类

| 类型 | 描述 | 处理方式 |
|------|------|----------|
| critical | 关键任务（开会提醒） | 双重保障 + 立即重试 |
| important | 重要任务（复盘、推送） | 监控 + 延迟补偿 |
| normal | 一般任务（检查类） | 基础保障 |

---

## 使用方法

### 1. 添加任务（整合 task-scheduler）

```bash
# 添加定时任务
python3 ../task-scheduler/skill.py add "任务名" "命令" "cron表达式" "描述"

# 示例：每日复盘
python3 ../task-scheduler/skill.py add "daily-review" "python3 daily.py" "0 20 * * *" "每日复盘"

# 示例：每5分钟检查
python3 ../task-scheduler/skill.py add "check-status" "python3 check.py" "*/5 * * * *" "状态检查"
```

### 2. 查看任务

```bash
# 查看所有任务
python3 ../task-scheduler/skill.py list

# 查看健康状态
python3 cron_manager.py status

# 查看失败任务
python3 monitor.py
```

### 3. 执行任务

```bash
# 手动执行任务
python3 cron_manager.py run <task_name>

# 补偿执行（用于错过后补执行）
python3 cron_manager.py catchup <task_name>
```

### 4. 删除任务

```bash
python3 ../task-scheduler/skill.py remove "任务名"
```

---

## 任务状态

- ✅ success - 成功执行
- ⏳ running - 执行中
- ❌ failed - 执行失败
- ⏰ missed - 错过执行时间
- 🔄 retrying - 重试中

---

## 告警规则

| 任务类型 | 失败重试次数 | 告警阈值 |
|----------|--------------|----------|
| critical | 3次 | 立即 |
| important | 2次 | 2次后 |
| normal | 1次 | 不告警 |

---

## 文件结构

```
workspace/skills/
├── cron-manager/           # 本技能
│   ├── SKILL.md            # 本文件
│   ├── cron_manager.py     # 核心管理（监控+补偿+历史）
│   ├── monitor.py          # 健康检查脚本
│   ├── auto_compensate.py  # 自动补偿脚本
│   ├── run_compensate.sh   # 补偿执行入口
│   └── config/
│       ├── history.json    # 执行历史
│       └── compensate_status.json  # 补偿状态
└── task-scheduler/         # 依赖技能（任务添加/删除）
    ├── skill.py            # 任务管理核心
    ├── skill.sh            # Shell 包装
    └── config.json         # 配置
```

**注意**：task-scheduler 管理**系统级 cron**，cron-manager 提供**可靠性保障**（监控+补偿）。
