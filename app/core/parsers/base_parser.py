"""
Base parser interface.
"""
import ast
from typing import Dict


class BaseParser:
    def parse(self, file_path: str) -> ast.AST:
        raise NotImplementedError

    def extract_metrics(self, tree: ast.AST) -> Dict:
        raise NotImplementedError

    def get_language(self) -> str:
        raise NotImplementedError
