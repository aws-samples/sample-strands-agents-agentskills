# Agent Skills Examples

**English | [한국어](README_kr.md)**

Complete examples for using Agent Skills with Strands Agents SDK.

## Prerequisites

```bash
# Install dependencies
pip install strands-agents strands-agents-tools pyyaml

# Install agentskills
cd strands_agentskills
pip install -e .
```

## 3 Implementation Patterns

This package provides **3 implementation patterns** for using Agent Skills in Strands Agents SDK:

| Pattern | Example File | Features | Recommended For |
|---------|-------------|----------|-----------------|
| **File-based** | 1-discovery_skills.py | LLM reads directly via file_read | Most natural approach |
| **Tool-based** | 2-skill_tool_with_progressive_disclosure.py | Explicit load via skill tool | When structured approach needed |
| **Meta-Tool** | 3-skill_agent_tool.py | Use Sub-agent as tool | When context separation needed |

---

## Example List

### 1. 📁 Pattern 1: File-based - [1-discovery_skills.py](1-discovery_skills.py)

Basic example of **File-based approach**. LLM directly reads SKILL.md using file_read tool.

```bash
python examples/1-discovery_skills.py
```

**Demonstration:**
- **Phase 1**: Skill discovery (load only metadata into system prompt)
- **Phase 2**: LLM reads SKILL.md via file_read (true progressive disclosure)
- **Phase 3**: LLM reads resources when needed
- Colorful streaming output with TerminalStreamRenderer

> **Recommended for:** Most natural usage, when flexible integration is needed

---

### 2. 🔧 Pattern 2: Tool-based - [2-skill_tool_with_progressive_disclosure.py](2-skill_tool_with_progressive_disclosure.py)

Example of **Tool-based approach**. Explicitly load instructions via skill tool.

```bash
python examples/2-skill_tool_with_progressive_disclosure.py
```

**Demonstration:**
- **Phase 1**: Discovery - load metadata (~100 tokens/skill)
- **Phase 1.5**: Generate system prompt and connect skill tool
- **Phase 2**: Load instructions via skill(skill_name=...) call
- Token usage estimation per phase
- Structured approach

> **Recommended for:** When explicit skill activation is needed, when token usage tracking is needed

---

### 3. 🔗 Pattern 3: Meta-Tool (Agent as Tool) - [3-skill_agent_tool.py](3-skill_agent_tool.py) 

Example of **Meta-Tool approach**. Each Skill runs in an isolated Sub-agent as a tool.

```bash
python examples/3-skill_agent_tool.py
```

**Demonstration:**
- Create skill agent tool (use_skill) - Agent as Tool pattern
- Each skill runs in isolated sub-agent (as a tool)
- Sub-agent uses its own context and SKILL.md as system prompt
- Complete context separation (isolated from main agent)
- Provide file_read, file_write, shell tools to Sub-agent

> **Recommended for:** When context isolation is needed, when modular execution of complex Skills is needed

---

### 4. 🎨 Prompt Load Demo: [4-streamlit_prompt_simulation.py](4-streamlit_prompt_simulation.py) 

Streamlit-based **Progressive Disclosure visualization demo**. Check what is loaded at each phase and how it's included in Agent's prompt through separate tabs for Phase 1→2→3.

```bash
# Streamlit installation required
pip install streamlit

# Run
streamlit run examples/4-streamlit_prompt_simulation.py
```

**Demonstration:**
- **Phase 1 Tab**: Discovery - Skill discovery and metadata display, check generated System Prompt
- **Phase 2 Tab**: Activation - Simulate Skill activation, track Instructions loading and Tool calls
- **Phase 3 Tab**: Resources - Resource file list and read simulation, token usage visualization
- Token usage estimation and comparison per phase
- Tool call tracking and real-time prompt content checking

> **Recommended for:** When you want to visually understand how Progressive Disclosure works

---

### 5. 🚀 Strands Agents SDK + Agent Skills Integration Demo: [5-streamlit_strands_integration.py](5-streamlit_strands_integration.py)

Streamlit app that compares three Agent Skills execution modes (File-based, Tool-based, Meta-tool-Agent) and checks real-time behavior.

```bash
# Streamlit installation required
pip install streamlit

# Run
streamlit run examples/5-streamlit_strands_integration.py
```

**Demonstration:**
- **File-based Mode**: LLM directly reads SKILL.md via file_read (most natural approach)
- **Tool-based Mode**: Explicit activation via skill tool call
- **Meta-Tool Mode**: Isolated execution using Sub-agent as tool (Agent as Tool pattern)
- Real-time streaming responses and Tool call visualization
- Mode switching and comparison
- Sub-agent event handling with StreamlitStreamRenderer

> **Recommended for:** When you want to compare differences between three patterns, when checking actual Agent behavior

---

## Running Examples

Check if Skills exist in `skills/` directory:

```
skills/
├── web-research/
│   ├── SKILL.md
│   ├── scripts/
│   │   └── search.py
│   └── references/
│       └── apis.md
└── file-processing/
    └── SKILL.md
```

For Skill format standards, refer to [AgentSkills.io](https://agentskills.io).

---

## Learn More

- [AgentSkills.io Standard Documentation](https://agentskills.io/specification)
- [Strands Agents SDK Documentation](https://strandsagents.com)
- [Main README](../README.md)

