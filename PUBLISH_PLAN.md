# ClawHub 发布计划

## 目标
将 workspace 中的优质技能发布到 ClawHub，让更多人发现和使用。

## 已发布技能
- ✅ searxng (v1.0.3) - 已发布

## 待发布技能列表

### 高优先级（核心功能）

| 技能 | 描述 | 状态 |
|------|------|------|
| byterover | 文件系统导航和管理 | ⚠️ 需要完善文档 |
| clawdirect | 原生消息通信 | ⚠️ 需要完善文档 |
| capability-evolver | 自我进化能力 | ⚠️ 需要完善文档 |
| whisper-stt | 语音识别（中文） | ⚠️ 依赖问题待解决 |

### 中优先级（实用工具）

| 技能 | 描述 | 状态 |
|------|------|------|
| humanize-ai-text | AI 文本人性化 | ✅ 可发布 |
| self-improvement | 自我提升指导 | ✅ 可发布 |
| find-skills | 技能搜索工具 | ✅ 可发布 |

### 低优先级（特定场景）

| 技能 | 描述 | 状态 |
|------|------|------|
| polymarket-odds | Polymarket 赔率 | ✅ 可发布 |
| youtube-watcher | YouTube 监控 | ⚠️ 需要测试 |
| video-frames | 视频帧处理 | ⚠️ 需要测试 |
| tavily | Tavily 搜索 | ⚠️ 需要 API key |
| agent-browser | Agent 浏览器 | ⚠️ 需要测试 |

## 发布步骤

1. **登录 ClawHub**
   ```bash
   export PATH=$PATH:/home/admin/.npm-global/bin
   clawhub login
   ```

2. **批量同步发布**
   ```bash
   cd /home/admin/.openclaw/workspace
   clawhub sync --all --bump patch
   ```

3. **验证发布**
   - 访问 https://clawhub.com
   - 搜索技能名称确认发布成功

## 技能优化清单

发布前需要为每个技能添加：
- [ ] 完整的 SKILL.md（包含用法示例）
- [ ] README.md（详细说明）
- [ ] _meta.json（版本信息）
- [ ] 适当的标签和分类

## 发布后工作

1. 在 GitHub 上创建 OpenClaw 技能集合仓库
2. 编写技能使用指南
3. 分享到社区（Discord、论坛等）

---
*创建时间：2026-03-21*
*执行人：米仔*
