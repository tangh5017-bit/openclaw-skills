# Site Watcher - 网站监控器

> 🔍 监控网页变化，不错过任何重要更新

## 快速开始

### 1. 添加监控目标

```bash
cd skills/site-watcher

# 监控商品价格
node scripts/watcher.js add "iPhone 15" "https://example.com/iphone" \
  --selector ".price" \
  --condition "value<100" \
  --interval 30

# 监控博客更新
node scripts/watcher.js add "OpenClaw Blog" "https://docs.openclaw.ai/blog" \
  --selector "article" \
  --interval 1440
```

### 2. 查看监控列表

```bash
node scripts/watcher.js list
```

### 3. 手动检查

```bash
node scripts/watcher.js check "iPhone 15"
```

### 4. 运行所有监控（用于 cron）

```bash
node scripts/watcher.js run --all
```

## 配置示例

编辑 `config.yaml`:

```yaml
targets:
  - name: "iPhone 15"
    url: "https://example.com/iphone"
    selector: ".price"
    interval: 30
    condition: "value<100"
    notify: "heartbeat"
    enabled: true
    
  - name: "GitHub Status"
    url: "https://www.githubstatus.com"
    selector: ".status-indicator"
    interval: 5
    condition: "any"
    notify: "heartbeat"
    enabled: true
```

## 条件语法

| 条件 | 描述 | 示例 |
|------|------|------|
| `any` | 任何变化都通知 | `--condition "any"` |
| `value<100` | 数值小于 100 | 价格低于 100 元 |
| `value>50` | 数值大于 50 | 库存大于 50 |
| `contains="text"` | 包含特定文本 | 包含"有货" |

## Cron 定时任务

```bash
# 每 30 分钟检查一次
*/30 * * * * cd /home/admin/.openclaw/workspace/skills/site-watcher && node scripts/watcher.js run --all
```

## 文件结构

```
site-watcher/
├── SKILL.md           # 技能说明
├── README.md          # 使用指南
├── scripts/
│   └── watcher.js     # 主脚本
├── config.yaml        # 配置文件
└── data/
    └── snapshots.json # 历史快照
```

---
*版本：0.1.0 | 创建时间：2026-03-30 | 作者：米仔*
