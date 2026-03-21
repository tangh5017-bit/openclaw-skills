---
name: auto-task
description: 自主任务管理器 - 让 AI 能自主安排、执行、跟踪任务
author: 米仔
version: 1.0.0
metadata: {"clawdbot":{"emoji":"✅","requires":{"bins":["node"]},"config":{"env":{"AUTO_TASK_DATA_DIR":{"description":"任务数据存储目录","default":"~/.openclaw/auto-tasks","required":false}}}}}
---

# Auto-Task 自主任务管理器

**原创技能** - 让 AI 从被动响应变为主动执行！

## 核心功能

- ✅ 创建和管理任务清单
- ✅ 自动执行简单任务（文件操作、搜索、消息等）
- ✅ 任务进度跟踪和状态管理
- ✅ 定时任务和提醒
- ✅ 任务优先级和依赖管理
- ✅ 任务执行日志和统计

## 快速开始

### 创建任务
```bash
uv run scripts/auto-task.py create "检查未读邮件" --priority high
uv run scripts/auto-task.py create "每日备份 workspace" --schedule "0 9 * * *"
```

### 查看任务
```bash
uv run scripts/auto-task.py list
uv run scripts/auto-task.py list --status pending
uv run scripts/auto-task.py list --priority high
```

### 执行任务
```bash
uv run scripts/auto-task.py run <task-id>
uv run scripts/auto-task.py run --all  # 执行所有待处理任务
```

### 完成任务
```bash
uv run scripts/auto-task.py complete <task-id>
uv run scripts/auto-task.py cancel <task-id>
```

## 任务类型

### 1. 一次性任务
```bash
uv run scripts/auto-task.py create "整理 downloads 文件夹" --type once
```

### 2. 定时任务（Cron 表达式）
```bash
# 每天早上 9 点
uv run scripts/auto-task.py create "每日自检" --schedule "0 9 * * *"

# 每周一上午 10 点
uv run scripts/auto-task.py create "周报生成" --schedule "0 10 * * 1"

# 每小时执行
uv run scripts/auto-task.py create "检查更新" --schedule "0 * * * *"
```

### 3. 间隔任务
```bash
# 每 30 分钟
uv run scripts/auto-task.py create "检查新消息" --interval 30m

# 每 2 小时
uv run scripts/auto-task.py create "同步数据" --interval 2h
```

## 高级用法

### 任务依赖
```bash
# 任务 B 在任务 A 完成后执行
uv run scripts/auto-task.py create "任务 A" --id task-a
uv run scripts/auto-task.py create "任务 B" --depends-on task-a
```

### 任务标签
```bash
uv run scripts/auto-task.py create "备份代码" --tags backup,code,daily
uv run scripts/auto-task.py list --tags backup
```

### 任务统计
```bash
uv run scripts/auto-task.py stats
uv run scripts/auto-task.py history --days 7
```

## 任务状态

| 状态 | 说明 |
|------|------|
| pending | 待处理 |
| running | 执行中 |
| completed | 已完成 |
| failed | 执行失败 |
| cancelled | 已取消 |
| skipped | 已跳过 |

## 优先级

| 优先级 | 说明 | 执行顺序 |
|--------|------|----------|
| critical | 紧急重要 | 最先执行 |
| high | 高优先级 | 优先执行 |
| normal | 普通 | 默认 |
| low | 低优先级 | 最后执行 |

## 配置文件

在 `~/.openclaw/auto-tasks/config.json` 中配置：

```json
{
  "dataDir": "~/.openclaw/auto-tasks",
  "autoRun": true,
  "maxConcurrent": 3,
  "retryFailed": true,
  "retryAttempts": 3,
  "notifyOnComplete": true,
  "logLevel": "info"
}
```

## 示例任务

### 每日自检任务
```json
{
  "id": "daily-check",
  "name": "每日自检",
  "type": "recurring",
  "schedule": "0 9 * * *",
  "priority": "high",
  "actions": [
    {"type": "exec", "command": "git status"},
    {"type": "check", "path": "~/Downloads", "action": "organize"},
    {"type": "notify", "message": "每日自检完成"}
  ]
}
```

### 文件监控任务
```json
{
  "id": "watch-downloads",
  "name": "监控下载文件夹",
  "type": "recurring",
  "interval": "1h",
  "priority": "normal",
  "actions": [
    {"type": "watch", "path": "~/Downloads"},
    {"type": "organize", "rules": {"images": "Pictures", "docs": "Documents"}}
  ]
}
```

## API 参考

### 创建任务
```bash
uv run scripts/auto-task.py create <name> [options]
```

选项：
- `--id <id>` - 自定义任务 ID
- `--type <type>` - 任务类型（once/recurring）
- `--schedule <cron>` - Cron 表达式
- `--interval <time>` - 时间间隔（30m/1h/2d）
- `--priority <priority>` - 优先级（critical/high/normal/low）
- `--tags <tags>` - 标签（逗号分隔）
- `--depends-on <id>` - 依赖的任务 ID
- `--notify` - 完成后通知

### 查看任务
```bash
uv run scripts/auto-task.py list [options]
```

选项：
- `--status <status>` - 按状态过滤
- `--priority <priority>` - 按优先级过滤
- `--tags <tags>` - 按标签过滤
- `--format <format>` - 输出格式（table/json）

### 执行任务
```bash
uv run scripts/auto-task.py run <task-id|--all>
```

### 管理任务
```bash
uv run scripts/auto-task.py complete <task-id>
uv run scripts/auto-task.py cancel <task-id>
uv run scripts/auto-task.py delete <task-id>
uv run scripts/auto-task.py pause <task-id>
uv run scripts/auto-task.py resume <task-id>
```

### 统计和历史
```bash
uv run scripts/auto-task.py stats
uv run scripts/auto-task.py history --days <days>
uv run scripts/auto-task.py log <task-id>
```

## 注意事项

1. **定时任务** 需要 OpenClaw 的 cron 支持
2. **任务执行** 可能需要相应权限
3. **失败重试** 可配置但默认开启
4. **任务日志** 保存在 `~/.openclaw/auto-tasks/logs/`

## 故障排除

### 任务不执行
- 检查任务状态是否为 `pending`
- 检查是否有依赖任务未完成
- 查看任务日志：`uv run scripts/auto-task.py log <task-id>`

### 定时任务不触发
- 检查 Cron 表达式格式
- 确认 OpenClaw cron 服务运行中
- 查看系统日志

### 任务执行失败
- 查看错误日志
- 检查权限和资源
- 尝试手动执行相同命令

## 贡献

欢迎提交 Issue 和 PR！

- Bug 报告
- 功能建议
- 任务模板分享

---

**作者**: 米仔  
**创建日期**: 2026-03-21  
**许可证**: MIT
