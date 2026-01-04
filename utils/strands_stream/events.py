"""Event data classes for Strands SDK stream events"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Literal


class BaseEvent(ABC):
    """Abstract base class for all stream events"""
    
    @property
    @abstractmethod
    def event_type(self) -> str:
        """Return the event type identifier"""
        pass


@dataclass
class TextEvent(BaseEvent):
    """Text chunk event from model"""
    data: str
    source: str | None = None  # sub-agent skill_name or None for main agent
    
    @property
    def event_type(self) -> str:
        return "text"


@dataclass
class CurrentToolUseEvent(BaseEvent):
    """Tool use event (current_tool_use from Strands SDK)"""
    tool_name: str
    tool_id: str | None = None
    tool_input: dict | None = None
    source: str | None = None  # sub-agent skill_name or None for main agent
    
    @property
    def event_type(self) -> str:
        return "current_tool_use"


@dataclass
class ToolResultEvent(BaseEvent):
    """Tool result event"""
    data: str
    tool_name: str | None = None
    tool_id: str | None = None
    metadata: dict | None = None
    source: str | None = None  # sub-agent skill_name or None for main agent
    
    @property
    def event_type(self) -> str:
        return "tool_result"


@dataclass
class ToolStreamEvent(BaseEvent):
    """Tool stream event - data streamed from a tool (tool_stream_event from Strands SDK)"""
    tool_use: dict  # The ToolUse for the tool that streamed the event
    data: Any  # The data streamed from the tool
    
    @property
    def event_type(self) -> str:
        return "tool_stream_event"


@dataclass
class ReasoningEvent(BaseEvent):
    """Reasoning text event"""
    data: str
    metadata: dict | None = None
    
    @property
    def event_type(self) -> str:
        return "reasoning"


@dataclass
class LifecycleEvent(BaseEvent):
    """Lifecycle event (init, start, complete, force_stop)"""
    lifecycle_type: Literal["init", "start", "complete", "force_stop"]
    message: dict | None = None
    force_stop_reason: str | None = None
    result: Any = None
    
    @property
    def event_type(self) -> str:
        return "lifecycle"


@dataclass
class MultiAgentNodeStartEvent(BaseEvent):
    """Multi-agent node start event"""
    node_id: str
    node_type: str
    
    @property
    def event_type(self) -> str:
        return "multiagent_node_start"


@dataclass
class MultiAgentNodeStreamEvent(BaseEvent):
    """Multi-agent node stream event (forwarded inner events)"""
    node_id: str
    inner_event: dict
    
    @property
    def event_type(self) -> str:
        return "multiagent_node_stream"


@dataclass
class MultiAgentNodeStopEvent(BaseEvent):
    """Multi-agent node stop event"""
    node_id: str
    node_result: Any
    
    @property
    def event_type(self) -> str:
        return "multiagent_node_stop"


@dataclass
class MultiAgentHandoffEvent(BaseEvent):
    """Multi-agent handoff event"""
    from_node_ids: list[str]
    to_node_ids: list[str]
    message: str | None = None
    
    @property
    def event_type(self) -> str:
        return "multiagent_handoff"


@dataclass
class MultiAgentResultEvent(BaseEvent):
    """Multi-agent final result event"""
    result: Any
    
    @property
    def event_type(self) -> str:
        return "multiagent_result"


@dataclass
class StreamOutput:
    """Structured output from renderer with source tracking"""
    content: str
    source: str | None = None  # None for main agent
    event_type: str = "content"  # content, tool_start, tool_result, etc.

