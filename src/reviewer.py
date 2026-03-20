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
    maintainability_index: float

@dataclass 
class ReviewFinding:
    severity: str
    message: str
    line: int
    recommendation: str

class CodeReviewer:
    def __init__(self):
        self.metrics = None
        self.findings = []

    def analyze_file(self, filepath: Path) -> typing.Tuple[CodeMetrics, list[ReviewFinding]]:
        """Analyze a Python source file and return metrics and review findings."""
        with open(filepath) as f:
            content = f.read()
        
        # Parse AST
        tree = ast.parse(content)
        
        # Calculate metrics
        self.metrics = self._calculate_metrics(content, tree)
        
        # Generate findings
        self.findings = []
        self._check_complexity(tree)
        self._check_naming(tree)
        self._check_best_practices(tree)
        
        return self.metrics, self.findings

    def _calculate_metrics(self, content: str, tree: ast.AST) -> CodeMetrics:
        lines = len(content.splitlines())
        functions = len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)])
        classes = len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)])
        comments = len([l for l in content.splitlines() if l.strip().startswith('#')])
        
        # Calculate cyclomatic complexity
        complexity = 1
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        
        # Simple maintainability index calculation
        maintainability = 100 - (complexity * 0.5 + lines * 0.1)
        
        return CodeMetrics(
            complexity=complexity,
            lines=lines,
            functions=functions,
            classes=classes,
            comments=comments,
            maintainability_index=maintainability
        )

    def _check_complexity(self, tree: ast.AST) -> None:
        """Check for complexity issues"""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if len(node.body) > 50:
                    self.findings.append(ReviewFinding(
                        severity='high',
                        message=f'Function {node.name} is too long',
                        line=node.lineno,
                        recommendation='Consider breaking down into smaller functions'
                    ))

    def _check_naming(self, tree: ast.AST) -> None:
        """Check naming conventions"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if not node.name[0].isupper():
                    self.findings.append(ReviewFinding(
                        severity='medium',
                        message=f'Class {node.name} should use CapWords convention',
                        line=node.lineno,
                        recommendation='Rename using CapWords style'
                    ))

    def _check_best_practices(self, tree: ast.AST) -> None:
        """Check Python best practices"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Compare):
                if isinstance(node.ops[0], (ast.Is, ast.IsNot)) and \
                   isinstance(node.comparators[0], ast.Constant) and \
                   node.comparators[0].value in (True, False, None):
                    self.findings.append(ReviewFinding(
                        severity='low',
                        message='Use == instead of is for literal comparisons',
                        line=node.lineno,
                        recommendation='Replace is with == for comparing with literals'
                    ))

def review_code(filepath: str) -> str:
    """Main entry point for code review"""
    reviewer = CodeReviewer()
    metrics, findings = reviewer.analyze_file(Path(filepath))
    
    report = [f"Code Review Report for {filepath}\n"]
    report.append("\nMetrics:")
    report.append(f"- Complexity: {metrics.complexity}")
    report.append(f"- Lines: {metrics.lines}")
    report.append(f"- Functions: {metrics.functions}")
    report.append(f"- Classes: {metrics.classes}")
    report.append(f"- Comments: {metrics.comments}")
    report.append(f"- Maintainability Index: {metrics.maintainability_index:.1f}/100\n")
    
    if findings:
        report.append("\nFindings:")
        for finding in findings:
            report.append(f"\n[{finding.severity.upper()}] Line {finding.line}")
            report.append(f"Message: {finding.message}")
            report.append(f"Recommendation: {finding.recommendation}")
    
    return '\n'.join(report)
