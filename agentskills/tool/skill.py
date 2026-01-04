"""Skill tool for Strands Agents (Inline Mode)

This module creates a Strands tool for progressive disclosure of skills.
The skill tool loads instructions into the main agent's context.

For Agent as Tool pattern (isolated sub-agents), see agent_skill.py
"""

import logging
from pathlib import Path
from typing import List

from strands import tool

from ..models import SkillProperties
from ..errors import SkillActivationError
from ..tool_utils import validate_skill_name

logger = logging.getLogger(__name__)


def create_skill_tool(skills: List[SkillProperties], skills_dir: str | Path):
    """Create a Strands tool for skill activation (Inline Mode)

    This factory function creates a tool that implements Progressive Disclosure:
    - Phase 1: Metadata in system prompt (already loaded)
    - Phase 2: Load full instructions when skill is invoked
    - Phase 3: LLM uses file_read to access resources as needed

    Args:
        skills: List of discovered skill properties
        skills_dir: Base directory containing skills

    Returns:
        A Strands tool function decorated with @tool

    Example:
        >>> from agentskills import discover_skills, create_skill_tool
        >>> from strands import Agent
        >>> from strands_tools import file_read
        >>>
        >>> skills = discover_skills("./skills")
        >>> skill_tool = create_skill_tool(skills, "./skills")
        >>>
        >>> agent = Agent(
        ...     tools=[skill_tool, file_read]
        ... )
    """
    skills_dir = Path(skills_dir).expanduser().resolve()

    # Create a lookup map for fast skill access
    skill_map = {skill.name: skill for skill in skills}

    @tool
    def skill(skill_name: str) -> str:
        """Load specialized skill instructions.

        Args:
            skill_name: Name of the skill (see system prompt for available skills)

        Returns:
            Full skill instructions with resource access information

        Example:
            skill(skill_name="web-research")
        """
        # Validate skill exists
        skill_props = validate_skill_name(skill_name, skill_map)

        try:
            # Phase 2: Load instructions only (not frontmatter)
            from ..parser import load_instructions

            instructions = load_instructions(skill_props.path)
            logger.info(f"Loaded skill: {skill_name}")

            return instructions

        except Exception as e:
            logger.error(f"Error loading skill '{skill_name}': {e}", exc_info=True)
            raise SkillActivationError(
                f"Failed to load skill '{skill_name}': {e}"
            ) from e

    return skill


__all__ = ["create_skill_tool"]

