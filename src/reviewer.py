import os
from typing import List, Dict
from dataclasses import dataclass

@dataclass
class CodeReview:
    summary: str
    issues: List[Dict]
    suggestions: List[str]
    code_quality_score: float

class AICodeReviewer:
    def __init__(self, model_name: str = 'gpt-4'):
        self.model_name = model_name
        self.review_patterns = {
            'security': ['eval(', 'exec(', 'os.system('],
            'performance': ['O(n^2)', '.*while True.*'],
            'style': ['\t', '  +']
        }
    
    def review_file(self, file_path: str) -> CodeReview:
        """Perform an AI-powered code review on a single file."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f'File not found: {file_path}')

        with open(file_path, 'r') as f:
            code = f.read()
        
        return self._analyze_code(code)
    
    def _analyze_code(self, code: str) -> CodeReview:
        """Analyze code and generate comprehensive review."""
        issues = []
        suggestions = []
        quality_score = 10.0  # Start with perfect score

        # Analyze code structure
        lines = code.split('\n')
        if len(lines) > 500:
            issues.append({
                'type': 'complexity',
                'message': 'File exceeds recommended length of 500 lines'
            })
            quality_score -= 1.0

        # Check for security issues
        for pattern in self.review_patterns['security']:
            if pattern in code:
                issues.append({
                    'type': 'security',
                    'message': f'Potentially unsafe pattern found: {pattern}'
                })
                quality_score -= 2.0

        # Check code style
        for pattern in self.review_patterns['style']:
            if pattern in code:
                issues.append({
                    'type': 'style',
                    'message': 'Inconsistent indentation detected'
                })
                quality_score -= 0.5

        # Generate improvement suggestions
        if len(issues) > 0:
            suggestions.append('Consider breaking down large files into smaller modules')
            suggestions.append('Implement input validation for potentially unsafe operations')
            suggestions.append('Follow PEP 8 style guidelines for consistent formatting')

        # Ensure quality score stays within bounds
        quality_score = max(0.0, min(10.0, quality_score))

        # Generate summary
        summary = f'Code Review Summary:\n'
        summary += f'- Found {len(issues)} potential issues\n'
        summary += f'- Quality Score: {quality_score}/10\n'
        summary += f'- {len(suggestions)} improvement suggestions provided'

        return CodeReview(
            summary=summary,
            issues=issues,
            suggestions=suggestions,
            code_quality_score=quality_score
        )

    def batch_review(self, file_paths: List[str]) -> Dict[str, CodeReview]:
        """Perform code review on multiple files."""
        reviews = {}
        for file_path in file_paths:
            try:
                reviews[file_path] = self.review_file(file_path)
            except Exception as e:
                print(f'Error reviewing {file_path}: {str(e)}')
        return reviews

def main():
    reviewer = AICodeReviewer()
    review = reviewer.review_file('example.py')
    print(review.summary)
    for issue in review.issues:
        print(f'Issue: {issue["type"]} - {issue["message"]}')

if __name__ == '__main__':
    main()