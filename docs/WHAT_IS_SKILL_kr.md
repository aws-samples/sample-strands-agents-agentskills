**[English](WHAT_IS_SKILL.md) | 한국어**

## SKILL

스킬은 기본적으로 `SKILL.md` 파일이 포함된 폴더입니다. 이 파일에는 메타데이터(최소한 이름과 설명)와 에이전트가 특정 작업을 수행하는 방법을 알려주는 지침이 포함되어 있습니다. 스킬에는 스크립트, 템플릿 및 참조 자료도 함께 포함될 수 있습니다.

```markdown
my-skill/
├── SKILL.md          # Required: instructions + metadata
├── scripts/          # Optional: executable code
├── references/       # Optional: documentation
└── assets/           # Optional: templates, resources
```

## SKILL 작동 방식

Skill은 Progressive Disclosure (점진적 정보 공개) 방식을 사용하여 컨텍스트를 효율적으로 관리합니다.
- **Discovery**: 에이전트는 시작 시 사용 가능한 각 스킬의 이름과 설명만 로드합니다. 이는 해당 스킬이 언제 관련될 수 있는지 파악하는 데 필요한 최소한의 정보입니다.
- **Activation**: 작업이 스킬 설명과 일치하면 에이전트는 SKILL.md 파일의 전체 지침을 컨텍스트에 읽어들입니다.
- **Execution**: 에이전트는 지침을 따르며, 필요에 따라 참조된 파일을 로드하거나 번들된 코드를 실행합니다.

## `SKILL.md` 형식

모든 스킬은 YAML 형식의 프런트매터와 Markdown 형식의 지침이 포함된 `SKILL.md` 파일로 시작합니다.

```markdown
---
name: web-research
description: 웹 검색과 분석을 통해 포괄적인 리서치 수행
allowed-tools: WebFetch, Grep
license: MIT
---

# instructions

이 Skill을 사용하면...

## 1단계: 검색

...
```

### 필수 필드

- `name`: kebab-case 형식 (예: `web-research`)
- `description`: Skill의 기능과 사용 시기

### 선택 필드

- `license`: 스킬 라이센스
- `compatibility`: 호환성 정보
- `allowed-tools`: Skill이 사용할 수 있는 tool 패턴
- `metadata`: 사용자 정의 key-value 쌍
