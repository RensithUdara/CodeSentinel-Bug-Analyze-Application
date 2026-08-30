from dataclasses import dataclass
from typing import Optional


@dataclass
class File:
    path: str
    analysis_id: Optional[int] = None
    file_id: Optional[int] = None
    language: str = ""
    loc: int = 0
    comment_lines: int = 0
    function_count: int = 0
    class_count: int = 0
    complexity: float = 0.0
    maintainability: float = 0.0
