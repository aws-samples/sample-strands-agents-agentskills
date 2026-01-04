"""Streamlit Demo - Progressive Disclosure 시각화

이 Streamlit 앱은 Agent Skills의 Progressive Disclosure가 어떻게 작동하는지
시각적으로 보여줍니다. 실제 Strands Agents SDK를 사용하여 질의를 받고
자동으로 Phase 1->2->3을 순차적으로 수행하는 과정을 실시간으로 확인할 수 있습니다.
"""

import sys
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from agentskills import (
    discover_skills,
    generate_skills_prompt,
    load_instructions,
    load_resource,
    create_skill_tool,
)

# 페이지 설정
st.set_page_config(
    page_title="Agent Skills - Progressive Disclosure Demo",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)


def estimate_tokens(text: str) -> int:
    """대략적인 토큰 수 추정 (1 token ≈ 4 characters)"""
    return len(text) // 4


def format_number(num: int) -> str:
    """숫자를 읽기 쉬운 형식으로 변환"""
    if num >= 1000:
        return f"{num / 1000:.1f}K"
    return str(num)


# Session state 초기화
if "skills" not in st.session_state:
    st.session_state.skills = []
if "tool_calls" not in st.session_state:
    st.session_state.tool_calls = []
if "current_phase" not in st.session_state:
    st.session_state.current_phase = "Phase 1"
if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = ""


# Tool 호출 추적을 위한 전역 변수 (Streamlit에서는 session_state 사용)
def init_tracking():
    """추적 변수 초기화"""
    if "tracker" not in st.session_state:
        st.session_state.tracker = {
            "skill_calls": [],
            "file_read_calls": [],
            "prompt_content": {
                "initial_system_prompt": "",
                "tool_results": [],
            },
            "agent_responses": [],
            "current_query": "",
            "is_running": False,
        }






# 메인 타이틀
st.title("🚀 Agent Skills - Progressive Disclosure Demo")
st.markdown("""
이 데모는 **Progressive Disclosure** 패턴이 어떻게 작동하는지 시각적으로 보여줍니다.
각 Phase에서 무엇이 로드되고, Agent의 prompt에 어떻게 포함되는지 확인할 수 있습니다.
""")

# 사이드바
with st.sidebar:
    st.header("📋 설정")
    
    skills_dir = Path(__file__).parent.parent / "skills"
    st.info(f"Skills 디렉토리: `{skills_dir}`")
    
    if st.button("🔄 Skills 다시 로드", use_container_width=True, key="reload_skills"):
        st.session_state.skills = discover_skills(skills_dir)
        st.session_state.tool_calls = []
        st.session_state.current_phase = "Phase 1"
        init_tracking()
        st.rerun()
    
    st.divider()
    
    st.header("ℹ️ Progressive Disclosure란?")
    st.markdown("""
    **Progressive Disclosure**는 필요한 정보만 필요한 시점에 로드하는 패턴입니다:
    
    1. **Phase 1**: metadata만 로드 (~100 tokens/skill)
    2. **Phase 2**: skill 사용 시 instructions 로드 (~1000-5000 tokens)
    3. **Phase 3**: 필요 시 resources만 로드 (가변)
    
    이렇게 하면 전체 skill을 미리 로드하는 것보다 훨씬 효율적입니다!
    """)


# Phase 1: Discovery
def show_phase1():
    """Phase 1: Discovery 시각화"""
    st.header("📦 Phase 1: Discovery (Metadata Only)")
    
    skills_dir = Path(__file__).parent.parent / "skills"
    
    if not st.session_state.skills:
        if st.button("🔍 Skills 발견하기", use_container_width=True, key="discover_skills"):
            with st.spinner("Skills 디렉토리를 스캔하는 중..."):
                st.session_state.skills = discover_skills(skills_dir)
                init_tracking()
                st.rerun()
        return
    
    # Skills 목록 표시
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("발견된 Skills")
        
        total_tokens = 0
        for i, skill in enumerate(st.session_state.skills, 1):
            metadata_text = (
                f"{skill.name} {skill.description} "
                f"{skill.license or ''} {skill.compatibility or ''} "
                f"{skill.allowed_tools or ''}"
            )
            tokens = estimate_tokens(metadata_text)
            total_tokens += tokens
            
            with st.expander(f"📦 {skill.name}", expanded=(i == 1)):
                st.write(f"**설명:** {skill.description}")
                st.write(f"**경로:** `{skill.path}`")
                if skill.allowed_tools:
                    st.write(f"**허용 도구:** {skill.allowed_tools}")
                st.metric("예상 토큰", f"~{tokens} tokens")
        
        st.divider()
        st.metric("총 토큰 (Phase 1)", f"~{total_tokens} tokens", f"{len(st.session_state.skills)}개 skill")
    
    with col2:
        st.subheader("Phase 1 요약")
        st.info(f"""
        ✅ **{len(st.session_state.skills)}개** Skill 발견
        
        📊 **토큰 사용량:**
        - 총: ~{total_tokens} tokens
        - 평균: ~{total_tokens // len(st.session_state.skills) if st.session_state.skills else 0} tokens/skill
        
        💡 **포함된 내용:**
        - ✅ Skill 이름
        - ✅ 설명 (description)
        - ✅ 경로 (location)
        - ❌ Instructions (아직 없음)
        - ❌ Resources (아직 없음)
        """)
    
    # System Prompt 생성 및 표시
    st.divider()
    st.subheader("생성된 System Prompt (Phase 1)")
    
    base_prompt = "You are a helpful AI assistant."
    skills_prompt = generate_skills_prompt(st.session_state.skills)
    full_prompt = f"{base_prompt}\n\n{skills_prompt}"
    
    st.session_state.system_prompt = full_prompt
    st.session_state.tracker["prompt_content"]["initial_system_prompt"] = full_prompt
    
    prompt_tokens = estimate_tokens(full_prompt)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.code(full_prompt, language="markdown")
    with col2:
        st.metric("Prompt 크기", f"~{format_number(prompt_tokens)} tokens")
        st.metric("문자 수", f"{len(full_prompt):,}")
    

