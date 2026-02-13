"""Web search tool configuration and helpers for subagents."""

from __future__ import annotations

from typing import Any

# Anthropic server-side web search tool definitions.
# These are passed via the ``tools`` parameter of ``messages.create``.

SAP_WEB_SEARCH_TOOL: dict[str, Any] = {
    "type": "web_search_20250305",
    "name": "web_search",
    "max_uses": 3,
}

GENERAL_WEB_SEARCH_TOOL: dict[str, Any] = {
    "type": "web_search_20250305",
    "name": "web_search",
    "max_uses": 2,
}


def extract_text_from_response(response: Any) -> str:
    """Extract the final text content from a response that may include tool-use blocks.

    The Anthropic Messages API returns ``content`` as a list of typed blocks.
    When server-side tools (like ``web_search``) are used, the response will
    contain a mix of ``web_search_tool_result`` and ``text`` blocks.  This
    helper concatenates all ``text`` blocks into a single string.
    """
    parts: list[str] = []
    for block in response.content:
        if getattr(block, "type", None) == "text":
            parts.append(block.text)
    return "\n".join(parts)
