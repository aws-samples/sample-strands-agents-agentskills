# Agent Skills 예제

**[English](README.md) | 한국어**

Strands Agents SDK에서 Agent Skills를 사용하는 완전한 예제들입니다.

## 사전 준비

```bash
# 의존성 설치
pip install strands-agents strands-agents-tools pyyaml

# agentskills 설치
cd strands_agentskills
pip install -e .
```

## 3가지 구현 패턴

이 패키지는 Strands Agents SDK에서 Agent Skills를 사용하기 위한 **3가지 구현 패턴**을 제공합니다:

| 패턴 | 예제 파일 | 특징 | 추천 대상 |
|------|----------|------|----------|
| **File-based** | 1-discovery_skills.py | LLM이 file_read로 직접 읽기 | 가장 자연스러운 방식 |
| **Tool-based** | 2-skill_tool_with_progressive_disclosure.py | skill tool로 명시적 로드 | 구조화된 접근 필요시 |
| **Meta-Tool** | 3-skill_agent_tool.py | Sub-agent를 tool로 사용 | Context 분리 필요시 |

---

## 예제 목록

### 1. 📁 Pattern 1: File-based - [1-discovery_skills.py](1-discovery_skills.py)

**File-based 접근 방식**의 기본 예제입니다. LLM이 직접 file_read 도구로 SKILL.md를 읽습니다.

```bash
python examples/1-discovery_skills.py
```

**시연 내용:**
- **Phase 1**: Skill discovery (metadata만 system prompt에 로드)
- **Phase 2**: LLM이 file_read로 SKILL.md 읽기 (true progressive disclosure)
- **Phase 3**: LLM이 필요시 resources 읽기
- TerminalStreamRenderer로 컬러풀한 스트리밍 출력

> **추천 대상:** 가장 자연스러운 사용 방식, 유연한 통합이 필요한 경우

---

### 2. 🔧 Pattern 2: Tool-based - [2-skill_tool_with_progressive_disclosure.py](2-skill_tool_with_progressive_disclosure.py)

**Tool-based 접근 방식**의 예제입니다. skill tool을 통해 명시적으로 instructions를 로드합니다.

```bash
python examples/2-skill_tool_with_progressive_disclosure.py
```

**시연 내용:**
- **Phase 1**: Discovery - metadata 로드 (~100 tokens/skill)
- **Phase 1.5**: System prompt 생성 및 skill tool 연결
- **Phase 2**: skill(skill_name=...) 호출로 instructions 로드
- 각 단계별 토큰 사용량 추정
- 구조화된 접근 방식

> **추천 대상:** 명시적 skill activation이 필요한 경우, 토큰 사용량 추적이 필요한 경우

---

### 3. 🔗 Pattern 3: Meta-Tool (Agent as Tool) - [3-skill_agent_tool.py](3-skill_agent_tool.py) 

**Meta-Tool 접근 방식**의 예제입니다. 각 Skill이 독립된 Sub-agent를 tool로 사용하여 격리 실행됩니다.

```bash
python examples/3-skill_agent_tool.py
```

**시연 내용:**
- Skill agent tool 생성 (use_skill) - Agent as Tool 패턴
- 각 skill이 isolated sub-agent (as a tool)에서 실행
- Sub-agent가 자체 context와 SKILL.md를 system prompt로 사용
- 완전한 context 분리 (main agent와 격리)
- Sub-agent에 file_read, file_write, shell 도구 제공

> **추천 대상:** Context 격리가 필요한 경우, 복잡한 Skill의 모듈화된 실행이 필요한 경우

---

### 4. 🎨 프롬프트 로드 데모: [4-streamlit_prompt_simulation.py](4-streamlit_prompt_simulation.py) 

Streamlit 기반의 **Progressive Disclosure 시각화 데모**입니다. Phase 1→2→3을 탭으로 구분하여 각 단계에서 무엇이 로드되고 Agent의 prompt에 어떻게 포함되는지 확인할 수 있습니다.

```bash
# Streamlit 설치 필요
pip install streamlit

# 실행
streamlit run examples/4-streamlit_prompt_simulation.py
```

**시연 내용:**
- **Phase 1 탭**: Discovery - Skills 발견 및 metadata 표시, 생성된 System Prompt 확인
- **Phase 2 탭**: Activation - Skill 활성화 시뮬레이션, Instructions 로드 및 Tool 호출 추적
- **Phase 3 탭**: Resources - Resource 파일 목록 및 읽기 시뮬레이션, 토큰 사용량 시각화
- 각 Phase별 토큰 사용량 추정 및 비교
- Tool 호출 추적 및 Prompt 내용 실시간 확인

> **추천 대상:** Progressive Disclosure의 작동 방식을 시각적으로 이해하고 싶은 경우

---

### 5. 🚀 Strands Agents SDK + Agent Skills 통합 데모: [5-streamlit_strands_integration.py](5-streamlit_strands_integration.py)

세 가지 Agent Skills 실행 모드(File-based, Tool-based, Meta-tool-Agent)를 비교하고 실시간으로 동작을 확인할 수 있는 Streamlit 앱입니다.

```bash
# Streamlit 설치 필요
pip install streamlit

# 실행
streamlit run examples/5-streamlit_strands_integration.py
```

**시연 내용:**
- **File-based Mode**: LLM이 file_read로 SKILL.md 직접 읽기 (가장 자연스러운 방식)
- **Tool-based Mode**: skill tool 호출을 통한 명시적 activation
- **Meta-Tool Mode**: Sub-agent를 tool로 사용하여 격리 실행 (Agent as Tool 패턴)
- 실시간 스트리밍 응답 및 Tool 호출 시각화
- 모드 간 전환 및 비교
- StreamlitStreamRenderer로 Sub-agent 이벤트 처리

> **추천 대상:** 세 가지 패턴의 차이점을 비교하고 싶은 경우, 실제 Agent 동작 확인

---

## 예제 실행

`skills/` 디렉토리에 Skill이 있는지 확인하세요:

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

스킬 형식 표준은 [AgentSkills.io](https://agentskills.io)를 참고하세요.

---

## 더 알아보기

- [AgentSkills.io 표준 문서](https://agentskills.io/specification)
- [Strands Agents SDK 문서](https://strandsagents.com)
- [메인 README](../README.md)
