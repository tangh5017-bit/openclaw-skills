#!/usr/bin/env python3
"""
Auto-Task 自主任务管理器
让 AI 能自主安排、执行、跟踪任务

用法：
    python auto-task.py create "任务名称" --priority high
    python auto-task.py list
    python auto-task.py run <task-id>
    python auto-task.py complete <task-id>
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
import hashlib

# 配置
DATA_DIR = os.getenv(
    "AUTO_TASK_DATA_DIR",
    os.path.expanduser("~/.openclaw/auto-tasks")
)
TASKS_FILE = os.path.join(DATA_DIR, "tasks.json")
LOGS_DIR = os.path.join(DATA_DIR, "logs")

def ensure_dirs():
    """确保数据目录存在"""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(LOGS_DIR, exist_ok=True)
    if not os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, 'w', encoding='utf-8') as f:
            json.dump({"tasks": [], "next_id": 1}, f, ensure_ascii=False, indent=2)

def load_tasks():
    """加载任务数据"""
    ensure_dirs()
    with open(TASKS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_tasks(data):
    """保存任务数据"""
    ensure_dirs()
    with open(TASKS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def generate_id(name):
    """生成任务 ID"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    hash_part = hashlib.md5(f"{name}{timestamp}".encode()).hexdigest()[:6]
    return f"task-{hash_part}"

def create_task(args):
    """创建新任务"""
    data = load_tasks()
    
    task_id = args.id or generate_id(args.name)
    
    # 检查 ID 是否已存在
    if any(t["id"] == task_id for t in data["tasks"]):
        print(f"❌ 任务 ID '{task_id}' 已存在")
        sys.exit(1)
    
    task = {
        "id": task_id,
        "name": args.name,
        "description": args.description or "",
        "type": args.type or "once",
        "status": "pending",
        "priority": args.priority or "normal",
        "tags": args.tags.split(",") if args.tags else [],
        "depends_on": args.depends_on.split(",") if args.depends_on else [],
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "completed_at": None,
        "schedule": args.schedule,
        "interval": args.interval,
        "actions": [],
        "metadata": {}
    }
    
    # 如果有 --notify 标志
    if args.notify:
        task["notify_on_complete"] = True
    
    data["tasks"].append(task)
    data["next_id"] += 1
    save_tasks(data)
    
    print(f"✅ 任务创建成功!")
    print(f"   ID: {task_id}")
    print(f"   名称：{task['name']}")
    print(f"   优先级：{task['priority']}")
    print(f"   状态：{task['status']}")
    if task["schedule"]:
        print(f"   计划：{task['schedule']}")
    if task["interval"]:
        print(f"   间隔：{task['interval']}")

def list_tasks(args):
    """列出任务"""
    data = load_tasks()
    tasks = data["tasks"]
    
    # 过滤
    if args.status:
        tasks = [t for t in tasks if t["status"] == args.status]
    if args.priority:
        tasks = [t for t in tasks if t["priority"] == args.priority]
    if args.tags:
        tag_list = args.tags.split(",")
        tasks = [t for t in tasks if any(tag in t["tags"] for tag in tag_list)]
    
    if not tasks:
        print("📭 没有找到任务")
        return
    
    # 输出
    if args.format == "json":
        print(json.dumps(tasks, ensure_ascii=False, indent=2))
    else:
        print(f"\n{'='*60}")
        print(f"📋 任务列表 ({len(tasks)} 个任务)")
        print(f"{'='*60}\n")
        
        # 按优先级排序
        priority_order = {"critical": 0, "high": 1, "normal": 2, "low": 3}
        tasks.sort(key=lambda t: priority_order.get(t["priority"], 2))
        
        for task in tasks:
            status_icon = {
                "pending": "⏳",
                "running": "🔄",
                "completed": "✅",
                "failed": "❌",
                "cancelled": "🚫",
                "skipped": "⏭️"
            }.get(task["status"], "❓")
            
            priority_icon = {
                "critical": "🔴",
                "high": "🟠",
                "normal": "🟢",
                "low": "⚪"
            }.get(task["priority"], "")
            
            print(f"{status_icon} {priority_icon} [{task['id']}] {task['name']}")
            print(f"   状态：{task['status']} | 优先级：{task['priority']}")
            if task["tags"]:
                print(f"   标签：{', '.join(task['tags'])}")
            if task["schedule"]:
                print(f"   计划：{task['schedule']}")
            if task["interval"]:
                print(f"   间隔：{task['interval']}")
            print(f"   创建：{task['created_at']}")
            print()

