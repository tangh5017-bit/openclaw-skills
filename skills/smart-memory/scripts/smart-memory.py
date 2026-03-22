#!/usr/bin/env python3
"""
Smart Memory - 智能记忆管理工具

功能:
- 整理每日记忆
- 归档旧记忆
- 搜索记忆内容
- 优化记忆结构
"""

import os
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# 配置
MEMORY_DIR = Path.home() / ".openclaw" / "workspace" / "memory"
LONG_TERM_MEMORY = Path.home() / ".openclaw" / "workspace" / "MEMORY.md"

def get_memory_files(days_back=None):
    """获取记忆文件列表"""
    if not MEMORY_DIR.exists():
        print(f"❌ 记忆目录不存在：{MEMORY_DIR}")
        return []
    
    files = sorted(MEMORY_DIR.glob("*.md"), reverse=True)
    
    if days_back:
        cutoff = datetime.now() - timedelta(days=days_back)
        files = [f for f in files if datetime.fromtimestamp(f.stat().st_mtime) > cutoff]
    
    return files

def consolidate_today():
    """整理今日记忆"""
    today = datetime.now().strftime("%Y-%m-%d")
    today_file = MEMORY_DIR / f"{today}.md"
    
    if today_file.exists():
        print(f"✅ 今日记忆文件已存在：{today_file}")
        with open(today_file, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"📄 文件大小：{len(content)} 字符")
            print(f"📝 前 200 字符预览:\n{content[:200]}...")
    else:
        print(f"⚠️  今日记忆文件不存在，创建中...")
        today_file.write_text(f"# {today} - 自主运行记录\n\n## 今日工作\n\n- [ ] 待填写\n\n---\n*米仔*\n", encoding='utf-8')
        print(f"✅ 已创建：{today_file}")

def archive_old_memory(days=30):
    """归档旧记忆"""
    print(f"📦 归档 {days} 天前的记忆文件...")
    
    files = get_memory_files()
    cutoff = datetime.now() - timedelta(days=days)
    
    archived = 0
    for file in files:
        mtime = datetime.fromtimestamp(file.stat().st_mtime)
        if mtime < cutoff:
            archive_dir = MEMORY_DIR / "archive" / mtime.strftime("%Y-%m")
            archive_dir.mkdir(parents=True, exist_ok=True)
            file.rename(archive_dir / file.name)
            archived += 1
            print(f"  📁 归档：{file.name} → {archive_dir}/")
    
    print(f"✅ 归档完成：{archived} 个文件")

def search_memory(query):
    """搜索记忆内容"""
    print(f"🔍 搜索记忆：'{query}'")
    
    files = get_memory_files()
    results = []
    
    for file in files:
        content = file.read_text(encoding='utf-8')
        if query.lower() in content.lower():
            lines = content.split('\n')
            matching_lines = [i+1 for i, line in enumerate(lines) if query.lower() in line.lower()]
            results.append((file.name, matching_lines[:5]))  # 最多显示 5 行
    
    if results:
        print(f"\n✅ 找到 {len(results)} 个匹配文件:")
        for filename, lines in results:
            print(f"  📄 {filename}: 第 {', '.join(map(str, lines))} 行")
    else:
        print("❌ 未找到匹配内容")

def optimize_memory():
    """优化记忆结构"""
    print("🔧 优化记忆结构...")
    
    # 检查重复文件
    files = get_memory_files()
    print(f"  📊 总记忆文件数：{len(files)}")
    
    # 检查长期记忆
    if LONG_TERM_MEMORY.exists():
        content = LONG_TERM_MEMORY.read_text(encoding='utf-8')
        print(f"  📄 长期记忆大小：{len(content)} 字符")
    else:
        print(f"  ⚠️  长期记忆文件不存在")
    
    # 检查文件命名规范
    invalid_files = [f for f in files if not f.name.startswith(('20', 'archive'))]
    if invalid_files:
        print(f"  ⚠️  发现 {len(invalid_files)} 个命名不规范的文件:")
        for f in invalid_files:
            print(f"    - {f.name}")
    else:
        print(f"  ✅ 所有文件命名规范")
    
    print("✅ 优化完成")

def main():
    parser = argparse.ArgumentParser(description="Smart Memory - 智能记忆管理")
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # consolidate 命令
    consolidate_parser = subparsers.add_parser('consolidate', help='整理记忆')
    consolidate_parser.add_argument('--today', action='store_true', help='整理今日记忆')
    
    # archive 命令
    archive_parser = subparsers.add_parser('archive', help='归档旧记忆')
    archive_parser.add_argument('--older-than', type=int, default=30, help='归档多少天前的记忆')
    
    # search 命令
    search_parser = subparsers.add_parser('search', help='搜索记忆')
    search_parser.add_argument('query', help='搜索关键词')
    
    # optimize 命令
    optimize_parser = subparsers.add_parser('optimize', help='优化记忆结构')
    
    args = parser.parse_args()
    
    if args.command == 'consolidate':
        if args.today:
            consolidate_today()
        else:
            print("❌ 请指定 --today 参数")
    elif args.command == 'archive':
        archive_old_memory(args.older_than)
    elif args.command == 'search':
        search_memory(args.query)
    elif args.command == 'optimize':
        optimize_memory()
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
