from setuptools import setup, find_packages

setup(
    name="strands_agentskills",
    version="0.2.0",
    description="Agent Skills for Strands Agents SDK",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "strands-agents>=1.0.0",
        "strands-agents-tools>=0.2.0",  # Required by internal skills_ref module
        "strictyaml>=1.0.0",  # YAML parsing for SKILL.md frontmatter
    ],
    extras_require={
        "dev": ["pytest>=7.0", "pytest-asyncio>=0.21.0"],
    },
)
