from __future__ import annotations

from eam_council.council import llm
from eam_council.council.runtime_config import DEFAULT_TOKENS_PER_MINUTE, load_runtime_config


def test_runtime_config_tpm_defaults(monkeypatch):
    monkeypatch.delenv("EAM_TOKENS_PER_MINUTE", raising=False)
    monkeypatch.delenv("EAM_ENABLE_TPM_THROTTLE", raising=False)
    cfg = load_runtime_config()
    assert cfg.tokens_per_minute == DEFAULT_TOKENS_PER_MINUTE
    assert cfg.enable_tpm_throttle is True


def test_estimate_tokens_includes_prompt_and_max_tokens():
    kwargs = {
        "system": "sys" * 200,
        "messages": [{"role": "user", "content": "hello" * 100}],
        "max_tokens": 123,
    }
    est = llm._estimate_tokens(kwargs)
    assert est >= 123
    assert est > 200
