# WebHook Skill - 使用指南

## 快速开始

### 1. 安装依赖

```bash
cd skills/web-hook
npm install js-yaml
```

### 2. 配置 Webhook

编辑 `config.yaml`，启用你需要的 webhook 来源：

```yaml
webhooks:
  github:
    enabled: true
    secret: "your-github-secret"
    signatureHeader: "X-Hub-Signature-256"
    notifyChannel: heartbeat
```

### 3. 启动服务器

```bash
node server.js
```

服务器将在 `http://localhost:3456` 启动。

### 4. 配置外部服务

在你的 GitHub/GitLab/Stripe 等平台配置 webhook URL：

```
http://your-server-ip:3456/webhook/github
```

使用你在 `config.yaml` 中设置的 secret 作为签名密钥。

## 使用示例

### GitHub Push 通知

1. 在 GitHub 仓库设置中添加 Webhook：
   - Payload URL: `http://your-ip:3456/webhook/github`
   - Secret: `your-secret`
   - Events: Push, Pull Request, Issues

2. 当有 push 事件时，你会收到通知：

```
🔔 **WebHook 通知：github**

事件：push
时间：2026-03-26 06:00:00
仓库：tangh5017-bit/openclaw-skills
分支：refs/heads/master
用户：tangh5017-bit
```

### Stripe 支付通知

1. 在 Stripe Dashboard 添加 Endpoint：
   - URL: `http://your-ip:3456/webhook/stripe`
   - Secret: 使用 Stripe 提供的 signing secret

2. 当支付成功时，你会收到通知。

## 高级用法

### 自定义事件处理器

```javascript
const { WebHookRouter } = require('./router');

const router = new WebHookRouter();

// 注册 GitHub push 事件处理器
router.register('github', 'push', async (event) => {
  console.log('New push to', event.repository.full_name);
  // 自定义逻辑...
});

// 注册过滤器（只处理 master 分支）
const { githubBranchFilter } = require('./router');
router.addFilter('github', githubBranchFilter('master'));
```

### 自定义通知模板

```javascript
const { WebHookNotifier } = require('./notifier');

const notifier = new WebHookNotifier({
  template: (source, event) => {
    return `【${source}】${event.event.action} - ${new Date().toLocaleString()}`;
  },
  aggregationWindow: 10 * 60 * 1000, // 10 分钟聚合
});
```

## API 参考

### HTTP 端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/webhook/:source` | POST | 接收 webhook 事件 |
| `/health` | GET | 健康检查 |

### 响应格式

**成功接收：**
```json
{
  "status": "received",
  "event_id": "abc123"
}
```

**重复事件：**
```json
{
  "status": "duplicate_ignored"
}
```

**签名验证失败：**
```json
{
  "error": "Invalid signature"
}
```

## 安全建议

1. **始终使用签名**：不要禁用签名验证
2. **使用强密钥**：至少 32 字符随机字符串
3. **限制 IP**：在生产环境中配置 IP 白名单
4. **HTTPS**：在公网部署时使用 HTTPS
5. **定期轮换密钥**：建议每季度更换一次

## 故障排除

### 收不到通知

1. 检查服务器是否运行：`curl http://localhost:3456/health`
2. 检查配置：`config.yaml` 中 `enabled: true`
3. 查看日志：服务器控制台输出

### 签名验证失败

1. 确认 secret 匹配
2. 检查签名头名称（GitHub: `X-Hub-Signature-256`）
3. 确认没有额外的空格或换行

### 通知重复

调整 `aggregationWindow` 配置项，增加聚合时间窗口。

## 文件结构

```
web-hook/
├── SKILL.md       # 技能说明
├── README.md      # 使用指南（本文件）
├── server.js      # HTTP 服务器
├── router.js      # 事件路由
├── notifier.js    # 通知输出
├── config.yaml    # 配置文件
└── events.json    # 事件存储（运行时生成）
```

## 下一步

- [ ] 添加 IP 白名单支持
- [ ] 实现持久化存储（SQLite/Redis）
- [ ] 添加 Web 管理界面
- [ ] 支持更多平台（Discord, Slack, etc.）

---
*版本：0.1.0 | 最后更新：2026-03-26*
