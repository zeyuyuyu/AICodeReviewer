import ast
import typing
from dataclasses import dataclass
from pathlib import Path

@dataclass
class CodeMetrics:
    cyclomatic_complexity: int
    cognitive_complexity: int
    lines_of_code: int
    num_functions: int
    recommendations: list[str]

class CodeReviewer:
    def __init__(self):
        self.complexity_threshold = 10

    def analyze_file(self, file_path: Path) -> CodeMetrics:
        """Analyzes a Python file and returns code quality metrics with recommendations."""
        with open(file_path) as f:
            content = f.read()
        
        tree = ast.parse(content)
        metrics = self._calculate_metrics(tree)
        recommendations = self._generate_recommendations(metrics)
        
        return CodeMetrics(
            cyclomatic_complexity=metrics['cyclomatic'],
            cognitive_complexity=metrics['cognitive'],
            lines_of_code=metrics['loc'],
            num_functions=metrics['functions'],
            recommendations=recommendations
        )
    
    def _calculate_metrics(self, tree: ast.AST) -> dict:
        """Calculates various code complexity metrics from AST."""
        metrics = {
            'cyclomatic': 1,  # Base complexity of 1
            'cognitive': 0,
            'loc': len(tree.body),
            'functions': 0
        }
        
        for node in ast.walk(tree):
            # Count control flow statements for cyclomatic complexity
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                metrics['cyclomatic'] += 1
            elif isinstance(node, ast.BoolOp):
                metrics['cyclomatic'] += len(node.values) - 1
                
            # Count nested structures for cognitive complexity
            if isinstance(node, (ast.If, ast.While, ast.For)):
                metrics['cognitive'] += 1
                
            # Count function definitions
            if isinstance(node, ast.FunctionDef):
                metrics['functions'] += 1
                
        return metrics
    
    def _generate_recommendations(self, metrics: dict) -> list[str]:
        """Generates specific recommendations based on code metrics."""
        recommendations = []
        
        if metrics['cyclomatic'] > self.complexity_threshold:
            recommendations.append(
                f"High cyclomatic complexity ({metrics['cyclomatic']}). Consider breaking down complex functions."
            )
            
        if metrics['cognitive'] > self.complexity_threshold:
            recommendations.append(
                f"High cognitive complexity ({metrics['cognitive']}). Consider simplifying nested logic."
            )
            
        if metrics['loc'] > 300:
            recommendations.append(
                "File is quite long. Consider splitting into multiple modules."
            )
            
        if metrics['functions'] > 10:
            recommendations.append(
                "Large number of functions. Consider grouping related functions into separate classes/modules."
            )
            
        return recommendations

    def review(self, file_path: Path) -> str:
        """Main entry point for code review."""
        try:
            metrics = self.analyze_file(file_path)
            
            report = [f"Code Review Report for {file_path}\n"]
            report.append(f"Lines of Code: {metrics.lines_of_code}")
            report.append(f"Cyclomatic Complexity: {metrics.cyclomatic_complexity}")
            report.append(f"Cognitive Complexity: {metrics.cognitive_complexity}")
            report.append(f"Number of Functions: {metrics.num_functions}\n")
            
            if metrics.recommendations:
                report.append("Recommendations:")
                for i, rec in enumerate(metrics.recommendations, 1):
                    report.append(f"{i}. {rec}")
            else:
                report.append("No specific recommendations - code looks good!")
                
            return '\n'.join(report)
            
        except Exception as e:
            return f"Error analyzing {file_path}: {str(e)}"
