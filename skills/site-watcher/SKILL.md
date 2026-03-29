---
name: site-watcher
description: 网站监控器 - 监控网页变化、价格追踪、内容更新通知
metadata:
  {
    "openclaw":
      {
        "requires": { "bins": ["node", "curl"] }
      }
  }
---

# Site Watcher Skill - 网站监控器

## Purpose

监控指定网页的变化，包括：
- 价格变动（电商商品）
- 内容更新（新闻、博客）
- 状态变化（服务状态页）
- 库存变化（有货/无货）

当检测到变化时，通过 OpenClaw 发送通知。

## Usage

### 基本用法

```bash
cd skills/site-watcher

# 添加监控目标
node scripts/watcher.js add "商品名称" "https://example.com/product/123" --selector ".price"

# 查看所有监控任务
node scripts/watcher.js list

# 立即检查一次
node scripts/watcher.js check "商品名称"

# 删除监控任务
node scripts/watcher.js remove "商品名称"
```

### 配置选项

| 选项 | 描述 | 默认值 |
|------|------|--------|
| `--selector` | CSS 选择器，提取特定元素 | `body` (整个页面) |
| `--interval` | 检查间隔（分钟） | 60 |
| `--notify` | 通知渠道 | `heartbeat` |
| `--condition` | 触发条件（如 `price<100`） | `any` (任何变化) |

### 示例

```bash
# 监控商品价格，低于 100 元时通知
node scripts/watcher.js add "iPhone 15" "https://example.com/iphone" \
  --selector ".price" \
  --condition "value<100" \
  --interval 30

# 监控博客更新
node scripts/watcher.js add "OpenClaw Blog" "https://docs.openclaw.ai/blog" \
  --selector "article" \
  --interval 1440

# 监控服务状态
node scripts/watcher.js add "GitHub Status" "https://www.githubstatus.com" \
  --selector ".status-indicator" \
  --interval 5
```

## Configuration

配置文件：`config.yaml`

```yaml
targets:
  - name: "商品名称"
    url: "https://example.com/product"
    selector: ".price"
    interval: 30  # 分钟
    condition: "value<100"
    notify: "heartbeat"
    enabled: true
```

## Features

### 1. 智能内容提取

- 支持 CSS 选择器精确定位
- 自动提取文本、价格、状态等信息
- 支持正则表达式过滤

### 2. 变化检测

- 内容哈希对比
- 数值比较（价格、数量）
- 文本差异检测

### 3. 条件触发

支持的条件：
- `value<100` - 数值小于 100
- `value>50` - 数值大于 50
- `contains="关键词"` - 包含特定文本
- `any` - 任何变化都通知

### 4. 通知聚合

- 避免频繁通知（可配置聚合窗口）
- 合并相同目标的变化
- 支持多渠道通知

## Scripts

### `scripts/watcher.js`

主脚本，提供 CLI 接口：

```bash
# 添加监控
node scripts/watcher.js add <name> <url> [options]

# 列出所有监控
node scripts/watcher.js list

# 手动检查
node scripts/watcher.js check <name>

# 删除监控
node scripts/watcher.js remove <name>

# 运行所有监控（用于 cron）
node scripts/watcher.js run --all
```

### `scripts/server.js` (可选)

后台运行模式，自动按计划检查：

```bash
node scripts/server.js
```

## Integration

### Cron 定时任务

```bash
# 每 30 分钟检查一次
*/30 * * * * cd /path/to/site-watcher && node scripts/watcher.js run --all
```

### OpenClaw 集成

通过 `sessions_send` 或 `message` 工具发送通知：

```javascript
// 在 notifier.js 中
const { execSync } = require('child_process');

function notify(message) {
  // 通过 OpenClaw 发送消息
  execSync(`openclaw message send --message "${message}"`);
}
```

## Safety

- 尊重 robots.txt
- 设置合理的检查间隔（避免频繁请求）
- 添加 User-Agent 标识
- 支持请求延迟（rate limiting）

## Troubleshooting

### 无法获取页面

1. 检查 URL 是否正确
2. 确认网络连接
3. 检查是否需要登录/Cookie
4. 尝试添加 `--user-agent` 选项

### 选择器不匹配

1. 在浏览器开发者工具中测试选择器
2. 确认页面结构未变化
3. 尝试更通用的选择器

### 通知不发送

1. 检查通知渠道配置
2. 确认 OpenClaw 正常运行
3. 查看日志输出

## File Structure

```
site-watcher/
├── SKILL.md           # 技能说明（本文件）
├── README.md          # 详细使用指南
├── scripts/
│   ├── watcher.js     # 主脚本
│   ├── server.js      # 后台服务模式
│   └── notifier.js    # 通知模块
├── config.yaml        # 配置文件
├── data/
│   └── snapshots.json # 历史快照存储
└── package.json       # Node.js 依赖
```

## Next Steps

- [ ] 添加截图对比功能
- [ ] 支持 JavaScript 渲染页面（Puppeteer）
- [ ] 添加 Web 管理界面
- [ ] 支持多条件组合
- [ ] 导出监控报告

---
*版本：0.1.0 | 创建时间：2026-03-30 | 作者：米仔*
