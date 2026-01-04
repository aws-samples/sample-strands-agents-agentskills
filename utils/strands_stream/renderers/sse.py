"""SSE stream renderer for FastAPI Server-Sent Events"""

import json
from typing import Any

from ..events import (
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
from .base import BaseStreamRenderer


class SSEStreamRenderer(BaseStreamRenderer):
    """Stream renderer for FastAPI Server-Sent Events (returns JSON strings)"""
    
    def _safe_serialize(self, obj: Any) -> Any:
        """Try to serialize complex objects safely
        
        Args:
            obj: Object to serialize
            
        Returns:
            JSON-serializable representation of the object
        """
        if obj is None:
            return None
        try:
            # Test if object is JSON serializable
            json.dumps(obj)
            return obj
        except (TypeError, ValueError):
            # Extract common attributes if available
            if hasattr(obj, '__dict__'):
                return {k: str(v) for k, v in obj.__dict__.items() 
                        if not k.startswith('_')}
            return str(obj)
    
    def on_text(self, event: TextEvent) -> str:
        """Format text event as SSE"""
        payload = {
            "type": "text",
            "data": event.data,
        }
        if event.source:
            payload["source"] = event.source
        return f"data: {json.dumps(payload)}\n\n"
    
    def on_tool_use(self, event: CurrentToolUseEvent) -> str:
        """Format tool use as SSE"""
        payload = {
            "type": "current_tool_use",
            "tool_name": event.tool_name,
            "tool_id": event.tool_id,
            "tool_input": event.tool_input,
        }
        if event.source:
            payload["source"] = event.source
        return f"data: {json.dumps(payload)}\n\n"
    
    def on_tool_result(self, event: ToolResultEvent) -> str:
        """Format tool result as SSE"""
        payload = {
            "type": "tool_result",
            "tool_name": event.tool_name,
            "tool_id": event.tool_id,
            "data": event.data,
            "metadata": event.metadata,
        }
        if event.source:
            payload["source"] = event.source
        return f"data: {json.dumps(payload)}\n\n"
    
    def on_tool_stream(self, event: ToolStreamEvent) -> str:
        """Format tool stream event as SSE"""
        payload = {
            "type": "tool_stream_event",
            "tool_use": event.tool_use,
            "data": event.data,
        }
        return f"data: {json.dumps(payload)}\n\n"
    
    def on_reasoning(self, event: ReasoningEvent) -> str:
        """Format reasoning event as SSE"""
        payload = {
            "type": "reasoning",
            "data": event.data,
            "metadata": event.metadata,
        }
        return f"data: {json.dumps(payload)}\n\n"
    
    def on_lifecycle(self, event: LifecycleEvent) -> str:
        """Format lifecycle event as SSE"""
        payload = {
            "type": "lifecycle",
            "lifecycle_type": event.lifecycle_type,
            "message": event.message,
            "force_stop_reason": event.force_stop_reason,
            "result": self._safe_serialize(event.result),
        }
        return f"data: {json.dumps(payload)}\n\n"
    
    def on_multiagent_node_start(self, event: MultiAgentNodeStartEvent) -> str:
        """Format multi-agent node start as SSE"""
        payload = {
            "type": "multiagent_node_start",
            "node_id": event.node_id,
            "node_type": event.node_type,
        }
        return f"data: {json.dumps(payload)}\n\n"
    
    def on_multiagent_node_stream(self, event: MultiAgentNodeStreamEvent) -> list:
        """Process multi-agent node stream (recursively process inner event)"""
        # Recursively process inner event
        return self.process(event.inner_event)
    
    def on_multiagent_node_stop(self, event: MultiAgentNodeStopEvent) -> str:
        """Format multi-agent node stop as SSE"""
        payload = {
            "type": "multiagent_node_stop",
            "node_id": event.node_id,
            "node_result": self._safe_serialize(event.node_result),
        }
        return f"data: {json.dumps(payload)}\n\n"
    
    def on_multiagent_handoff(self, event: MultiAgentHandoffEvent) -> str:
        """Format multi-agent handoff as SSE"""
        payload = {
            "type": "multiagent_handoff",
            "from_node_ids": event.from_node_ids,
            "to_node_ids": event.to_node_ids,
            "message": event.message,
        }
        return f"data: {json.dumps(payload)}\n\n"
    
    def on_multiagent_result(self, event: MultiAgentResultEvent) -> str:
        """Format multi-agent final result as SSE"""
        payload = {
            "type": "multiagent_result",
            "result": self._safe_serialize(event.result),
        }
        return f"data: {json.dumps(payload)}\n\n"


# Backward compatibility aliases
SSERenderer = SSEStreamRenderer
SSEAdapter = SSEStreamRenderer

