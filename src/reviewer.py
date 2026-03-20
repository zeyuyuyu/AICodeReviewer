import ast
import typing
from dataclasses import dataclass
from enum import Enum

@dataclass
class CodeMetrics:
    complexity: int
    lines_of_code: int
    comment_ratio: float
    max_nesting: int
    avg_function_length: float

@dataclass 
class ReviewResult:
    score: float  # 0-100
    metrics: CodeMetrics
    suggestions: list[str]
    severity: str

class Severity(Enum):
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    CRITICAL = 'critical'

class CodeReviewer:
    def __init__(self):
        self.ast_analyzer = ASTAnalyzer()

    def review_code(self, code: str) -> ReviewResult:
        """Analyzes code and returns detailed review metrics"""
        tree = ast.parse(code)
        metrics = self._calculate_metrics(tree, code)
        score = self._calculate_score(metrics)
        suggestions = self._generate_suggestions(metrics)
        severity = self._determine_severity(score)

        return ReviewResult(
            score=score,
            metrics=metrics,
            suggestions=suggestions,
            severity=severity
        )

    def _calculate_metrics(self, tree: ast.AST, raw_code: str) -> CodeMetrics:
        complexity = self.ast_analyzer.calculate_complexity(tree)
        lines = len(raw_code.splitlines())
        comments = self.ast_analyzer.count_comments(raw_code)
        nesting = self.ast_analyzer.max_nesting_depth(tree)
        avg_func_len = self.ast_analyzer.average_function_length(tree)

        return CodeMetrics(
            complexity=complexity,
            lines_of_code=lines,
            comment_ratio=comments/lines if lines > 0 else 0,
            max_nesting=nesting,
            avg_function_length=avg_func_len
        )

    def _calculate_score(self, metrics: CodeMetrics) -> float:
        # Weight different factors to produce overall 0-100 score
        weights = {
            'complexity': -0.2,
            'nesting': -0.2,
            'comment_ratio': 0.3,
            'function_length': -0.3
        }

        score = 100
        score += metrics.complexity * weights['complexity']
        score += metrics.max_nesting * weights['nesting'] 
        score += metrics.comment_ratio * 100 * weights['comment_ratio']
        score += metrics.avg_function_length * weights['function_length']

        return max(0, min(100, score))

    def _generate_suggestions(self, metrics: CodeMetrics) -> list[str]:
        suggestions = []
        
        if metrics.complexity > 10:
            suggestions.append('Consider breaking down complex logic into smaller functions')
        if metrics.comment_ratio < 0.1:
            suggestions.append('Add more documentation comments to improve code clarity')
        if metrics.max_nesting > 4:
            suggestions.append('Reduce nesting depth by extracting logic into helper functions')
        if metrics.avg_function_length > 20:
            suggestions.append('Break long functions into smaller, more focused ones')

        return suggestions

    def _determine_severity(self, score: float) -> str:
        if score < 40:
            return Severity.CRITICAL.value
        elif score < 60:
            return Severity.HIGH.value
        elif score < 80:
            return Severity.MEDIUM.value
        return Severity.LOW.value

class ASTAnalyzer:
    def calculate_complexity(self, tree: ast.AST) -> int:
        """Calculate cyclomatic complexity"""
        complexity = 1
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.Try,
                               ast.ExceptHandler, ast.With, ast.Assert)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        return complexity

    def count_comments(self, code: str) -> int:
        """Count number of comment lines"""
        return len([line for line in code.splitlines() 
                   if line.strip().startswith('#')])

    def max_nesting_depth(self, tree: ast.AST) -> int:
        """Calculate maximum nesting depth"""
        def get_depth(node, current=0):
            max_depth = current
            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.If, ast.For, ast.While, ast.With)):
                    child_depth = get_depth(child, current + 1)
                    max_depth = max(max_depth, child_depth)
                else:
                    child_depth = get_depth(child, current)
                    max_depth = max(max_depth, child_depth)
            return max_depth
        
        return get_depth(tree)

    def average_function_length(self, tree: ast.AST) -> float:
        """Calculate average function length in lines"""
        lengths = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                lengths.append(node.end_lineno - node.lineno)
        return sum(lengths) / len(lengths) if lengths else 0