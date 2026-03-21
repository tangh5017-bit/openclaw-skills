#!/usr/bin/env python3
"""
Agent Registry - Agent 注册与发现系统
"""

import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class AgentCapability:
    """Agent 能力描述"""
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    tags: List[str]


@dataclass
class Agent:
    """Agent 定义"""
    id: str
    name: str
    description: str
    type: str
    capabilities: List[AgentCapability]
    config: Dict[str, Any]
    created_at: str
    updated_at: str
    status: str = "active"  # active, inactive, busy


class AgentRegistry:
    """Agent 注册表"""
    
    def __init__(self, storage_path: str = "~/.neuralflow/agents.json"):
        self.storage_path = os.path.expanduser(storage_path)
        self.agents: Dict[str, Agent] = {}
        self._load()
    
    def _load(self):
        """从文件加载"""
        if os.path.exists(self.storage_path):
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for agent_id, agent_data in data.items():
                    self.agents[agent_id] = Agent(**agent_data)
    
    def _save(self):
        """保存到文件"""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        data = {k: asdict(v) for k, v in self.agents.items()}
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def register(self, agent: Agent):
        """注册 Agent"""
        self.agents[agent.id] = agent
        self._save()
        print(f"✅ Agent 已注册：{agent.id} ({agent.name})")
    
    def unregister(self, agent_id: str):
        """注销 Agent"""
        if agent_id in self.agents:
            del self.agents[agent_id]
            self._save()
            print(f"✅ Agent 已注销：{agent_id}")
        else:
            print(f"❌ Agent 不存在：{agent_id}")
    
    def get(self, agent_id: str) -> Optional[Agent]:
        """获取 Agent"""
        return self.agents.get(agent_id)
    
    def list_all(self) -> List[Agent]:
        """列出所有 Agent"""
        return list(self.agents.values())
    
    def search_by_capability(self, required_capability: str) -> List[Agent]:
        """根据能力搜索 Agent"""
        matches = []
        for agent in self.agents.values():
            if agent.status != "active":
                continue
            for cap in agent.capabilities:
                if (required_capability.lower() in cap.name.lower() or
                    required_capability.lower() in cap.description.lower() or
                    any(required_capability.lower() in tag.lower() for tag in cap.tags)):
                    matches.append(agent)
                    break
        return matches
    
    def find_best_agent(self, task_description: str) -> Optional[Agent]:
        """为任务找到最合适的 Agent"""
        candidates = self.search_by_capability(task_description)
        if not candidates:
            return None
        # 简单策略：返回第一个（后续可以加入评分机制）
        return candidates[0]
    
    def update_status(self, agent_id: str, status: str):
        """更新 Agent 状态"""
        if agent_id in self.agents:
            self.agents[agent_id].status = status
            self.agents[agent_id].updated_at = datetime.now().isoformat()
            self._save()


# 预定义的 Agent 模板
BUILTIN_AGENTS = {
    "researcher": Agent(
        id="researcher",
        name="Researcher Agent",
        description="搜索和研究信息的 Agent",
        type="search",
        capabilities=[
            AgentCapability(
                name="web_search",
                description="搜索互联网信息",
                input_schema={"type": "object", "properties": {"query": {"type": "string"}}},
                output_schema={"type": "object", "properties": {"results": {"type": "array"}}},
                tags=["search", "research", "web"]
            ),
            AgentCapability(
                name="information_gathering",
                description="收集特定主题的信息",
                input_schema={"type": "object", "properties": {"topic": {"type": "string"}}},
                output_schema={"type": "object", "properties": {"data": {"type": "string"}}},
                tags=["research", "gather"]
            )
        ],
        config={"model": "gpt-4", "search_engine": "searxng"},
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat()
    ),
    
    "writer": Agent(
        id="writer",
        name="Writer Agent",
        description="撰写内容的 Agent",
        type="writing",
        capabilities=[
            AgentCapability(
                name="article_writing",
                description="撰写文章",
                input_schema={"type": "object", "properties": {"topic": {"type": "string"}, "outline": {"type": "string"}}},
                output_schema={"type": "object", "properties": {"content": {"type": "string"}}},
                tags=["write", "article", "content"]
            ),
            AgentCapability(
                name="creative_writing",
                description="创意写作",
                input_schema={"type": "object", "properties": {"prompt": {"type": "string"}}},
                output_schema={"type": "object", "properties": {"content": {"type": "string"}}},
                tags=["write", "creative"]
            )
        ],
        config={"model": "gpt-4", "style": "professional"},
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat()
    ),
    
    "editor": Agent(
        id="editor",
        name="Editor Agent",
        description="审核和编辑内容的 Agent",
        type="review",
        capabilities=[
            AgentCapability(
                name="content_review",
                description="审核内容质量",
                input_schema={"type": "object", "properties": {"content": {"type": "string"}}},
                output_schema={"type": "object", "properties": {"feedback": {"type": "string"}, "revisions": {"type": "string"}}},
                tags=["edit", "review", "quality"]
            ),
            AgentCapability(
                name="proofreading",
                description="校对和修正",
                input_schema={"type": "object", "properties": {"text": {"type": "string"}}},
                output_schema={"type": "object", "properties": {"corrected": {"type": "string"}}},
                tags=["edit", "proofread"]
            )
        ],
        config={"model": "gpt-4", "focus": ["grammar", "clarity", "accuracy"]},
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat()
    ),
    
    "publisher": Agent(
        id="publisher",
        name="Publisher Agent",
        description="发布内容到平台的 Agent",
        type="publish",
        capabilities=[
            AgentCapability(
                name="blog_publish",
                description="发布到博客平台",
                input_schema={"type": "object", "properties": {"content": {"type": "string"}, "platform": {"type": "string"}}},
                output_schema={"type": "object", "properties": {"url": {"type": "string"}, "status": {"type": "string"}}},
                tags=["publish", "blog", "wordpress"]
            ),
            AgentCapability(
                name="social_media_post",
                description="发布到社交媒体",
                input_schema={"type": "object", "properties": {"content": {"type": "string"}, "platform": {"type": "string"}}},
                output_schema={"type": "object", "properties": {"post_id": {"type": "string"}}},
                tags=["publish", "social", "twitter"]
            )
        ],
        config={"platforms": ["wordpress", "medium", "twitter"]},
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat()
    )
}


def init_default_registry() -> AgentRegistry:
    """初始化默认注册表（包含内置 Agent）"""
    registry = AgentRegistry()
    for agent in BUILTIN_AGENTS.values():
        registry.register(agent)
    return registry


if __name__ == "__main__":
    # 测试
    registry = init_default_registry()
    print(f"\n📋 已注册 {len(registry.agents)} 个 Agent:\n")
    for agent in registry.list_all():
        print(f"  • {agent.id}: {agent.name} ({agent.type})")
    
    # 测试搜索
    print("\n🔍 搜索 'writing' 相关 Agent:")
    matches = registry.search_by_capability("writing")
    for agent in matches:
        print(f"  • {agent.id}: {agent.name}")
