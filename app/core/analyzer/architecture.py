import ast
from collections import defaultdict
from typing import Dict, Set, List, Tuple


class ArchitectureAnalyzer:
    def __init__(self):
        self.imports: Dict[str, Set[str]] = defaultdict(set)

    def analyze_file(self, file_path: str, tree: ast.AST) -> None:
        """Extract imports from a single AST."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self.imports[file_path].add(alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    self.imports[file_path].add(node.module.split('.')[0])

    def find_circular_dependencies(self) -> List[List[str]]:
        """Detect cycles in the dependency graph using DFS."""
        graph = {k: list(v) for k, v in self.imports.items()}
        visited = set()
        rec_stack = set()
        cycles = []

        def dfs(node: str, path: List[str]) -> bool:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor, path):
                        return True
                elif neighbor in rec_stack:
                    idx = path.index(neighbor)
                    cycles.append(path[idx:] + [neighbor])
                    return True
            rec_stack.remove(node)
            path.pop()
            return False

        for node in list(graph.keys()):
            if node not in visited:
                dfs(node, [])
        return cycles

    def compute_architecture_score(self) -> float:
        """Score: 100 - penalty for cycles and high coupling."""
        cycles = self.find_circular_dependencies()
        penalty = len(cycles) * 10
        total_files = len(self.imports)
        if total_files == 0:
            return 80.0
        avg_fan_out = sum(len(v) for v in self.imports.values()) / total_files
        if avg_fan_out > 5:
            penalty += (avg_fan_out - 5) * 2
        return max(0.0, 100.0 - penalty)

    def get_dependency_graph(self) -> Dict[str, Set[str]]:
        return self.imports
