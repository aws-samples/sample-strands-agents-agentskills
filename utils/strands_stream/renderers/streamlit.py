"""Streamlit stream renderer for markdown output"""

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
    StreamOutput,
)
from .base import BaseStreamRenderer


class StreamlitStreamRenderer(BaseStreamRenderer):
    """Stream renderer for Streamlit output (returns StreamOutput objects)"""
    
    def __init__(self, parser=None):
        super().__init__(parser)
        # Track displayed tool calls by (source, tool_id) or (source, tool_name) for deduplication
        self.displayed_tool_calls = set()
        self.current_reasoning_active: dict[str | None, bool] = {}  # Track reasoning state per source
    
    def format_tool_display(self, tool_name: str, tool_input: dict | None) -> str:
        """Format tool name and arguments for display"""
        if not tool_input:
            return f"{tool_name}()"
        
        formatted_args = []
        for k, v in tool_input.items():
            if isinstance(v, str) and len(v) > 50:
                formatted_args.append(f"{k}='{v[:50]}...'")
            else:
                formatted_args.append(f"{k}={v!r}")
        
        return f"{tool_name}({', '.join(formatted_args)})"
    
    def on_text(self, event: TextEvent) -> StreamOutput:
        """Return text chunk as StreamOutput"""
        # Reset reasoning state for this source when text event occurs
        if event.source in self.current_reasoning_active:
            self.current_reasoning_active[event.source] = False
        return StreamOutput(
            content=event.data,
            source=event.source,
            event_type="text"
        )
    
    def on_tool_use(self, event: CurrentToolUseEvent) -> StreamOutput | None:
        """Return tool call as StreamOutput - shows accumulated input as it streams"""
        # Reset reasoning state for this source when tool use occurs
        if event.source in self.current_reasoning_active:
            self.current_reasoning_active[event.source] = False
        
        # Use (source, tool_id) or (source, tool_name) for deduplication
        dedup_key = (event.source, event.tool_id or event.tool_name)
        is_new_tool_call = dedup_key not in self.displayed_tool_calls
        
        if is_new_tool_call:
            self.displayed_tool_calls.add(dedup_key)
        
        if is_new_tool_call:
            # First time - show full tool call
            content = "\n\n**⚙️ Tool 호출:**"
            # Show tool_id if available
            if event.tool_id:
                content += f" **`{event.tool_name}`** (`{event.tool_id}`)\n\n"
            else:
                content += f" **`{event.tool_name}`**\n\n"
            return StreamOutput(
                content=content,
                source=event.source,
                event_type="tool_start"
            )
        else:
            # Update - show input update (for streaming accumulation)
            if event.tool_input:
                content = f"\n```json\n{json.dumps(event.tool_input, indent=2, ensure_ascii=False)}\n```\n\n"
                return StreamOutput(
                    content=content,
                    source=event.source,
                    event_type="tool_input_update"
                )
        return None
    
    def on_tool_result(self, event: ToolResultEvent) -> StreamOutput | None:
        """Return tool result as StreamOutput"""
        # Reset reasoning state for this source when tool result occurs
        if event.source in self.current_reasoning_active:
            self.current_reasoning_active[event.source] = False
        
        if not event.data:
            return None
        
        preview_len = min(500, len(event.data))
        preview = event.data[:preview_len]
        if len(event.data) > preview_len:
            preview += "\n...(생략)"
        
        content = f"\n\n**✅ Tool 결과:** {len(event.data):,} chars\n\n"
        content += f"```\n{preview}\n```\n\n"
        content += "\n\n---\n\n"
        return StreamOutput(
            content=content,
            source=event.source,
            event_type="tool_result"
        )
    
    def on_tool_stream(self, event: ToolStreamEvent) -> StreamOutput | None:
        """Return tool stream event as StreamOutput"""
        tool_use_dict = event.tool_use if isinstance(event.tool_use, dict) else {}
        tool_name = tool_use_dict.get("name", "unknown")
        tool_id = tool_use_dict.get("toolUseId")
        tool_input = tool_use_dict.get("input", {})
        
        # Try to extract source from tool_use if available (for sub-agent tools)
        source = None  # ToolStreamEvent doesn't have source, but we can infer from context
        
        content = f"\n\n**📡 Tool Stream: `{tool_name}`**"
        if tool_id:
            content += f" (`{tool_id}`)"
        content += "\n\n"
        
        # Show tool_input if available
        if tool_input:
            content += f"```json\n{json.dumps(tool_input, indent=2, ensure_ascii=False)}\n```\n\n"
        
        # Show stream data
        if event.data:
            if isinstance(event.data, str):
                preview_len = min(500, len(event.data))
                preview = event.data[:preview_len]
                if len(event.data) > preview_len:
                    preview += "\n...(생략)"
                content += f"```\n{preview}\n```\n\n"
            else:
                content += f"```json\n{json.dumps(event.data, indent=2, ensure_ascii=False)}\n```\n\n"
        
        return StreamOutput(
            content=content,
            source=source,
            event_type="tool_stream"
        )
    
    def on_reasoning(self, event: ReasoningEvent) -> StreamOutput:
        """Return reasoning text as StreamOutput with > prefix (blockquote style)"""
        # Reasoning events don't have source, so we use None (main agent)
        source = None
        
        # Replace newlines with newline + > to maintain blockquote across multiple lines
        text = event.data.replace("\n", "\n> ")
        
        # Add > prefix and 💭 emoji only when reasoning starts (not on every token)
        if source not in self.current_reasoning_active:
            self.current_reasoning_active[source] = False
        
        if not self.current_reasoning_active[source]:
            self.current_reasoning_active[source] = True
            content = f"> 💭 {text}"
        else:
            content = text
        
        return StreamOutput(
            content=content,
            source=source,
            event_type="reasoning"
        )
    
    def on_lifecycle(self, event: LifecycleEvent) -> StreamOutput | None:
        """Return lifecycle event as StreamOutput"""
        if event.lifecycle_type == "init":
            content = "\n\n> :orange[🔄 **Event loop initialized**]\n\n"
        elif event.lifecycle_type == "start":
            content = "\n\n> :orange[▶️ **Event loop cycle starting**]\n\n"
        elif event.lifecycle_type == "complete":
            content = "\n\n> :green[✅ **Cycle completed**]\n\n"
        elif event.lifecycle_type == "force_stop":
            reason = event.force_stop_reason or "unknown reason"
            content = f"\n\n> :red[🛑 **Event loop force-stopped**: {reason}]\n\n"
        else:
            return None
        
        return StreamOutput(
            content=content,
            source=None,  # Lifecycle events are always from main agent
            event_type="lifecycle"
        )
    
    def on_multiagent_node_start(self, event: MultiAgentNodeStartEvent) -> StreamOutput:
        """Return multi-agent node start as StreamOutput"""
        return StreamOutput(
            content=f"\n\n:blue[🔄 **Node [{event.node_id}]** ({event.node_type}) starting]\n\n",
            source=None,  # Multi-agent events are at main level
            event_type="multiagent_node_start"
        )
    
    def on_multiagent_node_stream(self, event: MultiAgentNodeStreamEvent) -> list[Any]:
        """Process multi-agent node stream (recursively process inner event)"""
        # Recursively process inner event
        return self.process(event.inner_event)
    
    def on_multiagent_node_stop(self, event: MultiAgentNodeStopEvent) -> StreamOutput:
        """Return multi-agent node stop as StreamOutput"""
        node_result = event.node_result
        if hasattr(node_result, 'execution_time'):
            exec_time = node_result.execution_time
            content = f"\n\n:green[✅ **Node [{event.node_id}]** completed in {exec_time} ms]\n\n"
        else:
            content = f"\n\n:green[✅ **Node [{event.node_id}]** completed]\n\n"
        
        return StreamOutput(
            content=content,
            source=None,  # Multi-agent events are at main level
            event_type="multiagent_node_stop"
        )
    
    def on_multiagent_handoff(self, event: MultiAgentHandoffEvent) -> StreamOutput:
        """Return multi-agent handoff as StreamOutput"""
        from_nodes = ", ".join(event.from_node_ids)
        to_nodes = ", ".join(event.to_node_ids)
        content = f"\n\n:purple[🔀 **Handoff**: {from_nodes} → {to_nodes}]\n\n"
        if event.message:
            content += f":purple[   Message: {event.message}]\n\n"
        
        return StreamOutput(
            content=content,
            source=None,  # Multi-agent events are at main level
            event_type="multiagent_handoff"
        )
    
    def on_multiagent_result(self, event: MultiAgentResultEvent) -> StreamOutput:
        """Return multi-agent final result as StreamOutput"""
        result = event.result
        if hasattr(result, 'status'):
            content = f"\n\n:green[📊 **Multi-agent completed**: {result.status}]\n\n"
        else:
            content = "\n\n:green[📊 **Multi-agent completed**]\n\n"
        
        return StreamOutput(
            content=content,
            source=None,  # Multi-agent events are at main level
            event_type="multiagent_result"
        )
    
    def reset(self):
        """Reset renderer state"""
        super().reset()
        self.displayed_tool_calls.clear()
        self.current_reasoning_active.clear()


# Backward compatibility alias
StreamlitAdapter = StreamlitStreamRenderer

