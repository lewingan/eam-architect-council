"""Simple run telemetry for prompt/cost diagnostics."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class StageMetric:
    stage: str
    prompt_chars: int
    completion_chars: int
    elapsed_ms: int
    tool_uses: int = 0


@dataclass
class RunTelemetry:
    started_at: float = field(default_factory=time.time)
    stages: list[StageMetric] = field(default_factory=list)

    def record(
        self,
        *,
        stage: str,
        prompt_chars: int,
        completion_chars: int,
        elapsed_ms: int,
        tool_uses: int = 0,
    ) -> None:
        self.stages.append(
            StageMetric(
                stage=stage,
                prompt_chars=prompt_chars,
                completion_chars=completion_chars,
                elapsed_ms=elapsed_ms,
                tool_uses=tool_uses,
            )
        )

    def summarize(self) -> dict:
        return {
            "duration_ms": int((time.time() - self.started_at) * 1000),
            "stage_count": len(self.stages),
            "total_prompt_chars": sum(s.prompt_chars for s in self.stages),
            "total_completion_chars": sum(s.completion_chars for s in self.stages),
            "total_tool_uses": sum(s.tool_uses for s in self.stages),
            "stages": [s.__dict__ for s in self.stages],
        }

    def write_json(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.summarize(), indent=2), encoding="utf-8")
