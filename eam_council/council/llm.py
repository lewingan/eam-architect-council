"""Anthropic call helpers with retry/backoff and optional TPM throttling."""

from __future__ import annotations

import threading
import time
from collections import deque
from typing import Any

from eam_council.council.runtime_config import load_runtime_config

_WINDOW_SECONDS = 60.0
_lock = threading.Lock()
_usage_events: deque[tuple[float, int]] = deque()


def _prune_old_events(now: float) -> None:
    cutoff = now - _WINDOW_SECONDS
    while _usage_events and _usage_events[0][0] < cutoff:
        _usage_events.popleft()


def _current_usage(now: float) -> int:
    _prune_old_events(now)
    return sum(tokens for _, tokens in _usage_events)


def _wait_for_capacity(requested_tokens: int, tokens_per_minute: int) -> None:
    if tokens_per_minute <= 0:
        return

    # Avoid deadlocking when one request is larger than the budget.
    requested_tokens = min(requested_tokens, tokens_per_minute)

    while True:
        with _lock:
            now = time.monotonic()
            in_window = _current_usage(now)
            if in_window + requested_tokens <= tokens_per_minute:
                _usage_events.append((now, requested_tokens))
                return

            oldest_ts = _usage_events[0][0] if _usage_events else now
            sleep_for = max(0.01, _WINDOW_SECONDS - (now - oldest_ts))
        time.sleep(sleep_for)


def _estimate_tokens(kwargs: dict[str, Any]) -> int:
    """Rough token estimate from request payload and completion budget."""
    text_parts: list[str] = []

    system = kwargs.get("system")
    if isinstance(system, str):
        text_parts.append(system)

    for msg in kwargs.get("messages", []) or []:
        content = msg.get("content") if isinstance(msg, dict) else None
        if isinstance(content, str):
            text_parts.append(content)

    prompt_chars = sum(len(p) for p in text_parts)
    prompt_tokens = max(1, prompt_chars // 4)
    max_tokens = int(kwargs.get("max_tokens", 0) or 0)
    return prompt_tokens + max_tokens


def create_with_retry(client: Any, *, retries: int = 2, **kwargs: Any) -> Any:
    cfg = load_runtime_config()
    if cfg.enable_tpm_throttle:
        _wait_for_capacity(
            requested_tokens=_estimate_tokens(kwargs),
            tokens_per_minute=cfg.tokens_per_minute,
        )

    last_exc: Exception | None = None
    for attempt in range(retries + 1):
        try:
            return client.messages.create(**kwargs)
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            if attempt >= retries:
                raise
            time.sleep(min(2**attempt, 4))
    if last_exc:
        raise last_exc
    raise RuntimeError("create_with_retry failed unexpectedly")
