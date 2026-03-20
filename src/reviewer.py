import os
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

class SeverityLevel(Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

@dataclass
class CodeReviewSuggestion:
    line_number: int
    message: str
    severity: SeverityLevel
    suggested_fix: Optional[str] = None

class AICodeReviewer:
    def __init__(self, model_name: str = "gpt-3.5-turbo"):
        self.model_name = model_name
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable must be set")

    def review_file(self, file_path: str) -> List[CodeReviewSuggestion]:
        """Review a single file and return a list of suggestions."""
        with open(file_path, 'r') as f:
            content = f.read()
        return self.review_code(content)

    def review_code(self, code: str) -> List[CodeReviewSuggestion]:
        """Analyze code and return review suggestions with severity levels."""
        # TODO: Implement actual LLM call here
        suggestions = []

        # Example static analysis rules (to be replaced with LLM)
        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            # Check for long lines
            if len(line) > 100:
                suggestions.append(
                    CodeReviewSuggestion(
                        line_number=i,
                        message="Line exceeds 100 characters",
                        severity=SeverityLevel.LOW
                    )
                )

            # Check for TODO comments
            if 'TODO' in line:
                suggestions.append(
                    CodeReviewSuggestion(
                        line_number=i,
                        message="TODO comment found - consider implementing or removing",
                        severity=SeverityLevel.MEDIUM
                    )
                )

            # Check for potential security issues
            if 'eval(' in line or 'exec(' in line:
                suggestions.append(
                    CodeReviewSuggestion(
                        line_number=i,
                        message="Potentially dangerous code execution detected",
                        severity=SeverityLevel.HIGH,
                        suggested_fix="Consider using safer alternatives to eval/exec"
                    )
                )

        return suggestions

    def format_suggestions(self, suggestions: List[CodeReviewSuggestion]) -> str:
        """Format review suggestions into a readable report."""
        if not suggestions:
            return "No issues found!"

        report = ["Code Review Report:\n"]
        for suggestion in sorted(suggestions, key=lambda x: x.severity.value):
            report.append(
                f"[{suggestion.severity.value}] Line {suggestion.line_number}: {suggestion.message}")
            if suggestion.suggested_fix:
                report.append(f"  Suggestion: {suggestion.suggested_fix}")

        return '\n'.join(report)

    def review_and_report(self, file_path: str) -> str:
        """Convenience method to review a file and get formatted results."""
        suggestions = self.review_file(file_path)
        return self.format_suggestions(suggestions)

def main():
    reviewer = AICodeReviewer()
    # Example usage
    result = reviewer.review_and_report("example.py")
    print(result)

if __name__ == "__main__":
    main()
