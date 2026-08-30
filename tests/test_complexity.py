"""
Unit tests for CodeSentinel analysis components.
"""
import ast
import pytest
from app.core.analyzer.complexity import ComplexityAnalyzer
from app.core.analyzer.smells import SmellDetector
from app.core.analyzer.security import SecurityAnalyzer
from app.core.analyzer.duplication import DuplicationDetector
from app.core.analyzer.maintainability import MaintainabilityCalculator
from app.core.analyzer.technical_debt import TechnicalDebtEstimator
from app.core.analyzer.scoring import ScoringEngine
from app.core.models.issue import Issue


class TestComplexityAnalyzer:
    def test_simple_function(self):
        code = """
def foo():
    return 1
"""
        tree = ast.parse(code)
        complexity = ComplexityAnalyzer.calculate_cyclomatic(tree)
        assert complexity == 1

    def test_function_with_if(self):
        code = """
def foo(x):
    if x > 0:
        return 1
    elif x < 0:
        return -1
    return 0
"""
        tree = ast.parse(code)
        complexity = ComplexityAnalyzer.calculate_cyclomatic(tree)
        assert complexity == 3

    def test_function_with_loop(self):
        code = """
def foo(n):
    for i in range(n):
        if i % 2 == 0:
            print(i)
"""
        tree = ast.parse(code)
        complexity = ComplexityAnalyzer.calculate_cyclomatic(tree)
        assert complexity == 3

    def test_nesting_depth(self):
        code = """
def foo(x):
    if x > 0:
        if x > 10:
            if x > 100:
                return 1
    return 0
"""
        tree = ast.parse(code)
        depth = ComplexityAnalyzer.calculate_nesting_depth(tree)
        assert depth == 3


class TestSmellDetector:
    def test_long_method(self):
        code = """
def long_function():
    x = 1
""" + "\n".join([f"    x += {i}" for i in range(60)])
        tree = ast.parse(code)
        detector = SmellDetector()
        issues = detector.detect(tree, "test.py")
        assert len(issues) >= 1
        assert any(i.category == "Long Method" for i in issues)

    def test_too_many_parameters(self):
        code = """
def foo(a, b, c, d, e, f, g):
    return a + b + c + d + e + f + g
"""
        tree = ast.parse(code)
        detector = SmellDetector()
        issues = detector.detect(tree, "test.py")
        assert any(i.category == "Too Many Parameters" for i in issues)

    def test_deep_nesting(self):
        code = """
def nested(x):
    if x:
        if x > 1:
            if x > 2:
                if x > 3:
                    if x > 4:
                        return True
    return False
"""
        tree = ast.parse(code)
        detector = SmellDetector()
        issues = detector.detect(tree, "test.py")
        assert any(i.category == "Deep Nesting" for i in issues)


class TestSecurityAnalyzer:
    def test_hardcoded_secret(self):
        code = """
API_KEY = "sk-12345"
"""
        tree = ast.parse(code)
        analyzer = SecurityAnalyzer()
        issues = analyzer.analyze(tree, "config.py")
        assert len(issues) >= 1
        assert any(i.category == "Hardcoded Secret" for i in issues)

    def test_dangerous_eval(self):
        code = """
def process(user_input):
    return eval(user_input)
"""
        tree = ast.parse(code)
        analyzer = SecurityAnalyzer()
        issues = analyzer.analyze(tree, "app.py")
        assert any(i.category == "Dangerous Function" for i in issues)

    def test_weak_crypto(self):
        code = """
import hashlib
def hash_password(pw):
    return hashlib.md5(pw.encode())
"""
        tree = ast.parse(code)
        analyzer = SecurityAnalyzer()
        issues = analyzer.analyze(tree, "auth.py")
        assert any(i.category == "Weak Cryptography" for i in issues)


