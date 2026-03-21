---
name: api-connector
description: 通用 API 连接器 - 统一接口调用任何 API
author: 米仔
version: 1.0.0
metadata: {"clawdbot":{"emoji":"🔌","requires":{"bins":["node","curl"]},"config":{"env":{"API_CONNECTOR_CONFIG":{"description":"配置文件路径","default":"~/.openclaw/api-connector/config.json","required":false}}}}}
---

# API Connector 通用 API 连接器

**基础设施技能** - 让任何 API 调用变得简单！

## 核心价值

- 🔌 **统一接口** - 用一种方式调用所有 API
- 🔐 **认证管理** - 安全存储 API Key/OAuth Token
- 📝 **请求构建** - 简化 HTTP 请求构造
- 🔄 **自动重试** - 处理网络波动和速率限制
- 📊 **响应处理** - JSON/XML 自动解析
- 📈 **调用统计** - 追踪 API 使用情况

## 快速开始

### 1. 配置 API

```bash
# 添加一个 API 配置
uv run scripts/api-connector.py config add github \
  --base-url "https://api.github.com" \
  --auth-type "bearer" \
  --token "$GITHUB_TOKEN"
```

### 2. 调用 API

```bash
# 简单 GET 请求
uv run scripts/api-connector.py call github /users/mizai

# 带参数
uv run scripts/api-connector.py call github /repos/{owner}/{repo} \
  --params owner=mizai repo=auto-task

# POST 请求
uv run scripts/api-connector.py call github /repos \
  --method POST \
  --body '{"name":"my-repo","private":true}'
```

### 3. 查看响应

```bash
# 默认输出 JSON
uv run scripts/api-connector.py call github /user

# 输出特定字段
uv run scripts/api-connector.py call github /user --field login,name,email

# 输出为表格
uv run scripts/api-connector.py call github /repos --format table
```

## 支持的认证类型

### API Key
```bash
uv run scripts/api-connector.py config add weather \
  --base-url "https://api.weather.com" \
  --auth-type "api-key" \
  --api-key "$WEATHER_API_KEY" \
  --api-key-header "X-API-Key"
```

### Bearer Token
```bash
uv run scripts/api-connector.py config add openai \
  --base-url "https://api.openai.com/v1" \
  --auth-type "bearer" \
  --token "$OPENAI_API_KEY"
```

### OAuth 2.0
```bash
uv run scripts/api-connector.py config add google \
  --base-url "https://www.googleapis.com" \
  --auth-type "oauth2" \
  --client-id "$GOOGLE_CLIENT_ID" \
  --client-secret "$GOOGLE_CLIENT_SECRET" \
  --redirect-uri "http://localhost:8080/callback"
```

### Basic Auth
```bash
uv run scripts/api-connector.py config add jenkins \
  --base-url "https://jenkins.example.com" \
  --auth-type "basic" \
  --username "$JENKINS_USER" \
  --password "$JENKINS_TOKEN"
```

## 高级功能

### 请求模板

在配置文件中定义常用请求模板：

```json
{
  "apis": {
    "github": {
      "templates": {
        "create-repo": {
          "method": "POST",
          "path": "/user/repos",
          "body": {
            "name": "{{repo_name}}",
            "private": "{{private|false}}",
            "description": "{{description}}"
          }
        },
        "list-issues": {
          "method": "GET",
          "path": "/repos/{owner}/{repo}/issues",
          "params": {
            "state": "{{state|all}}",
            "per_page": "{{per_page|30}}"
          }
        }
      }
    }
  }
}
```

使用模板：
```bash
uv run scripts/api-connector.py template github create-repo \
  --vars repo_name=my-project private=true description="My awesome project"
```

### 批量请求

```bash
# 并行执行多个请求
uv run scripts/api-connector.py batch \
  --requests \
    "github /user" \
    "github /notifications" \
    "github /repos" \
  --parallel 3
```

### 速率限制处理

```json
{
  "apis": {
    "github": {
      "rateLimit": {
        "requests": 5000,
        "period": 3600,
        "retryAfter": 60,
        "backoff": "exponential"
      }
    }
  }
}
```

### 响应缓存

```bash
# 启用缓存（5 分钟）
uv run scripts/api-connector.py call github /repos \
  --cache-ttl 300

# 清除缓存
uv run scripts/api-connector.py cache clear github
```

## 配置文件

位置：`~/.openclaw/api-connector/config.json`

