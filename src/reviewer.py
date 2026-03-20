import ast
import typing
from dataclasses import dataclass
from pathlib import Path

@dataclass
class CodeIssue:
    line_number: int
    message: str
    severity: str  # 'error', 'warning', or 'info'
    suggestion: str

class CodeReviewer:
    def __init__(self):
        self.issues: typing.List[CodeIssue] = []

    def review_file(self, filepath: Path) -> typing.List[CodeIssue]:
        """Analyze a Python file for code quality issues"""
        with open(filepath, 'r') as f:
            content = f.read()
        
        try:
            tree = ast.parse(content)
            self._analyze_complexity(tree)
            self._check_naming_conventions(tree)
            self._detect_anti_patterns(tree)
            return self.issues
        except SyntaxError as e:
            self.issues.append(CodeIssue(
                line_number=e.lineno or 0,
                message=f'Syntax error: {str(e)}',
                severity='error',
                suggestion='Fix the syntax error to proceed with analysis'
            ))
            return self.issues

    def _analyze_complexity(self, tree: ast.AST) -> None:
        """Analyze code complexity metrics"""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check function length
                if len(node.body) > 20:
                    self.issues.append(CodeIssue(
                        line_number=node.lineno,
                        message=f'Function {node.name} is too long ({len(node.body)} lines)',
                        severity='warning',
                        suggestion='Consider breaking this function into smaller, more focused functions'
                    ))
                
                # Check number of arguments
                if len(node.args.args) > 5:
                    self.issues.append(CodeIssue(
                        line_number=node.lineno,
                        message=f'Function {node.name} has too many parameters ({len(node.args.args)})',
                        severity='warning',
                        suggestion='Consider grouping related parameters into a class or data structure'
                    ))

    def _check_naming_conventions(self, tree: ast.AST) -> None:
        """Check Python naming conventions"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if not node.name[0].isupper():
                    self.issues.append(CodeIssue(
                        line_number=node.lineno,
                        message=f'Class name {node.name} should use CapWords convention',
                        severity='info',
                        suggestion=f'Rename to {node.name[0].upper() + node.name[1:]}'
                    ))
            elif isinstance(node, ast.FunctionDef):
                if not node.name.islower():
                    self.issues.append(CodeIssue(
                        line_number=node.lineno,
                        message=f'Function name {node.name} should use lowercase_with_underscores convention',
                        severity='info',
                        suggestion=f'Rename to {node.name.lower()}'
                    ))

    def _detect_anti_patterns(self, tree: ast.AST) -> None:
        """Detect common anti-patterns"""
        for node in ast.walk(tree):
            # Detect bare except clauses
            if isinstance(node, ast.ExceptHandler) and node.type is None:
                self.issues.append(CodeIssue(
                    line_number=node.lineno,
                    message='Bare except clause detected',
                    severity='error',
                    suggestion='Specify the exception types you want to catch'
                ))
            
            # Detect mutable default arguments
            if isinstance(node, ast.FunctionDef):
                for default in node.args.defaults:
                    if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                        self.issues.append(CodeIssue(
                            line_number=node.lineno,
                            message='Mutable default argument detected',
                            severity='warning',
                            suggestion='Use None as default and initialize mutable objects inside the function'
                        ))

def review_code(filepath: str) -> typing.List[CodeIssue]:
    """Main entry point for code review"""
    reviewer = CodeReviewer()
    return reviewer.review_file(Path(filepath))