# Phase 2: Activation
def show_phase2():
    """Phase 2: Activation 시각화"""
    st.header("🎯 Phase 2: Activation (Instructions 로드)")
    
    if not st.session_state.skills:
        st.warning("먼저 Phase 1에서 Skills를 발견해주세요.")
        if st.button("⬅️ Phase 1로 돌아가기", key="back_to_phase1_from_phase2"):
            st.session_state.current_phase = "Phase 1"
            st.rerun()
        return
    
    # System Prompt 생성
    base_prompt = "You are a helpful AI assistant."
    skills_prompt = generate_skills_prompt(st.session_state.skills)
    full_prompt = f"{base_prompt}\n\n{skills_prompt}"
    
    if not st.session_state.tracker["prompt_content"]["initial_system_prompt"]:
        st.session_state.tracker["prompt_content"]["initial_system_prompt"] = full_prompt
    
    # Skill 활성화 시뮬레이션
    st.subheader("Skill 활성화 시뮬레이션")
    st.info("💡 **Phase 2:** Skill을 선택하면 Instructions가 로드되어 Prompt에 추가됩니다!")
    
    skill_names = [s.name for s in st.session_state.skills]
    selected_skill = st.selectbox(
        "활성화할 Skill 선택:",
        skill_names,
        key="skill_selector_phase2",
        index=0 if "web-research" in skill_names else None
    )
    
    if st.button("🎯 Skill 활성화 시뮬레이션", use_container_width=True, type="primary", key="simulate_skill_activation"):
        skills_dir = Path(__file__).parent.parent / "skills"
        skill_tool = create_skill_tool(st.session_state.skills, skills_dir)
        result = skill_tool(selected_skill)
        
        # Tracking
        if "tracker" in st.session_state:
            st.session_state.tracker["skill_calls"].append({
                "skill_name": selected_skill,
                "phase": 2,
                "timestamp": time.time(),
            })
            st.session_state.tracker["prompt_content"]["tool_results"].append({
                "type": "skill",
                "skill_name": selected_skill,
                "content": result,
                "tokens": estimate_tokens(result),
            })
        
        if result:
            st.success(f"✅ {selected_skill} Skill 활성화 완료! Instructions가 로드되었습니다.")
            st.rerun()
    
    # Tool 호출 추적 표시
    if st.session_state.tracker["skill_calls"]:
        st.divider()
        st.subheader("🔧 Tool 호출 추적")
        
        for i, call in enumerate(st.session_state.tracker["skill_calls"], 1):
            skill_name = call["skill_name"]
            with st.expander(f"호출 #{i}: skill('{skill_name}')", expanded=True):
                # 해당 skill의 instructions 로드
                skill = next((s for s in st.session_state.skills if s.name == skill_name), None)
                if skill:
                    instructions = load_instructions(skill.path)
                    tokens = estimate_tokens(instructions)
                    
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.code(instructions, language="markdown")
                    with col2:
                        st.metric("Instructions 토큰", f"~{format_number(tokens)} tokens")
                        st.metric("Instructions 크기", f"{len(instructions):,} chars")
    
    # Prompt 상태 표시
    st.divider()
    st.subheader("📋 현재 Prompt 상태")
    
    initial_tokens = estimate_tokens(st.session_state.tracker["prompt_content"]["initial_system_prompt"])
    tool_tokens = sum(r.get("tokens", 0) for r in st.session_state.tracker["prompt_content"]["tool_results"])
    total_tokens = initial_tokens + tool_tokens
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("System Prompt", f"~{format_number(initial_tokens)} tokens")
    with col2:
        st.metric("Tool 결과", f"~{format_number(tool_tokens)} tokens")
    with col3:
        st.metric("총 Prompt", f"~{format_number(total_tokens)} tokens")
    
    # Prompt 내용 표시
    with st.expander("📄 전체 Prompt 내용 보기", expanded=False):
        st.write("**System Prompt (Phase 1):**")
        st.code(st.session_state.tracker["prompt_content"]["initial_system_prompt"], language="markdown")
        
        for i, result in enumerate(st.session_state.tracker["prompt_content"]["tool_results"], 1):
            st.write(f"**Tool 결과 #{i} ({result.get('type', 'unknown')}):**")
            content = str(result.get("content", ""))
            st.code(content, language="markdown")
    

