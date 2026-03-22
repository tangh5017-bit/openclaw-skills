---
name: smart-memory
description: 智能记忆管理 - 自动整理、归档、优化 AI 助手的记忆系统
author: 米仔
version: 0.1.0
metadata:
  {
    "openclaw":
      {
        "requires": { "bins": ["node"] }
      }
  }
---

# Smart Memory - 智能记忆管理

自动整理、归档、优化 AI 助手的记忆系统，确保长期记忆的准确性和可用性。

## 核心功能

### 1. 记忆整理
- 扫描 memory/ 目录下的每日记忆文件
- 识别重要事件、决策、学习内容
- 提取关键信息到 MEMORY.md

### 2. 记忆归档
- 自动归档超过 30 天的记忆文件
- 创建月度/年度摘要
- 压缩旧记忆以节省空间

### 3. 记忆优化
- 删除重复或过时的记忆
- 合并相关记忆条目
- 优化记忆结构和标签

### 4. 记忆检索
- 语义搜索记忆内容
- 按日期、主题、重要性过滤
- 快速定位相关记忆

## 使用方式

### 手动触发
```bash
# 整理今日记忆
uv run scripts/smart-memory.py consolidate --today

# 归档旧记忆
uv run scripts/smart-memory.py archive --older-than 30

# 搜索记忆
uv run scripts/smart-memory.py search "关键词"

# 优化记忆结构
uv run scripts/smart-memory.py optimize
```

### 自动触发
通过 cron 设置每日/每周自动执行：
- 每日：整理当日记忆
- 每周：归档旧记忆 + 优化

## 配置文件

在 `~/.openclaw/openclaw.json` 中添加：

```json
{
  "skills": {
    "smart-memory": {
      "archiveAfterDays": 30,
      "consolidateDaily": true,
      "optimizeWeekly": true,
      "searchEngine": "semantic"
    }
  }
}
```

## 记忆结构

### 每日记忆文件 (memory/YYYY-MM-DD.md)
```markdown
# 2026-03-23 - 描述

## 重要事件
- 事件 1
- 事件 2

## 学习内容
- 知识点 1
- 知识点 2

## 决策记录
- 决策 1
- 决策 2
```

### 长期记忆 (MEMORY.md)
```markdown
# 长期记忆

## 用户偏好
- 偏好 1
- 偏好 2

## 重要决策
- 决策 1 (日期)
- 决策 2 (日期)

## 技能与能力
- 技能 1
- 技能 2
```

## 安全与隐私

- 所有记忆操作可逆
- 归档前自动备份
- 敏感信息自动脱敏
- 支持手动审查模式

## 与其他技能集成

- **capability-evolver**: 提供进化历史记忆
- **auto-task**: 记录任务执行历史
- **searxng**: 保存搜索历史和学习内容

## 待实现功能

- [ ] 语义搜索引擎
- [ ] 自动标签生成
- [ ] 记忆重要性评分
- [ ] 跨文件记忆关联
- [ ] 记忆可视化图表

---

*版本：0.1.0 | 作者：米仔 | 创建日期：2026-03-23*
