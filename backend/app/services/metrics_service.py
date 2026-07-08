import os
import platform
from datetime import datetime, timezone

import psutil

from app.schemas.metrics import SystemMetrics


def _load_average() -> list[float]:
    # os.getloadavg is unavailable on Windows.
    try:
        return [round(v, 2) for v in os.getloadavg()]
    except (OSError, AttributeError):
        return [0.0, 0.0, 0.0]


def collect_system_metrics() -> SystemMetrics:
    virtual = psutil.virtual_memory()
    return SystemMetrics(
        cpu_percent=psutil.cpu_percent(interval=0.1),
        cpu_count=psutil.cpu_count(logical=True) or 0,
        load_average=_load_average(),
        memory_total_mb=round(virtual.total / (1024 * 1024), 2),
        memory_used_mb=round(virtual.used / (1024 * 1024), 2),
        memory_percent=virtual.percent,
        architecture=platform.machine(),
        processor=platform.processor() or platform.machine(),
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
