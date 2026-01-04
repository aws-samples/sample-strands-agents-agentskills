"""Agent Skills - Simple skill system for Strands Agents SDK

This package provides a clean implementation of Agent Skills for Strands SDK
following the AgentSkills.io specification.

Core Features:
    - Progressive Disclosure: Load metadata first, full content on activation
    - Simple Integration: Works seamlessly with Strands SDK
    - Standards Compliant: Follows AgentSkills.io specification

Core Components:
    - models: SkillProperties, SkillMetadata
    - parser: SKILL.md parsing (YAML frontmatter)
    - validator: Validation against AgentSkills.io spec
    - discovery: Skill directory scanning
    - tool: Inline skill tool (loads instructions into main agent context)
    - tool.agent_skill: Agent as Tool pattern (isolated sub-agent execution)
    - prompt: System prompt generation
    - errors: Exception hierarchy
"""

# Core models
from .models import SkillProperties

# Parser functions
from .parser import (
    find_skill_md,
    load_metadata,
    load_instructions,
    load_resource,
)

# Validator functions
from .validator import validate, validate_metadata

# Discovery
from .discovery import discover_skills

# Agent Model
from .agent_model import get_bedrock_agent_model

# Prompt generation
from .prompt import generate_skills_prompt, generate_default_system_prompt, generate_skill_instructions_prompt

# Tool (Inline Mode)
from .tool import create_skill_tool

# Agent Tool (Agent as Tool Mode)
from .tool import create_skill_agent_tool

# Errors
from .errors import (
    SkillError,
    ParseError,
    ValidationError,
    SkillNotFoundError,
    SkillActivationError,
)

__version__ = "1.0.0"

__all__ = [
    # Models
    "SkillProperties",
    # Progressive Disclosure API
    "find_skill_md",
    "load_metadata",  # Phase 1: Load metadata only
    "load_instructions",  # Phase 2: Load instructions
    "load_resource",  # Phase 3: Load resources
    # Validator
    "validate",
    "validate_metadata",
    # Discovery
    "discover_skills",
    # Agent Model
    "get_bedrock_agent_model",
    # Prompt
    "generate_skills_prompt",
    "generate_default_system_prompt",
    "generate_skill_instructions_prompt",
    # Tool (Inline Mode)
    "create_skill_tool",
    # Agent Tool (Agent as Tool Mode)
    "create_skill_agent_tool",
    # Errors
    "SkillError",
    "ParseError",
    "ValidationError",
    "SkillNotFoundError",
    "SkillActivationError",
]
