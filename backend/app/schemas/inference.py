from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class InferenceCreate(BaseModel):
    model_name: str = Field(min_length=1, max_length=255)
    prompt: str = Field(min_length=1)
    runtime: str = Field(default="onnxruntime", max_length=64)
    max_tokens: int = Field(default=128, ge=1, le=8192)


class InferenceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    model_name: str
    runtime: str
    prompt: str
    max_tokens: int
    status: str
    output: str | None
    error: str | None
    prompt_tokens: int
    generated_tokens: int
    latency_ms: int | None
    created_at: datetime
