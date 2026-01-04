"""Core parser for Strands SDK events - no output logic, only parsing"""

import json
from typing import Any

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


class StrandsEventParser:
    """Core parser for Strands SDK events - no output logic, only parsing"""
    
    def __init__(self):
        self.displayed_tool_calls = set()  # Track displayed tool calls by toolUseId
        self.processed_event_ids = set()  # Track processed events by event_loop_cycle_id
        self.processed_data_events = set()  # Track processed data events
        self.processed_subagent_data_events = set()  # Track processed sub-agent data events
        self.tool_use_mapping = {}  # Map toolUseId -> tool_name for tool results
        self.last_tool_input = {}  # Map toolUseId -> last seen input (to detect changes for streaming)
        self.active_subagent_tools = set()  # Track active sub-agent skill tools by toolUseId
    
    def extract_tool_use_from_event(self, event: dict) -> dict | None:
        """Extract toolUse information from event"""
        tool_use = None
        
        # Check top-level toolUse
        if "toolUse" in event:
            tool_use = event["toolUse"]
        # Check current_tool_use (Strands SDK pattern)
        elif "current_tool_use" in event:
            tool_use = event["current_tool_use"]
        # Check message -> content -> toolUse structure
        elif "message" in event:
            message = event["message"]
            if isinstance(message, dict):
                content_list = message.get("content", [])
                if isinstance(content_list, list):
                    for content in content_list:
                        if isinstance(content, dict) and "toolUse" in content:
                            tool_use = content["toolUse"]
                            break
        
        return tool_use if isinstance(tool_use, dict) else None
    
    def extract_tool_result_from_event(self, event: dict) -> dict | None:
        """Extract toolResult information from event"""
        if "message" not in event:
            return None
        
        message = event["message"]
        if not isinstance(message, dict):
            return None
        
        content_list = message.get("content", [])
        if not isinstance(content_list, list):
            return None
        
        for content in content_list:
            if isinstance(content, dict) and "toolResult" in content:
                tool_result = content.get("toolResult", {})
                if isinstance(tool_result, dict):
                    return tool_result
        
        return None
    
    def extract_result_content(self, tool_result: dict) -> str:
        """Extract text content from tool result"""
        if not isinstance(tool_result, dict):
            return str(tool_result)
        
        # Check for content field
        if "content" in tool_result:
            content = tool_result["content"]
            if isinstance(content, list) and len(content) > 0:
                first_item = content[0]
                if isinstance(first_item, dict) and "text" in first_item:
                    return first_item["text"]
                return str(first_item)
            elif isinstance(content, str):
                return content
            return str(content)
        
        # Check for text field
        if "text" in tool_result:
            return tool_result["text"]
        
        # Return JSON string for other dict structures
        return json.dumps(tool_result, indent=2, ensure_ascii=False)
    
    def _emit_tool_use_event(
        self,
        tool_use: dict,
        source: str | None,
        parsed_events: list[BaseEvent],
    ) -> None:
        """Helper method to emit tool use events (extracted to reduce duplication)
        
        Args:
            tool_use: Tool use dictionary from event
            source: Sub-agent skill_name or None for main agent
            parsed_events: List to append events to
        """
        tool_use_id = tool_use.get("toolUseId", "")
        tool_name = tool_use.get("name", "unknown")
        # SDK provides accumulated input, so we get the current accumulated value
        tool_input = tool_use.get("input", {}) if isinstance(tool_use.get("input"), dict) else {}
        
        # Store mapping for tool results
        if tool_use_id and tool_name:
            self.tool_use_mapping[tool_use_id] = tool_name
        
        # Check if this is a new tool call or input has changed (for streaming updates)
        is_new_tool_call = tool_use_id and tool_use_id not in self.displayed_tool_calls
        input_changed = False
        
        if tool_use_id:
            # Use unique key for sub-agent: (skill_name, tool_use_id) or just tool_use_id for main agent
            tool_key = (source, tool_use_id) if source else tool_use_id
            
            # Check if input has changed since last time
            if tool_key not in self.last_tool_input:
                # First time seeing this tool
                self.last_tool_input[tool_key] = tool_input.copy() if isinstance(tool_input, dict) else tool_input
                input_changed = True
            else:
                # Compare with last seen input (SDK already accumulated it)
                last_input = self.last_tool_input[tool_key]
                if tool_input != last_input:
                    input_changed = True
                    # Update stored value
                    self.last_tool_input[tool_key] = tool_input.copy() if isinstance(tool_input, dict) else tool_input
        else:
            # No tool_use_id, always emit
            input_changed = True
        
        # Emit event for new tool calls or when input changes (for streaming updates)
        if is_new_tool_call:
            self.displayed_tool_calls.add(tool_use_id)
            parsed_events.append(
                CurrentToolUseEvent(
                    tool_name=tool_name,
                    tool_id=tool_use_id,
                    tool_input=tool_input if tool_input else None,
                    source=source,
                )
            )
        elif input_changed:
            # Emit update event when input changes (for streaming accumulation display)
            parsed_events.append(
                CurrentToolUseEvent(
                    tool_name=tool_name,
                    tool_id=tool_use_id,
                    tool_input=tool_input if tool_input else None,
                    source=source,
                )
            )
    
    def parse(self, event: dict, debug: bool = False) -> list[BaseEvent]:
        """Parse raw event into list of BaseEvent objects"""
        if not isinstance(event, dict):
            return []
        
        parsed_events: list[BaseEvent] = []
                
        # Check for multi-agent events first (by type field)
        event_type = event.get("type")
        if event_type:
            if event_type == "multiagent_node_start":
                parsed_events.append(
                    MultiAgentNodeStartEvent(
                        node_id=event.get("node_id", "unknown"),
                        node_type=event.get("node_type", "unknown"),
                    )
                )
                return parsed_events  # Multi-agent events are handled separately
            
            elif event_type == "multiagent_node_stream":
                node_id = event.get("node_id", "unknown")
                inner_event = event.get("event", {})
                parsed_events.append(
                    MultiAgentNodeStreamEvent(
                        node_id=node_id,
                        inner_event=inner_event,
                    )
                )
                # Note: Don't parse inner_event here - the renderer's on_multiagent_node_stream
                # will call process(inner_event) to handle it. Parsing here would cause
                # duplicate processing/output.
                return parsed_events
            
            elif event_type == "multiagent_node_stop":
                parsed_events.append(
                    MultiAgentNodeStopEvent(
                        node_id=event.get("node_id", "unknown"),
                        node_result=event.get("node_result"),
                    )
                )
                return parsed_events
            
            elif event_type == "multiagent_handoff":
                parsed_events.append(
                    MultiAgentHandoffEvent(
                        from_node_ids=event.get("from_node_ids", []),
                        to_node_ids=event.get("to_node_ids", []),
                        message=event.get("message"),
                    )
                )
                return parsed_events
            
            elif event_type == "multiagent_result":
                parsed_events.append(
                    MultiAgentResultEvent(
                        result=event.get("result"),
                    )
                )
                return parsed_events
        
        # Check for lifecycle events
        if event.get("init_event_loop", False):
            parsed_events.append(
                LifecycleEvent(
                    lifecycle_type="init",
                    message=event.get("message"),
                )
            )
        
        if event.get("start_event_loop", False):
            parsed_events.append(
                LifecycleEvent(
                    lifecycle_type="start",
                    message=event.get("message"),
                )
            )
        
        if event.get("complete", False):
            parsed_events.append(
                LifecycleEvent(
                    lifecycle_type="complete",
                    result=event.get("result"),
                )
            )
        
        if event.get("force_stop", False):
            parsed_events.append(
                LifecycleEvent(
                    lifecycle_type="force_stop",
                    force_stop_reason=event.get("force_stop_reason"),
                )
            )
        
        # Check for tool_stream_event (official Strands SDK pattern)
        tool_stream = event.get("tool_stream_event", {})
        if tool_stream:
            tool_use = tool_stream.get("tool_use")
            stream_data = tool_stream.get("data")
            
            # Check if this is a sub-agent event (has event and skill_name in data)
            if isinstance(stream_data, dict) and "event" in stream_data and "skill_name" in stream_data:
                sub_event = stream_data["event"]
                skill_name = stream_data["skill_name"]
                
                # Mark this tool as active sub-agent (to suppress duplicate main agent events)
                if isinstance(tool_use, dict) and tool_use.get("toolUseId"):
                    self.active_subagent_tools.add(tool_use["toolUseId"])
                
                # Parse sub-agent events recursively with source
                sub_parsed = self._parse_subagent_event(sub_event, skill_name)
                parsed_events.extend(sub_parsed)
                return parsed_events  # Sub-agent events handled, skip main event
            else:
                # Regular tool stream event
                if tool_use or stream_data is not None:
                    parsed_events.append(
                        ToolStreamEvent(
                            tool_use=tool_use if isinstance(tool_use, dict) else {},
                            data=stream_data,
                        )
                    )
                    return parsed_events
        
        # Main agent text data
        # Note: Don't deduplicate text events by event_loop_cycle_id alone
        # because multiple text chunks can share the same cycle id during streaming
        if "data" in event:
            chunk_text = event["data"]
            if chunk_text:
                parsed_events.append(TextEvent(data=chunk_text, source=None))
        
        # Tool use (current_tool_use or toolUse)
        # Skip main agent tool events if sub-agent is active (SDK sends duplicate events)
        tool_use = self.extract_tool_use_from_event(event)
        if tool_use and not self.active_subagent_tools:
            self._emit_tool_use_event(tool_use, None, parsed_events)
        
        # Tool result
        tool_result = self.extract_tool_result_from_event(event)
        if tool_result:
            tool_use_id = tool_result.get("toolUseId", "")
            tool_name = self.tool_use_mapping.get(tool_use_id, "unknown")
            result_content = self.extract_result_content(tool_result)
            status = tool_result.get("status", "")
            
            # Check if this is the result for an active sub-agent tool
            if tool_use_id in self.active_subagent_tools:
                # Sub-agent tool completed - remove from active set
                self.active_subagent_tools.discard(tool_use_id)
                # Don't emit here - sub-agent result is handled via tool_stream_event
            else:
                # Regular main agent tool result
                parsed_events.append(
                    ToolResultEvent(
                        data=result_content,
                        tool_name=tool_name,
                        tool_id=tool_use_id,
                        metadata={"status": status} if status else None,
                        source=None,
                    )
                )
        
        # Reasoning text
        if "reasoningText" in event:
            reasoning_text = event["reasoningText"]
            if reasoning_text:
                parsed_events.append(
                    ReasoningEvent(
                        data=reasoning_text,
                        metadata={"signature": event.get("reasoning_signature", "")} if "reasoning_signature" in event else None,
                    )
                )
        
        return parsed_events
    
    def _parse_subagent_event(self, event: dict, skill_name: str) -> list[BaseEvent]:
        """Parse sub-agent event (recursive call) - uses consolidated events with source field"""
        parsed_events: list[BaseEvent] = []
        
        # Sub-agent text
        # Note: Don't deduplicate text events by event_loop_cycle_id alone
        # because multiple text chunks can share the same cycle id during streaming
        if "data" in event:
            chunk_text = event["data"]
            if chunk_text:
                parsed_events.append(
                    TextEvent(
                        data=chunk_text,
                        source=skill_name,
                    )
                )
        
        # Sub-agent tool use
        tool_use = self.extract_tool_use_from_event(event)
        if tool_use:
            self._emit_tool_use_event(tool_use, skill_name, parsed_events)
        
        # Sub-agent tool result
        tool_result = self.extract_tool_result_from_event(event)
        if tool_result:
            tool_use_id = tool_result.get("toolUseId", "")
            tool_name = self.tool_use_mapping.get(tool_use_id, "unknown")
            result_content = self.extract_result_content(tool_result)
            status = tool_result.get("status", "")
            
            parsed_events.append(
                ToolResultEvent(
                    data=result_content,
                    tool_name=tool_name,
                    tool_id=tool_use_id,
                    source=skill_name,
                    metadata={"status": status} if status else None,
                )
            )
        
        return parsed_events
    
    def reset(self):
        """Reset parser state for a new query"""
        self.displayed_tool_calls.clear()
        self.processed_event_ids.clear()
        self.processed_data_events.clear()
        self.processed_subagent_data_events.clear()
        self.tool_use_mapping.clear()
        self.last_tool_input.clear()
        self.active_subagent_tools.clear()

