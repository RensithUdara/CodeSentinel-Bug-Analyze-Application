from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class Project:
    name: str
    path: str
    description: str = ""
    primary_language: str = ""
    git_repo: str = ""
    project_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
