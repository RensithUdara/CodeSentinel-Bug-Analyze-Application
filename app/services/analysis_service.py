"""
Orchestrates the full analysis pipeline.
"""
import os
import ast
from typing import List, Dict
from app.core.parsers.python_parser import PythonParser
from app.core.analyzer.complexity import ComplexityAnalyzer
from app.core.analyzer.smells import SmellDetector
from app.core.analyzer.security import SecurityAnalyzer
from app.core.analyzer.duplication import DuplicationDetector
from app.core.analyzer.maintainability import MaintainabilityCalculator
from app.core.analyzer.technical_debt import TechnicalDebtEstimator
from app.core.analyzer.scoring import ScoringEngine
from app.core.analyzer.architecture import ArchitectureAnalyzer
from app.core.models.project import Project
from app.core.models.analysis_run import AnalysisRun
from app.core.models.file import File
from app.database.repository import Repository
from app.git.git_integration import GitIntegration


class AnalysisService:
    def __init__(self, db_manager):
        self.db = db_manager
        self.repo = Repository(db_manager)

    def analyze_project(self, project_path: str, incremental: bool = False, base_commit: str = None) -> AnalysisRun:
        git_integration = GitIntegration(project_path)

        if incremental and git_integration.is_git_repo():
            current_commit = git_integration.get_current_commit()
            if base_commit and current_commit:
                changed_files = git_integration.get_changed_files(base_commit, current_commit)
                if not changed_files:
                    return self.repo.get_latest_analysis()
                all_py_files = self._find_python_files(project_path)
                python_files = [f for f in all_py_files if f in changed_files]
                if not python_files:
                    raise ValueError("No changed Python files to analyze.")
            else:
                python_files = self._find_python_files(project_path)
        else:
            python_files = self._find_python_files(project_path)

        if not python_files:
            raise ValueError("No Python files found in the specified directory.")

        parser = PythonParser()
        file_nodes = {}
        all_issues = []
        file_metrics = {}
        arch_analyzer = ArchitectureAnalyzer()

        for file_path in python_files:
            try:
                tree = parser.parse(file_path)
                file_nodes[file_path] = tree
                metrics = parser.extract_metrics(tree)
                complexity = ComplexityAnalyzer.calculate_cyclomatic(tree)
                nesting = ComplexityAnalyzer.calculate_nesting_depth(tree)
                cognitive = ComplexityAnalyzer.calculate_cognitive(tree)

                arch_analyzer.analyze_file(file_path, tree)

                smells = SmellDetector().detect(tree, file_path)
                all_issues.extend(smells)

                security = SecurityAnalyzer().analyze(tree, file_path)
                all_issues.extend(security)

                file_metrics[file_path] = {
                    "loc": self._count_loc(file_path),
                    "complexity": complexity,
                    "nesting": nesting,
                    "cognitive": cognitive,
                    "functions": metrics.get("function_count", 0),
                    "classes": metrics.get("class_count", 0),
                    "imports": metrics.get("import_count", 0),
                }
            except Exception as e:
                all_issues.append(Issue(
                    type="Parse Error",
                    category="Parser Failure",
                    severity="Low",
                    file_path=file_path,
                    message=f"Failed to parse: {str(e)}",
                    recommendation="Check file syntax.",
                ))
                continue

        dup_detector = DuplicationDetector()
        duplicates = dup_detector.detect(file_nodes)

        maintainability_scores = {}
        for fpath, met in file_metrics.items():
            mi = MaintainabilityCalculator.calculate(
                complexity=met["complexity"],
                loc=met["loc"],
                comment_ratio=0.1,
            )
            maintainability_scores[fpath] = mi

        avg_complexity = (
            sum(m["complexity"] for m in file_metrics.values()) / max(len(file_metrics), 1)
        )
        avg_maintainability = (
            sum(maintainability_scores.values()) / max(len(maintainability_scores), 1)
        )

        critical_sec = sum(1 for i in all_issues if i.type == "Security" and i.severity == "Critical")
        high_sec = sum(1 for i in all_issues if i.type == "Security" and i.severity == "High")
        security_score = max(0, 100 - (critical_sec * 20 + high_sec * 10))

        dup_score = 100.0
        if duplicates:
            avg_sim = sum(d.similarity for d in duplicates) / len(duplicates)
            dup_score = max(0, 100 - avg_sim * 100)

        smell_count = len([i for i in all_issues if i.type == "Code Smell"])
        smell_score = max(0, 100 - smell_count * 2)

        complexity_score = max(0, 100 - avg_complexity * 2)

        arch_score = arch_analyzer.compute_architecture_score()

        metrics = {
            "maintainability": avg_maintainability,
            "complexity": complexity_score,
            "security": security_score,
            "duplication": dup_score,
            "smells": smell_score,
            "architecture": arch_score,
        }
        scoring = ScoringEngine()
        quality_score = scoring.compute_score(metrics)

        tech_debt = TechnicalDebtEstimator.estimate(all_issues, avg_complexity)

        project = Project(name=os.path.basename(project_path), path=project_path)
        project_id = self.repo.add_project(project)

        run = AnalysisRun(
            project_id=project_id,
            quality_score=quality_score,
            security_score=security_score,
            complexity_score=complexity_score,
            maintainability_score=avg_maintainability,
            duplication_score=dup_score,
            architecture_score=arch_score,
            technical_debt=tech_debt,
        )
        analysis_id = self.repo.add_analysis_run(run)

        for fpath, met in file_metrics.items():
            file = File(
                analysis_id=analysis_id,
                path=fpath,
                language="Python",
                loc=met["loc"],
                function_count=met["functions"],
                class_count=met["classes"],
                complexity=met["complexity"],
                maintainability=maintainability_scores[fpath],
            )
            file_id = self.repo.add_file(file)
            file_issues = [i for i in all_issues if i.file_path == fpath]
            for issue in file_issues:
                issue.analysis_id = analysis_id
                issue.file_id = file_id
                self.repo.add_issue(issue)

        for dup in duplicates:
            dup.analysis_id = analysis_id
            self.repo.add_duplicate(dup)

        return run

    def _find_python_files(self, path: str) -> List[str]:
        files = []
        exclude_dirs = {'.git', 'node_modules', '__pycache__', 'venv', '.venv', 'env', '.env', 'dist', 'build', '.tox', '.eggs'}
        for root, dirs, filenames in os.walk(path):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            for f in filenames:
                if f.endswith('.py'):
                    files.append(os.path.join(root, f))
        return files

    def _count_loc(self, file_path: str) -> int:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                return len(f.readlines())
        except Exception:
            return 0


from app.core.models.issue import Issue
