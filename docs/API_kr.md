**[English](API.md) | 한국어**

## 핵심 API

### 전체 Public API 목록

**Models:**
- `SkillProperties` - Skill 메타데이터 데이터 클래스

**Progressive Disclosure API (Phase 1-3):**
- `discover_skills()` - Phase 1: 모든 스킬의 metadata 발견
- `load_metadata()` - Phase 1: 단일 스킬의 metadata 로드
- `find_skill_md()` - SKILL.md 파일 찾기
- `load_instructions()` - Phase 2: 스킬 instructions 로드
- `load_resource()` - Phase 3: 리소스 파일 로드

**Validator:**
- `validate()` - 스킬 디렉토리 전체 검증
- `validate_metadata()` - 메타데이터만 검증

**Prompt & Tool:**
- `generate_skills_prompt()` - 시스템 프롬프트 생성
- `create_skill_tool()` - Pattern 2: Tool-based 스킬 활성화 도구
- `create_skill_agent_tool()` - Pattern 3: Meta-Tool Sub-agent 실행 도구

**Errors:**
- `SkillError` - 기본 예외 클래스
- `ParseError` - 파싱 오류
- `ValidationError` - 검증 오류
- `SkillNotFoundError` - 스킬을 찾을 수 없음
- `SkillActivationError` - 스킬 활성화 실패

### `create_skill_tool(skills, skills_dir)`

Progressive disclosure를 지원하는 `skill` 도구 생성 (Pattern 2: Tool-based).

```python
from agentskills import create_skill_tool
from strands import Agent
from strands_tools import file_read

skill_tool = create_skill_tool(skills, "./skills")

# skill + file_read 조합으로 완전한 progressive disclosure
agent = Agent(tools=[skill_tool, file_read])

# LLM이 사용하는 방법:
# - skill(skill_name="web-research")  # instructions 로드
# - file_read(path="/path/to/skill/scripts/helper.py")  # resources 읽기
```

### `create_skill_agent_tool(skills, skills_dir, base_agent_model, additional_tools)`

Meta-Tool 모드를 위한 `use_skill` 도구 생성 (Pattern 3). 각 Skill을 격리된 Sub-agent에서 실행합니다.

```python
from agentskills import create_skill_agent_tool
from strands import Agent
from strands_tools import file_read, web_search

skill_agent_tool = create_skill_agent_tool(
    skills,
    "./skills",
    base_agent_model="us.anthropic.claude-sonnet-4-5-20250929-v1:0",  # 선택사항
    additional_tools=[file_read, web_search]  # Sub-agent에게 제공할 tools
)

agent = Agent(tools=[skill_agent_tool])

# LLM이 사용하는 방법:
# - use_skill(skill_name="web-research", request="양자 컴퓨팅 조사")
# → Sub-agent 생성하여 격리 실행
```

**Parameters:**
- `skills`: 발견된 skill 목록
- `skills_dir`: Skill 디렉토리 경로
- `base_agent_model`: Sub-agent에서 사용할 기본 모델 (선택사항)
- `additional_tools`: Sub-agent에게 제공할 도구 목록 (선택사항)

### `generate_skills_prompt(skills)`

Skill을 LLM용 시스템 프롬프트로 변환합니다.

```python
from agentskills import generate_skills_prompt

prompt = generate_skills_prompt(skills)
print(prompt)
```

### `validate(skill_dir) / validate_metadata(metadata, skill_dir)`

Agent Skills 표준에 따라 스킬 디렉토리 또는 메타데이터를 검증합니다.

```python
from agentskills import validate, validate_metadata
from pathlib import Path

# 스킬 디렉토리 전체 검증
errors = validate(Path("./skills/web-research"))
if not errors:
    print("✅ 유효한 스킬입니다")
else:
    for error in errors:
        print(f"❌ {error}")
```
