"""
Code smell detection.
"""
import ast
from typing import List, Dict
from app.core.models.issue import Issue


class SmellDetector:
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.max_method_lines = self.config.get("max_method_lines", 50)
        self.max_parameters = self.config.get("max_parameters", 5)
        self.max_class_methods = self.config.get("max_class_methods", 20)
        self.max_nesting = self.config.get("max_nesting", 4)
        self.max_local_vars = self.config.get("max_local_vars", 10)

    def detect(self, tree: ast.AST, file_path: str) -> List[Issue]:
        issues = []
        visitor = SmellVisitor(self, file_path)
        visitor.visit(tree)
        issues.extend(visitor.issues)
        return issues


class SmellVisitor(ast.NodeVisitor):
    def __init__(self, detector: SmellDetector, file_path: str):
        self.detector = detector
        self.file_path = file_path
        self.issues: List[Issue] = []
        self.current_class = None

    def visit_FunctionDef(self, node):
        self._check_function(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        self._check_function(node)
        self.generic_visit(node)

    def _check_function(self, node):
        lines = (node.end_lineno or node.lineno) - node.lineno + 1
        if lines > self.detector.max_method_lines:
            self.issues.append(Issue(
                type="Code Smell",
                category="Long Method",
                severity="Medium" if lines < 100 else "High",
                file_path=self.file_path,
                line=node.lineno,
                message=f"Function '{node.name}' has {lines} lines (threshold {self.detector.max_method_lines})",
                recommendation="Split the method into smaller, focused functions.",
                metric_value=float(lines),
                threshold=float(self.detector.max_method_lines),
            ))

        param_count = len(node.args.args) + len(node.args.kwonlyargs)
        if node.args.vararg:
            param_count += 1
        if node.args.kwarg:
            param_count += 1
        if param_count > self.detector.max_parameters:
            self.issues.append(Issue(
                type="Code Smell",
                category="Too Many Parameters",
                severity="Medium",
                file_path=self.file_path,
                line=node.lineno,
                message=f"Function '{node.name}' has {param_count} parameters",
                recommendation="Consider using a parameter object or splitting the function.",
                metric_value=float(param_count),
                threshold=float(self.detector.max_parameters),
            ))

        depth = self._compute_nesting(node)
        if depth > self.detector.max_nesting:
            self.issues.append(Issue(
                type="Code Smell",
                category="Deep Nesting",
                severity="High",
                file_path=self.file_path,
                line=node.lineno,
                message=f"Function '{node.name}' has nesting depth {depth}",
                recommendation="Refactor to reduce nesting with guard clauses or early returns.",
                metric_value=float(depth),
                threshold=float(self.detector.max_nesting),
            ))

        local_vars = self._count_locals(node)
        if local_vars > self.detector.max_local_vars:
            self.issues.append(Issue(
                type="Code Smell",
                category="Too Many Local Variables",
                severity="Medium",
                file_path=self.file_path,
                line=node.lineno,
                message=f"Function '{node.name}' has {local_vars} local variables",
                recommendation="Consider extracting logic into separate functions.",
                metric_value=float(local_vars),
                threshold=float(self.detector.max_local_vars),
            ))

    def visit_ClassDef(self, node):
        method_count = sum(1 for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)))
        if method_count > self.detector.max_class_methods:
            self.issues.append(Issue(
                type="Code Smell",
                category="Large Class",
                severity="Medium",
                file_path=self.file_path,
                line=node.lineno,
                message=f"Class '{node.name}' has {method_count} methods",
                recommendation="Split the class into smaller, single-responsibility classes.",
                metric_value=float(method_count),
                threshold=float(self.detector.max_class_methods),
            ))
        self.generic_visit(node)

    def _compute_nesting(self, node) -> int:
        class NestVisitor(ast.NodeVisitor):
            def __init__(self):
                self.max_depth = 0
                self.depth = 0

            def _increase(self, n):
                self.depth += 1
                self.max_depth = max(self.max_depth, self.depth)
                self.generic_visit(n)
                self.depth -= 1

            def visit_If(self, n):
                self._increase(n)

            def visit_For(self, n):
                self._increase(n)

            def visit_AsyncFor(self, n):
                self._increase(n)

            def visit_While(self, n):
                self._increase(n)

            def visit_Try(self, n):
                self._increase(n)

            def visit_With(self, n):
                self._increase(n)

        v = NestVisitor()
        v.visit(node)
        return v.max_depth

    def _count_locals(self, node) -> int:
        count = 0
        for child in ast.walk(node):
            if isinstance(child, ast.Assign):
                count += len(child.targets)
        return count
