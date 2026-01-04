"""Generate skills prompt for agent system prompts

This module provides XML-formatted prompt generation following the AgentSkills.io specification.
"""

from pathlib import Path
from typing import List
from .models import SkillProperties

# Directory paths for agent file operations
ROOT_DIR = Path(__file__).parent.parent  # Project root
SCRATCH_DIR = ROOT_DIR / "_scratch"
OUTPUT_DIR = ROOT_DIR / "_output"

# Ensure directories exist
SCRATCH_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


DEFAULT_SYSTEM_PROMPT = """
You are a helpful AI assistant. You have access to a skills library that provides specialized capabilities and domain knowledge.

## Tool usage policy

- Use specialized tools instead of bash commands when possible, as this provides a better user experience. Reserve bash tools exclusively for actual system commands and terminal operations that require shell execution. 
- After completing a task that involves tool use, provide a quick summary of the work you've done.

<file_operations_policy>
- **Root directory**: `{root_dir}` - All operations must stay within this boundary
- **Scratch directory**: `{root_dir}/_scratch` - Use for ALL temporary/intermediate files
- **Output directory**: `{root_dir}/_output` - Final deliverables go here
- **[IMPORTANT]**: Never use absolute paths like `/home`, `/tmp`, `/etc`, or `~` that fall outside the root boundary. 
</file_operations_policy>
"""

SKILLS_SYSTEM_PROMPT = """
{default_system_prompt}

## Skills System

You have access to a skills library that provides specialized capabilities and domain knowledge.

<skills_instructions>
**How to Use Skills:**

Your efforts are greatly aided by reading the skill documentation BEFORE writing any code, creating any files, or using any computer tools.
Skills follow a **progressive disclosure** pattern - you know they exist (name + description above), but you only read the full instructions when needed:

1. **Recognize when a skill applies**: Check if the user's task matches any skill's description
2. **Read the skill's full instructions**: 
   - If a `skill` tool is available, call it with the skill name
     - `skill(skill_name="web-research")` - invoke the web-research skill
   - When a user's request matches one of the available skills, use the use_skill tool
     - `use_skill(skill_name="skill-name", request="specific request")`
   - Alternative: Use the absolute path shown above to read SKILL.md directly
   - Only use skills listed in <available_skills> below
3. **Follow the skill's instructions**: SKILL.md contains step-by-step workflows, best practices, and examples
4. **Access supporting files**: Skills may include Python scripts, configs, or reference docs - always use absolute paths

**When to Use Skills:**
- When the user's request matches a skill's domain (e.g., "research X" → web-research skill)
- When you need specialized knowledge or structured workflows
- When a skill provides proven patterns for complex tasks

**Remember:** Skills are tools to make you more capable and consistent. When in doubt, check if a skill exists for the task!
</skills_instructions>

<available_skills>
{skills_list}
</available_skills>
"""

SKILL_INSTRUCTIONS_PROMPT = """
{default_system_prompt}

## Skill Execution Guidelines

<skills_instructions>
1. **Follow the instructions**: Instructions contains step-by-step workflows, best practices, and examples
2. **Access supporting files**: Instructions may include Python scripts, configs, or reference docs - always use absolute paths
</skills_instructions>

## Instructions

{instructions}
"""


def generate_skills_prompt(skills: List[SkillProperties]) -> str:
    """Generate XML system prompt section from SkillProperties list

    This generates a concise prompt with skill metadata only (Phase 1 of Progressive Disclosure),
    following the AgentSkills.io specification format using XML.

    Args:
        skills: List of discovered skill properties

    Returns:
        XML formatted prompt text with <available_skills> section

    Example:
        >>> from agentskills import discover_skills, generate_skills_prompt
        >>> skills = discover_skills("./skills")
        >>> prompt = generate_skills_prompt(skills)
        >>> agent = Agent(system_prompt=base + "\\n\\n" + prompt)
    """
    if not skills:
        return ""

    # Build XML skills list (metadata only)
    skill_elements = []
    for skill in sorted(skills, key=lambda s: s.name):
        skill_xml = (
            "  <skill>\n"
            f"    <name>{skill.name}</name>\n"
            f"    <description>{skill.description}</description>\n"
            f"    <location>{skill.path}</location>\n"
            "  </skill>"
        )
        skill_elements.append(skill_xml)

    skills_list = "\n".join(skill_elements)

    # Format the template with skills list and directory paths
    return SKILLS_SYSTEM_PROMPT.format(
        default_system_prompt=generate_default_system_prompt(),
        skills_list=skills_list,        
    )


def generate_default_system_prompt() -> str:
    """Generate default system prompt"""
    return DEFAULT_SYSTEM_PROMPT.format(
        root_dir=str(ROOT_DIR.resolve())
    )

def generate_skill_instructions_prompt(instructions: str) -> str:
    """Generate skill instructions prompt"""
    return SKILL_INSTRUCTIONS_PROMPT.format(
        default_system_prompt=generate_default_system_prompt(),
        instructions=instructions
    )


__all__ = ["generate_skills_prompt", "generate_default_system_prompt", "generate_skill_instructions_prompt"]
