"""Terminal stream renderer for colored output using colorama"""

import json
from typing import Any

try:
    from colorama import Fore, Style, init as colorama_init
    colorama_init(autoreset=True)
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False
    # Fallback if colorama is not available
    class Fore:
        YELLOW = ""
        GREEN = ""
        RED = ""
        CYAN = ""
        MAGENTA = ""
        BLUE = ""
    class Style:
        RESET_ALL = ""
        BRIGHT = ""

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


class TerminalStreamRenderer(BaseStreamRenderer):
    """Stream renderer for terminal output with colors using colorama"""
    
    # Sentinel value to force header on next text event
    _TEXT_SOURCE_RESET = object()
    
    def __init__(self, parser=None, use_colors: bool = True, debug: bool = False):
        super().__init__(parser, debug=debug)
        self.tool_call_counter = 0
        self.use_colors = use_colors and COLORAMA_AVAILABLE
        self.displayed_tool_calls = {}  # Map tool_id -> tool_call_number (to track which tool calls we've seen)
        self.current_text_source: str | None | object = None  # Track current text source to show prefix only on change
        self.current_reasoning_active: bool = False  # Track if reasoning is currently active to show different color only on start
    
    def _colorize(self, text: str, *colors) -> str:
        """Apply color/style to text if colors are enabled
        
        Args:
            text: Text to colorize
            *colors: One or more colorama Fore/Style constants
        """
        if self.use_colors and colors:
            color_codes = "".join(str(c) for c in colors)
            return f"{color_codes}{text}{Style.RESET_ALL}"
        return text
    
    def _print_status(self, icon: str, message: str, color=None) -> None:
        """Print a status message with optional color"""
        if color and self.use_colors:
            print(self._colorize(f"{icon} {message}", color))
        else:
            print(f"{icon} {message}")
    
    def on_text(self, event: TextEvent) -> None:
        """Print text chunk"""
        # If reasoning was active, add newlines before text
        if self.current_reasoning_active:
            print("\n\n", end="", flush=True)
        # Reset reasoning state when text event occurs
        self.current_reasoning_active = False
        # Add source prefix only when source changes (not on every token)
        previous_source = self.current_text_source
        if event.source != previous_source:
            self.current_text_source = event.source
            if event.source:
                # Sub-agent text starting
                print(f"\n{self._colorize(f'[Sub-Agent ⚡ {event.source}] ', Fore.YELLOW)}", end="", flush=True)
            elif previous_source is self._TEXT_SOURCE_RESET:
                # Switching back to main agent after tool event - add newline for readability
                print("\n", end="", flush=True)
        
        # Sub-agent text is printed in yellow to distinguish from main agent
        if event.source:
            print(self._colorize(event.data, Fore.MAGENTA), end="", flush=True)
        else:
            print(event.data, end="", flush=True)
        return None  # Terminal output doesn't return values
    
    def on_tool_use(self, event: CurrentToolUseEvent) -> None:
        """Print tool call with formatting - shows accumulated input as it streams"""
        # Reset text source so next text event will show header again
        self.current_text_source = self._TEXT_SOURCE_RESET
        # If reasoning was active, add newlines before tool use
        if self.current_reasoning_active:
            print("\n\n", end="", flush=True)
        # Reset reasoning state when tool use occurs
        self.current_reasoning_active = False
        
        tool_key = event.tool_id or event.tool_name
        is_new_tool_call = tool_key and tool_key not in self.displayed_tool_calls
        
        if is_new_tool_call:
            self.tool_call_counter += 1
            self.displayed_tool_calls[tool_key] = self.tool_call_counter
        
        tool_number = self.displayed_tool_calls.get(tool_key, self.tool_call_counter)
        separator = "─" * 60
        
        if is_new_tool_call:
            # First time seeing this tool - show header
            header = f"Tool #{tool_number}: {event.tool_name}"
            if event.source:
                header = f"[Sub-Agent: {event.source}] {header}"
            print(f"\n{separator}")
            print(self._colorize(header, Style.BRIGHT, Fore.BLUE))
        
        if event.tool_input:
            print(self._colorize(json.dumps(event.tool_input, indent=2, ensure_ascii=False), Style.BRIGHT, Fore.CYAN))

        print(f"{separator}")
        return None
    
    def on_tool_result(self, event: ToolResultEvent) -> None:
        """Print tool result with formatting"""
        # Reset text source so next text event will show header again
        self.current_text_source = self._TEXT_SOURCE_RESET
        # If reasoning was active, add newlines before tool result
        if self.current_reasoning_active:
            print("\n\n", end="", flush=True)
        # Reset reasoning state when tool result occurs
        self.current_reasoning_active = False
        
        separator = "─" * 60
        print(separator)
        header_parts = ["Tool Result:"]
        if event.source:
            header_parts[0] = f"[Sub-Agent: {event.source}] Tool Result:"
        if event.tool_id:
            header_parts.append(f"[toolUseId] {event.tool_id}")
        if event.metadata and event.metadata.get("status"):
            header_parts.append(f"[status] {event.metadata['status']}")
        header_parts.append(f"[content length] {len(event.data)} characters")
        
        header = "\n".join(header_parts)
        print(self._colorize(header, Style.BRIGHT, Fore.GREEN))
        print(separator)
        
        if event.data:
            if len(event.data) > 1000:
                preview = event.data[:1000] + "\n...(생략)"
                print(preview)
            else:
                print(event.data)
        print(f"{separator}\n")
        return None
    
    def on_tool_stream(self, event: ToolStreamEvent) -> None:
        """Print tool stream event"""
        # Reset text source so next text event will show header again
        self.current_text_source = self._TEXT_SOURCE_RESET
        # If reasoning was active, add newlines before tool stream
        if self.current_reasoning_active:
            print("\n\n", end="", flush=True)
        # Reset reasoning state when tool stream occurs
        self.current_reasoning_active = False
        
        tool_use_dict = event.tool_use if isinstance(event.tool_use, dict) else {}
        tool_name = tool_use_dict.get("name", "unknown")
        tool_id = tool_use_dict.get("toolUseId")
        tool_input = tool_use_dict.get("input", {})
        
        separator = "─" * 60
        print(f"\n{separator}")
        header = f"Tool Stream: {tool_name}"
        if tool_id:
            header += f" [toolUseId: {tool_id}]"
        print(self._colorize(header, Style.BRIGHT, Fore.MAGENTA))
        print(separator)
        # Show tool_input if available
        if tool_input:
            print(self._colorize(json.dumps(tool_input, indent=2, ensure_ascii=False), Style.BRIGHT, Fore.CYAN))
            print(separator)
        # Show stream data
        if event.data:
            if isinstance(event.data, str):
                print(self._colorize(event.data, Style.BRIGHT, Fore.CYAN))
            else:
                print(self._colorize(json.dumps(event.data, indent=2, ensure_ascii=False), Style.BRIGHT, Fore.CYAN))
        print(f"{separator}\n")
        return None
    
    def on_reasoning(self, event: ReasoningEvent) -> None:
        """Print reasoning text with different color on start (only on first chunk to avoid inserting chars between tokens)"""
        if not self.current_reasoning_active:
            self.current_reasoning_active = True
            print(self._colorize(f"💭 {event.data}", Fore.MAGENTA), end="", flush=True)
        else:
            print(self._colorize(event.data, Fore.MAGENTA), end="", flush=True)
        return None
    
    def on_lifecycle(self, event: LifecycleEvent) -> None:
        """Print lifecycle event"""
        if event.lifecycle_type == "init":
            self._print_status("🔄", "Event loop initialized", Fore.YELLOW)
        elif event.lifecycle_type == "start":
            self._print_status("▶️", "Event loop cycle starting", Fore.YELLOW)
        elif event.lifecycle_type == "complete":
            self._print_status("✅", "Cycle completed", Fore.GREEN)
        elif event.lifecycle_type == "force_stop":
            reason = event.force_stop_reason or "unknown reason"
            self._print_status("🛑", f"Event loop force-stopped: {reason}", Fore.RED)
        return None
    
    def on_multiagent_node_start(self, event: MultiAgentNodeStartEvent) -> None:
        """Print multi-agent node start"""
        message = f"Node [{event.node_id}] ({event.node_type}) starting"
        print(f"\n{self._colorize(f'🔄 {message}', Fore.CYAN)}")
        return None
    
    def on_multiagent_node_stream(self, event: MultiAgentNodeStreamEvent) -> list[Any]:
        """Process multi-agent node stream (recursively process inner event)"""
        # Recursively process inner event
        return self.process(event.inner_event)
    
    def on_multiagent_node_stop(self, event: MultiAgentNodeStopEvent) -> None:
        """Print multi-agent node stop"""
        node_result = event.node_result
        if hasattr(node_result, 'execution_time'):
            exec_time = node_result.execution_time
            message = f"Node [{event.node_id}] completed in {exec_time} ms"
        else:
            message = f"Node [{event.node_id}] completed"
        print(f"\n{self._colorize(f'✅ {message}', Fore.GREEN)}")
        return None
    
    def on_multiagent_handoff(self, event: MultiAgentHandoffEvent) -> None:
        """Print multi-agent handoff"""
        from_nodes = ", ".join(event.from_node_ids)
        to_nodes = ", ".join(event.to_node_ids)
        message = f"Handoff: {from_nodes} → {to_nodes}"
        print(f"\n{self._colorize(f'🔀 {message}', Fore.MAGENTA)}")
        if event.message:
            print(self._colorize(f"   Message: {event.message}", Fore.MAGENTA))
        return None
    
    def on_multiagent_result(self, event: MultiAgentResultEvent) -> None:
        """Print multi-agent final result"""
        result = event.result
        if hasattr(result, 'status'):
            message = f"Multi-agent completed: {result.status}"
        else:
            message = "Multi-agent completed"
        print(f"\n{self._colorize(f'📊 {message}', Fore.GREEN)}")
        return None
    
    def reset(self):
        """Reset renderer state"""
        super().reset()
        self.tool_call_counter = 0
        self.displayed_tool_calls.clear()
        self.current_text_source = None
        self.current_reasoning_active = False


# Backward compatibility alias
TerminalAdapter = TerminalStreamRenderer

