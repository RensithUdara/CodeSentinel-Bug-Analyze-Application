"""
Python parser using ast.
"""
import ast
from typing import Dict, List
from app.core.parsers.base_parser import BaseParser


class PythonParser(BaseParser):
    def parse(self, file_path: str) -> ast.AST:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        return ast.parse(content, filename=file_path)

    def extract_metrics(self, tree: ast.AST) -> Dict:
        class Visitor(ast.NodeVisitor):
            def __init__(self):
                self.functions = 0
                self.classes = 0
                self.imports = 0
                self.methods = 0

            def visit_FunctionDef(self, node):
                self.functions += 1
                self.generic_visit(node)

            def visit_AsyncFunctionDef(self, node):
                self.functions += 1
                self.generic_visit(node)

            def visit_ClassDef(self, node):
                self.classes += 1
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        self.methods += 1
                self.generic_visit(node)

            def visit_Import(self, node):
                self.imports += len(node.names)
                self.generic_visit(node)

            def visit_ImportFrom(self, node):
                self.imports += len(node.names)
                self.generic_visit(node)

        visitor = Visitor()
        visitor.visit(tree)
        return {
            "function_count": visitor.functions,
            "class_count": visitor.classes,
            "method_count": visitor.methods,
            "import_count": visitor.imports,
        }

    def get_language(self) -> str:
        return "Python"
