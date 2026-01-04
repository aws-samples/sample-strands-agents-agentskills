"""Strands Agents SDK Stream Event Processing

This module provides stream renderers for processing streaming events
from Strands Agents SDK across different environments
(Terminal, Streamlit, FastAPI SSE).

Architecture:
- StrandsEventParser: Core parsing logic (no output)
- BaseStreamRenderer: Abstract renderer interface
- TerminalStreamRenderer, StreamlitStreamRenderer, SSEStreamRenderer: Environment-specific renderers
"""

from .parser import StrandsEventParser
from .renderers import (
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

# Re-export events for advanced usage
from .events import (
    BaseEvent,
    TextEvent,
    CurrentToolUseEvent,
    ToolResultEvent,
    ToolStreamEvent,
    ReasoningEvent,
    LifecycleEvent,
    MultiAgentNodeStartEvent,
    MultiAgentNodeStreamEvent,
    MultiAgentNodeStopEvent,
    MultiAgentHandoffEvent,
    MultiAgentResultEvent,
)

__all__ = [
    # Parser
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
    # Events (for advanced usage)
    "BaseEvent",
    "TextEvent",
    "CurrentToolUseEvent",
    "ToolResultEvent",
    "ToolStreamEvent",
    "ReasoningEvent",
    "LifecycleEvent",
    "MultiAgentNodeStartEvent",
    "MultiAgentNodeStreamEvent",
    "MultiAgentNodeStopEvent",
    "MultiAgentHandoffEvent",
    "MultiAgentResultEvent",
]

