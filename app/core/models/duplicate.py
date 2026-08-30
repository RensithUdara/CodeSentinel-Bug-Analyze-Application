from dataclasses import dataclass
from typing import Optional


@dataclass
class Duplicate:
    file_a: str
    file_b: str
    similarity: float
    start_line_a: int = 0
    end_line_a: int = 0
    start_line_b: int = 0
    end_line_b: int = 0
    duplicate_id: Optional[int] = None
    analysis_id: Optional[int] = None
