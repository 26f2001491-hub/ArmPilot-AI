from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BenchmarkCreate(BaseModel):
    model_name: str = Field(min_length=1, max_length=255)
    runtime: str = Field(default="onnxruntime", max_length=64)
    quantization: str | None = Field(default=None, max_length=64)
    prompt_tokens: int = Field(default=0, ge=0)
    generated_tokens: int = Field(default=0, ge=0)
    latency_ms: float | None = Field(default=None, ge=0)
    throughput_tps: float | None = Field(default=None, ge=0)
    ttft_ms: float | None = Field(default=None, ge=0)
    memory_mb: float | None = Field(default=None, ge=0)
    cpu_percent: float | None = Field(default=None, ge=0, le=100)
    notes: str | None = None


class BenchmarkRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    model_name: str
    runtime: str
    quantization: str | None
    prompt_tokens: int
    generated_tokens: int
    latency_ms: float | None
    throughput_tps: float | None
    ttft_ms: float | None
    memory_mb: float | None
    cpu_percent: float | None
    status: str
    notes: str | None
    created_at: datetime
