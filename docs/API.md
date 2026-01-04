**English | [한국어](API_kr.md)**

## Core API

### Complete Public API List

**Models:**
- `SkillProperties` - Skill metadata data class

**Progressive Disclosure API (Phase 1-3):**
- `discover_skills()` - Phase 1: Discover metadata for all skills
- `load_metadata()` - Phase 1: Load metadata for a single skill
- `find_skill_md()` - Find SKILL.md file
- `load_instructions()` - Phase 2: Load skill instructions
- `load_resource()` - Phase 3: Load resource files

**Validator:**
- `validate()` - Validate entire skill directory
- `validate_metadata()` - Validate metadata only

**Prompt & Tool:**
- `generate_skills_prompt()` - Generate system prompt
- `create_skill_tool()` - Pattern 2: Tool-based skill activation tool
- `create_skill_agent_tool()` - Pattern 3: Meta-Tool Sub-agent execution tool

**Errors:**
- `SkillError` - Base exception class
- `ParseError` - Parsing error
- `ValidationError` - Validation error
- `SkillNotFoundError` - Skill not found
- `SkillActivationError` - Skill activation failed

### `create_skill_tool(skills, skills_dir)`

Create a `skill` tool that supports progressive disclosure (Pattern 2: Tool-based).

```python
from agentskills import create_skill_tool
from strands import Agent
from strands_tools import file_read

skill_tool = create_skill_tool(skills, "./skills")

# Complete progressive disclosure with skill + file_read combination
agent = Agent(tools=[skill_tool, file_read])

# How LLM uses it:
# - skill(skill_name="web-research")  # load instructions
# - file_read(path="/path/to/skill/scripts/helper.py")  # read resources
```

### `create_skill_agent_tool(skills, skills_dir, base_agent_model, additional_tools)`

Create a `use_skill` tool for Meta-Tool mode (Pattern 3). Executes each Skill in an isolated Sub-agent.

```python
from agentskills import create_skill_agent_tool
from strands import Agent
from strands_tools import file_read, web_search

skill_agent_tool = create_skill_agent_tool(
    skills,
    "./skills",
    base_agent_model="us.anthropic.claude-sonnet-4-5-20250929-v1:0",  # optional
    additional_tools=[file_read, web_search]  # tools to provide to Sub-agent
)

agent = Agent(tools=[skill_agent_tool])

# How LLM uses it:
# - use_skill(skill_name="web-research", request="Research quantum computing")
# → Creates Sub-agent for isolated execution
```

**Parameters:**
- `skills`: List of discovered skills
- `skills_dir`: Skill directory path
- `base_agent_model`: Base model to use in Sub-agent (optional)
- `additional_tools`: List of tools to provide to Sub-agent (optional)

### `generate_skills_prompt(skills)`

Converts Skills into a system prompt for LLM.

```python
from agentskills import generate_skills_prompt

prompt = generate_skills_prompt(skills)
print(prompt)
```

### `validate(skill_dir) / validate_metadata(metadata, skill_dir)`

Validates skill directory or metadata according to Agent Skills standard.

```python
from agentskills import validate, validate_metadata
from pathlib import Path

# Validate entire skill directory
errors = validate(Path("./skills/web-research"))
if not errors:
    print("✅ Valid skill")
else:
    for error in errors:
        print(f"❌ {error}")
```

