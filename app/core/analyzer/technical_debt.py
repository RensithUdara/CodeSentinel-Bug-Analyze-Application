"""
Technical debt estimation based on issues and complexity.
"""
from typing import List, Dict
from app.core.models.issue import Issue


class TechnicalDebtEstimator:
    @staticmethod
    def estimate(issues: List[Issue], complexity_score: float) -> float:
        hours = 0.0
        severity_map = {"Critical": 2.0, "High": 1.0, "Medium": 0.5, "Low": 0.2}
        for issue in issues:
            hours += severity_map.get(issue.severity, 0.2)
        if complexity_score > 80:
            hours *= 1.2
        elif complexity_score > 60:
            hours *= 1.1
        return round(hours, 1)

    @staticmethod
    def estimate_by_category(issues: List[Issue]) -> Dict[str, float]:
        severity_map = {"Critical": 2.0, "High": 1.0, "Medium": 0.5, "Low": 0.2}
        categories: Dict[str, float] = {}
        for issue in issues:
            hours = severity_map.get(issue.severity, 0.2)
            cat = issue.category
            categories[cat] = categories.get(cat, 0) + hours
        return {k: round(v, 1) for k, v in categories.items()}
