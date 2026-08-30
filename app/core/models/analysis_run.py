from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class AnalysisRun:
    project_id: int
    analysis_id: Optional[int] = None
    commit_hash: str = ""
    timestamp: Optional[datetime] = None
    quality_score: float = 0.0
    security_score: float = 0.0
    complexity_score: float = 0.0
    maintainability_score: float = 0.0
    duplication_score: float = 0.0
    architecture_score: float = 0.0
    technical_debt: float = 0.0
