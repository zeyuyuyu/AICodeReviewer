import ast
import typing
from dataclasses import dataclass
from pathlib import Path

@dataclass
class CodeMetrics:
    complexity: int
    lines: int
    functions: int
    classes: int
    comments: int
    cognitive_score: float

@dataclass 
class ReviewResult:
    quality_score: float # 0-100
    metrics: CodeMetrics
    suggestions: list[str]

class CodeReviewer:
    def __init__(self):
        self.quality_weights = {
            'complexity': 0.3,
            'documentation': 0.2,
            'structure': 0.3,
            'style': 0.2
        }

    def review_file(self, file_path: Path) -> ReviewResult:
        """Analyzes Python code and returns detailed quality metrics."""
        with open(file_path) as f:
            code = f.read()
        
        tree = ast.parse(code)
        metrics = self._analyze_code(tree, code)
        suggestions = self._generate_suggestions(metrics)
        quality_score = self._calculate_quality_score(metrics)
        
        return ReviewResult(
            quality_score=quality_score,
            metrics=metrics,
            suggestions=suggestions
        )
    
    def _analyze_code(self, tree: ast.AST, raw_code: str) -> CodeMetrics:
        """Extract code metrics from AST and raw code."""
        complexity = 0
        functions = 0
        classes = 0
        comments = 0
        
        # Calculate cyclomatic complexity
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.Try)):
                complexity += 1
            elif isinstance(node, ast.FunctionDef):
                functions += 1
            elif isinstance(node, ast.ClassDef):
                classes += 1
        
        # Count comments
        lines = raw_code.split('\n')
        for line in lines:
            if line.strip().startswith('#'):
                comments += 1
                
        # Calculate cognitive complexity based on nesting and structures
        cognitive_score = self._calculate_cognitive_complexity(tree)
        
        return CodeMetrics(
            complexity=complexity,
            lines=len(lines),
            functions=functions,
            classes=classes,
            comments=comments,
            cognitive_score=cognitive_score
        )
    
    def _calculate_cognitive_complexity(self, tree: ast.AST) -> float:
        """Calculate cognitive complexity score based on code structure."""
        score = 0.0
        nesting_level = 0
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For)):
                score += (1 + nesting_level)
                nesting_level += 1
            elif isinstance(node, ast.FunctionDef):
                nesting_level = 0
        
        return score
    
    def _calculate_quality_score(self, metrics: CodeMetrics) -> float:
        """Calculate overall quality score from 0-100."""
        # Complexity score (lower is better)
        complexity_score = max(0, 100 - (metrics.complexity * 5))
        
        # Documentation score
        doc_ratio = metrics.comments / max(1, metrics.lines)
        doc_score = min(100, doc_ratio * 500)
        
        # Structure score
        structure_score = min(100, (
            (metrics.functions + metrics.classes) / 
            max(1, metrics.lines) * 300
        ))
        
        # Style score based on cognitive complexity
        style_score = max(0, 100 - (metrics.cognitive_score * 10))
        
        # Weighted average
        final_score = (
            complexity_score * self.quality_weights['complexity'] +
            doc_score * self.quality_weights['documentation'] +
            structure_score * self.quality_weights['structure'] +
            style_score * self.quality_weights['style']
        )
        
        return round(final_score, 2)
    
    def _generate_suggestions(self, metrics: CodeMetrics) -> list[str]:
        """Generate improvement suggestions based on metrics."""
        suggestions = []
        
        if metrics.complexity > 10:
            suggestions.append(
                'Consider breaking down complex logic into smaller functions'
            )
        
        if metrics.cognitive_score > 15:
            suggestions.append(
                'High cognitive complexity - simplify nested conditions'
            )
            
        if metrics.comments / max(1, metrics.lines) < 0.1:
            suggestions.append('Add more documentation to improve maintainability')
            
        if metrics.lines / max(1, metrics.functions) > 50:
            suggestions.append('Functions may be too long - consider refactoring')
            
        return suggestions