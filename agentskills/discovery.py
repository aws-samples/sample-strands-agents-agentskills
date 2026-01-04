"""Skill discovery - Phase 1 of Progressive Disclosure

This module implements the discovery phase where skills are scanned
from a directory and their lightweight metadata is loaded.

The discovery process follows these principles:
1. Scan skill directories for SKILL.md files
2. Load only frontmatter metadata (~100 tokens per skill)
3. Validate metadata against Agent Skills specification
4. Return lightweight SkillMetadata objects for prompt injection
"""

import logging
from pathlib import Path
from typing import List, Optional

# Import from unified modules
from .parser import find_skill_md, load_metadata
from .errors import ParseError, ValidationError
from .models import SkillProperties

logger = logging.getLogger(__name__)


def is_safe_path(path: Path, base_dir: Path) -> bool:
    """Validate that path is safely contained within base_dir

    Prevents directory traversal attacks through symlinks or path manipulation.

    Args:
        path: Path to validate
        base_dir: Base directory that should contain the path

    Returns:
        True if path is safe, False otherwise
    """
    try:
        resolved_path = path.resolve()
        resolved_base = base_dir.resolve()
        resolved_path.relative_to(resolved_base)
        return True
    except (ValueError, OSError, RuntimeError):
        return False


def discover_skills(skills_dir: str | Path) -> List[SkillProperties]:
    """Discover all skills in a directory

    Scans the skills directory and loads metadata from each skill's
    SKILL.md frontmatter. This is Phase 1 of progressive disclosure.

    Directory structure:
        skills/
        ├── web-research/
        │   ├── SKILL.md          # Required
        │   ├── scripts/          # Optional
        │   │   └── helper.py
        │   └── references/       # Optional
        │       └── docs.md
        └── code-review/
            └── SKILL.md

    Args:
        skills_dir: Path to directory containing skill subdirectories

    Returns:
        List of SkillProperties objects, sorted by skill name

    Example:
        >>> skills = discover_skills("./skills")
        >>> for skill in skills:
        ...     print(f"{skill.name}: {skill.description}")
        ...     print(f"  Location: {skill.path}")
    """
    skills_dir = Path(skills_dir).expanduser().resolve()

    if not skills_dir.exists():
        logger.info(f"Skills directory does not exist: {skills_dir}")
        return []

    if not skills_dir.is_dir():
        logger.warning(f"Skills path is not a directory: {skills_dir}")
        return []

    skills: List[SkillProperties] = []

    # Scan each subdirectory
    for skill_dir in skills_dir.iterdir():
        if not skill_dir.is_dir():
            continue

        # Security: validate path
        if not is_safe_path(skill_dir, skills_dir):
            logger.warning(f"Skipping unsafe path: {skill_dir}")
            continue

        # Look for SKILL.md
        skill_md_path = find_skill_md(skill_dir)
        if skill_md_path is None:
            logger.debug(f"No SKILL.md found in {skill_dir}")
            continue

        # Security: validate SKILL.md path
        if not is_safe_path(skill_md_path, skills_dir):
            logger.warning(f"Skipping unsafe SKILL.md: {skill_md_path}")
            continue

        # Parse metadata
        try:
            skill_props = load_metadata(skill_dir)
            skills.append(skill_props)
            logger.debug(f"Discovered skill: {skill_props.name}")

        except (ParseError, ValidationError) as e:
            logger.warning(f"Skipping invalid skill in {skill_dir}: {e}")
            continue
        except Exception as e:
            logger.error(f"Unexpected error parsing {skill_dir}: {e}")
            continue

    # Sort by name for consistent ordering
    skills.sort(key=lambda s: s.name)

    logger.info(f"Discovered {len(skills)} skills in {skills_dir}")
    return skills
