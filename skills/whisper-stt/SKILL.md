---
name: whisper-stt
description: 本地语音识别（Whisper），免费离线，支持中文
author: 米仔
version: 1.0.0
metadata: {"clawdbot":{"emoji":"🎤","requires":{"bins":["python3","pip"]},"config":{"env":{"WHISPER_MODEL":{"description":"Whisper 模型大小 (tiny/base/small/medium/large)","default":"base","required":false}}}}}
---

# Whisper 语音识别 Skill

使用 OpenAI Whisper 进行本地语音识别，完全免费、离线运行。

## 安装依赖

```bash
pip install openai-whisper
# 或者
pip install faster-whisper  # 更快版本
```

## 使用方法

### 基础用法
```bash
uv run scripts/whisper-transcribe.py audio.mp3
uv run scripts/whisper-transcribe.py audio.wav --language zh
```

### 指定模型
```bash
export WHISPER_MODEL=small
uv run scripts/whisper-transcribe.py audio.mp3
```

### 输出格式
```bash
uv run scripts/whisper-transcribe.py audio.mp3 --format json
uv run scripts/whisper-transcribe.py audio.mp3 --format text
```

## 模型选择

| 模型 | 大小 | 速度 | 准确度 | 推荐场景 |
|------|------|------|--------|----------|
| tiny | 39M | 最快 | 一般 | 快速测试 |
| base | 74M | 快 | 好 | 日常使用 |
| small | 244M | 中等 | 很好 | 中文推荐 |
| medium | 769M | 慢 | 优秀 | 高精度 |
| large | 1.5G | 最慢 | 最佳 | 专业场景 |

## 支持的语言

- 中文 (zh) ✅
- 英语 (en) ✅
- 日语 (ja)
- 韩语 (ko)
- 等 100+ 语言（自动检测）

## 注意事项

- 首次运行会下载模型（74MB-1.5GB）
- 需要 Python 3.8+
- GPU 加速可选（需要 CUDA）
