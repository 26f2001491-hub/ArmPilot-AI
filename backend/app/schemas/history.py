from datetime import datetime

from pydantic import BaseModel, ConfigDict


class HistoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    action: str
    resource_type: str | None
    resource_id: str | None
    detail: str | None
    created_at: datetime
