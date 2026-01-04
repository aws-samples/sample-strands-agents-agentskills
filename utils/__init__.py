"""Utility modules for Strands AgentSkills"""

from .strands_stream import (
    StrandsEventParser,
    # New names (recommended)
    BaseStreamRenderer,
    TerminalStreamRenderer,
    StreamlitStreamRenderer,
    SSEStreamRenderer,
    # Legacy aliases (backward compatibility)
    BaseAdapter,
    TerminalAdapter,
    StreamlitAdapter,
    SSERenderer,
    SSEAdapter,
)

__all__ = [
    "StrandsEventParser",
    # Stream Renderers (recommended)
    "BaseStreamRenderer",
    "TerminalStreamRenderer",
    "StreamlitStreamRenderer",
    "SSEStreamRenderer",
    # Legacy aliases (backward compatibility)
    "BaseAdapter",
    "TerminalAdapter",
    "StreamlitAdapter",
    "SSERenderer",
    "SSEAdapter",
]

