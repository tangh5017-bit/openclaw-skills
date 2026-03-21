#!/usr/bin/env python3
"""
Orchestrator - 核心编排器
"""

import yaml
import json
import os
from typing import Dict, Any, Optional
from pathlib import Path

from .registry import AgentRegistry, init_default_registry
from .engine import ExecutionEngine


class Orchestrator:
    """NeuralFlow 编排器"""
    
    def __init__(self, registry: Optional[AgentRegistry] = None):
        self.registry = registry or init_default_registry()
        self.engine = ExecutionEngine(self.registry)
    
    def load_workflow(self, workflow_path: str) -> Dict[str, Any]:
        """加载工作流定义"""
        path = Path(workflow_path)
        
        if not path.exists():
            raise FileNotFoundError(f"工作流文件不存在：{workflow_path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            if path.suffix in ['.yaml', '.yml']:
                workflow = yaml.safe_load(f)
            elif path.suffix == '.json':
                workflow = json.load(f)
            else:
                raise ValueError(f"不支持的文件格式：{path.suffix}")
        
        return workflow
    
    def run(self, workflow_path: str) -> Any:
        """运行工作流"""
        print(f"\n🧠 NeuralFlow - AI Agent 编排系统")
        print(f"{'='*60}")
        
        # 加载工作流
        workflow = self.load_workflow(workflow_path)
        print(f"📄 工作流：{workflow.get('name', 'unnamed')}")
        print(f"📝 描述：{workflow.get('description', '无描述')}")
        print(f"🔢 步骤数：{len(workflow.get('steps', []))}")
        print(f"🤖 Agent 数：{len(workflow.get('agents', []))}")
        
        # 注册工作流中定义的 Agent
        for agent_def in workflow.get("agents", []):
            self._register_agent_from_def(agent_def)
        
        # 执行工作流
        result = self.engine.execute_workflow(workflow)
        
        return result
    
    def _register_agent_from_def(self, agent_def: Dict[str, Any]):
        """从定义注册 Agent"""
        from .registry import Agent, AgentCapability
        from datetime import datetime
        
        agent_id = agent_def.get("id")
        if not agent_id:
            return
        
        # 检查是否已存在
        existing = self.registry.get(agent_id)
        if existing:
            return  # 已存在，跳过
        
        # 创建 Agent
        agent = Agent(
            id=agent_id,
            name=agent_def.get("name", agent_id),
            description=agent_def.get("description", ""),
            type=agent_def.get("type", "generic"),
            capabilities=[
                AgentCapability(
                    name=agent_id,
                    description=agent_def.get("description", ""),
                    input_schema={"type": "object"},
                    output_schema={"type": "object"},
                    tags=[agent_def.get("type", "generic")]
                )
            ],
            config=agent_def.get("config", {}),
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        self.registry.register(agent)


def main():
    """CLI 入口"""
    import sys
    
    if len(sys.argv) < 2:
        print("用法：python orchestrator.py <workflow.yaml>")
        print("\n示例:")
        print("  python orchestrator.py examples/content_creation.yaml")
        sys.exit(1)
    
    workflow_path = sys.argv[1]
    
    orchestrator = Orchestrator()
    result = orchestrator.run(workflow_path)
    
    # 退出码
    if result.status.value == "completed":
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
