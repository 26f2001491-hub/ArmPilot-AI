from pydantic import BaseModel


class Recommendation(BaseModel):
    category: str
    severity: str  # info | warning | critical
    title: str
    detail: str
    suggested_action: str


class RecommendationReport(BaseModel):
    benchmark_id: int
    model_name: str
    score: float  # 0-100 overall efficiency score
    recommendations: list[Recommendation]
