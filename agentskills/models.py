"""Data models for Agent Skills

This module provides data models for working with Agent Skills following
the AgentSkills.io specification.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SkillProperties:
    """Skill metadata from SKILL.md frontmatter (Phase 1: ~100 tokens)

    This is Phase 1 of Progressive Disclosure - contains only lightweight metadata
    loaded during discovery. Instructions (Phase 2) and resources (Phase 3) are
    loaded separately on-demand.

    Attributes:
        name: Skill name in kebab-case (required)
        description: What the skill does and when to use it (required)
        path: Absolute path to SKILL.md file (for loading instructions)
        skill_dir: Absolute path to skill directory (for loading resources)
        license: License for the skill (optional)
        compatibility: Compatibility information (optional)
        allowed_tools: Tool patterns the skill requires (optional)
        metadata: Key-value pairs for custom properties (optional)
    """

    name: str
    description: str
    path: str
    skill_dir: str
    license: Optional[str] = None
    compatibility: Optional[str] = None
    allowed_tools: Optional[str] = None
    metadata: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary, excluding None values and paths"""
        result = {
            "name": self.name,
            "description": self.description,
            "path": self.path,
            "skill_dir": self.skill_dir,
        }
        if self.license is not None:
            result["license"] = self.license
        if self.compatibility is not None:
            result["compatibility"] = self.compatibility
        if self.allowed_tools is not None:
            result["allowed-tools"] = self.allowed_tools
        if self.metadata:
            result["metadata"] = self.metadata
        return result


__all__ = [
    "SkillProperties",
]
