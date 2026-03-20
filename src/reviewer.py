import os
import requests
from typing import List, Dict
from dataclasses import dataclass

@dataclass
class CodeDiff:
    filename: str
    changes: str
    added_lines: List[str]
    removed_lines: List[str]

@dataclass
class ReviewComment:
    path: str
    line: int
    body: str

class AICodeReviewer:
    def __init__(self, github_token: str, openai_key: str):
        self.github_token = github_token
        self.openai_key = openai_key
        self.github_headers = {
            'Authorization': f'token {github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }

    def get_pr_diff(self, repo: str, pr_number: int) -> List[CodeDiff]:
        """Fetch the PR diff from GitHub API"""
        url = f'https://api.github.com/repos/{repo}/pulls/{pr_number}'
        response = requests.get(f'{url}/files', headers=self.github_headers)
        response.raise_for_status()
        
        diffs = []
        for file in response.json():
            added = [line[1:] for line in file['patch'].split('\n') if line.startswith('+')]
            removed = [line[1:] for line in file['patch'].split('\n') if line.startswith('-')]
            diffs.append(CodeDiff(
                filename=file['filename'],
                changes=file['patch'],
                added_lines=added,
                removed_lines=removed
            ))
        return diffs

    def analyze_diff(self, diff: CodeDiff) -> List[ReviewComment]:
        """Generate review comments using LLM analysis"""
        prompt = f"""Review this code change and provide specific, actionable feedback:
        File: {diff.filename}
        Changes:
        {diff.changes}
        
        Focus on:
        1. Potential bugs or errors
        2. Security concerns
        3. Performance implications
        4. Code style and best practices
        5. Maintainability issues
        
        Format each issue as: <line_number>: <comment>"""

        # Call OpenAI API
        headers = {'Authorization': f'Bearer {self.openai_key}'}
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers=headers,
            json={
                'model': 'gpt-4',
                'messages': [{'role': 'user', 'content': prompt}],
                'temperature': 0.7
            }
        )
        response.raise_for_status()
        
        # Parse LLM response into ReviewComments
        comments = []
        for line in response.json()['choices'][0]['message']['content'].split('\n'):
            if ':' in line:
                line_num, comment = line.split(':', 1)
                try:
                    comments.append(ReviewComment(
                        path=diff.filename,
                        line=int(line_num),
                        body=comment.strip()
                    ))
                except ValueError:
                    continue
        return comments

    def review_pr(self, repo: str, pr_number: int) -> List[ReviewComment]:
        """Review a complete PR and return all review comments"""
        all_comments = []
        diffs = self.get_pr_diff(repo, pr_number)
        
        for diff in diffs:
            comments = self.analyze_diff(diff)
            all_comments.extend(comments)
            
        return all_comments

    def post_review(self, repo: str, pr_number: int, comments: List[ReviewComment]):
        """Post review comments to GitHub PR"""
        url = f'https://api.github.com/repos/{repo}/pulls/{pr_number}/reviews'
        
        review_body = 'AI Code Review Comments:\n\n'
        review_comments = []
        
        for comment in comments:
            review_body += f'* {comment.path} line {comment.line}: {comment.body}\n'
            review_comments.append({
                'path': comment.path,
                'line': comment.line,
                'body': comment.body
            })
        
        data = {
            'commit_id': self.get_pr_head_sha(repo, pr_number),
            'body': review_body,
            'event': 'COMMENT',
            'comments': review_comments
        }
        
        response = requests.post(url, headers=self.github_headers, json=data)
        response.raise_for_status()
        
    def get_pr_head_sha(self, repo: str, pr_number: int) -> str:
        """Get the HEAD SHA for the PR"""
        url = f'https://api.github.com/repos/{repo}/pulls/{pr_number}'
        response = requests.get(url, headers=self.github_headers)
        response.raise_for_status()
        return response.json()['head']['sha']
