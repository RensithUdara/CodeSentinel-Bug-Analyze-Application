"""
Maintainability index calculation.
"""
import math
from typing import Dict


class MaintainabilityCalculator:
    @staticmethod
    def calculate(complexity: float, loc: int, comment_ratio: float = 0.1) -> float:
        if loc == 0:
            return 100.0
        mi = 100 * (
            1
            - min(complexity / 100, 1) * 0.5
            - min(loc / 1000, 1) * 0.3
            - (1 - comment_ratio) * 0.2
        )
        return max(0.0, min(100.0, round(mi, 1)))

    @staticmethod
    def classify(score: float) -> str:
        if score >= 85:
            return "Excellent"
        elif score >= 70:
            return "Good"
        elif score >= 50:
            return "Moderate"
        elif score >= 30:
            return "Poor"
        else:
            return "Critical"