class TestDuplicationDetector:
    def test_similar_code(self):
        import tempfile
        code1 = """def calculate(a, b):
    result = a + b
    result = result * 2
    if result > 100:
        result = 100
    return result
"""
        code2 = """def compute(a, b):
    result = a + b
    result = result * 2
    if result > 100:
        result = 100
    return result
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f1:
            f1.write(code1)
            path1 = f1.name
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f2:
            f2.write(code2)
            path2 = f2.name
        try:
            tree1 = ast.parse(code1)
            tree2 = ast.parse(code2)
            detector = DuplicationDetector(min_similarity=0.3, min_tokens=5)
            duplicates = detector.detect({path1: tree1, path2: tree2})
            assert len(duplicates) >= 1
        finally:
            import os
            os.unlink(path1)
            os.unlink(path2)

    def test_dissimilar_code(self):
        import tempfile
        code1 = """def unique_function_one():
    return "completely different code here"
"""
        code2 = """def unique_function_two():
    x = 42
    y = x * 2
    return y + "nothing alike"
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f1:
            f1.write(code1)
            path1 = f1.name
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f2:
            f2.write(code2)
            path2 = f2.name
        try:
            tree1 = ast.parse(code1)
            tree2 = ast.parse(code2)
            detector = DuplicationDetector(min_similarity=0.8)
            duplicates = detector.detect({path1: tree1, path2: tree2})
            assert len(duplicates) == 0
        finally:
            import os
            os.unlink(path1)
            os.unlink(path2)


class TestMaintainabilityCalculator:
    def test_perfect_maintainability(self):
        score = MaintainabilityCalculator.calculate(complexity=1, loc=10, comment_ratio=0.3)
        assert score >= 80

    def test_poor_maintainability(self):
        score = MaintainabilityCalculator.calculate(complexity=50, loc=2000, comment_ratio=0.0)
        assert score < 60

    def test_classify(self):
        assert MaintainabilityCalculator.classify(90) == "Excellent"
        assert MaintainabilityCalculator.classify(75) == "Good"
        assert MaintainabilityCalculator.classify(55) == "Moderate"
        assert MaintainabilityCalculator.classify(35) == "Poor"
        assert MaintainabilityCalculator.classify(15) == "Critical"


class TestTechnicalDebtEstimator:
    def test_no_issues(self):
        debt = TechnicalDebtEstimator.estimate([], 0)
        assert debt == 0

    def test_with_issues(self):
        issues = [
            Issue(type="Security", category="Hardcoded Secret", severity="Critical", file_path="test.py"),
            Issue(type="Code Smell", category="Long Method", severity="High", file_path="test.py"),
            Issue(type="Code Smell", category="Deep Nesting", severity="Medium", file_path="test.py"),
        ]
        debt = TechnicalDebtEstimator.estimate(issues, 50)
        assert debt > 0

    def test_high_complexity_multiplier(self):
        issues = [Issue(type="Security", category="Hardcoded Secret", severity="Critical", file_path="test.py")]
        debt_low_complexity = TechnicalDebtEstimator.estimate(issues, 50)
        debt_high_complexity = TechnicalDebtEstimator.estimate(issues, 90)
        assert debt_high_complexity > debt_low_complexity


class TestScoringEngine:
    def test_perfect_score(self):
        engine = ScoringEngine()
        score = engine.compute_score({
            "maintainability": 100,
            "complexity": 100,
            "security": 100,
            "duplication": 100,
            "smells": 100,
            "architecture": 100,
        })
        assert score == 100

    def test_grade_a(self):
        engine = ScoringEngine()
        assert engine.grade(95) == "A"

    def test_grade_f(self):
        engine = ScoringEngine()
        assert engine.grade(45) == "F"

    def test_weighted_score(self):
        engine = ScoringEngine()
        score = engine.compute_score({
            "maintainability": 80,
            "complexity": 70,
            "security": 90,
        })
        expected = 80 * 0.25 + 70 * 0.20 + 90 * 0.20
        assert abs(score - expected) < 0.1
