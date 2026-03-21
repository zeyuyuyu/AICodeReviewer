import os
import openai
from typing import Dict, List, Optional

class AICodeReviewer:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError('OpenAI API key must be provided or set in OPENAI_API_KEY env var')
        openai.api_key = self.api_key

    def review_changes(self, diff: str) -> Dict[str, List[str]]:
        """Review code changes and provide feedback."""
        prompt = f"""As an expert code reviewer, analyze this diff and provide:
        1. Key improvements needed
        2. Potential bugs or security issues
        3. Style/best practice violations
        
        Code diff:
        {diff}
        """

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert code reviewer focused on code quality, security and best practices."},
                {"role": "user", "content": prompt}
            ]
        )

        # Parse response into structured feedback
        feedback = self._parse_review_feedback(response.choices[0].message.content)
        return feedback

    def generate_pr_summary(self, title: str, description: str, diff: str) -> str:
        """Generate a comprehensive PR summary with key changes and impact."""
        prompt = f"""Generate a clear, professional PR summary based on:

Title: {title}
Description: {description}

Code changes:
{diff}

Include:
1. Overview of changes
2. Technical impact
3. Testing considerations
"""

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a technical writer creating clear PR summaries."},
                {"role": "user", "content": prompt}
            ]
        )

        return response.choices[0].message.content

    def _parse_review_feedback(self, raw_feedback: str) -> Dict[str, List[str]]:
        """Parse raw feedback into structured categories."""
        categories = {
            'improvements': [],
            'bugs': [],
            'style': []
        }
        
        current_category = None
        for line in raw_feedback.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            if 'improvements' in line.lower():
                current_category = 'improvements'
            elif 'bugs' in line.lower() or 'security' in line.lower():
                current_category = 'bugs'
            elif 'style' in line.lower() or 'best practice' in line.lower():
                current_category = 'style'
            elif current_category and line.startswith('-'):
                categories[current_category].append(line.lstrip('- '))

        return categories

    def suggest_fixes(self, issue: str, code_context: str) -> str:
        """Suggest specific code fixes for identified issues."""
        prompt = f"""Provide specific code fixes for this issue:
        
Issue: {issue}

Code context:
{code_context}

Provide practical, production-ready code suggestions."""

        response = openai.ChatCompletion.create(
            model="gpt-4", 
            messages=[
                {"role": "system", "content": "You are an expert programmer providing specific code fixes."},
                {"role": "user", "content": prompt}
            ]
        )

        return response.choices[0].message.content