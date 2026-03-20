import difflib
import re
from typing import List, Dict, Tuple

class CodeReviewer:
    def __init__(self):
        self.common_issues = {
            'unused_import': r'^import \w+ as \w+$',
            'todo_comment': r'# TODO',
            'print_debug': r'print\(',
            'bare_except': r'except:'
        }

    def analyze_diff(self, old_content: str, new_content: str) -> List[Dict]:
        """Analyze code changes between versions and provide contextual feedback."""
        diff = list(difflib.unified_diff(
            old_content.splitlines(),
            new_content.splitlines(),
            lineterm=''
        ))
        
        issues = []
        context = []
        current_block = []
        
        for line in diff:
            if line.startswith('@@'):
                if current_block:
                    issues.extend(self._analyze_block(current_block, context))
                current_block = []
                context = []
            elif line.startswith((' ', '+', '-')):
                if line.startswith(' '):
                    context.append(line[1:])
                current_block.append(line)
        
        if current_block:
            issues.extend(self._analyze_block(current_block, context))
            
        return issues

    def _analyze_block(self, block: List[str], context: List[str]) -> List[Dict]:
        """Analyze a single diff block with its surrounding context."""
        issues = []
        
        added_lines = [line[1:] for line in block if line.startswith('+')]
        removed_lines = [line[1:] for line in block if line.startswith('-')]
        
        # Analyze code patterns
        for line in added_lines:
            for issue_type, pattern in self.common_issues.items():
                if re.search(pattern, line):
                    issues.append({
                        'type': issue_type,
                        'line': line,
                        'suggestion': self._get_suggestion(issue_type, line)
                    })
        
        # Analyze structural changes
        if len(added_lines) > 0 and len(removed_lines) > 0:
            similarity = self._calculate_similarity(added_lines[0], removed_lines[0])
            if similarity > 0.8:  # High similarity suggests a minor change
                issues.append(self._analyze_similar_changes(added_lines[0], removed_lines[0]))
        
        return issues

    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity ratio between two strings."""
        return difflib.SequenceMatcher(None, str1, str2).ratio()

    def _analyze_similar_changes(self, new_line: str, old_line: str) -> Dict:
        """Analyze and provide feedback for similar line changes."""
        differences = []
        for i, s in enumerate(difflib.ndiff(old_line, new_line)):
            if s[0] in '+-':
                differences.append(s[2])
        
        return {
            'type': 'minor_change',
            'old_line': old_line,
            'new_line': new_line,
            'differences': ''.join(differences),
            'suggestion': 'Consider if this minor change was intentional'
        }

    def _get_suggestion(self, issue_type: str, line: str) -> str:
        """Get specific suggestion based on the issue type."""
        suggestions = {
            'unused_import': 'Remove unused import or utilize the imported module',
            'todo_comment': 'Consider implementing TODO or creating an issue ticket',
            'print_debug': 'Remove debug print statements in production code',
            'bare_except': 'Specify exception type instead of using bare except'
        }
        return suggestions.get(issue_type, 'Review this line for potential improvements')

    def review_files(self, files: Dict[str, Tuple[str, str]]) -> Dict[str, List[Dict]]:
        """Review multiple files and their changes.
        
        Args:
            files: Dict mapping filenames to tuples of (old_content, new_content)
        """
        results = {}
        for filename, (old, new) in files.items():
            results[filename] = self.analyze_diff(old, new)
        return results