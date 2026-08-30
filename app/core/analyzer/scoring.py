"""
Overall quality scoring engine.
"""
from typing import Dict


class ScoringEngine:
    def __init__(self, weights: Dict[str, float] = None):
        self.weights = weights or {
            "maintainability": 0.25,
            "complexity": 0.20,
            "security": 0.20,
            "duplication": 0.15,
            "smells": 0.10,
            "architecture": 0.10,
        }

    def compute_score(self, metrics: Dict[str, float]) -> float:
        total = 0.0
        for key, val in metrics.items():
            if key in self.weights:
                total += val * self.weights[key]
        return round(total, 1)

    def grade(self, score: float) -> str:
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
