"""Inference runtime abstraction.

A real deployment plugs an Arm-optimized backend (llama.cpp, ONNX Runtime,
Ollama, ...) in here. Until a model backend is wired up, the default
``EchoRuntime`` provides a deterministic, clearly-labelled placeholder so the
end-to-end job lifecycle (queue -> run -> store result) is fully functional and
testable. It does *not* pretend to be a language model.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Protocol


@dataclass
class GenerationResult:
    output: str
    prompt_tokens: int
    generated_tokens: int
    latency_ms: int


def _count_tokens(text: str) -> int:
    return len([piece for piece in text.split() if piece])


class InferenceRuntime(Protocol):
    name: str

    def generate(self, prompt: str, max_tokens: int) -> GenerationResult: ...


class EchoRuntime:
    """Placeholder runtime. Returns a deterministic response and real timings."""

    name = "echo"

    def generate(self, prompt: str, max_tokens: int) -> GenerationResult:
        start = time.perf_counter()
        prompt_tokens = _count_tokens(prompt)
        words = prompt.split()
        echoed = " ".join(words[:max_tokens])
        output = (
            "[echo-runtime placeholder — no model backend configured] "
            f"Received {prompt_tokens} prompt token(s). Echo: {echoed}"
        )
        latency_ms = int((time.perf_counter() - start) * 1000)
        return GenerationResult(
            output=output,
            prompt_tokens=prompt_tokens,
            generated_tokens=_count_tokens(echoed),
            latency_ms=max(latency_ms, 1),
        )


_RUNTIMES: dict[str, InferenceRuntime] = {"echo": EchoRuntime()}


def get_runtime(name: str) -> InferenceRuntime:
    """Return a registered runtime, falling back to the echo placeholder."""
    return _RUNTIMES.get(name, _RUNTIMES["echo"])
