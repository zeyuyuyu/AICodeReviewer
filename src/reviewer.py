import ast
import typing
from dataclasses import dataclass
from pathlib import Path

@dataclass
class CodeMetrics:
    cognitive_complexity: int
    cyclomatic_complexity: int
    lines_of_code: int
    comment_ratio: float
    function_count: int
    class_count: int

@dataclass 
class ReviewFinding:
    severity: str
    message: str
    line_number: int
    suggestion: str

class CodeReviewer:
    def __init__(self):
        self.complexity_threshold = 15
        self.min_comment_ratio = 0.1

    def analyze_file(self, filepath: Path) -> tuple[CodeMetrics, list[ReviewFinding]]:
        """Analyzes a Python source file and returns metrics and review findings."""
        with open(filepath) as f:
            content = f.read()
        
        tree = ast.parse(content)
        metrics = self._calculate_metrics(tree, content)
        findings = self._generate_findings(metrics, tree)
        
        return metrics, findings

    def _calculate_metrics(self, tree: ast.AST, content: str) -> CodeMetrics:
        """Calculates code quality metrics from AST."""
        visitor = ComplexityVisitor()
        visitor.visit(tree)
        
        lines = content.splitlines()
        comment_lines = sum(1 for line in lines if line.strip().startswith('#'))
        
        return CodeMetrics(
            cognitive_complexity=visitor.cognitive_complexity,
            cyclomatic_complexity=visitor.cyclomatic_complexity,
            lines_of_code=len(lines),
            comment_ratio=comment_lines / len(lines) if lines else 0,
            function_count=len([node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]),
            class_count=len([node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)])
        )

    def _generate_findings(self, metrics: CodeMetrics, tree: ast.AST) -> list[ReviewFinding]:
        """Generates review findings based on metrics and code analysis."""
        findings = []
        
        if metrics.cognitive_complexity > self.complexity_threshold:
            findings.append(ReviewFinding(
                severity='high',
                message=f'Cognitive complexity of {metrics.cognitive_complexity} exceeds threshold of {self.complexity_threshold}',
                line_number=1,
                suggestion='Consider breaking down complex functions into smaller, more manageable pieces'
            ))
            
        if metrics.comment_ratio < self.min_comment_ratio:
            findings.append(ReviewFinding(
                severity='medium',
                message=f'Low comment ratio ({metrics.comment_ratio:.2%})',
                line_number=1,
                suggestion='Add more documentation to improve code maintainability'
            ))
            
        # Analyze function lengths
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if node.end_lineno - node.lineno > 50:
                    findings.append(ReviewFinding(
                        severity='medium',
                        message=f'Function {node.name} is too long ({node.end_lineno - node.lineno} lines)',
                        line_number=node.lineno,
                        suggestion='Consider breaking this function into smaller functions'
                    ))
        
        return findings

class ComplexityVisitor(ast.NodeVisitor):
    def __init__(self):
        self.cognitive_complexity = 0
        self.cyclomatic_complexity = 1  # Base complexity

    def visit_If(self, node):
        self.cognitive_complexity += 1
        self.cyclomatic_complexity += 1
        self.generic_visit(node)

    def visit_While(self, node):
        self.cognitive_complexity += 1
        self.cyclomatic_complexity += 1
        self.generic_visit(node)

    def visit_For(self, node):
        self.cognitive_complexity += 1
        self.cyclomatic_complexity += 1
        self.generic_visit(node)

    def visit_Try(self, node):
        self.cognitive_complexity += 1
        self.cyclomatic_complexity += len(node.handlers)
        self.generic_visit(node)

    def visit_BoolOp(self, node):
        self.cognitive_complexity += len(node.values) - 1
        self.generic_visit(node)