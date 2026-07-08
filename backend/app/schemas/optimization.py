from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class OptimizationProfileCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    thread_count: int = Field(default=4, ge=1, le=256)
    batch_size: int = Field(default=1, ge=1, le=1024)
    quantization: str | None = Field(default=None, max_length=64)
    kv_cache_enabled: bool = True
    cpu_affinity: str | None = Field(default=None, max_length=255)


class OptimizationProfileUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    thread_count: int | None = Field(default=None, ge=1, le=256)
    batch_size: int | None = Field(default=None, ge=1, le=1024)
    quantization: str | None = Field(default=None, max_length=64)
    kv_cache_enabled: bool | None = None
    cpu_affinity: str | None = Field(default=None, max_length=255)
    is_active: bool | None = None


class OptimizationProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    name: str
    description: str | None
    thread_count: int
    batch_size: int
    quantization: str | None
    kv_cache_enabled: bool
    cpu_affinity: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
