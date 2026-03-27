# WebHook 技能 - 事件驱动通知接收器

## 功能描述
创建一个通用的 Webhook 接收器技能，允许外部服务通过 HTTP POST 发送事件通知到 OpenClaw。

## 核心功能

### 1. 端点管理
- 创建唯一的 webhook URL 端点
- 支持按来源分类：`/webhook/:source` (如 github, stripe, gitlab)
- 端点启用/禁用控制

### 2. 安全验证
- HMAC-SHA256 签名验证
- 支持自定义签名头 (如 `X-Hub-Signature`, `X-Signature`)
- 时间戳验证防止重放攻击
- IP 白名单支持

### 3. 事件处理
- 事件类型路由和过滤
- 幂等性处理 (通过 event_id 去重)
- 异步处理队列
- 失败重试机制

### 4. 通知输出
- 将 webhook 事件转换为 OpenClaw 消息
- 支持多种通知渠道 (heartbeat, message, sessions_send)
- 可配置的通知模板
- 事件聚合 (避免短时间内重复通知)

## 使用场景
- GitHub/GitLab push 事件通知
- 支付成功通知 (Stripe/支付宝/微信)
- CI/CD 流水线状态更新
- 监控告警推送 (Prometheus, Grafana)
- 自定义应用事件通知

## 配置示例

```yaml
webhooks:
  github:
    enabled: true
    secret: "your-secret-key"
    signatureHeader: "X-Hub-Signature-256"
    events: ["push", "pull_request", "issues"]
    notifyChannel: "heartbeat"
  stripe:
    enabled: true
    secret: "stripe-secret"
    signatureHeader: "Stripe-Signature"
    events: ["payment_intent.succeeded", "charge.failed"]
```

## 实现要点

1. **快速响应**: 接收后立刻返回 200，后台异步处理
2. **签名验证**: 必须验证请求来源，拒绝未签名请求
3. **去重机制**: 使用 event_id 或请求哈希防止重复处理
4. **错误处理**: 记录失败事件，支持手动重试
5. **日志记录**: 详细记录所有接收的事件用于调试

## 文件结构

```
web-hook/
├── SKILL.md           # 技能说明 (本文件)
├── server.js          # HTTP 服务器实现
├── verifier.js        # 签名验证模块
├── router.js          # 事件路由和过滤
├── store.js           # 事件存储和去重
└── config.yaml        # 配置文件模板
```

## 实现进度

- [x] 实现基础 HTTP 服务器 (server.js)
  - [x] 路由系统：`/webhook/:source`
  - [x] HMAC-SHA256 签名验证
  - [x] 幂等性处理（event_id 去重）
  - [x] 事件存储（内存，最多 1000 条）
  - [x] 健康检查端点：`/health`
  - [x] CORS 支持
  - [x] Bug 修复：签名验证长度检查（2026-03-28）
- [x] 配置文件模板 (config.yaml)
- [x] 实现事件路由和过滤 (router.js)
  - [x] 路由注册系统
  - [x] 事件过滤器
  - [x] 通用事件类型检测
  - [x] 预定义过滤器 (GitHub branch, Stripe type, etc.)
- [x] 添加 OpenClaw 通知输出集成 (notifier.js)
  - [x] 通知模板系统
  - [x] 事件聚合（避免短时间重复）
  - [x] 写入记忆文件集成
  - [x] CLI 备选方案
- [x] 测试和文档
  - [x] 服务器启动测试
  - [x] 健康检查测试
  - [x] 签名验证测试
  - [x] 事件接收测试
- [ ] 生产部署（端口转发/HTTPS）

---
*创建时间：2026-03-26 | 优先级：P0 | 状态：开发中 (90%)*
