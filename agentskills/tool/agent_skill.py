"""Skill agent tool for Strands Agents (Agent as Tool Mode)

This module creates a Strands tool that executes skills in isolated sub-agents.
Each skill runs in a separate agent with its own context and system prompt.

For inline mode (instructions loaded into main agent), see skill.py
"""

import logging
from pathlib import Path
from typing import List, Optional, Any, AsyncIterator

from strands import tool, Agent
from strands.models import Model

from ..models import SkillProperties
from ..errors import SkillActivationError
from ..parser import load_instructions
from ..agent_model import get_bedrock_agent_model
from ..tool_utils import validate_skill_name
from ..prompt import generate_skill_instructions_prompt

logger = logging.getLogger(__name__)


def create_skill_agent_tool(
    skills: List[SkillProperties],
    skills_dir: str | Path,
    base_agent_model: Optional[Model] = None,
    additional_tools: Optional[List[Any]] = None
):
    """Create a Strands tool that uses sub-agent for skill execution (Agent as Tool pattern)

    This factory function creates a tool that implements the "Agent as Tool" pattern
    with real-time streaming of sub-agent events:
    - Each skill runs in an isolated sub-agent (used as a tool)
    - Skill instructions become the sub-agent's system prompt
    - Complete isolation from main agent context
    - Streams intermediate events via tool_stream_event
    - Uses Strands SDK's recommended AsyncIterator pattern

    Args:
        skills: List of discovered skill properties
        skills_dir: Base directory containing skills
        base_agent_model: Default model for sub-agents (optional)
        additional_tools: Tools to provide to sub-agents (optional)

    Returns:
        A Strands tool function decorated with @tool
    """
    skills_dir = Path(skills_dir).expanduser().resolve()

    # Create a lookup map for fast skill access
    skill_map = {skill.name: skill for skill in skills}

    # Default model
    model = base_agent_model or get_bedrock_agent_model(thinking=True)

    @tool
    async def use_skill(skill_name: str, request: str) -> AsyncIterator:
        """Execute a skill in an isolated sub-agent with real-time streaming.

        This tool activates a specialized skill and runs it in a separate agent
        with its own context and instructions. The skill agent will process
        your request and stream intermediate events (tool calls, text generation)
        before returning the final result.

        Args:
            skill_name: Name of the skill to use (see system prompt for available skills)
            request: Your specific request or task for the skill to accomplish

        Yields:
            dict: Intermediate events with keys: skill_name, agent, event

        Returns:
            Result from the skill execution

        Example:
            use_skill(skill_name="web-research", request="Research quantum computing trends")
        """
        # Validate skill exists
        skill = validate_skill_name(skill_name, skill_map)

        try:
            logger.info(f"Streaming skill '{skill_name}' execution in sub-agent")

            # Load skill instructions
            instructions = load_instructions(skill.path)

            # Create sub-agent for this skill
            sub_agent = _create_skill_agent(skill, instructions, model, additional_tools)

            result = None

            # Stream events from sub-agent and yield them wrapped in dict
            # This pattern is from Strands SDK documentation: "Sub-Agent Streaming Example"
            async for event in sub_agent.stream_async(request):
                # Yield each event wrapped in dict for main agent to process
                yield {
                    "skill_name": skill_name,
                    "agent": sub_agent,
                    "event": event
                }

                # Capture the final result
                if "result" in event:
                    result = event["result"]

            logger.info(f"Skill '{skill_name}' execution completed")

            # Yield final result string (this becomes the tool's return value)
            if result is not None:
                yield str(result.message) if hasattr(result, 'message') else str(result)
            else:
                yield f"Skill '{skill_name}' completed successfully"

        except Exception as e:
            logger.error(f"Error executing skill '{skill_name}': {e}", exc_info=True)
            raise SkillActivationError(
                f"Failed to execute skill '{skill_name}': {e}"
            ) from e

    return use_skill


def _create_skill_agent(
    skill: SkillProperties,
    instructions: str,
    model: Model,
    additional_tools: Optional[List[Any]] = None
) -> Agent:
    """Create a sub-agent configured for a specific skill

    Args:
        skill: The skill's properties (metadata)
        instructions: Full skill instructions from SKILL.md
        model: Model to use for the sub-agent
        additional_tools: Optional additional tools

    Returns:
        Configured Agent instance
    """
    skill_name = skill.name

    # Build system prompt with skill context
    system_prompt = generate_skill_instructions_prompt(instructions)
    
    # Determine which tools to provide
    tools = []
    if additional_tools:
        tools.extend(additional_tools)

    # Create sub-agent
    agent = Agent(
        model=model,
        tools=tools if tools else None,
        system_prompt=system_prompt,
        name=f"skill-{skill_name}",
        callback_handler=None,
    )

    return agent


__all__ = ["create_skill_agent_tool"]

