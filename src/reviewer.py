import ast
import typing
from dataclasses import dataclass
from pathlib import Path

@dataclass
class CodeMetrics:
    complexity: int
    lines_of_code: int
    comment_ratio: float
    max_nesting: int
    avg_function_length: float

@dataclass
class ReviewResult:
    metrics: CodeMetrics
    score: float  # 0-100
    suggestions: list[str]

class CodeReviewer:
    def __init__(self):
        self.quality_thresholds = {
            'max_complexity': 10,
            'max_nesting': 4,
            'min_comment_ratio': 0.1,
            'max_function_length': 50
        }

    def review_file(self, file_path: Path) -> ReviewResult:
        with open(file_path) as f:
            code = f.read()
        
        tree = ast.parse(code)
        metrics = self._calculate_metrics(tree, code)
        score = self._calculate_score(metrics)
        suggestions = self._generate_suggestions(metrics)
        
        return ReviewResult(metrics, score, suggestions)

    def _calculate_metrics(self, tree: ast.AST, code: str) -> CodeMetrics:
        complexity = 0
        max_nesting = 0
        function_lengths = []
        
        class Analyzer(ast.NodeVisitor):
            def __init__(self):
                self.current_nesting = 0

            def visit_If(self, node):
                nonlocal complexity
                complexity += 1
                self.current_nesting += 1
                max_nesting = max(max_nesting, self.current_nesting)
                self.generic_visit(node)
                self.current_nesting -= 1

            def visit_FunctionDef(self, node):
                function_lengths.append(node.end_lineno - node.lineno)
                self.generic_visit(node)

        Analyzer().visit(tree)

        lines = code.split('\n')
        comment_lines = sum(1 for line in lines if line.strip().startswith('#'))
        
        return CodeMetrics(
            complexity=complexity,
            lines_of_code=len(lines),
            comment_ratio=comment_lines / len(lines) if lines else 0,
            max_nesting=max_nesting,
            avg_function_length=sum(function_lengths) / len(function_lengths) if function_lengths else 0
        )

    def _calculate_score(self, metrics: CodeMetrics) -> float:
        score = 100.0
        
        if metrics.complexity > self.quality_thresholds['max_complexity']:
            score -= 10 * (metrics.complexity - self.quality_thresholds['max_complexity'])
            
        if metrics.max_nesting > self.quality_thresholds['max_nesting']:
            score -= 15 * (metrics.max_nesting - self.quality_thresholds['max_nesting'])
            
        if metrics.comment_ratio < self.quality_thresholds['min_comment_ratio']:
            score -= 20 * (self.quality_thresholds['min_comment_ratio'] - metrics.comment_ratio)
            
        if metrics.avg_function_length > self.quality_thresholds['max_function_length']:
            score -= 5 * (metrics.avg_function_length - self.quality_thresholds['max_function_length'])
            
        return max(0, min(100, score))

    def _generate_suggestions(self, metrics: CodeMetrics) -> list[str]:
        suggestions = []
        
        if metrics.complexity > self.quality_thresholds['max_complexity']:
            suggestions.append(f'Consider reducing cyclomatic complexity (current: {metrics.complexity})')
            
        if metrics.max_nesting > self.quality_thresholds['max_nesting']:
            suggestions.append(f'Reduce nesting depth (current max: {metrics.max_nesting})')
            
        if metrics.comment_ratio < self.quality_thresholds['min_comment_ratio']:
            suggestions.append('Add more comments to improve code documentation')
            
        if metrics.avg_function_length > self.quality_thresholds['max_function_length']:
            suggestions.append('Consider breaking down long functions into smaller ones')
            
        return suggestions
