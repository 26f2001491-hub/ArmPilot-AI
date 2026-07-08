from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SettingUpsert(BaseModel):
    key: str = Field(min_length=1, max_length=128)
    value: str | None = None


class SettingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    key: str
    value: str | None
    updated_at: datetime
