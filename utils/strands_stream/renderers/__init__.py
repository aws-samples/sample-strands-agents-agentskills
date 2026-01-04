"""Stream renderers for different output environments (Terminal, Streamlit, SSE)"""

from .base import BaseStreamRenderer, BaseAdapter
from .streamlit import StreamlitStreamRenderer, StreamlitAdapter
from .sse import SSEStreamRenderer, SSERenderer, SSEAdapter
from .terminal import TerminalStreamRenderer, TerminalAdapter

__all__ = [
    # New names (recommended)
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

