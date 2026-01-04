"""Tool module for Agent Skills

This module provides tools for skill activation in two modes:
- Inline Mode: Skills loaded into main agent context (skill.py)
- Agent as Tool Mode: Skills run in isolated sub-agents (agent_skill.py)
"""

from .skill import create_skill_tool
from .agent_skill import create_skill_agent_tool

__all__ = [
    "create_skill_tool",
    "create_skill_agent_tool",
]


