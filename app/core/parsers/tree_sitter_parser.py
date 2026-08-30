"""
Tree-sitter multi-language parser.
"""
import os
from typing import Dict, Optional


class TreeSitterParser:
    LANGUAGE_MAP = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.java': 'java',
    }

    def __init__(self):
        self.parsers = {}
        self._load_parsers()

    def _load_parsers(self):
        """Load available tree-sitter parsers."""
        try:
            from tree_sitter import Language, Parser
            import tree_sitter_python as tspython
            self.parsers['.py'] = self._create_parser(tspython.language())
        except ImportError:
            pass
        try:
            from tree_sitter import Language, Parser
            import tree_sitter_javascript as tsjavascript
            self.parsers['.js'] = self._create_parser(tsjavascript.language())
        except ImportError:
            pass
        try:
            from tree_sitter import Language, Parser
            import tree_sitter_java as tsjava
            self.parsers['.java'] = self._create_parser(tsjava.language())
        except ImportError:
            pass

    def _create_parser(self, language):
        from tree_sitter import Parser
        p = Parser()
        p.set_language(language)
        return p

    def parse(self, file_path: str):
        ext = os.path.splitext(file_path)[1]
        if ext not in self.parsers:
            raise ValueError(f"Unsupported extension: {ext}")
        with open(file_path, 'rb') as f:
            code = f.read()
        tree = self.parsers[ext].parse(code)
        return tree

    def extract_metrics(self, tree, file_path: str) -> Dict:
        """Extract function and class counts from tree-sitter AST."""
        func_types = ['function_definition', 'method_definition', 'function_declaration']
        class_types = ['class_definition', 'class_declaration']
        functions = 0
        classes = 0

        def traverse(node):
            nonlocal functions, classes
            if node.type in func_types:
                functions += 1
            elif node.type in class_types:
                classes += 1
            for child in node.children:
                traverse(child)

        traverse(tree.root_node)
        return {'function_count': functions, 'class_count': classes}

    def get_language(self, file_path: str) -> Optional[str]:
        ext = os.path.splitext(file_path)[1]
        return self.LANGUAGE_MAP.get(ext)
