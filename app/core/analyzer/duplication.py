import ast
import tokenize
from io import StringIO
from difflib import SequenceMatcher
from typing import List, Tuple, Dict
from app.core.models.duplicate import Duplicate


class DuplicationDetector:
    def __init__(self, min_similarity=0.8, min_tokens=20):
        self.min_similarity = min_similarity
        self.min_tokens = min_tokens

    def _tokenize_file(self, file_path: str) -> List[Tuple[int, str]]:
        """Return list of (line_number, token_string) for all tokens."""
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        tokens = []
        try:
            g = tokenize.generate_tokens(StringIO(content).readline)
            for tok in g:
                if tok.type not in (tokenize.COMMENT, tokenize.NL, tokenize.ENCODING):
                    tokens.append((tok.start[0], tok.string))
        except Exception:
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if hasattr(node, 'lineno') and isinstance(node, ast.Name):
                        tokens.append((node.lineno, node.id))
            except Exception:
                pass
        return tokens

    def detect(self, file_nodes: Dict[str, ast.AST]) -> List[Duplicate]:
        files_tokens = {}
        for path, _ in file_nodes.items():
            tokens = self._tokenize_file(path)
            if tokens:
                files_tokens[path] = tokens

        duplicates = []
        file_paths = list(files_tokens.keys())
        for i in range(len(file_paths)):
            for j in range(i + 1, len(file_paths)):
                path_a, path_b = file_paths[i], file_paths[j]
                seq_a = [t[1] for t in files_tokens[path_a]]
                seq_b = [t[1] for t in files_tokens[path_b]]
                if len(seq_a) < self.min_tokens or len(seq_b) < self.min_tokens:
                    continue
                sm = SequenceMatcher(None, seq_a, seq_b)
                matching_blocks = sm.get_matching_blocks()
                for block in matching_blocks:
                    if block.size > self.min_tokens:
                        line_a = files_tokens[path_a][block.a][0]
                        line_b = files_tokens[path_b][block.b][0]
                        end_line_a = files_tokens[path_a][block.a + block.size - 1][0]
                        end_line_b = files_tokens[path_b][block.b + block.size - 1][0]
                        similarity = block.size / max(len(seq_a), len(seq_b))
                        if similarity >= self.min_similarity:
                            duplicates.append(Duplicate(
                                file_a=path_a,
                                file_b=path_b,
                                similarity=round(similarity, 2),
                                start_line_a=line_a,
                                end_line_a=end_line_a,
                                start_line_b=line_b,
                                end_line_b=end_line_b
                            ))
        return duplicates
