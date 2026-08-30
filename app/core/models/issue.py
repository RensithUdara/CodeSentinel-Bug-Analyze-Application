from dataclasses import dataclass
from typing import Optional


@dataclass
class Issue:
    type: str
    category: str
    severity: str
    file_path: str
    line: Optional[int] = None
    message: str = ""
    recommendation: str = ""
    metric_value: Optional[float] = None
    threshold: Optional[float] = None
    status: str = "Open"
    issue_id: Optional[int] = None
    analysis_id: Optional[int] = None
    file_id: Optional[int] = None
