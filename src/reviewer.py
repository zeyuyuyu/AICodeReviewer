import ast
import difflib
from typing import List, Dict

class AICodeReviewer:
    def __init__(self):
        self.changes_detected = []
        self.insights = []

    def analyze_code(self, old_code: str, new_code: str) -> Dict:
        """Analyze code changes and generate review insights."""
        # Parse and analyze code differences
        diff = list(difflib.unified_diff(
            old_code.splitlines(keepends=True),
            new_code.splitlines(keepends=True)
        ))
        
        # Extract key changes
        self.changes_detected = self._parse_changes(diff)
        
        # Generate insights
        self._analyze_changes(old_code, new_code)
        
        return self._generate_review_summary()

    def _parse_changes(self, diff: List[str]) -> List[Dict]:
        """Parse diff output into structured changes."""
        changes = []
        current_change = None
        
        for line in diff:
            if line.startswith('@@'):
                if current_change:
                    changes.append(current_change)
                current_change = {'type': 'modification', 'lines': []}
            elif line.startswith('+'):
                if current_change:
                    current_change['lines'].append(('addition', line[1:]))
            elif line.startswith('-'):
                if current_change:
                    current_change['lines'].append(('deletion', line[1:]))
                    
        if current_change:
            changes.append(current_change)
            
        return changes

    def _analyze_changes(self, old_code: str, new_code: str) -> None:
        """Generate insights from code changes."""
        try:
            old_ast = ast.parse(old_code)
            new_ast = ast.parse(new_code)
            
            # Analyze complexity changes
            old_complexity = self._calculate_complexity(old_ast)
            new_complexity = self._calculate_complexity(new_ast)
            
            if new_complexity > old_complexity:
                self.insights.append({
                    'type': 'warning',
                    'message': 'Code complexity has increased'
                })
            
            # Analyze function changes
            old_functions = self._extract_functions(old_ast)
            new_functions = self._extract_functions(new_ast)
            
            # Check for function signature changes
            for func_name in set(old_functions) & set(new_functions):
                if old_functions[func_name] != new_functions[func_name]:
                    self.insights.append({
                        'type': 'info',
                        'message': f'Function signature changed: {func_name}'
                    })
                    
        except SyntaxError:
            self.insights.append({
                'type': 'error',
                'message': 'Invalid syntax detected in code'
            })

    def _calculate_complexity(self, tree: ast.AST) -> int:
        """Calculate code complexity score."""
        complexity = 0
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.For, ast.While, ast.FunctionDef)):
                complexity += 1
        return complexity

    def _extract_functions(self, tree: ast.AST) -> Dict:
        """Extract function definitions and their signatures."""
        functions = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                args = [arg.arg for arg in node.args.args]
                functions[node.name] = args
        return functions

    def _generate_review_summary(self) -> Dict:
        """Generate final review summary with insights."""
        return {
            'summary': {
                'total_changes': len(self.changes_detected),
                'insights': self.insights,
                'recommendation': self._generate_recommendation()
            }
        }

    def _generate_recommendation(self) -> str:
        """Generate overall recommendation based on insights."""
        if any(insight['type'] == 'error' for insight in self.insights):
            return 'NEEDS_REVISION'
        elif any(insight['type'] == 'warning' for insight in self.insights):
            return 'REVIEW_REQUIRED'
        return 'LOOKS_GOOD'