```json
{
  "apis": {
    "github": {
      "baseUrl": "https://api.github.com",
      "authType": "bearer",
      "token": "${GITHUB_TOKEN}",
      "headers": {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "api-connector/1.0"
      },
      "rateLimit": {
        "requests": 5000,
        "period": 3600
      },
      "retry": {
        "maxAttempts": 3,
        "backoff": "exponential"
      }
    },
    "openai": {
      "baseUrl": "https://api.openai.com/v1",
      "authType": "bearer",
      "token": "${OPENAI_API_KEY}",
      "headers": {
        "Content-Type": "application/json"
      }
    },
    "weather": {
      "baseUrl": "https://api.weather.com/v1",
      "authType": "api-key",
      "apiKey": "${WEATHER_API_KEY}",
      "apiKeyHeader": "X-API-Key"
    }
  },
  "defaults": {
    "timeout": 30,
    "retry": {
      "maxAttempts": 3
    }
  }
}
```

## 预配置 API 模板

### GitHub
```bash
uv run scripts/api-connector.py config add github \
  --base-url "https://api.github.com" \
  --auth-type "bearer" \
  --token "$GITHUB_TOKEN"
```

### OpenAI
```bash
uv run scripts/api-connector.py config add openai \
  --base-url "https://api.openai.com/v1" \
  --auth-type "bearer" \
  --token "$OPENAI_API_KEY"
```

### 阿里云
```bash
uv run scripts/api-connector.py config add aliyun \
  --base-url "https://openapi.aliyuncs.com" \
  --auth-type "ak-sk" \
  --access-key "$ALIYUN_ACCESS_KEY" \
  --secret-key "$ALIYUN_SECRET_KEY"
```

### 腾讯云
```bash
uv run scripts/api-connector.py config add tencent \
  --base-url "https://cvm.tencentcloudapi.com" \
  --auth-type "tc-sign" \
  --secret-id "$TENCENT_SECRET_ID" \
  --secret-key "$TENCENT_SECRET_KEY"
```

## 命令参考

### 配置管理
```bash
uv run scripts/api-connector.py config add <name> [options]
uv run scripts/api-connector.py config list
uv run scripts/api-connector.py config remove <name>
uv run scripts/api-connector.py config show <name>
```

### API 调用
```bash
uv run scripts/api-connector.py call <api> <path> [options]
uv run scripts/api-connector.py template <api> <template> [options]
uv run scripts/api-connector.py batch --requests <requests...>
```

### 缓存管理
```bash
uv run scripts/api-connector.py cache clear <api>
uv run scripts/api-connector.py cache stats
```

### 统计信息
```bash
uv run scripts/api-connector.py stats
uv run scripts/api-connector.py history --days 7
```

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `API_CONNECTOR_CONFIG` | 配置文件路径 | `~/.openclaw/api-connector/config.json` |
| `API_CONNECTOR_DEBUG` | 调试模式 | `false` |
| `API_CONNECTOR_TIMEOUT` | 默认超时（秒） | `30` |

## 安全最佳实践

1. **使用环境变量存储敏感信息**
   ```bash
   export GITHUB_TOKEN="your-token-here"
   ```

2. **不要在配置文件中硬编码密钥**
   ```json
   // ✅ 好
   "token": "${GITHUB_TOKEN}"
   
   // ❌ 坏
   "token": "ghp_xxxxxxxxxxxx"
   ```

3. **定期轮换密钥**
   ```bash
   uv run scripts/api-connector.py config rotate github
   ```

4. **限制 API 权限**
   - 使用最小权限原则
   - 为不同用途创建不同的密钥

## 故障排除

### 认证失败
```bash
# 检查配置
uv run scripts/api-connector.py config show github

# 测试连接
uv run scripts/api-connector.py call github /user --verbose
```

### 速率限制
```bash
# 查看剩余配额
uv run scripts/api-connector.py call github /rate_limit

# 等待重置
uv run scripts/api-connector.py wait github
```

### 响应解析错误
```bash
# 查看原始响应
uv run scripts/api-connector.py call github /repos --raw

# 检查内容类型
uv run scripts/api-connector.py call github /repos --headers
```

## 贡献

欢迎提交 Issue 和 PR！

- 新 API 适配器
- Bug 报告
- 功能建议

---

**作者**: 米仔  
**创建日期**: 2026-03-21  
**许可证**: MIT
