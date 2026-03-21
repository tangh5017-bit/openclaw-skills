# API Connector 通用 API 连接器

> **统一接口，调用任何 API**

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)]()
[![License](https://img.shields.io/badge/license-MIT-green.svg)]()
[![Author](https://img.shields.io/badge/author-米仔-orange.svg)]()

## 🌟 核心价值

- 🔌 **统一接口** - 用一种方式调用所有 API
- 🔐 **认证管理** - 安全存储 API Key/OAuth Token
- 📝 **请求构建** - 简化 HTTP 请求构造
- 🔄 **自动重试** - 处理网络波动和速率限制
- 📊 **响应处理** - JSON/XML 自动解析
- 📈 **调用统计** - 追踪 API 使用情况

## 🚀 快速开始

### 安装依赖

```bash
pip install httpx
# 或
pip install requests
```

### 配置第一个 API

```bash
# 配置 GitHub API
uv run scripts/api-connector.py config add github \
  --base-url "https://api.github.com" \
  --auth-type "bearer" \
  --token "$GITHUB_TOKEN"
```

### 调用 API

```bash
# 获取用户信息
uv run scripts/api-connector.py call github /users/mizai

# 获取仓库列表
uv run scripts/api-connector.py call github /user/repos

# 创建仓库
uv run scripts/api-connector.py call github /user/repos \
  --method POST \
  --body '{"name":"my-repo","private":true}'
```

## 📖 完整文档

详见 [SKILL.md](SKILL.md)

## 💡 使用场景

### 1. GitHub 自动化
```bash
# 查看我的仓库
uv run scripts/api-connector.py call github /user/repos --field name,html_url

# 查看通知
uv run scripts/api-connector.py call github /notifications
```

### 2. OpenAI 调用
```bash
# 配置 OpenAI
uv run scripts/api-connector.py config add openai \
  --base-url "https://api.openai.com/v1" \
  --auth-type "bearer" \
  --token "$OPENAI_API_KEY"

# 调用 ChatGPT
uv run scripts/api-connector.py call openai /chat/completions \
  --method POST \
  --body '{"model":"gpt-3.5-turbo","messages":[{"role":"user","content":"Hello"}]}'
```

### 3. 天气查询
```bash
# 配置天气 API
uv run scripts/api-connector.py config add weather \
  --base-url "https://api.weather.com/v1" \
  --auth-type "api-key" \
  --api-key "$WEATHER_API_KEY"

# 查询天气
uv run scripts/api-connector.py call weather /forecast \
  --query location=beijing days=3
```

## 🔧 支持的认证类型

| 类型 | 说明 | 示例 |
|------|------|------|
| `bearer` | Bearer Token | GitHub, OpenAI |
| `api-key` | API Key | 天气 API, 地图 API |
| `basic` | Basic Auth | Jenkins, 内部服务 |
| `oauth2` | OAuth 2.0 | Google, Microsoft |

## 📊 高级功能

### 缓存
```bash
# 启用 5 分钟缓存
uv run scripts/api-connector.py call github /repos --cache-ttl 300
```

### 详细模式
```bash
# 查看完整请求/响应
uv run scripts/api-connector.py call github /user --verbose
```

### 字段提取
```bash
# 只输出特定字段
uv run scripts/api-connector.py call github /user --field login,name,email
```

### 表格输出
```bash
# 表格格式
uv run scripts/api-connector.py call github /user/repos --format table
```

## 📋 命令参考

| 命令 | 说明 |
|------|------|
| `config add` | 添加 API 配置 |
| `config list` | 列出配置 |
| `config show` | 显示配置详情 |
| `config remove` | 删除配置 |
| `call` | 调用 API |
| `cache clear` | 清除缓存 |
| `stats` | 显示统计 |
| `history` | 查看历史 |

## 🔐 安全最佳实践

1. **使用环境变量存储密钥**
   ```bash
   export GITHUB_TOKEN="your-token"
   ```

2. **不要在配置中硬编码**
   ```json
   // ✅ 好
   "token": "${GITHUB_TOKEN}"
   
   // ❌ 坏
   "token": "ghp_xxxxx"
   ```

3. **定期轮换密钥**

## 🐛 故障排除

### 认证失败
```bash
# 检查配置
uv run scripts/api-connector.py config show github

# 测试连接
uv run scripts/api-connector.py call github /user --verbose
```

### 速率限制
```bash
# 查看配额
uv run scripts/api-connector.py call github /rate_limit
```

## 🤝 贡献

欢迎提交 Issue 和 PR！

## 📄 许可证

MIT License

## 👤 作者

**米仔** - 原创技能开发者

创建日期：2026-03-21

---

**让 API 调用变得简单！** 🔌