# Phase 3: Resources
def show_phase3():
    """Phase 3: Resources 시각화"""
    st.header("📚 Phase 3: Resources (필요시 로드)")
    
    if not st.session_state.skills:
        st.warning("먼저 Phase 1에서 Skills를 발견해주세요.")
        if st.button("⬅️ Phase 1로 돌아가기", key="back_to_phase1_from_phase3"):
            st.session_state.current_phase = "Phase 1"
            st.rerun()
        return
    
    # 사용 가능한 리소스 표시
    st.subheader("사용 가능한 Resources")
    
    # Phase 2에서 활성화된 skill 찾기
    activated_skill_name = None
    if st.session_state.tracker["skill_calls"]:
        activated_skill_name = st.session_state.tracker["skill_calls"][-1]["skill_name"]
    
    # 활성화된 skill이 없으면 skill 선택
    if not activated_skill_name:
        st.info("💡 Phase 2에서 skill을 활성화하면 해당 skill의 리소스를 볼 수 있습니다.")
        skill_names = [s.name for s in st.session_state.skills]
        selected_skill_name = st.selectbox(
            "리소스를 확인할 Skill 선택:",
            skill_names,
            key="skill_selector_phase3"
        )
        activated_skill_name = selected_skill_name
    
    # 선택된 skill 찾기
    selected_skill = next((s for s in st.session_state.skills if s.name == activated_skill_name), None)
    if not selected_skill:
        st.warning(f"{activated_skill_name} skill을 찾을 수 없습니다.")
        return
    
    if activated_skill_name and st.session_state.tracker["skill_calls"]:
        st.success(f"✅ {activated_skill_name} skill이 활성화되어 있습니다.")
    
    skill_dir = Path(selected_skill.skill_dir)
    resources = []
    for subdir in ["scripts", "references", "assets"]:
        resource_dir = skill_dir / subdir
        if resource_dir.exists() and resource_dir.is_dir():
            files = list(resource_dir.rglob("*"))
            for file_path in files:
                if file_path.is_file():
                    rel_path = f"{subdir}/{file_path.relative_to(resource_dir)}"
                    resources.append((rel_path, file_path))
    
    if not resources:
        st.info("이 skill에는 리소스 파일이 없습니다.")
    else:
        st.write(f"**{len(resources)}개** 리소스 파일 발견:")
        for rel_path, file_path in resources:
            size = file_path.stat().st_size
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"📄 `{rel_path}`")
            with col2:
                st.write(f"{size:,} bytes")
    
    # Resource 파일 읽기 시뮬레이션
    st.divider()
    st.subheader("Resource 파일 읽기 시뮬레이션")
    st.info("💡 **팁:** 리소스 파일을 선택하고 읽어보세요!")
    
    if resources:
        selected_resource = st.selectbox(
            "읽을 리소스 파일 선택:",
            [r[0] for r in resources],
            key="resource_selector"
        )
        
        if st.button("📄 Resource 파일 읽기 시뮬레이션", use_container_width=True, type="primary", key="simulate_file_read"):
            # 선택된 리소스의 정보 찾기
            selected_info = next((r for r in resources if r[0] == selected_resource), None)
            if selected_info:
                rel_path, file_path = selected_info
                # load_resource 사용
                try:
                    result = load_resource(selected_skill.skill_dir, rel_path)
                except Exception as e:
                    result = f"Error reading file: {str(e)}"
                
                # Tracking
                if "tracker" in st.session_state:
                    file_path_str = str(file_path)
                    st.session_state.tracker["file_read_calls"].append({
                        "path": file_path_str,
                        "rel_path": rel_path,
                        "phase": 3,
                        "timestamp": time.time(),
                    })
                    st.session_state.tracker["prompt_content"]["tool_results"].append({
                        "type": "file_read",
                        "path": file_path_str,
                        "rel_path": rel_path,
                        "content": result,
                        "tokens": estimate_tokens(result),
                    })
                
                if result:
                    st.success("✅ Resource 파일 로드 완료!")
                    st.rerun()
    
    # File read 호출 추적
    if st.session_state.tracker["file_read_calls"]:
        st.divider()
        st.subheader("🔧 File Read 호출 추적")
        
        for i, call in enumerate(st.session_state.tracker["file_read_calls"], 1):
            path = call["path"]
            # Tracker에서 해당 파일의 내용 찾기
            file_result = next(
                (r for r in st.session_state.tracker["prompt_content"]["tool_results"] 
                 if r.get("type") == "file_read" and (r.get("path") == path or r.get("rel_path") == call.get("rel_path"))),
                None
            )
            
            with st.expander(f"호출 #{i}: file_read('{path}')", expanded=True):
                if file_result:
                    content = file_result.get("content", "")
                    tokens = file_result.get("tokens", 0)
                    
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.code(content, language="markdown")
                    with col2:
                        st.metric("Resource 토큰", f"~{format_number(tokens)} tokens")
                        st.metric("Resource 크기", f"{len(content):,} chars")
                else:
                    st.warning("파일 내용을 찾을 수 없습니다.")
    
    # 최종 Prompt 상태
    st.divider()
    st.subheader("📋 최종 Prompt 상태")
    
    initial_tokens = estimate_tokens(st.session_state.tracker["prompt_content"]["initial_system_prompt"])
    tool_tokens = sum(r.get("tokens", 0) for r in st.session_state.tracker["prompt_content"]["tool_results"])
    total_tokens = initial_tokens + tool_tokens
    
    # 토큰 사용량 시각화
    col1, col2 = st.columns([2, 1])
    
    with col1:
        try:
            import plotly.graph_objects as go
            
            fig = go.Figure(data=[
            go.Bar(
                name="System Prompt",
                x=["Phase 1"],
                y=[initial_tokens],
                marker_color='#1f77b4',
            ),
            go.Bar(
                name="Tool Results",
                x=["Phase 2-3"],
                y=[tool_tokens],
                marker_color='#ff7f0e',
            ),
        ])
        
            fig.update_layout(
                title="토큰 사용량 비교",
                xaxis_title="Phase",
                yaxis_title="토큰 수",
                barmode='stack',
                height=300,
            )
            
            st.plotly_chart(fig, use_container_width=True)
        except ImportError:
            st.info("📊 Plotly가 설치되지 않아 차트를 표시할 수 없습니다. `pip install plotly`로 설치하세요.")
    
    with col2:
        st.metric("System Prompt", f"~{format_number(initial_tokens)} tokens")
        st.metric("Tool 결과", f"~{format_number(tool_tokens)} tokens")
        st.metric("총 Prompt", f"~{format_number(total_tokens)} tokens", delta=f"{len(st.session_state.tracker['prompt_content']['tool_results'])}개 tool 호출")
    
    # Progressive Disclosure 요약
    st.divider()
    st.subheader("💡 Progressive Disclosure 요약")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.success("""
        **Phase 1: Discovery**
        - ✅ Metadata만 로드
        - ✅ 최소한의 토큰 사용
        - ✅ 모든 skill 정보 포함
        """)
    
    with col2:
        st.info("""
        **Phase 2: Activation**
        - ✅ 필요할 때만 instructions 로드
        - ✅ skill tool 호출 시에만 추가
        - ✅ 선택적 로딩
        """)
    
    with col3:
        st.warning("""
        **Phase 3: Resources**
        - ✅ 필요한 리소스만 로드
        - ✅ file_read 호출 시에만 추가
        - ✅ 최소한의 컨텍스트 사용
        """)
    


# 메인 로직
def main():
    """메인 함수"""
    init_tracking()
    
    # Phase 선택
    phase = st.session_state.current_phase
    
    # Phase 탭
    tab1, tab2, tab3 = st.tabs(["📦 Phase 1: Discovery", "🎯 Phase 2: Activation", "📚 Phase 3: Resources"])
    
    with tab1:
        show_phase1()
    
    with tab2:
        show_phase2()
    
    with tab3:
        show_phase3()
    
    # 하단 요약
    st.divider()
    st.markdown("""
    ### 🎯 Progressive Disclosure의 장점
    
    1. **토큰 효율성**: 필요한 정보만 필요한 시점에 로드하여 토큰 사용량 최소화
    2. **의사결정 복잡도 감소**: Agent가 모든 skill의 전체 내용을 한 번에 보지 않아도 됨
    3. **확장성**: Skill이 많아져도 초기 로딩 비용이 크게 증가하지 않음
    4. **자연스러운 사용**: LLM이 필요하다고 판단할 때만 skill을 활성화
    """)


if __name__ == "__main__":
    main()

