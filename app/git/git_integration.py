"""
Git integration using GitPython.
"""
import os
from typing import List, Optional, Dict


class GitIntegration:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.repo = None

    def is_git_repo(self) -> bool:
        try:
            import git
            self.repo = git.Repo(self.repo_path)
            return True
        except Exception:
            return False

    def get_commits(self, limit: int = 10) -> List[Dict]:
        if not self.repo:
            return []
        commits = []
        for commit in list(self.repo.iter_commits())[:limit]:
            commits.append({
                'hash': commit.hexsha,
                'author': str(commit.author),
                'date': commit.committed_datetime.isoformat(),
                'message': commit.message.strip()
            })
        return commits

    def get_current_commit(self) -> Optional[str]:
        if not self.repo:
            return None
        return self.repo.head.commit.hexsha

    def get_changed_files(self, old_commit: str = None, new_commit: str = None) -> List[str]:
        """Return list of file paths changed between two commits."""
        if not self.repo:
            return []
        try:
            if old_commit and new_commit:
                diff = self.repo.git.diff(old_commit, new_commit, '--name-only').split('\n')
                return [f for f in diff if f.endswith('.py')]
            else:
                # Get changed files in working directory
                changed = [item.a_path for item in self.repo.index.diff(None)]
                changed.extend(self.repo.untracked_files)
                return [f for f in changed if f.endswith('.py')]
        except Exception:
            return []

    def get_branch(self) -> str:
        if not self.repo:
            return ""
        try:
            return self.repo.active_branch.name
        except Exception:
            return "DETACHED"
