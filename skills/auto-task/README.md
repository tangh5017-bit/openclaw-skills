# Auto-Task 自主任务管理器

> **让 AI 从被动响应变为主动执行！**

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)]()
[![License](https://img.shields.io/badge/license-MIT-green.svg)]()
[![Author](https://img.shields.io/badge/author-米仔-orange.svg)]()

## 🌟 特性

- ✅ **任务管理** - 创建、执行、跟踪任务
- 🔄 **定时任务** - Cron 表达式支持
- ⏰ **间隔任务** - 按固定间隔执行
- 🔗 **任务依赖** - 任务间的依赖关系
- 📊 **统计分析** - 任务完成情况统计
- 📝 **执行日志** - 完整的执行记录
- 🏷️ **标签系统** - 灵活的任务分类
- 🎯 **优先级** - 智能任务排序

## 🚀 快速开始

### 安装

```bash
# 通过 ClawHub 安装（发布后）
clawhub install auto-task

# 或手动克隆
git clone <repo-url> ~/.openclaw/workspace/skills/auto-task
```

### 创建第一个任务

```bash
# 创建一个高优先级任务
uv run scripts/auto-task.py create "检查未读邮件" --priority high

# 创建一个定时任务（每天早上 9 点）
uv run scripts/auto-task.py create "每日自检" --schedule "0 9 * * *"

# 创建一个间隔任务（每 30 分钟）
uv run scripts/auto-task.py create "检查新消息" --interval 30m
```

### 查看和管理任务

```bash
# 查看所有任务
uv run scripts/auto-task.py list

# 查看待处理任务
uv run scripts/auto-task.py list --status pending

# 执行任务
uv run scripts/auto-task.py run <task-id>

# 执行所有待处理任务
uv run scripts/auto-task.py run --all

# 完成任务
uv run scripts/auto-task.py complete <task-id>
```

## 📖 完整文档

详见 [SKILL.md](SKILL.md)

## 💡 使用场景

### 1. 个人效率
```bash
# 每日待办提醒
uv run scripts/auto-task.py create "今日计划" --schedule "0 9 * * *"
uv run scripts/auto-task.py create "下班总结" --schedule "0 18 * * *"
```

### 2. 文件管理
```bash
# 定期整理下载文件夹
uv run scripts/auto-task.py create "整理 Downloads" --interval 1h
```

### 3. 系统监控
```bash
# 检查磁盘空间
uv run scripts/auto-task.py create "检查磁盘" --interval 6h
```

### 4. 数据备份
```bash
# 每日备份
uv run scripts/auto-task.py create "备份 workspace" --schedule "0 2 * * *"
```

## 🔧 配置

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

## 📊 命令参考

| 命令 | 说明 |
|------|------|
| `create` | 创建新任务 |
| `list` | 列出任务 |
| `run` | 执行任务 |
| `complete` | 标记完成 |
| `cancel` | 取消任务 |
| `delete` | 删除任务 |
| `stats` | 显示统计 |
| `history` | 历史记录 |
| `log` | 查看日志 |

## 🎯 任务状态

- ⏳ `pending` - 待处理
- 🔄 `running` - 执行中
- ✅ `completed` - 已完成
- ❌ `failed` - 执行失败
- 🚫 `cancelled` - 已取消
- ⏭️ `skipped` - 已跳过

## 🏷️ 优先级

- 🔴 `critical` - 紧急重要
- 🟠 `high` - 高优先级
- 🟢 `normal` - 普通
- ⚪ `low` - 低优先级

## 📝 示例

### 创建带标签的任务
```bash
uv run scripts/auto-task.py create "备份代码" --tags backup,code,daily
```

### 创建依赖任务
```bash
# 先创建前置任务
uv run scripts/auto-task.py create "下载数据" --id task-download

# 创建依赖任务
uv run scripts/auto-task.py create "处理数据" --depends-on task-download
```

### 查看统计
```bash
uv run scripts/auto-task.py stats
```

### 查看历史
```bash
uv run scripts/auto-task.py history --days 7
```

## 🐛 故障排除

### 任务不执行
1. 检查任务状态是否为 `pending`
2. 检查依赖任务是否完成
3. 查看日志：`uv run scripts/auto-task.py log <task-id>`

### 定时任务不触发
1. 检查 Cron 表达式格式
2. 确认 OpenClaw cron 服务运行中

### 任务执行失败
1. 查看错误日志
2. 检查权限和资源
3. 尝试手动执行相同命令

## 🤝 贡献

欢迎提交 Issue 和 PR！

- Bug 报告
- 功能建议
- 任务模板分享

## 📄 许可证

MIT License

## 👤 作者

**米仔** - 原创技能开发者

创建日期：2026-03-21

---

**让 AI 真正自主起来！** 🚀
