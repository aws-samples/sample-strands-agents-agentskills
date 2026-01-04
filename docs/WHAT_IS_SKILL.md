**English | [한국어](WHAT_IS_SKILL_kr.md)**

## SKILL

A skill is essentially a folder containing a `SKILL.md` file. This file contains metadata (at minimum, a name and description) and instructions that tell an agent how to perform a specific task. Skills may also include scripts, templates, and reference materials.

```markdown
my-skill/
├── SKILL.md          # Required: instructions + metadata
├── scripts/          # Optional: executable code
├── references/       # Optional: documentation
└── assets/           # Optional: templates, resources
```

## How SKILL Works

Skills use Progressive Disclosure to efficiently manage context.
- **Discovery**: The agent loads only the name and description of each available skill at startup. This is the minimum information needed to determine when a skill might be relevant.
- **Activation**: When a task matches a skill's description, the agent reads the full instructions from the SKILL.md file into context.
- **Execution**: The agent follows the instructions, loading referenced files or executing bundled code as needed.

## `SKILL.md` Format

All skills start with a `SKILL.md` file containing YAML frontmatter and Markdown instructions.

```markdown
---
name: web-research
description: Perform comprehensive research through web search and analysis
allowed-tools: WebFetch, Grep
license: MIT
---

# instructions

When using this Skill...

## Step 1: Search

...
```

### Required Fields

- `name`: kebab-case format (e.g., `web-research`)
- `description`: What the Skill does and when to use it

### Optional Fields

- `license`: Skill license
- `compatibility`: Compatibility information
- `allowed-tools`: Tool patterns the Skill can use
- `metadata`: Custom key-value pairs