def run_task(args):
    """执行任务"""
    data = load_tasks()
    
    if args.all:
        # 执行所有待处理任务
        pending_tasks = [t for t in data["tasks"] if t["status"] == "pending"]
        if not pending_tasks:
            print("✅ 没有待处理的任务")
            return
        
        print(f"🚀 执行 {len(pending_tasks)} 个任务...\n")
        for task in pending_tasks:
            execute_task(task)
    else:
        # 执行指定任务
        task = next((t for t in data["tasks"] if t["id"] == args.task_id), None)
        if not task:
            print(f"❌ 任务 '{args.task_id}' 不存在")
            sys.exit(1)
        
        execute_task(task)
        save_tasks(data)

def execute_task(task):
    """执行单个任务"""
    print(f"🔄 执行任务：[{task['id']}] {task['name']}")
    
    # 检查依赖
    if task["depends_on"]:
        data = load_tasks()
        for dep_id in task["depends_on"]:
            dep_task = next((t for t in data["tasks"] if t["id"] == dep_id), None)
            if dep_task and dep_task["status"] != "completed":
                print(f"   ⏭️ 跳过 - 依赖任务 '{dep_id}' 未完成")
                task["status"] = "skipped"
                task["updated_at"] = datetime.now().isoformat()
                return
    
    # 更新状态
    task["status"] = "running"
    task["updated_at"] = datetime.now().isoformat()
    save_tasks(load_tasks())  # 保存中间状态
    
    # 这里可以添加实际的任务执行逻辑
    # 目前只是一个框架，实际执行需要扩展
    
    # 模拟执行成功
    task["status"] = "completed"
    task["completed_at"] = datetime.now().isoformat()
    task["updated_at"] = datetime.now().isoformat()
    
    # 记录日志
    log_file = os.path.join(LOGS_DIR, f"{task['id']}.log")
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"[{datetime.now().isoformat()}] Task completed successfully\n")
    
    print(f"✅ 任务完成：[{task['id']}] {task['name']}")
    
    # 如果需要通知
    if task.get("notify_on_complete"):
        print(f"   📬 发送完成通知...")

def complete_task(args):
    """标记任务为完成"""
    data = load_tasks()
    task = next((t for t in data["tasks"] if t["id"] == args.task_id), None)
    
    if not task:
        print(f"❌ 任务 '{args.task_id}' 不存在")
        sys.exit(1)
    
    task["status"] = "completed"
    task["completed_at"] = datetime.now().isoformat()
    task["updated_at"] = datetime.now().isoformat()
    
    save_tasks(data)
    print(f"✅ 任务已完成：[{task['id']}] {task['name']}")

def cancel_task(args):
    """取消任务"""
    data = load_tasks()
    task = next((t for t in data["tasks"] if t["id"] == args.task_id), None)
    
    if not task:
        print(f"❌ 任务 '{args.task_id}' 不存在")
        sys.exit(1)
    
    task["status"] = "cancelled"
    task["updated_at"] = datetime.now().isoformat()
    
    save_tasks(data)
    print(f"🚫 任务已取消：[{task['id']}] {task['name']}")

def delete_task(args):
    """删除任务"""
    data = load_tasks()
    task = next((t for t in data["tasks"] if t["id"] == args.task_id), None)
    
    if not task:
        print(f"❌ 任务 '{args.task_id}' 不存在")
        sys.exit(1)
    
    data["tasks"] = [t for t in data["tasks"] if t["id"] != args.task_id]
    save_tasks(data)
    print(f"🗑️ 任务已删除：[{task['id']}] {task['name']}")

def show_stats(args):
    """显示统计信息"""
    data = load_tasks()
    tasks = data["tasks"]
    
    total = len(tasks)
    by_status = {}
    by_priority = {}
    
    for task in tasks:
        status = task["status"]
        priority = task["priority"]
        by_status[status] = by_status.get(status, 0) + 1
        by_priority[priority] = by_priority.get(priority, 0) + 1
    
    print("\n" + "="*60)
    print("📊 任务统计")
    print("="*60 + "\n")
    
    print(f"总任务数：{total}")
    print()
    print("按状态:")
    for status, count in sorted(by_status.items()):
        print(f"  {status}: {count}")
    
    print()
    print("按优先级:")
    for priority, count in sorted(by_priority.items()):
        print(f"  {priority}: {count}")
    
    # 完成率
    completed = by_status.get("completed", 0)
    if total > 0:
        rate = (completed / total) * 100
        print(f"\n完成率：{rate:.1f}%")

