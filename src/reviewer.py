import ast
import typing
from dataclasses import dataclass

@dataclass
class ReviewComment:
    line: int
    message: str
    severity: str  # 'high', 'medium', 'low'

class CodeReviewer:
    def __init__(self):
        self.review_rules = [
            self._check_function_length,
            self._check_complexity,
            self._check_naming,
            self._check_docstrings
        ]

    def review_code(self, code: str) -> typing.List[ReviewComment]:
        """Analyze Python code and return review comments."""
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return [ReviewComment(e.lineno, f'Syntax error: {str(e)}', 'high')]

        comments = []
        for rule in self.review_rules:
            comments.extend(rule(tree))
        return comments

    def _check_function_length(self, tree: ast.AST) -> typing.List[ReviewComment]:
        comments = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                body_lines = len(node.body)
                if body_lines > 20:
                    comments.append(
                        ReviewComment(
                            node.lineno,
                            f'Function {node.name} is {body_lines} lines long. Consider breaking it down.',
                            'medium'
                        )
                    )
        return comments

    def _check_complexity(self, tree: ast.AST) -> typing.List[ReviewComment]:
        comments = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                nested_depth = 0
                for child in ast.walk(node):
                    if isinstance(child, (ast.For, ast.While, ast.If)):
                        nested_depth += 1
                if nested_depth > 3:
                    comments.append(
                        ReviewComment(
                            node.lineno,
                            f'Function {node.name} has high complexity with {nested_depth} nested blocks.',
                            'high'
                        )
                    )
        return comments

    def _check_naming(self, tree: ast.AST) -> typing.List[ReviewComment]:
        comments = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not node.name.islower():
                    comments.append(
                        ReviewComment(
                            node.lineno,
                            f'Function {node.name} should use snake_case naming.',
                            'low'
                        )
                    )
            elif isinstance(node, ast.ClassDef):
                if not node.name[0].isupper():
                    comments.append(
                        ReviewComment(
                            node.lineno,
                            f'Class {node.name} should use PascalCase naming.',
                            'low'
                        )
                    )
        return comments

    def _check_docstrings(self, tree: ast.AST) -> typing.List[ReviewComment]:
        comments = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                if not ast.get_docstring(node):
                    comments.append(
                        ReviewComment(
                            node.lineno,
                            f'Missing docstring for {node.name}.',
                            'medium'
                        )
                    )
        return comments

def review_file(filepath: str) -> typing.List[ReviewComment]:
    """Review a Python source file and return review comments."""
    with open(filepath, 'r') as f:
        code = f.read()
    reviewer = CodeReviewer()
    return reviewer.review_code(code)

def main():
    import sys
    if len(sys.argv) != 2:
        print('Usage: python reviewer.py <file.py>')
        sys.exit(1)
    
    comments = review_file(sys.argv[1])
    for comment in comments:
        print(f'Line {comment.line} - {comment.severity.upper()}: {comment.message}')

if __name__ == '__main__':
    main()