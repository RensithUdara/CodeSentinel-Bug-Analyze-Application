from app.database.db_manager import DatabaseManager
from app.core.models.project import Project
from app.core.models.analysis_run import AnalysisRun
from app.core.models.file import File
from app.core.models.issue import Issue
from app.core.models.duplicate import Duplicate
from typing import List, Optional


class Repository:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def add_project(self, project: Project) -> int:
        self.db.connect()
        cur = self.db.conn.cursor()
        cur.execute("""
            INSERT OR IGNORE INTO projects (name, path, description, primary_language, git_repo)
            VALUES (?, ?, ?, ?, ?)
        """, (project.name, project.path, project.description, project.primary_language, project.git_repo))
        self.db.conn.commit()
        if cur.lastrowid:
            project_id = cur.lastrowid
        else:
            cur.execute("SELECT project_id FROM projects WHERE path = ?", (project.path,))
            project_id = cur.fetchone()[0]
        self.db.close()
        return project_id

    def get_project_by_path(self, path: str) -> Optional[Project]:
        row = self.db.fetchone("SELECT * FROM projects WHERE path = ?", (path,))
        if row:
            return Project(
                project_id=row['project_id'],
                name=row['name'],
                path=row['path'],
                description=row['description'] or "",
                primary_language=row['primary_language'] or "",
                git_repo=row['git_repo'] or "",
            )
        return None

    def get_project_by_id(self, project_id: int) -> Optional[Project]:
        row = self.db.fetchone("SELECT * FROM projects WHERE project_id = ?", (project_id,))
        if row:
            return Project(
                project_id=row['project_id'],
                name=row['name'],
                path=row['path'],
                description=row['description'] or "",
                primary_language=row['primary_language'] or "",
                git_repo=row['git_repo'] or "",
            )
        return None

    def get_all_projects(self) -> List[Project]:
        rows = self.db.fetchall("SELECT * FROM projects ORDER BY created_at DESC")
        return [
            Project(
                project_id=r['project_id'],
                name=r['name'],
                path=r['path'],
                description=r['description'] or "",
                primary_language=r['primary_language'] or "",
                git_repo=r['git_repo'] or "",
            )
            for r in rows
        ]

    def add_analysis_run(self, run: AnalysisRun) -> int:
        self.db.connect()
        cur = self.db.conn.cursor()
        cur.execute("""
            INSERT INTO analysis_runs (project_id, commit_hash, quality_score, security_score,
                complexity_score, maintainability_score, duplication_score,
                architecture_score, technical_debt)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (run.project_id, run.commit_hash, run.quality_score, run.security_score,
              run.complexity_score, run.maintainability_score, run.duplication_score,
              run.architecture_score, run.technical_debt))
        analysis_id = cur.lastrowid
        self.db.conn.commit()
        self.db.close()
        return analysis_id

    def get_latest_analysis(self) -> Optional[AnalysisRun]:
        row = self.db.fetchone("SELECT * FROM analysis_runs ORDER BY timestamp DESC LIMIT 1")
        if row:
            return AnalysisRun(
                analysis_id=row['analysis_id'],
                project_id=row['project_id'],
                commit_hash=row['commit_hash'] or "",
                timestamp=row['timestamp'],
                quality_score=row['quality_score'] or 0,
                security_score=row['security_score'] or 0,
                complexity_score=row['complexity_score'] or 0,
                maintainability_score=row['maintainability_score'] or 0,
                duplication_score=row['duplication_score'] or 0,
                architecture_score=row['architecture_score'] or 0,
                technical_debt=row['technical_debt'] or 0,
            )
        return None

    def get_analysis_history(self, project_id: int, limit: int = 10) -> List[AnalysisRun]:
        rows = self.db.fetchall(
            "SELECT * FROM analysis_runs WHERE project_id = ? ORDER BY timestamp DESC LIMIT ?",
            (project_id, limit)
        )
        return [
            AnalysisRun(
                analysis_id=r['analysis_id'],
                project_id=r['project_id'],
                commit_hash=r['commit_hash'] or "",
                timestamp=r['timestamp'],
                quality_score=r['quality_score'] or 0,
                security_score=r['security_score'] or 0,
                complexity_score=r['complexity_score'] or 0,
                maintainability_score=r['maintainability_score'] or 0,
                duplication_score=r['duplication_score'] or 0,
                architecture_score=r['architecture_score'] or 0,
                technical_debt=r['technical_debt'] or 0,
            )
            for r in rows
        ]

    def add_file(self, file: File) -> int:
        self.db.connect()
        cur = self.db.conn.cursor()
        cur.execute("""
            INSERT INTO files (analysis_id, path, language, loc, comment_lines,
                function_count, class_count, complexity, maintainability)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (file.analysis_id, file.path, file.language, file.loc, file.comment_lines,
              file.function_count, file.class_count, file.complexity, file.maintainability))
        file_id = cur.lastrowid
        self.db.conn.commit()
        self.db.close()
        return file_id

    def get_files_for_analysis(self, analysis_id: int) -> List[File]:
        rows = self.db.fetchall("SELECT * FROM files WHERE analysis_id = ?", (analysis_id,))
        return [
            File(
                file_id=r['file_id'],
                analysis_id=r['analysis_id'],
                path=r['path'],
                language=r['language'] or "",
                loc=r['loc'] or 0,
                comment_lines=r['comment_lines'] or 0,
                function_count=r['function_count'] or 0,
                class_count=r['class_count'] or 0,
                complexity=r['complexity'] or 0,
                maintainability=r['maintainability'] or 0,
            )
            for r in rows
        ]

    def add_issue(self, issue: Issue) -> int:
        self.db.connect()
        cur = self.db.conn.cursor()
        cur.execute("""
            INSERT INTO issues (analysis_id, file_id, type, category, severity,
                line_number, message, metric_value, threshold, recommendation, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (issue.analysis_id, issue.file_id, issue.type, issue.category,
              issue.severity, issue.line, issue.message, issue.metric_value,
              issue.threshold, issue.recommendation, issue.status))
        issue_id = cur.lastrowid
        self.db.conn.commit()
        self.db.close()
        return issue_id

    def get_issues_for_analysis(self, analysis_id: int) -> List[Issue]:
        rows = self.db.fetchall("""
            SELECT i.*, f.path as file_path
            FROM issues i
            LEFT JOIN files f ON i.file_id = f.file_id
            WHERE i.analysis_id = ?
        """, (analysis_id,))
        return [
            Issue(
                issue_id=r['issue_id'],
                analysis_id=r['analysis_id'],
                file_id=r['file_id'],
                type=r['type'],
                category=r['category'],
                severity=r['severity'],
                file_path=r['file_path'] if r['file_path'] is not None else '',
                line=r['line_number'],
                message=r['message'] or "",
                recommendation=r['recommendation'] or "",
                metric_value=r['metric_value'],
                threshold=r['threshold'],
                status=r['status'] or "Open",
            )
            for r in rows
        ]

    def get_recent_issues(self, analysis_id: int, limit: int = 10) -> List[Issue]:
        rows = self.db.fetchall("""
            SELECT i.*, f.path as file_path
            FROM issues i
            LEFT JOIN files f ON i.file_id = f.file_id
            WHERE i.analysis_id = ?
            ORDER BY i.severity DESC
            LIMIT ?
        """, (analysis_id, limit))
        return [
            Issue(
                issue_id=r['issue_id'],
                analysis_id=r['analysis_id'],
                file_id=r['file_id'],
                type=r['type'],
                category=r['category'],
                severity=r['severity'],
                file_path=r['file_path'] if r['file_path'] is not None else '',
                line=r['line_number'],
                message=r['message'] or "",
                recommendation=r['recommendation'] or "",
                metric_value=r['metric_value'],
                threshold=r['threshold'],
                status=r['status'] or "Open",
            )
            for r in rows
        ]

    def get_issue_count_for_file(self, file_id: int) -> int:
        row = self.db.fetchone("SELECT COUNT(*) as cnt FROM issues WHERE file_id = ?", (file_id,))
        return row['cnt'] if row else 0

    def add_duplicate(self, dup: Duplicate) -> int:
        self.db.connect()
        cur = self.db.conn.cursor()
        cur.execute("""
            INSERT INTO duplicates (analysis_id, file_a, file_b, similarity,
                start_line_a, end_line_a, start_line_b, end_line_b)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (dup.analysis_id, dup.file_a, dup.file_b, dup.similarity,
              dup.start_line_a, dup.end_line_a, dup.start_line_b, dup.end_line_b))
        dup_id = cur.lastrowid
        self.db.conn.commit()
        self.db.close()
        return dup_id

    def get_duplicates_for_analysis(self, analysis_id: int) -> List[Duplicate]:
        rows = self.db.fetchall("SELECT * FROM duplicates WHERE analysis_id = ?", (analysis_id,))
        return [
            Duplicate(
                duplicate_id=r['duplicate_id'],
                analysis_id=r['analysis_id'],
                file_a=r['file_a'],
                file_b=r['file_b'],
                similarity=r['similarity'],
                start_line_a=r['start_line_a'],
                end_line_a=r['end_line_a'],
                start_line_b=r['start_line_b'],
                end_line_b=r['end_line_b'],
            )
            for r in rows
        ]
