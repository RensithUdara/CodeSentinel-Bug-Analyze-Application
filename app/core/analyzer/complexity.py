"""
Cyclomatic and cognitive complexity analysis.
"""
import ast
from typing import Dict, List


class ComplexityAnalyzer:
    @staticmethod
    def calculate_cyclomatic(node: ast.AST) -> int:
        class ComplexityVisitor(ast.NodeVisitor):
            def __init__(self):
                self.complexity = 1

            def visit_If(self, node):
                self.complexity += 1
                self.generic_visit(node)

            def visit_For(self, node):
                self.complexity += 1
                self.generic_visit(node)

            def visit_AsyncFor(self, node):
                self.complexity += 1
                self.generic_visit(node)

            def visit_While(self, node):
                self.complexity += 1
                self.generic_visit(node)

            def visit_BoolOp(self, node):
                self.complexity += len(node.values) - 1
                self.generic_visit(node)

            def visit_ExceptHandler(self, node):
                self.complexity += 1
                self.generic_visit(node)

            def visit_With(self, node):
                self.complexity += 1
                self.generic_visit(node)

        visitor = ComplexityVisitor()
        visitor.visit(node)
        return visitor.complexity

    @staticmethod
    def calculate_nesting_depth(node: ast.AST) -> int:
        class NestingVisitor(ast.NodeVisitor):
            def __init__(self):
                self.max_depth = 0
                self.current_depth = 0

            def _increase(self, node):
                self.current_depth += 1
                self.max_depth = max(self.max_depth, self.current_depth)
                self.generic_visit(node)
                self.current_depth -= 1

            def visit_If(self, node):
                self._increase(node)

            def visit_For(self, node):
                self._increase(node)

            def visit_AsyncFor(self, node):
                self._increase(node)

            def visit_While(self, node):
                self._increase(node)

            def visit_Try(self, node):
                self._increase(node)

            def visit_With(self, node):
                self._increase(node)

        visitor = NestingVisitor()
        visitor.visit(node)
        return visitor.max_depth

    @staticmethod
    def get_severity(complexity: int) -> str:
        if complexity <= 5:
            return "Low"
        elif complexity <= 10:
            return "Medium"
        elif complexity <= 15:
            return "High"
        else:
            return "Critical"

    @staticmethod
    def analyze_functions(tree: ast.AST) -> List[Dict]:
        results = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                complexity = ComplexityAnalyzer.calculate_cyclomatic(node)
                nesting = ComplexityAnalyzer.calculate_nesting_depth(node)
                results.append({
                    "name": node.name,
                    "line": node.lineno,
                    "complexity": complexity,
                    "nesting_depth": nesting,
                    "severity": ComplexityAnalyzer.get_severity(complexity),
                })
        return results

    @staticmethod
    def calculate_cognitive(tree: ast.AST) -> int:
        """Calculate cognitive complexity using SonarQube-style rules."""
        visitor = CognitiveComplexityVisitor()
        visitor.visit(tree)
        return visitor.complexity


class CognitiveComplexityVisitor(ast.NodeVisitor):
    """SonarQube-style cognitive complexity."""
    def __init__(self):
        self.complexity = 0
        self.nesting = 0
        self._in_bool_op = False

    def _add_penalty(self, base=1):
        self.complexity += base + self.nesting

    def visit_If(self, node):
        self._add_penalty()
        self.nesting += 1
        self.generic_visit(node)
        self.nesting -= 1

    def visit_For(self, node):
        self._add_penalty()
        self.nesting += 1
        self.generic_visit(node)
        self.nesting -= 1

    def visit_While(self, node):
        self._add_penalty()
        self.nesting += 1
        self.generic_visit(node)
        self.nesting -= 1

    def visit_BoolOp(self, node):
        if not self._in_bool_op:
            self._in_bool_op = True
            self.complexity += len(node.values) - 1
            self.generic_visit(node)
            self._in_bool_op = False
        else:
            self.generic_visit(node)

    def visit_ExceptHandler(self, node):
        self._add_penalty()
        self.nesting += 1
        self.generic_visit(node)
        self.nesting -= 1

    def visit_With(self, node):
        self._add_penalty()
        self.nesting += 1
        self.generic_visit(node)
        self.nesting -= 1
