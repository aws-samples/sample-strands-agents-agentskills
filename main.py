"""
Agent Skills Demo - Three Execution Modes

This demo shows three different ways to use Agent Skills:
1. File-based Mode: LLM reads SKILL.md directly using file_read
2. Tool-based Mode: skill tool loads instructions into context
3. Meta-Tool Mode: Sub-agents execute skills as a tool (Agent as Tool pattern)

Choose your preferred mode based on your needs!
"""

import asyncio
from pathlib import Path
from strands import Agent
from strands_tools import file_read, file_write, shell
from utils.strands_stream import TerminalStreamRenderer
from agentskills import (
    discover_skills,
    generate_skills_prompt,
    create_skill_tool,
    create_skill_agent_tool,
    get_bedrock_agent_model,
)


def discovery(skills_dir):
    """Phase 1: Discover skills (load metadata only)"""
    print("=" * 60)
    print("Phase 1: Discovery (Metadata Only)")
    print("=" * 60)

    skills = discover_skills(skills_dir)

    print(f"\nDiscovered {len(skills)} skills:\n")
    for skill in skills:
        print(f"📦 {skill.name}")
        print(f"   Description: {skill.description}")
        print(f"   Location: {skill.path}")
        if skill.allowed_tools:
            print(f"   Allowed tools: {skill.allowed_tools}")
        print()

    return skills


def create_agent_file_based(skills, skills_dir):
    """Create agent using file-based mode

    In this mode:
    - LLM sees skill metadata in system prompt
    - LLM uses file_read to directly read SKILL.md files
    - Most flexible and natural approach
    """
    print("\n" + "=" * 60)
    print("Creating Agent: FILE-BASED MODE")
    print("=" * 60)

    # Generate system prompt with skill metadata
    system_prompt = """You are a helpful AI assistant with access to specialized skills.

When a user's request matches one of the available skills, use the file_read tool to:
1. Read the SKILL.md file at the path shown in the skill list
2. Follow the instructions in that file to help the user
3. Read any additional resource files if needed

This gives you the most flexibility to use skills naturally."""

    skills_prompt = generate_skills_prompt(skills)
    full_prompt = f"{system_prompt}\n\n{skills_prompt}"

    print("\n📝 System Prompt includes:")
    print("  - Skill metadata (names, descriptions, paths)")
    print("  - Instructions to read SKILL.md files as needed")
    
    agent_model = get_bedrock_agent_model(thinking=True)
    agent = Agent(
        system_prompt=full_prompt,
        tools=[file_read, file_write, shell],
        model=agent_model,
        callback_handler=None,
    )

    print("\n✅ File-based agent created!")
    return agent


def create_agent_tool_based(skills, skills_dir):
    """Create agent using tool-based mode

    In this mode:
    - LLM sees skill metadata in system prompt
    - LLM uses skill tool to load instructions
    - More structured than file-based
    """
    print("\n" + "=" * 60)
    print("Creating Agent: TOOL-BASED MODE")
    print("=" * 60)

    # Create skill tool
    skill_tool = create_skill_tool(skills, skills_dir)

    # Generate system prompt
    system_prompt = """You are a helpful AI assistant with access to specialized skills.

When a user's request matches one of the available skills, use the skill tool to:
1. Load the skill's instructions: skill(skill_name="skill-name")
2. Follow the instructions provided
3. Use file_read for any additional resource files if needed

The skill tool provides a structured way to activate skills."""

    skills_prompt = generate_skills_prompt(skills)
    full_prompt = f"{system_prompt}\n\n{skills_prompt}"

    print("\n📝 System Prompt includes:")
    print("  - Skill metadata (names, descriptions)")
    print("  - Instructions to use skill tool")

    agent_model = get_bedrock_agent_model(thinking=True)
    agent = Agent(
        system_prompt=full_prompt,
        tools=[skill_tool, file_read, file_write, shell],
        model=agent_model,
        callback_handler=None,
    )

    print("\n✅ Tool-based agent created!")
    return agent


