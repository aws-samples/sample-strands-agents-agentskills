"""YAML frontmatter parsing for SKILL.md files

This module handles parsing of SKILL.md files following the AgentSkills.io specification.
"""

import re
from pathlib import Path
from typing import Optional

import strictyaml

from .errors import ParseError, ValidationError


def find_skill_md(skill_dir: Path) -> Optional[Path]:
    """Find the SKILL.md file in a skill directory

    Prefers SKILL.md (uppercase) but accepts skill.md (lowercase).

    Args:
        skill_dir: Path to the skill directory

    Returns:
        Path to the SKILL.md file, or None if not found
    """
    for name in ("SKILL.md", "skill.md"):
        path = skill_dir / name
        if path.exists():
            return path
    return None


def _parse_skill_md(content: str) -> tuple[dict, str]:
    """Parse SKILL.md content into frontmatter and body

    This is the core parsing function that splits SKILL.md into:
    - frontmatter: YAML metadata
    - body: Markdown instructions

    Args:
        content: Raw SKILL.md content

    Returns:
        Tuple of (frontmatter dict, body string)

    Raises:
        ParseError: If frontmatter is invalid
    """
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n?(.*)$', content, re.DOTALL)
    if not match:
        raise ParseError("SKILL.md must start with YAML frontmatter (---) and close with ---")

    frontmatter_str = match.group(1)
    body = match.group(2).strip()

    try:
        parsed = strictyaml.load(frontmatter_str)
        frontmatter = parsed.data
    except strictyaml.YAMLError as e:
        raise ParseError(f"Invalid YAML in frontmatter: {e}")

    if not isinstance(frontmatter, dict):
        raise ParseError("SKILL.md frontmatter must be a YAML mapping")

    # Ensure metadata field is dict of strings
    if "metadata" in frontmatter and isinstance(frontmatter["metadata"], dict):
        frontmatter["metadata"] = {
            str(k): str(v) for k, v in frontmatter["metadata"].items()
        }

    return frontmatter, body


def load_metadata(skill_dir: str | Path):
    """Load skill metadata from SKILL.md frontmatter (Phase 1: ~100 tokens)

    This is Phase 1 of Progressive Disclosure - loads only lightweight metadata
    without the full instructions body.

    Args:
        skill_dir: Path to the skill directory

    Returns:
        SkillProperties with parsed metadata (instructions NOT loaded)

    Raises:
        ParseError: If SKILL.md is missing or has invalid YAML
        ValidationError: If required fields (name, description) are missing
    """
    from .models import SkillProperties

    skill_dir = Path(skill_dir).resolve()
    skill_md = find_skill_md(skill_dir)

    if skill_md is None:
        raise ParseError(f"SKILL.md not found in {skill_dir}")

    # Read file and extract frontmatter (ignoring body)
    content = skill_md.read_text()
    frontmatter, _ = _parse_skill_md(content)

    # Validate required fields
    if "name" not in frontmatter:
        raise ValidationError("Missing required field in frontmatter: name")
    if "description" not in frontmatter:
        raise ValidationError("Missing required field in frontmatter: description")

    name = frontmatter["name"]
    description = frontmatter["description"]

    if not isinstance(name, str) or not name.strip():
        raise ValidationError("Field 'name' must be a non-empty string")
    if not isinstance(description, str) or not description.strip():
        raise ValidationError("Field 'description' must be a non-empty string")

    return SkillProperties(
        name=name.strip(),
        description=description.strip(),
        path=str(skill_md.absolute()),
        skill_dir=str(skill_dir.absolute()),
        license=frontmatter.get("license"),
        compatibility=frontmatter.get("compatibility"),
        allowed_tools=frontmatter.get("allowed-tools"),
        metadata=frontmatter.get("metadata"),
    )


def load_instructions(skill_path: str | Path) -> str:
    """Load skill instructions from SKILL.md body (Phase 2: <5000 tokens)

    This is Phase 2 of Progressive Disclosure - loads the full markdown body
    (instructions) when the skill is activated.

    Args:
        skill_path: Path to SKILL.md file

    Returns:
        Markdown body (instructions) without frontmatter

    Raises:
        ParseError: If file cannot be read or parsed
    """
    skill_path = Path(skill_path)

    try:
        content = skill_path.read_text(encoding="utf-8")
        _, instructions = _parse_skill_md(content)
        return instructions
    except Exception as e:
        raise ParseError(f"Failed to read instructions from {skill_path}: {e}")


def load_resource(skill_dir: str | Path, resource_path: str) -> str:
    """Load a resource file from skill directory (Phase 3: as needed)

    This is Phase 3 of Progressive Disclosure - loads files from scripts/,
    references/, or assets/ only when explicitly needed.

    Args:
        skill_dir: Path to skill directory
        resource_path: Relative path to resource (e.g., "scripts/helper.py")

    Returns:
        Content of the resource file

    Raises:
        ParseError: If resource cannot be read or is outside skill directory

    Example:
        >>> content = load_resource("/path/to/skill", "references/api-docs.md")
    """
    skill_dir = Path(skill_dir).resolve()
    resource_file = (skill_dir / resource_path).resolve()

    # Security: ensure resource is within skill directory
    try:
        resource_file.relative_to(skill_dir)
    except ValueError:
        raise ParseError(f"Resource path '{resource_path}' is outside skill directory")

    if not resource_file.exists():
        raise ParseError(f"Resource not found: {resource_path}")

    if not resource_file.is_file():
        raise ParseError(f"Resource is not a file: {resource_path}")

    # File size limit (10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024
    if resource_file.stat().st_size > MAX_FILE_SIZE:
        raise ParseError(f"Resource too large (max 10MB): {resource_path}")

    try:
        return resource_file.read_text(encoding="utf-8")
    except Exception as e:
        raise ParseError(f"Failed to read resource {resource_path}: {e}")


__all__ = [
    "find_skill_md",
    "load_metadata",
    "load_instructions",
    "load_resource",
]
