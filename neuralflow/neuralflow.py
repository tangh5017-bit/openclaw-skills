#!/usr/bin/env python3
"""
NeuralFlow CLI - AI Agent 编排系统
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.orchestrator import Orchestrator


def main():
    if len(sys.argv) < 2:
        print_help()
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "run":
        if len(sys.argv) < 3:
            print("❌ 错误：请指定工作流文件")
            print("用法：python neuralflow.py run <workflow.yaml>")
            sys.exit(1)
        
        workflow_path = sys.argv[2]
        run_workflow(workflow_path)
    
    elif command == "list":
        list_agents()
    
    elif command == "help":
        print_help()
    
    else:
        print(f"❌ 未知命令：{command}")
        print_help()
        sys.exit(1)


def run_workflow(workflow_path):
    """运行工作流"""
    orchestrator = Orchestrator()
    result = orchestrator.run(workflow_path)
    
    print(f"\n{'='*60}")
    if result.status.value == "completed":
        print("✅ 工作流执行成功!")
    else:
        print(f"❌ 工作流执行失败：{result.error}")
        sys.exit(1)


def list_agents():
    """列出已注册的 Agent"""
    from core.registry import init_default_registry
    
    registry = init_default_registry()
    
    print("\n📋 已注册的 Agent:\n")
    for agent in registry.list_all():
        print(f"  • {agent.id}: {agent.name} ({agent.type})")
        print(f"    状态：{agent.status}")
        print(f"    能力：{', '.join([c.name for c in agent.capabilities])}")
        print()


def print_help():
    """打印帮助信息"""
    help_text = """
🧠 NeuralFlow - AI Agent 编排系统

用法：python neuralflow.py <command> [options]

命令:
  run <workflow.yaml>    运行工作流
  list                   列出已注册的 Agent
  help                   显示帮助信息

示例:
  python neuralflow.py run examples/content_creation.yaml
  python neuralflow.py list

文档：https://github.com/tangh5017-bit/openclaw-skills/tree/main/neuralflow
"""
    print(help_text)


if __name__ == "__main__":
    main()
