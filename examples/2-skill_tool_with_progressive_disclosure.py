"""Tool-Based usage example of Agent Skills

This example demonstrates the Tool-Based approach:
LLM uses the 'skill' tool to load instructions, then file_read for resources.

For Filesystem-Based approach, see: 1-basic_usage.py
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from strands import Agent
from strands_tools import file_read
from agentskills import discover_skills, create_skill_tool, generate_skills_prompt, get_bedrock_agent_model
from utils.strands_stream import TerminalStreamRenderer


def estimate_tokens(text: str) -> int:
    """Rough token estimation (1 token ≈ 4 characters)"""
    return len(text) // 4


def print_section(title: str, phase: str = ""):
    """Print formatted section header"""
    print("\n" + "=" * 70)
    if phase:
        print(f"[{phase}] {title}")
    else:
        print(title)
    print("=" * 70)


async def main():
    """Tool-based usage example with progressive disclosure"""

    print_section("Progressive Disclosure: Tool-Based Usage", "")
    print("\n🎯 Progressive Disclosure (점진적 공개): 이 접근 방식은 컨텍스트 사용을 최소화하고 효율성을 극대화합니다")
    print("   1. 최소한의 초기 로드 (Phase 1: 메타데이터만)")
    print("   2. 스킬이 활성화될 때만 지시사항 로드 (Phase 2)")
    print("   3. 실제로 필요할 때만 리소스 로드 (Phase 3)")
    
    # ========================================================================
    # Phase 1: Discovery - Load only metadata
    # ========================================================================
    print_section("Phase 1: Discovery (메타데이터만)", "PHASE 1")

    skills_dir = Path(__file__).parent.parent / "skills"
    print(f"\n📂 스캔 중: {skills_dir}")
    print("⏳ 메타데이터만 로드 중 (지시사항이나 리소스는 로드하지 않음)...\n")

    skills = discover_skills(skills_dir)

    total_tokens = 0
    print(f"✅ {len(skills)}개의 스킬을 발견했습니다\n")

    for i, skill in enumerate(skills, 1):
        # Calculate approximate tokens for metadata
        metadata_text = (
            f"{skill.name} {skill.description} "
            f"{skill.license or ''} {skill.compatibility or ''} "
            f"{skill.allowed_tools or ''}"
        )
        tokens = estimate_tokens(metadata_text)
        total_tokens += tokens

        print(f"{i}. 📦 {skill.name}")
        print(f"   설명: {skill.description[:80]}...")
        print(f"   📊 예상 토큰 수: ~{tokens} 토큰")

        if skill.allowed_tools:
            print(f"   🔧 허용된 도구: {skill.allowed_tools}")
        if skill.compatibility:
            print(f"   ⚙️  호환성: {skill.compatibility}")

        print(f"   📁 경로: {skill.path}")
        print()

    if skills:
        print(f"💡 Phase 1 총계: {len(skills)}개 스킬에 대해 ~{total_tokens} 토큰")
        print(f"\n✓ 메타데이터가 시스템 프롬프트에 로드됨 (Phase 1 완료)")
        print(f"   ✓ 지시사항은 아직 로드되지 않음 (Phase 2에서 로드 예정)")
        print(f"   ✓ 리소스는 아직 로드되지 않음 (Phase 3에서 로드 예정)")

    if not skills:
        print("\n⚠️  스킬을 찾을 수 없습니다. 'skills/' 디렉토리에 스킬을 생성하세요.")
        return

    # ========================================================================
    # Phase 1: Generate system prompt with skill metadata
    # ========================================================================
    input("\n⏸  Press Enter to continue to generate system prompt...")
    print_section("Phase 1: 시스템 프롬프트 생성", "PHASE 1.5")

    base_prompt = "You are a helpful AI assistant."
    skills_prompt = generate_skills_prompt(skills)
    full_prompt = f"{base_prompt}\n\n{skills_prompt}"

    prompt_tokens = estimate_tokens(full_prompt)
    print(f"\n📝 스킬 메타데이터가 포함된 시스템 프롬프트 생성됨")
    print(f"   📊 시스템 프롬프트 크기: {len(full_prompt)} 문자")
    print(f"   📊 예상 토큰 수: ~{prompt_tokens} 토큰")
    print(f"   ✓ {len(skills)}개 스킬의 메타데이터 포함")
    print(f"\n📄 생성된 시스템 프롬프트:")
    print(full_prompt)

    # ========================================================================
    # Create agent with skill tool + file_read
    # ========================================================================
    input("\n⏸  Press Enter to continue to create agent...")
    print_section("에이전트 초기화", "")

    skill_tool = create_skill_tool(skills, skills_dir)
    tool_name = getattr(skill_tool, '__name__', 'skill')
    print(f"\n🔧 스킬 도구 생성됨: {tool_name}")
    print(f"   ✓ 지시사항이 필요할 때 LLM이 호출할 수 있음")
    print(f"   ✓ LLM이 skill(skill_name=...)을 호출하면 Phase 2가 트리거됨")

    agent_model = get_bedrock_agent_model(thinking=True)
    agent = Agent(
        system_prompt=full_prompt,
        tools=[skill_tool, file_read],
        model=agent_model,
        callback_handler=None,  # Disable default callback for custom streaming
    )

    print(f"\n✅ 에이전트가 다음으로 생성됨:")
    print(f"   - 시스템 프롬프트 (Phase 1 메타데이터 포함)")
    print(f"   - skill 도구 (Phase 2 트리거)")
    print(f"   - file_read 도구 (Phase 3 트리거)")

    # ========================================================================
    # Example 1: Asking about available skills (Phase 1 only)
    # ========================================================================
    input("\n⏸  Press Enter to continue to example 1...")
    prompt = "사용 가능한 스킬에 대해 설명해주세요."

    print_section(f"질문 1: {prompt}\n : 이 쿼리는 Phase 1 메타데이터만 사용 (skill 도구 호출 불필요)", "")
    
    renderer = TerminalStreamRenderer()
    async for event in agent.stream_async(prompt):
        renderer.process(event)
    print()

    # ========================================================================
    # Example 2: LLM will use skill tool to load instructions (Phase 2)
    # ========================================================================
    input("\n⏸  Press Enter to continue to example 2...")

    if skills:
        prompt = f"{skills[0].name} 스킬은 어떻게 사용할 수 있나요?"
        print_section(f"질문 2: {prompt}\n : 이 쿼리는 Phase 2를 트리거함 (skill 도구 호출)", "")

        renderer.reset()
        async for event in agent.stream_async(prompt):
            renderer.process(event)
        
        print()


if __name__ == "__main__":
    asyncio.run(main())
