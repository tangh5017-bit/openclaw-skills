#!/usr/bin/env python3
"""
Whisper 语音识别脚本
用法：python whisper-transcribe.py <音频文件> [--language zh] [--model base] [--format text|json]
"""

import sys
import os
import json
import argparse

def check_dependencies():
    """检查依赖是否已安装"""
    try:
        import whisper
        return "whisper"
    except ImportError:
        pass
    
    try:
        from faster_whisper import WhisperModel
        return "faster-whisper"
    except ImportError:
        return None

def transcribe_with_whisper(audio_path, model_name, language):
    """使用 openai-whisper 转录"""
    import whisper
    
    print(f"⏳ 加载模型：{model_name}...", file=sys.stderr)
    model = whisper.load_model(model_name)
    
    print(f"🎤 转录中：{audio_path}", file=sys.stderr)
    options = {}
    if language:
        options["language"] = language
    
    result = model.transcribe(audio_path, **options)
    return result["text"]

def transcribe_with_faster_whisper(audio_path, model_name, language):
    """使用 faster-whisper 转录（更快）"""
    from faster_whisper import WhisperModel
    
    print(f"⏳ 加载模型：{model_name}...", file=sys.stderr)
    model = WhisperModel(model_name, device="auto", compute_type="auto")
    
    print(f"🎤 转录中：{audio_path}", file=sys.stderr)
    segments, info = model.transcribe(audio_path, language=language if language else None)
    
    text = " ".join([segment.text for segment in segments])
    return text

def main():
    parser = argparse.ArgumentParser(description="Whisper 语音识别")
    parser.add_argument("audio_file", help="音频文件路径")
    parser.add_argument("--language", "-l", default=None, help="语言代码 (如：zh, en)")
    parser.add_argument("--model", "-m", default=os.getenv("WHISPER_MODEL", "base"), 
                        help="模型大小：tiny/base/small/medium/large")
    parser.add_argument("--format", "-f", choices=["text", "json"], default="text",
                        help="输出格式")
    
    args = parser.parse_args()
    
    # 检查文件是否存在
    if not os.path.exists(args.audio_file):
        print(f"❌ 文件不存在：{args.audio_file}", file=sys.stderr)
        sys.exit(1)
    
    # 检查依赖
    lib = check_dependencies()
    if not lib:
        print("❌ 未安装 Whisper 依赖！", file=sys.stderr)
        print("请运行：pip install openai-whisper", file=sys.stderr)
        print("或：pip install faster-whisper (推荐，更快)", file=sys.stderr)
        sys.exit(1)
    
    print(f"✅ 使用 {lib}", file=sys.stderr)
    
    # 转录
    try:
        if lib == "faster-whisper":
            text = transcribe_with_faster_whisper(args.audio_file, args.model, args.language)
        else:
            text = transcribe_with_whisper(args.audio_file, args.model, args.language)
        
        # 输出结果
        if args.format == "json":
            output = {
                "success": True,
                "file": args.audio_file,
                "model": args.model,
                "language": args.language or "auto",
                "text": text.strip()
            }
            print(json.dumps(output, ensure_ascii=False, indent=2))
        else:
            print(text.strip())
        
    except Exception as e:
        print(f"❌ 转录失败：{e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
