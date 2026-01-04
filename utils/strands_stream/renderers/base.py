"""Base stream renderer class for environment-specific renderers"""

from abc import ABC, abstractmethod
from typing import Any

from ..events import (
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
from ..parser import StrandsEventParser


class BaseStreamRenderer(ABC):
    """Abstract base class for environment-specific stream renderers"""
    
    def __init__(self, parser: StrandsEventParser | None = None, debug: bool = False):
        self.parser = parser or StrandsEventParser()
        self.debug = debug
    
    def process(self, event: dict) -> list[Any]:
        """Process raw event and return environment-specific output"""
        parsed_events = self.parser.parse(event, debug=self.debug)
        results = []
        
        for parsed_event in parsed_events:
            # Handle all BaseEvent types
            if isinstance(parsed_event, TextEvent):
                result = self.on_text(parsed_event)
            elif isinstance(parsed_event, CurrentToolUseEvent):
                result = self.on_tool_use(parsed_event)
            elif isinstance(parsed_event, ToolResultEvent):
                result = self.on_tool_result(parsed_event)
            elif isinstance(parsed_event, ToolStreamEvent):
                result = self.on_tool_stream(parsed_event)
            elif isinstance(parsed_event, ReasoningEvent):
                result = self.on_reasoning(parsed_event)
            elif isinstance(parsed_event, LifecycleEvent):
                result = self.on_lifecycle(parsed_event)
            elif isinstance(parsed_event, MultiAgentNodeStartEvent):
                result = self.on_multiagent_node_start(parsed_event)
            elif isinstance(parsed_event, MultiAgentNodeStreamEvent):
                result = self.on_multiagent_node_stream(parsed_event)
            elif isinstance(parsed_event, MultiAgentNodeStopEvent):
                result = self.on_multiagent_node_stop(parsed_event)
            elif isinstance(parsed_event, MultiAgentHandoffEvent):
                result = self.on_multiagent_handoff(parsed_event)
            elif isinstance(parsed_event, MultiAgentResultEvent):
                result = self.on_multiagent_result(parsed_event)
            else:
                result = None
            
            if result is not None:
                if isinstance(result, list):
                    results.extend(result)
                else:
                    results.append(result)
        
        return results
    
    @abstractmethod
    def on_text(self, event: TextEvent) -> Any:
        """Handle text event"""
        pass
    
    @abstractmethod
    def on_tool_use(self, event: CurrentToolUseEvent) -> Any:
        """Handle tool use event (current_tool_use)"""
        pass
    
    @abstractmethod
    def on_tool_result(self, event: ToolResultEvent) -> Any:
        """Handle tool result event"""
        pass
    
    def on_tool_stream(self, event: ToolStreamEvent) -> Any:
        """Handle tool stream event (tool_stream_event) - default: no-op"""
        return None
    
    @abstractmethod
    def on_reasoning(self, event: ReasoningEvent) -> Any:
        """Handle reasoning event"""
        pass
    
    def on_lifecycle(self, event: LifecycleEvent) -> Any:
        """Handle lifecycle event (init, start, complete, force_stop)"""
        return None  # Default: no-op
    
    def on_multiagent_node_start(self, event: MultiAgentNodeStartEvent) -> Any:
        """Handle multi-agent node start event"""
        return None  # Default: no-op
    
    def on_multiagent_node_stream(self, event: MultiAgentNodeStreamEvent) -> Any:
        """Handle multi-agent node stream event (recursively process inner event)"""
        # Recursively process inner event
        return self.process(event.inner_event)
    
    def on_multiagent_node_stop(self, event: MultiAgentNodeStopEvent) -> Any:
        """Handle multi-agent node stop event"""
        return None  # Default: no-op
    
    def on_multiagent_handoff(self, event: MultiAgentHandoffEvent) -> Any:
        """Handle multi-agent handoff event"""
        return None  # Default: no-op
    
    def on_multiagent_result(self, event: MultiAgentResultEvent) -> Any:
        """Handle multi-agent final result event"""
        return None  # Default: no-op
    
    def reset(self):
        """Reset renderer state"""
        self.parser.reset()


# Backward compatibility alias
BaseAdapter = BaseStreamRenderer

