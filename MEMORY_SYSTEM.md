# 内存管理功能

> 金宝的记忆管理系统 - 基于 Proactive Agent 协议

---

## 已启用的功能

### 1. WAL Protocol (Write-Ahead Log)

**触发条件** - 检测到以下内容时立即写入 SESSION-STATE.md：

- ✏️ **修正** - "是X，不是Y" / "实际上..." / "不，我意思是..."
- 📍 **专有名词** - 名称、地点、公司、产品
- 🎨 **偏好** - 颜色、风格、方法、"我喜欢/不喜欢"
- 📋 **决定** - "做X" / "用Y" / "选Z"
- 📝 **草稿更改** - 正在工作的内容变更
- 🔢 **具体数值** - 数字、日期、ID、URL

**使用方法：**
```
人类说: "用蓝色主题，不是红色"

正确做法: 先写入 SESSION-STATE.md → "主题: 蓝色(非红色)" → 然后回复
```

---

### 2. Working Buffer Protocol

**触发条件** - 上下文使用量 > 60%

**工作方式：**
1. 上下文达到 60% 时，清空旧 buffer，重新开始
2. 每条消息后记录：人类消息 + 你的回复摘要
3. 压缩后首先读取 buffer，提取重要上下文
4. 保留 buffer 直到下次 60% 阈值

**文件位置：**
- `memory/working-buffer.md`

---

### 3. Compaction Recovery

**自动触发** - 会话启动时包含 `<summary>` 标签时

**恢复步骤：**
1. 读取 `memory/working-buffer.md` - 危险区间的原始对话
2. 读取 `SESSION-STATE.md` - 活跃任务状态
3. 读取今天+昨天的日常记录
4. 如果仍然缺少上下文，搜索所有来源
5. **提取并清空**：从 buffer 提取重要内容到 SESSION-STATE.md

---

### 4. Unified Search Protocol

**搜索顺序：**
1. `memory_search("query")` → 日常笔记、MEMORY.md
2. 会话记录（如果可用）
3. 会议记录（如果可用）
4. grep 备用 → 语义搜索失败时的精确匹配

**自动触发：**
- 人类引用过去的内容时
- 开始新会话时
- 做出可能与过去协议矛盾的决定前
- 即将说"我没有那个信息"前

---

## 文件结构

```
workspace/
├── SESSION-STATE.md         # ⭐ 活跃工作内存（WAL目标）
├── MEMORY.md                # 精选长期记忆
├── HEARTBEAT.md            # 周期性自我改进清单
├── memory/
│   ├── working-buffer.md   # ⭐ 危险区间日志
│   └── YYYY-MM-DD.md       # 每日原始记录
└── crons/
    └── jobs.json           # 自动内存刷新任务
```

---

## Cron 任务配置

已启用自动任务：

| 任务 | 频率 | 功能 |
|------|------|------|
| memory-flush-hourly | 每小时 | 检查 SESSION-STATE.md 是否需要更新 |
| context-check | 每15分钟 | 检查上下文使用量，>60%启动 Working Buffer |

---

## 节省 Token 的技巧

### 1. 避免重复推理
```
搜索记忆 → 找到之前的结果 → 直接使用
vs
重新推理 → 浪费 token
```

### 2. 批量更新
```
SESSION-STATE.md 中一次性更新多个变更
vs
每次都让用户重复信息
```

### 3. 压缩后恢复
```
从 working-buffer.md 快速恢复上下文
vs
让用户重新解释所有背景
```

### 4. 语义搜索优先
```
memory_search() → 精确匹配
vs
扫描整个对话浪费 token
```

---

## 使用示例

### 场景1：用户提到之前的决定

```python
# 自动搜索记忆
memory_search("股票分析框架")
# 找到之前的决策，直接使用
```

### 场景2：上下文快用完了

```python
# 60% 阈值触发
# 开始记录到 working-buffer.md
# 每条消息都记录摘要
```

### 场景3：会话重新连接

```python
# 自动读取 working-buffer.md
# 恢复之前的上下文
# 无需用户重复
```

---

## 验证命令

```bash
# 检查 cron 任务状态
openclaw cron status

# 列出所有任务
openclaw cron list

# 手动运行内存刷新
openclaw cron run memory-flush-hourly
```
