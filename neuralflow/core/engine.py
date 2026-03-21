#!/usr/bin/env python3
"""
Execution Engine - 执行引擎
"""

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import asyncio


class StepStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class StepResult:
    """步骤执行结果"""
    step_name: str
    agent_id: str
    status: StepStatus
    input_data: Optional[Dict[str, Any]]
    output_data: Optional[Dict[str, Any]]
    error: Optional[str]
    started_at: Optional[str]
    completed_at: Optional[str]


@dataclass
class WorkflowResult:
    """工作流执行结果"""
    workflow_name: str
    status: StepStatus
    step_results: List[StepResult]
    final_output: Optional[Dict[str, Any]]
    started_at: str
    completed_at: Optional[str]
    error: Optional[str]


class ExecutionEngine:
    """执行引擎"""
    
    def __init__(self, agent_registry):
        self.registry = agent_registry
        self.logs_dir = os.path.expanduser("~/.neuralflow/logs")
        os.makedirs(self.logs_dir, exist_ok=True)
    
    def execute_workflow(self, workflow: Dict[str, Any]) -> WorkflowResult:
        """执行工作流"""
        workflow_name = workflow.get("name", "unnamed")
        started_at = datetime.now().isoformat()
        
        print(f"\n🚀 执行工作流：{workflow_name}")
        print(f"{'='*60}\n")
        
        step_results = []
        context = {}  # 步骤间共享的数据上下文
        final_output = None
        workflow_status = StepStatus.RUNNING
        error = None
        
        try:
            steps = workflow.get("steps", [])
            
            for step in steps:
                result = self._execute_step(step, context)
                step_results.append(result)
                
                if result.status == StepStatus.FAILED:
                    workflow_status = StepStatus.FAILED
                    error = result.error
                    break
                
                if result.status == StepStatus.COMPLETED and result.output_data:
                    # 将输出存入上下文，供后续步骤使用
                    context[step.get("output", "result")] = result.output_data
                    final_output = result.output_data
            
            if workflow_status != StepStatus.FAILED:
                workflow_status = StepStatus.COMPLETED
                
        except Exception as e:
            workflow_status = StepStatus.FAILED
            error = str(e)
        
        completed_at = datetime.now().isoformat()
        
        result = WorkflowResult(
            workflow_name=workflow_name,
            status=workflow_status,
            step_results=step_results,
            final_output=final_output,
            started_at=started_at,
            completed_at=completed_at,
            error=error
        )
        
        # 保存日志
        self._save_log(result)
        
        # 打印总结
        self._print_summary(result)
        
        return result
    
    def _execute_step(self, step: Dict[str, Any], context: Dict[str, Any]) -> StepResult:
        """执行单个步骤"""
        step_name = step.get("name", "unknown")
        agent_id = step.get("agent")
        
        print(f"⏳ 执行步骤：{step_name} (Agent: {agent_id})")
        
        started_at = datetime.now().isoformat()
        
        # 获取 Agent
        agent = self.registry.get(agent_id)
        if not agent:
            return StepResult(
                step_name=step_name,
                agent_id=agent_id,
                status=StepStatus.FAILED,
                input_data=None,
                output_data=None,
                error=f"Agent '{agent_id}' not found",
                started_at=started_at,
                completed_at=datetime.now().isoformat()
            )
        
        # 准备输入数据
        input_data = {}
        if "input" in step:
            input_key = step["input"]
            if input_key in context:
                input_data = context[input_key]
            else:
                input_data = {"data": input_key}  # 直接使用字符串
        
        # 模拟 Agent 执行（实际应该调用真实的 Agent）
        output_data = self._simulate_agent_execution(agent, step, input_data)
        
        completed_at = datetime.now().isoformat()
        
        print(f"✅ 步骤完成：{step_name}\n")
        
        return StepResult(
            step_name=step_name,
            agent_id=agent_id,
            status=StepStatus.COMPLETED,
            input_data=input_data,
            output_data=output_data,
            error=None,
            started_at=started_at,
            completed_at=completed_at
        )
    
    def _simulate_agent_execution(self, agent, step: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        模拟 Agent 执行
        实际实现应该调用真实的 Agent API
        """
        # 这里只是模拟，实际应该根据 Agent 类型调用不同的服务
        agent_type = agent.type
        
        if agent_type == "search":
            return {
                "data": f"[Research] Searched for: {input_data.get('query', 'topic')}",
                "sources": ["source1.com", "source2.com"],
                "summary": "Research summary here..."
            }
        elif agent_type == "writing":
            return {
                "content": f"[Article] Written based on: {str(input_data)[:100]}...",
                "word_count": 1000,
                "outline": ["Introduction", "Body", "Conclusion"]
            }
        elif agent_type == "review":
            return {
                "feedback": "Good content, minor improvements needed",
                "revisions": "Revised content here...",
                "score": 8.5
            }
        elif agent_type == "publish":
            return {
                "url": "https://example.com/post/123",
                "status": "published",
                "post_id": "123"
            }
        else:
            return {
                "result": f"Executed by {agent.id}",
                "data": input_data
            }
    
    def _save_log(self, result: WorkflowResult):
        """保存执行日志"""
        log_file = os.path.join(
            self.logs_dir,
            f"{result.workflow_name.replace(' ', '_')}_{result.started_at[:19].replace(':', '-')}.json"
        )
        
        log_data = {
            "workflow_name": result.workflow_name,
            "status": result.status.value,
            "started_at": result.started_at,
            "completed_at": result.completed_at,
            "error": result.error,
            "steps": [
                {
                    "name": sr.step_name,
                    "agent": sr.agent_id,
                    "status": sr.status.value,
                    "started_at": sr.started_at,
                    "completed_at": sr.completed_at,
                    "error": sr.error
                }
                for sr in result.step_results
            ]
        }
        
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, ensure_ascii=False, indent=2)
    
    def _print_summary(self, result: WorkflowResult):
        """打印执行总结"""
        print(f"\n{'='*60}")
        print(f"📊 执行总结")
        print(f"{'='*60}")
        print(f"工作流：{result.workflow_name}")
        print(f"状态：{result.status.value}")
        print(f"开始：{result.started_at}")
        print(f"完成：{result.completed_at}")
        print(f"步骤数：{len(result.step_results)}")
        
        if result.error:
            print(f"错误：{result.error}")
        
        print(f"\n步骤详情:")
        for i, step in enumerate(result.step_results, 1):
            status_icon = {
                "completed": "✅",
                "failed": "❌",
                "skipped": "⏭️"
            }.get(step.status.value, "❓")
            print(f"  {i}. {status_icon} {step.step_name} ({step.agent_id})")
        
        if result.final_output:
            print(f"\n最终输出:")
            print(f"  {json.dumps(result.final_output, indent=2)[:200]}...")
