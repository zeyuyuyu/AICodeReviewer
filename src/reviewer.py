import ast
import typing
from dataclasses import dataclass
from pathlib import Path

@dataclass
class CodeMetrics:
    cognitive_complexity: int
    maintainability_index: float
    lines_of_code: int
    comment_ratio: float

@dataclass
class ReviewFinding:
    severity: str  # 'high', 'medium', 'low'
    message: str
    line_number: int
    suggestion: str

class CodeReviewer:
    def __init__(self):
        self.findings = []

    def review_file(self, file_path: Path) -> typing.List[ReviewFinding]:
        """Perform comprehensive automated code review"""
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Parse AST
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            self.findings.append(
                ReviewFinding('high', f'Syntax error: {str(e)}', e.lineno, 'Fix syntax error')
            )
            return self.findings

        # Analyze code metrics
        metrics = self._calculate_metrics(content, tree)
        
        # Check complexity
        if metrics.cognitive_complexity > 15:
            self.findings.append(
                ReviewFinding(
                    'high',
                    f'High cognitive complexity: {metrics.cognitive_complexity}',
                    1,
                    'Consider breaking down complex logic into smaller functions'
                )
            )

        # Check maintainability
        if metrics.maintainability_index < 65:
            self.findings.append(
                ReviewFinding(
                    'medium', 
                    'Poor maintainability score',
                    1,
                    'Improve code structure and documentation'
                )
            )

        # Check comment ratio
        if metrics.comment_ratio < 0.1:
            self.findings.append(
                ReviewFinding(
                    'low',
                    'Low comment ratio',
                    1,
                    'Consider adding more documentation'
                )
            )

        # Analyze patterns
        self._check_antipatterns(tree)
        
        return self.findings

    def _calculate_metrics(self, content: str, tree: ast.AST) -> CodeMetrics:
        """Calculate various code quality metrics"""
        # Count lines
        lines = content.splitlines()
        loc = len([l for l in lines if l.strip() and not l.strip().startswith('#')])
        
        # Count comments
        comments = len([l for l in lines if l.strip().startswith('#')])
        comment_ratio = comments / len(lines) if lines else 0

        # Calculate cognitive complexity
        complexity = self._calculate_cognitive_complexity(tree)

        # Calculate maintainability index
        # Using a simplified version of the standard formula
        maintainability = 100 - complexity * 0.25 - loc * 0.05

        return CodeMetrics(
            cognitive_complexity=complexity,
            maintainability_index=maintainability,
            lines_of_code=loc,
            comment_ratio=comment_ratio
        )

    def _calculate_cognitive_complexity(self, tree: ast.AST) -> int:
        """Calculate cognitive complexity score"""
        complexity = 0
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For)):
                complexity += 1
            elif isinstance(node, ast.FunctionDef):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1

        return complexity

    def _check_antipatterns(self, tree: ast.AST) -> None:
        """Check for common anti-patterns"""
        for node in ast.walk(tree):
            # Check for large functions
            if isinstance(node, ast.FunctionDef):
                if len(node.body) > 50:
                    self.findings.append(
                        ReviewFinding(
                            'medium',
                            f'Function {node.name} is too large',
                            node.lineno,
                            'Split into smaller functions'
                        )
                    )

            # Check for nested loops
            if isinstance(node, (ast.For, ast.While)):
                for child in ast.walk(node):
                    if isinstance(child, (ast.For, ast.While)) and child is not node:
                        self.findings.append(
                            ReviewFinding(
                                'medium',
                                'Nested loop detected',
                                child.lineno,
                                'Consider restructuring to reduce nesting'
                            )
                        )

def review_code(file_path: str) -> typing.List[ReviewFinding]:
    """Main entry point for code review"""
    reviewer = CodeReviewer()
    return reviewer.review_file(Path(file_path))