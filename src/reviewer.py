"""AI-powered code review automation with quality scoring."""

import ast
from dataclasses import dataclass
from typing import List, Dict
import statistics

@dataclass
class CodeMetrics:
    complexity: int
    lines: int 
    comments: int
    functions: int
    classes: int
    score: float
    suggestions: List[str]

class CodeReviewer:
    def __init__(self):
        self.quality_thresholds = {
            'complexity': {'good': 10, 'warning': 20},
            'comments_ratio': {'good': 0.1, 'warning': 0.05},
            'function_length': {'good': 20, 'warning': 40}
        }
    
    def analyze_code(self, code: str) -> CodeMetrics:
        """Analyze code and return detailed metrics with quality score."""
        tree = ast.parse(code)
        
        metrics = CodeMetrics(
            complexity=self._calculate_complexity(tree),
            lines=len(code.splitlines()),
            comments=self._count_comments(code),
            functions=len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]),
            classes=len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]),
            score=0.0,
            suggestions=[]
        )
        
        metrics.score = self._calculate_quality_score(metrics)
        metrics.suggestions = self._generate_suggestions(metrics)
        
        return metrics
    
    def _calculate_complexity(self, tree: ast.AST) -> int:
        """Calculate cyclomatic complexity."""
        complexity = 1
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        return complexity
    
    def _count_comments(self, code: str) -> int:
        """Count number of comment lines."""
        return len([line for line in code.splitlines() 
                   if line.strip().startswith('#') or line.strip().startswith('"""")])
    
    def _calculate_quality_score(self, metrics: CodeMetrics) -> float:
        """Calculate overall code quality score (0-10)."""
        scores = []
        
        # Complexity score
        if metrics.complexity <= self.quality_thresholds['complexity']['good']:
            scores.append(10)
        elif metrics.complexity <= self.quality_thresholds['complexity']['warning']:
            scores.append(7)
        else:
            scores.append(4)
        
        # Comments ratio score
        comments_ratio = metrics.comments / metrics.lines if metrics.lines > 0 else 0
        if comments_ratio >= self.quality_thresholds['comments_ratio']['good']:
            scores.append(10)
        elif comments_ratio >= self.quality_thresholds['comments_ratio']['warning']:
            scores.append(7)
        else:
            scores.append(4)
        
        # Average function length score
        avg_func_length = metrics.lines / metrics.functions if metrics.functions > 0 else metrics.lines
        if avg_func_length <= self.quality_thresholds['function_length']['good']:
            scores.append(10)
        elif avg_func_length <= self.quality_thresholds['function_length']['warning']:
            scores.append(7)
        else:
            scores.append(4)
            
        return statistics.mean(scores)
    
    def _generate_suggestions(self, metrics: CodeMetrics) -> List[str]:
        """Generate improvement suggestions based on metrics."""
        suggestions = []
        
        if metrics.complexity > self.quality_thresholds['complexity']['warning']:
            suggestions.append(
                f'High complexity ({metrics.complexity}). Consider breaking down complex functions.')
        
        comments_ratio = metrics.comments / metrics.lines if metrics.lines > 0 else 0
        if comments_ratio < self.quality_thresholds['comments_ratio']['warning']:
            suggestions.append('Low comment density. Consider adding more documentation.')
        
        avg_func_length = metrics.lines / metrics.functions if metrics.functions > 0 else metrics.lines
        if avg_func_length > self.quality_thresholds['function_length']['warning']:
            suggestions.append(
                f'Average function length ({avg_func_length:.1f} lines) is high. Consider breaking down large functions.')
        
        return suggestions

    def review(self, code: str) -> Dict:
        """Perform automated code review with metrics and suggestions."""
        metrics = self.analyze_code(code)
        return {
            'quality_score': round(metrics.score, 2),
            'metrics': {
                'complexity': metrics.complexity,
                'total_lines': metrics.lines,
                'comment_lines': metrics.comments,
                'functions': metrics.functions,
                'classes': metrics.classes
            },
            'suggestions': metrics.suggestions
        }