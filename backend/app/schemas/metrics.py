from pydantic import BaseModel


class SystemMetrics(BaseModel):
    cpu_percent: float
    cpu_count: int
    load_average: list[float]
    memory_total_mb: float
    memory_used_mb: float
    memory_percent: float
    architecture: str
    processor: str
    timestamp: str
