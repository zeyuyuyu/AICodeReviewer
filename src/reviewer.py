import ast
from typing import Dict, List, Tuple

class CodeReviewer:
    def __init__(self):
        self.metrics = {
            'complexity': 0,
            'maintainability': 0,
            'documentation': 0
        }

    def analyze_code(self, code: str) -> Dict:
        """Analyze code and return comprehensive review results."""
        try:
            tree = ast.parse(code)
            review_results = {
                'metrics': self._calculate_metrics(tree),
                'suggestions': self._generate_suggestions(tree),
                'code_smells': self._detect_code_smells(tree)
            }
            return review_results
        except SyntaxError as e:
            return {'error': f'Syntax error in code: {str(e)}'}

    def _calculate_metrics(self, tree: ast.AST) -> Dict:
        """Calculate code quality metrics."""
        metrics = {
            'complexity': self._calculate_complexity(tree),
            'lines_of_code': len(ast.unparse(tree).splitlines()),
            'function_count': len([node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]),
            'class_count': len([node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]),
            'comment_ratio': self._calculate_comment_ratio(tree)
        }
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

    def _calculate_comment_ratio(self, tree: ast.AST) -> float:
        """Calculate ratio of comments to code."""
        code_lines = len(ast.unparse(tree).splitlines())
        comment_lines = len([node for node in ast.walk(tree) if isinstance(node, ast.Expr) 
                            and isinstance(node.value, ast.Str)])
        return comment_lines / code_lines if code_lines > 0 else 0

    def _generate_suggestions(self, tree: ast.AST) -> List[str]:
        """Generate improvement suggestions based on code analysis."""
        suggestions = []
        
        # Check for long functions
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if len(node.body) > 15:
                    suggestions.append(f'Consider breaking down function "{node.name}" into smaller functions')
                if len(node.args.args) > 5:
                    suggestions.append(f'Function "{node.name}" has too many parameters. Consider refactoring')

        # Check for nested complexity
        self._check_nesting(tree, suggestions)
        
        return suggestions

    def _check_nesting(self, tree: ast.AST, suggestions: List[str], max_depth: int = 3) -> None:
        """Check for deeply nested code."""
        def get_nesting_level(node, current_depth=0):
            if isinstance(node, (ast.If, ast.For, ast.While)):
                current_depth += 1
                if current_depth > max_depth:
                    suggestions.append(f'Deep nesting detected. Consider refactoring to reduce complexity')
            for child in ast.iter_child_nodes(node):
                get_nesting_level(child, current_depth)
                
        get_nesting_level(tree)

    def _detect_code_smells(self, tree: ast.AST) -> List[str]:
        """Detect common code smells."""
        smells = []
        
        # Check for large classes
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                method_count = len([n for n in node.body if isinstance(n, ast.FunctionDef)])
                if method_count > 10:
                    smells.append(f'Class "{node.name}" might violate Single Responsibility Principle')

        # Check for duplicate code (simplified)
        seen_code = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                code = ast.unparse(node)
                if code in seen_code:
                    smells.append(f'Possible code duplication in function "{node.name}"')
                seen_code.add(code)

        return smells

    def generate_report(self, review_results: Dict) -> str:
        """Generate a formatted report from review results."""
        report = ["=== Code Review Report ==="]
        
        # Add metrics section
        report.append("\nCode Metrics:")
        for metric, value in review_results.get('metrics', {}).items():
            report.append(f"- {metric}: {value}")

        # Add suggestions section
        report.append("\nSuggestions:")
        for suggestion in review_results.get('suggestions', []):
            report.append(f"- {suggestion}")

        # Add code smells section
        report.append("\nCode Smells:")
        for smell in review_results.get('code_smells', []):
            report.append(f"- {smell}")

        return '\n'.join(report)
