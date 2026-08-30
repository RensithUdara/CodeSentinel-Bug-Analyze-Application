"""
Project management service.
"""
import os
from typing import List, Optional
from app.core.models.project import Project
from app.database.repository import Repository


class ProjectService:
    def __init__(self, db_manager):
        self.db = db_manager
        self.repo = Repository(db_manager)

    def register_project(self, path: str, name: str = "", description: str = "") -> int:
        if not os.path.isdir(path):
            raise ValueError(f"Invalid directory: {path}")

        project_name = name or os.path.basename(path)
        existing = self.repo.get_project_by_path(path)
        if existing:
            return existing.project_id

        project = Project(
            name=project_name,
            path=path,
            description=description,
            primary_language="Python",
        )
        return self.repo.add_project(project)

    def get_all_projects(self) -> List[Project]:
        return self.repo.get_all_projects()

    def get_project(self, project_id: int) -> Optional[Project]:
        projects = self.repo.get_all_projects()
        for p in projects:
            if p.project_id == project_id:
                return p
        return None
