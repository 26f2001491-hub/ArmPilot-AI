from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ReportCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    report_type: str = Field(default="benchmark_summary", max_length=64)


class ReportRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    title: str
    report_type: str
    summary: str | None
    data: dict[str, Any]
    created_at: datetime
