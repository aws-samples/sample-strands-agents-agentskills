"""Agent as Tool (Meta-Tool) usage example of Agent Skills

This example demonstrates the Agent as Tool pattern:
- Skills run in isolated sub-agents (used as a tool)
- use_skill(skill_name, request) executes skill in sub-agent
- Complete isolation between main agent and skill execution

For Filesystem-Based approach, see: 1-discovery_skills.py
For Tool-Based approach, see: 2-skill_tool_with_progressive_disclosure.py
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from strands import Agent
from strands_tools import file_read, file_write, shell
from agentskills import (
    discover_skills,
    generate_skills_prompt,
    create_skill_agent_tool,
    get_bedrock_agent_model,
)
from utils.strands_stream import TerminalStreamRenderer


def estimate_tokens(text: str) -> int:
    """Rough token estimation (1 token ≈ 4 characters)"""
    return len(text) // 4


async def main():
    """Agent as Tool usage example with isolated skill execution"""

    print("\n🚀 Agent Skills - Meta-Tool Mode Demo (Agent as Tool)\n")

    # ========================================================================
    # Phase 1: Discovery (loads only metadata)
    # ========================================================================
    print("=" * 60)
    print("Phase 1: Discovery (Metadata Only)")
    print("=" * 60)

    skills_dir = Path(__file__).parent.parent / "skills"
    skills = discover_skills(skills_dir)

    print(f"\n✓ Discovered {len(skills)} skills:\n")
    for skill in skills:
        print(f"  📦 {skill.name}")
        print(f"     Description: {skill.description}")
        print(f"     Location: {skill.path}")
        if skill.allowed_tools:
            print(f"     Allowed tools: {skill.allowed_tools}")
        print()

    if not skills:
        print("\n⚠️  No skills found. Create skills in 'skills/' directory.")
        return

    # ========================================================================
    # Create skill agent tool (Agent as Tool pattern)
    # ========================================================================
    print("\n" + "=" * 60)
    print("Creating Skill Agent Tool (Agent as Tool)")
    print("=" * 60)

    skill_agent_tool = create_skill_agent_tool(
        skills,
        skills_dir,
        additional_tools=[file_read, file_write, shell]
    )

    print("\n🔧 Skill agent tool created: use_skill")
    print("   ✓ Each skill runs in isolated sub-agent (as a tool)")
    print("   ✓ Sub-agent has: file_read, file_write, shell")
    print("   ✓ Complete context separation from main agent")

    # ========================================================================
    # Generate system prompt
    # ========================================================================
    print("\n" + "=" * 60)
    print("System Prompt (with skill metadata)")
    print("=" * 60)

    base_prompt = """You are a helpful AI assistant with access to specialized skills.

When a user's request matches one of the available skills, use the use_skill tool:
- use_skill(skill_name="skill-name", request="specific request")

Each skill runs in an isolated sub-agent (as a tool) with its own context and instructions.
This provides complete separation between your context and the skill's execution.

After the skill completes, you'll receive the result and can present it to the user."""

    skills_prompt = generate_skills_prompt(skills)
    full_prompt = f"{base_prompt}\n\n{skills_prompt}"

    prompt_tokens = estimate_tokens(full_prompt)
    print(f"\n📊 System prompt size: ~{prompt_tokens} tokens")

    # ========================================================================
    # Create agent
    # ========================================================================
    agent_model = get_bedrock_agent_model(thinking=True)
    agent = Agent(
        system_prompt=full_prompt,
        tools=[skill_agent_tool],  # Only use_skill tool - isolation!
        model=agent_model,
        callback_handler=None,
    )

    print("\n✅ Agent created with:")
    print("   - use_skill tool (Agent as Tool execution)")
    print("   - No direct access to file_read/shell (isolation)")

    # Create renderer
    renderer = TerminalStreamRenderer()

    # ========================================================================
    # Example: Execute skill in sub-agent
    # ========================================================================
    if skills:
        # input("\n⏸  Press Enter to continue to Example...")

        print("\n" + "=" * 60)
        print("Example: Execute skill in isolated sub-agent (as a tool)")
        print("=" * 60)
        first_skill = skills[0]
        prompt = f"{first_skill.name} skill 을 어떻게 사용할 수 있나요?"
        print(f"\nAsking: '{prompt}'\n")

        renderer.reset()
        async for event in agent.stream_async(prompt):
            renderer.process(event)

        print()
        print("✓ Skill executed in isolated sub-agent (as a tool)")
        print("✓ Sub-agent had its own context with SKILL.md as system prompt")
        print("✓ Main agent received result without seeing internal execution")


if __name__ == "__main__":
    asyncio.run(main())

