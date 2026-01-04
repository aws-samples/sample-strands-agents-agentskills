"""Utility functions for skill tools

Shared functions used by skill tool implementations.
"""

import logging
from pathlib import Path
from typing import Dict, List

from .models import SkillProperties
from .errors import SkillNotFoundError

logger = logging.getLogger(__name__)


def validate_skill_name(skill_name: str, skill_map: Dict[str, SkillProperties]) -> SkillProperties:
    """Validate that a skill exists and return its properties.

    Args:
        skill_name: Name of the skill to validate
        skill_map: Dictionary mapping skill names to SkillProperties

    Returns:
        SkillProperties for the validated skill

    Raises:
        SkillNotFoundError: If the skill doesn't exist
    """
    if skill_name not in skill_map:
        available = ", ".join(skill_map.keys())
        raise SkillNotFoundError(
            f"Skill '{skill_name}' not found. "
            f"Available skills: {available}"
        )
    return skill_map[skill_name]


def scan_skill_resources(skill_dir: Path) -> List[str]:
    """Scan skill directory for available resources.

    Scans the standard subdirectories (scripts, references, assets)
    and returns a list of absolute file paths.

    Args:
        skill_dir: Path to the skill directory

    Returns:
        List of absolute file paths to resources
    """
    resources = []
    for subdir in ["scripts", "references", "assets"]:
        resource_dir = skill_dir / subdir
        if resource_dir.exists() and resource_dir.is_dir():
            for file_path in sorted(resource_dir.rglob("*")):
                if file_path.is_file():
                    resources.append(str(file_path.absolute()))
    return resources


def build_skill_header(
    skill: SkillProperties,
    include_resources: bool = True,
) -> str:
    """Build a header string with skill metadata and resources.

    Args:
        skill: The skill's properties
        include_resources: Whether to scan and include resource list
        include_instructions_label: Whether to add "# Instructions" label

    Returns:
        Formatted header string
    """

    header = (
        f"# Skill: {skill.name}\n\n"
        f"**Description:** {skill.description}\n\n"
        f"**Skill Directory:** `{skill.skill_dir}/`\n\n"
    )

    # Add allowed-tools reminder if specified
    if skill.allowed_tools:
        header += f"\n**IMPORTANT:** Only use these tools: `{skill.allowed_tools}`\n"

    # Scan and list available resources if requested
    if include_resources:
        skill_dir = Path(skill.skill_dir)
        resources = scan_skill_resources(skill_dir)

        if resources:
            header += "\n**Available Resources:**\n"
            for resource in resources:
                header += f"- `{resource}`\n"
            header += "\n"

    header += "---\n\n"

    return header


__all__ = [
    "validate_skill_name",
    "scan_skill_resources",
    "build_skill_header",
]

