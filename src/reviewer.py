import ast
import typing
from dataclasses import dataclass
from pathlib import Path

@dataclass
class CodeMetrics:
    complexity: int
    lines_of_code: int
    comment_ratio: float
    function_count: int
    class_count: int
    maintainability_index: float

@dataclass 
class ReviewSuggestion:
    line_number: int
    severity: str
    message: str
    suggestion: str

class CodeReviewer:
    def __init__(self):
        self.metrics = None
        self.suggestions = []

    def analyze_file(self, filepath: Path) -> tuple[CodeMetrics, list[ReviewSuggestion]]:
        """Analyze a Python source file and return metrics and suggestions."""
        with open(filepath) as f:
            content = f.read()
        
        tree = ast.parse(content)
        
        # Calculate metrics
        self.metrics = self._calculate_metrics(content, tree)
        
        # Generate suggestions
        self.suggestions = []
        self._analyze_complexity(tree)
        self._analyze_naming(tree)
        self._analyze_documentation(tree)
        
        return self.metrics, self.suggestions

    def _calculate_metrics(self, content: str, tree: ast.AST) -> CodeMetrics:
        lines = content.splitlines()
        comment_lines = sum(1 for line in lines if line.strip().startswith('#'))
        
        function_nodes = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        class_nodes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        
        # Simple complexity = number of branches and loops
        complexity = len([node for node in ast.walk(tree)
                         if isinstance(node, (ast.If, ast.For, ast.While))])
        
        # Basic maintainability index calculation
        maintainability = 100 - (complexity * 0.5 + len(lines) * 0.1)
        
        return CodeMetrics(
            complexity=complexity,
            lines_of_code=len(lines),
            comment_ratio=comment_lines / len(lines) if lines else 0,
            function_count=len(function_nodes),
            class_count=len(class_nodes),
            maintainability_index=maintainability
        )

    def _analyze_complexity(self, tree: ast.AST) -> None:
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                complexity = len([n for n in ast.walk(node)
                                if isinstance(n, (ast.If, ast.For, ast.While))])
                if complexity > 5:
                    self.suggestions.append(ReviewSuggestion(
                        line_number=node.lineno,
                        severity='warning',
                        message=f'Function {node.name} has high cyclomatic complexity of {complexity}',
                        suggestion='Consider breaking down this function into smaller, more focused functions'
                    ))

    def _analyze_naming(self, tree: ast.AST) -> None:
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                if not node.name.islower() and isinstance(node, ast.FunctionDef):
                    self.suggestions.append(ReviewSuggestion(
                        line_number=node.lineno,
                        severity='style',
                        message=f'Function {node.name} does not follow snake_case naming convention',
                        suggestion=f'Rename to {node.name.lower()}'
                    ))
                elif not node.name[0].isupper() and isinstance(node, ast.ClassDef):
                    self.suggestions.append(ReviewSuggestion(
                        line_number=node.lineno,
                        severity='style',
                        message=f'Class {node.name} does not follow PascalCase naming convention',
                        suggestion=f'Rename to {node.name.capitalize()}'
                    ))

    def _analyze_documentation(self, tree: ast.AST) -> None:
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                if not ast.get_docstring(node):
                    self.suggestions.append(ReviewSuggestion(
                        line_number=node.lineno,
                        severity='documentation',
                        message=f'Missing docstring for {node.name}',
                        suggestion='Add a descriptive docstring explaining purpose and parameters'
                    ))

def review_code(filepath: str) -> str:
    """Main entry point for code review."""
    reviewer = CodeReviewer()
    metrics, suggestions = reviewer.analyze_file(Path(filepath))
    
    report = [
        'Code Review Report',
        '=================\n',
        'Metrics:',
        f'- Lines of code: {metrics.lines_of_code}',
        f'- Cyclomatic complexity: {metrics.complexity}',
        f'- Comment ratio: {metrics.comment_ratio:.2%}',
        f'- Function count: {metrics.function_count}',
        f'- Class count: {metrics.class_count}',
        f'- Maintainability index: {metrics.maintainability_index:.1f}/100\n',
        'Suggestions:'
    ]
    
    for suggestion in suggestions:
        report.append(f'Line {suggestion.line_number} [{suggestion.severity}]: {suggestion.message}')
        report.append(f'  → {suggestion.suggestion}\n')
    
    return '\n'.join(report)