def create_agent_meta_tool(skills, skills_dir):
    """Create agent using meta-tool mode (Agent as Tool pattern)

    In this mode:
    - LLM sees skill metadata in system prompt
    - LLM uses use_skill tool to execute in sub-agent (as a tool)
    - Complete isolation between main and skill agents
    """
    print("\n" + "=" * 60)
    print("Creating Agent: META-TOOL MODE (Agent as Tool)")
    print("=" * 60)

    # Create skill agent tool (Agent as Tool pattern)
    skill_agent_tool = create_skill_agent_tool(
        skills,
        skills_dir,
        additional_tools=[file_read, file_write, shell]
    )

    # Generate system prompt
    system_prompt = """You are a helpful AI assistant with access to specialized skills.

When a user's request matches one of the available skills, use the use_skill tool:
- use_skill(skill_name="skill-name", request="specific request")

Each skill runs in an isolated sub-agent (as a tool) with its own context and instructions.
This provides complete separation between your context and the skill's execution.

After the skill completes, you'll receive the result and can present it to the user."""

    skills_prompt = generate_skills_prompt(skills)
    full_prompt = f"{system_prompt}\n\n{skills_prompt}"

    print("\n📝 System Prompt includes:")
    print("  - Skill metadata (names, descriptions)")
    print("  - Instructions to use use_skill tool")
    print("\n🔧 Tools provided:")
    print("  - use_skill: Execute skills in isolated sub-agents (as a tool)")
    print("\n🤖 Sub-agents have access to:")
    print("  - file_read, file_write, shell, web_search")

    agent_model = get_bedrock_agent_model(thinking=True)
    agent = Agent(
        system_prompt=full_prompt,
        tools=[skill_agent_tool],
        model=agent_model,
        callback_handler=None,
    )

    print("\n✅ Meta-tool agent created!")
    return agent


async def interactive_chat(agent, mode_name):
    """Interactive chat with agent using skills"""
    print("\n" + "=" * 60)
    print(f"Interactive Chat - {mode_name}")
    print("=" * 60)
    print("\nCommands: 'quit', 'exit', 'q' to stop")
    print("Try asking about skills or requesting a task!")

    renderer = TerminalStreamRenderer()

    while True:
        user_input = input("\n👤 You: ").strip()

        if user_input.lower() in ["quit", "exit", "q"]:
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        print("\n🤖 Agent: ", end="")

        # Reset renderer for new query
        renderer.reset()
        async for event in agent.stream_async(user_input):
            renderer.process(event)
        print()  # New line after response


def select_mode():
    """Let user select which mode to use"""
    print("\n" + "=" * 60)
    print("SELECT EXECUTION MODE")
    print("=" * 60)
    print("\nChoose how you want skills to be executed:\n")
    print("1. FILE-BASED MODE (Recommended)")
    print("   → LLM reads SKILL.md files directly")
    print("   → Most flexible and natural")
    print("   → Best for general use\n")
    print("2. TOOL-BASED MODE")
    print("   → skill tool loads instructions")
    print("   → More structured approach")
    print("   → Good for explicit skill activation\n")
    print("3. META-TOOL MODE (Agent as Tool)")
    print("   → Skills run in isolated sub-agents (as a tool)")
    print("   → Complete context separation")
    print("   → Best for delegated, modular execution\n")

    while True:
        choice = input("Enter your choice (1/2/3): ").strip()
        if choice in ["1", "2", "3"]:
            return int(choice)
        print("Invalid choice. Please enter 1, 2, or 3.")


async def main():
    """Main entry point"""
    try:
        print("\n")
        print("╔════════════════════════════════════════════════════════════╗")
        print("║                                                            ║")
        print("║           Agent Skills Demo - Three Modes                  ║")
        print("║                                                            ║")
        print("╚════════════════════════════════════════════════════════════╝")

        # 1. Discover skills (Phase 1: loads only metadata)
        skills_dir = Path(__file__).parent.parent / "skills"
        skills = discovery(skills_dir)

        if not skills:
            print("\n❌ No skills found. Please create some skills first.")
            return

        # 2. Select mode
        mode = select_mode()

        # 3. Create agent based on selected mode
        if mode == 1:
            agent = create_agent_file_based(skills, skills_dir)
            mode_name = "FILE-BASED MODE"
        elif mode == 2:
            agent = create_agent_tool_based(skills, skills_dir)
            mode_name = "TOOL-BASED MODE"
        else:  # mode == 3
            agent = create_agent_meta_tool(skills, skills_dir)
            mode_name = "META-TOOL MODE"

        # 4. Start interactive chat
        await interactive_chat(agent, mode_name)

    except KeyboardInterrupt:
        print("\n\nGoodbye!")
        return
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return


if __name__ == "__main__":
    asyncio.run(main())
