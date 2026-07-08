"""ORM models.

Importing this package registers every model on ``Base.metadata`` so that
table creation / migrations can discover them.
"""

from app.models.benchmark import BenchmarkRun
from app.models.history import HistoryEntry
from app.models.inference import InferenceJob
from app.models.optimization import OptimizationProfile
from app.models.report import Report
from app.models.settings import UserSetting
from app.models.user import User

__all__ = [
    "BenchmarkRun",
    "HistoryEntry",
    "InferenceJob",
    "OptimizationProfile",
    "Report",
    "UserSetting",
    "User",
]
