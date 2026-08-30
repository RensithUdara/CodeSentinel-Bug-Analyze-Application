"""
Security pattern detection.
"""
import ast
import re
from typing import List
from app.core.models.issue import Issue


class SecurityAnalyzer:
    def __init__(self):
        self.secret_patterns = [
            (r'api[_-]?key', "API Key"),
            (r'password', "Password"),
            (r'token', "Token"),
            (r'secret', "Secret"),
            (r'credential', "Credential"),
            (r'aws[_-]?key', "AWS Key"),
            (r'private[_-]?key', "Private Key"),
        ]
        self.dangerous_functions = ['eval', 'exec', 'compile', '__import__', 'execfile']
        self.weak_crypto = ['md5', 'sha1', 'des', 'rc4']
        self.sql_patterns = [r'SELECT\s+.*\s+FROM', r'INSERT\s+INTO', r'DELETE\s+FROM', r'UPDATE\s+.*\s+SET']

    def analyze(self, tree: ast.AST, file_path: str) -> List[Issue]:
        issues = []
        visitor = SecurityVisitor(self, file_path)
        visitor.visit(tree)
        issues.extend(visitor.issues)
        return issues


class SecurityVisitor(ast.NodeVisitor):
    def __init__(self, analyzer: SecurityAnalyzer, file_path: str):
        self.analyzer = analyzer
        self.file_path = file_path
        self.issues: List[Issue] = []

    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name):
                var_name = target.id.lower()
                for pattern, desc in self.analyzer.secret_patterns:
                    if re.search(pattern, var_name):
                        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                            if len(node.value.value) > 0:
                                self.issues.append(Issue(
                                    type="Security",
                                    category="Hardcoded Secret",
                                    severity="Critical",
                                    file_path=self.file_path,
                                    line=node.lineno,
                                    message=f"Hardcoded {desc} in variable '{target.id}'",
                                    recommendation="Move to environment variables or secure vault.",
                                ))
        self.generic_visit(node)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            if func_name in self.analyzer.dangerous_functions:
                self.issues.append(Issue(
                    type="Security",
                    category="Dangerous Function",
                    severity="High",
                    file_path=self.file_path,
                    line=node.lineno,
                    message=f"Use of dangerous function '{func_name}'",
                    recommendation="Avoid dynamic code execution; use safer alternatives.",
                ))
            if func_name in self.analyzer.weak_crypto:
                self.issues.append(Issue(
                    type="Security",
                    category="Weak Cryptography",
                    severity="Medium",
                    file_path=self.file_path,
                    line=node.lineno,
                    message=f"Weak cryptographic algorithm '{func_name}' used",
                    recommendation="Use modern algorithms like SHA-256 or AES.",
                ))
        elif isinstance(node.func, ast.Attribute):
            if node.func.attr in self.analyzer.weak_crypto:
                self.issues.append(Issue(
                    type="Security",
                    category="Weak Cryptography",
                    severity="Medium",
                    file_path=self.file_path,
                    line=node.lineno,
                    message=f"Weak cryptographic algorithm '{node.func.attr}' used",
                    recommendation="Use modern algorithms like SHA-256 or AES.",
                ))
        self.generic_visit(node)

    def visit_Constant(self, node):
        if isinstance(node.value, str):
            for pattern in self.analyzer.sql_patterns:
                if re.search(pattern, node.value, re.IGNORECASE):
                    if any(op in node.value for op in ['+', '%', 'format', 'f"', "f'"]):
                        self.issues.append(Issue(
                            type="Security",
                            category="SQL Injection Risk",
                            severity="High",
                            file_path=self.file_path,
                            line=getattr(node, 'lineno', 0),
                            message="Potential SQL injection vulnerability detected",
                            recommendation="Use parameterized queries instead of string concatenation.",
                        ))
                        break
        self.generic_visit(node)