def show_history(args):
    """显示历史记录"""
    data = load_tasks()
    tasks = data["tasks"]
    
    # 过滤已完成和已取消的任务
    history = [t for t in tasks if t["status"] in ["completed", "cancelled", "failed"]]
    
    # 按时间排序
    history.sort(key=lambda t: t.get("completed_at") or t["updated_at"], reverse=True)
    
    # 限制天数
    if args.days:
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(days=args.days)
        history = [
            t for t in history 
            if datetime.fromisoformat(t.get("completed_at") or t["updated_at"]) > cutoff
        ]
    
    if not history:
        print("📭 没有历史记录")
        return
    
    print(f"\n{'='*60}")
    print(f"📜 历史记录 ({len(history)} 个任务)")
    print(f"{'='*60}\n")
    
    for task in history[:20]:  # 只显示最近 20 个
        status_icon = {
            "completed": "✅",
            "cancelled": "🚫",
            "failed": "❌"
        }.get(task["status"], "❓")
        
        completed_at = task.get("completed_at") or task["updated_at"]
        print(f"{status_icon} [{task['id']}] {task['name']}")
        print(f"   完成时间：{completed_at}")
        print()

def show_log(args):
    """显示任务日志"""
    log_file = os.path.join(LOGS_DIR, f"{args.task_id}.log")
    
    if not os.path.exists(log_file):
        print(f"📭 没有找到任务 '{args.task_id}' 的日志")
        return
    
    with open(log_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"\n📜 任务日志：{args.task_id}\n")
    print(content)

def main():
    parser = argparse.ArgumentParser(
        description="Auto-Task 自主任务管理器",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    # create 命令
    create_parser = subparsers.add_parser("create", help="创建新任务")
    create_parser.add_argument("name", help="任务名称")
    create_parser.add_argument("--id", help="自定义任务 ID")
    create_parser.add_argument("--description", "-d", help="任务描述")
    create_parser.add_argument("--type", "-t", choices=["once", "recurring"], default="once",
                               help="任务类型")
    create_parser.add_argument("--schedule", "-s", help="Cron 表达式")
    create_parser.add_argument("--interval", "-i", help="时间间隔 (30m/1h/2d)")
    create_parser.add_argument("--priority", "-p", 
                               choices=["critical", "high", "normal", "low"],
                               default="normal", help="优先级")
    create_parser.add_argument("--tags", help="标签（逗号分隔）")
    create_parser.add_argument("--depends-on", help="依赖的任务 ID")
    create_parser.add_argument("--notify", "-n", action="store_true",
                               help="完成后通知")
    
    # list 命令
    list_parser = subparsers.add_parser("list", help="列出任务")
    list_parser.add_argument("--status", "-s", 
                             choices=["pending", "running", "completed", 
                                      "failed", "cancelled", "skipped"],
                             help="按状态过滤")
    list_parser.add_argument("--priority", "-p",
                             choices=["critical", "high", "normal", "low"],
                             help="按优先级过滤")
    list_parser.add_argument("--tags", "-t", help="按标签过滤")
    list_parser.add_argument("--format", "-f", choices=["table", "json"],
                             default="table", help="输出格式")
    
    # run 命令
    run_parser = subparsers.add_parser("run", help="执行任务")
    run_parser.add_argument("task_id", nargs="?", help="任务 ID")
    run_parser.add_argument("--all", "-a", action="store_true",
                            help="执行所有待处理任务")
    
    # complete 命令
    complete_parser = subparsers.add_parser("complete", help="标记任务为完成")
    complete_parser.add_argument("task_id", help="任务 ID")
    
    # cancel 命令
    cancel_parser = subparsers.add_parser("cancel", help="取消任务")
    cancel_parser.add_argument("task_id", help="任务 ID")
    
    # delete 命令
    delete_parser = subparsers.add_parser("delete", help="删除任务")
    delete_parser.add_argument("task_id", help="任务 ID")
    
    # stats 命令
    stats_parser = subparsers.add_parser("stats", help="显示统计信息")
    
    # history 命令
    history_parser = subparsers.add_parser("history", help="显示历史记录")
    history_parser.add_argument("--days", "-d", type=int,
                                help="显示最近 N 天的记录")
    
    # log 命令
    log_parser = subparsers.add_parser("log", help="显示任务日志")
    log_parser.add_argument("task_id", help="任务 ID")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    commands = {
        "create": create_task,
        "list": list_tasks,
        "run": run_task,
        "complete": complete_task,
        "cancel": cancel_task,
        "delete": delete_task,
        "stats": show_stats,
        "history": show_history,
        "log": show_log
    }
    
    commands[args.command](args)

if __name__ == "__main__":
    main()
