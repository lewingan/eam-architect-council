"""Runtime configuration for cost/performance controls."""

from __future__ import annotations

import os
from dataclasses import dataclass


DEFAULT_TOKENS_PER_MINUTE = 30_000


def _env_bool(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


@dataclass(frozen=True)
class RuntimeConfig:
    context_routing_v2: bool = True
    minimal_mode: bool = False
    conditional_search: bool = True
    search_budget: int = 3
    lead_compaction: bool = True
    lead_max_tokens: int = 4096
    lead_max_tokens_escalated: int = 8192
    enable_retry: bool = True
    retries: int = 2
    enable_tpm_throttle: bool = True
    tokens_per_minute: int = DEFAULT_TOKENS_PER_MINUTE


def load_runtime_config() -> RuntimeConfig:
    return RuntimeConfig(
        context_routing_v2=_env_bool("EAM_CONTEXT_ROUTING_V2", True),
        minimal_mode=_env_bool("EAM_MINIMAL_MODE", False),
        conditional_search=_env_bool("EAM_CONDITIONAL_SEARCH", True),
        search_budget=_env_int("EAM_SEARCH_BUDGET", 3),
        lead_compaction=_env_bool("EAM_LEAD_COMPACTION", True),
        lead_max_tokens=_env_int("EAM_LEAD_MAX_TOKENS", 4096),
        lead_max_tokens_escalated=_env_int("EAM_LEAD_MAX_TOKENS_ESCALATED", 8192),
        enable_retry=_env_bool("EAM_ENABLE_RETRY", True),
        retries=_env_int("EAM_RETRIES", 2),
        enable_tpm_throttle=_env_bool("EAM_ENABLE_TPM_THROTTLE", True),
        tokens_per_minute=_env_int("EAM_TOKENS_PER_MINUTE", DEFAULT_TOKENS_PER_MINUTE),
    )
