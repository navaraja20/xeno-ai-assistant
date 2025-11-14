"""
GitHub automation module for XENO AI Assistant.
Handles repository management, README updates, issues, and more.
"""

from github import Github, GithubException
from typing import List, Dict, Optional
import logging
from datetime import datetime

logger = logging.getLogger("XENO.GitHubManager")


class GitHubManager:
    """Handles all GitHub automation tasks."""
    
    def __init__(self, username: str, token: str):
        """
        Initialize GitHub manager.
        
        Args:
            username: GitHub username
            token: Personal access token (PAT)
        """
        self.username = username
        self.token = token
        self.github = Github(token)
        self.user = None
        logger.info(f"GitHubManager initialized for {username}")
    
    def connect(self) -> bool:
        """Verify connection to GitHub."""
        try:
            self.user = self.github.get_user()
            logger.info(f"Connected to GitHub as {self.user.login}")
            return True
        except GithubException as e:
            logger.error(f"Failed to connect to GitHub: {e}")
            return False
    
    def get_repositories(self, include_private: bool = True) -> List[Dict]:
        """
        Get list of user's repositories.
        
        Args:
            include_private: Include private repositories
            
        Returns:
            List of repository dictionaries
        """
        try:
            if not self.user:
                self.connect()
            
            repos = []
            for repo in self.user.get_repos():
                if not include_private and repo.private:
                    continue
                
                repos.append({
                    'name': repo.name,
                    'full_name': repo.full_name,
                    'description': repo.description or '',
                    'url': repo.html_url,
                    'stars': repo.stargazers_count,
                    'forks': repo.forks_count,
                    'language': repo.language or 'Unknown',
                    'private': repo.private,
                    'created': repo.created_at.isoformat(),
                    'updated': repo.updated_at.isoformat()
                })
            
            logger.info(f"Retrieved {len(repos)} repositories")
            return repos
            
        except GithubException as e:
            logger.error(f"Error getting repositories: {e}")
            return []
    
    def create_repository(self, name: str, description: str = '', 
                         private: bool = False, auto_init: bool = True) -> Optional[Dict]:
        """
        Create a new repository.
        
        Args:
            name: Repository name
            description: Repository description
            private: Make repository private
            auto_init: Initialize with README
            
        Returns:
            Repository data if successful
        """
        try:
            if not self.user:
                self.connect()
            
            repo = self.user.create_repo(
                name=name,
                description=description,
                private=private,
                auto_init=auto_init
            )
            
            logger.info(f"Created repository: {repo.full_name}")
            return {
                'name': repo.name,
                'full_name': repo.full_name,
                'url': repo.html_url,
                'private': repo.private
            }
            
        except GithubException as e:
            logger.error(f"Failed to create repository: {e}")
            return None
    
    def update_readme(self, repo_name: str, content: str, commit_message: str = "Update README") -> bool:
        """
        Update repository README file.
        
        Args:
            repo_name: Repository name (e.g., "username/repo")
            content: New README content
            commit_message: Commit message
            
        Returns:
            True if successful
        """
        try:
            repo = self.github.get_repo(repo_name)
            
            # Get existing README
            try:
                readme = repo.get_contents("README.md")
                repo.update_file(
                    path="README.md",
                    message=commit_message,
                    content=content,
                    sha=readme.sha
                )
            except GithubException:
                # README doesn't exist, create it
                repo.create_file(
                    path="README.md",
                    message=commit_message,
                    content=content
                )
            
            logger.info(f"Updated README for {repo_name}")
            return True
            
        except GithubException as e:
            logger.error(f"Failed to update README: {e}")
            return False
    
    def get_issues(self, repo_name: str, state: str = 'open') -> List[Dict]:
        """
        Get issues from a repository.
        
        Args:
            repo_name: Repository name
            state: Issue state ('open', 'closed', 'all')
            
        Returns:
            List of issues
        """
        try:
            repo = self.github.get_repo(repo_name)
            issues = []
            
            for issue in repo.get_issues(state=state):
                # Skip pull requests (they show up as issues)
                if issue.pull_request:
                    continue
                
                issues.append({
                    'number': issue.number,
                    'title': issue.title,
                    'body': issue.body or '',
                    'state': issue.state,
                    'author': issue.user.login,
                    'created': issue.created_at.isoformat(),
                    'updated': issue.updated_at.isoformat(),
                    'comments': issue.comments,
                    'url': issue.html_url
                })
            
            logger.info(f"Retrieved {len(issues)} issues from {repo_name}")
            return issues
            
        except GithubException as e:
            logger.error(f"Error getting issues: {e}")
            return []
    
    def create_issue(self, repo_name: str, title: str, body: str = '', 
                    labels: List[str] = None) -> Optional[Dict]:
        """
        Create a new issue.
        
        Args:
            repo_name: Repository name
            title: Issue title
            body: Issue body
            labels: List of label names
            
        Returns:
            Issue data if successful
        """
        try:
            repo = self.github.get_repo(repo_name)
            
            issue = repo.create_issue(
                title=title,
                body=body,
                labels=labels or []
            )
            
            logger.info(f"Created issue #{issue.number} in {repo_name}")
            return {
                'number': issue.number,
                'title': issue.title,
                'url': issue.html_url
            }
            
        except GithubException as e:
            logger.error(f"Failed to create issue: {e}")
            return None
    
    def close_issue(self, repo_name: str, issue_number: int, comment: str = '') -> bool:
        """
        Close an issue.
        
        Args:
            repo_name: Repository name
            issue_number: Issue number
            comment: Optional closing comment
            
        Returns:
            True if successful
        """
        try:
            repo = self.github.get_repo(repo_name)
            issue = repo.get_issue(issue_number)
            
            if comment:
                issue.create_comment(comment)
            
            issue.edit(state='closed')
            
            logger.info(f"Closed issue #{issue_number} in {repo_name}")
            return True
            
        except GithubException as e:
            logger.error(f"Failed to close issue: {e}")
            return False
    
    def get_pull_requests(self, repo_name: str, state: str = 'open') -> List[Dict]:
        """
        Get pull requests from a repository.
        
        Args:
            repo_name: Repository name
            state: PR state ('open', 'closed', 'all')
            
        Returns:
            List of pull requests
        """
        try:
            repo = self.github.get_repo(repo_name)
            prs = []
            
            for pr in repo.get_pulls(state=state):
                prs.append({
                    'number': pr.number,
                    'title': pr.title,
                    'body': pr.body or '',
                    'state': pr.state,
                    'author': pr.user.login,
                    'created': pr.created_at.isoformat(),
                    'updated': pr.updated_at.isoformat(),
                    'url': pr.html_url,
                    'mergeable': pr.mergeable
                })
            
            logger.info(f"Retrieved {len(prs)} pull requests from {repo_name}")
            return prs
            
        except GithubException as e:
            logger.error(f"Error getting pull requests: {e}")
            return []
    
    def get_user_stats(self) -> Dict:
        """
        Get user statistics.
        
        Returns:
            Dictionary with user stats
        """
        try:
            if not self.user:
                self.connect()
            
            repos = list(self.user.get_repos())
            
            total_stars = sum(repo.stargazers_count for repo in repos)
            total_forks = sum(repo.forks_count for repo in repos)
            
            stats = {
                'username': self.user.login,
                'name': self.user.name or self.user.login,
                'bio': self.user.bio or '',
                'public_repos': self.user.public_repos,
                'followers': self.user.followers,
                'following': self.user.following,
                'total_stars': total_stars,
                'total_forks': total_forks,
                'created': self.user.created_at.isoformat()
            }
            
            logger.info("Retrieved user stats")
            return stats
            
        except GithubException as e:
            logger.error(f"Error getting user stats: {e}")
            return {}
    
    def search_repositories(self, query: str, language: str = None, 
                          max_results: int = 20) -> List[Dict]:
        """
        Search GitHub repositories.
        
        Args:
            query: Search query
            language: Filter by programming language
            max_results: Maximum results to return
            
        Returns:
            List of repository results
        """
        try:
            search_query = query
            if language:
                search_query += f" language:{language}"
            
            repos = []
            for repo in self.github.search_repositories(search_query)[:max_results]:
                repos.append({
                    'name': repo.name,
                    'full_name': repo.full_name,
                    'description': repo.description or '',
                    'url': repo.html_url,
                    'stars': repo.stargazers_count,
                    'language': repo.language or 'Unknown',
                    'owner': repo.owner.login
                })
            
            logger.info(f"Found {len(repos)} repositories for '{query}'")
            return repos
            
        except GithubException as e:
            logger.error(f"Error searching repositories: {e}")
            return []
    
    def star_repository(self, repo_name: str) -> bool:
        """Star a repository."""
        try:
            if not self.user:
                self.connect()
            
            repo = self.github.get_repo(repo_name)
            self.user.add_to_starred(repo)
            
            logger.info(f"Starred repository: {repo_name}")
            return True
            
        except GithubException as e:
            logger.error(f"Failed to star repository: {e}")
            return False
    
    def unstar_repository(self, repo_name: str) -> bool:
        """Unstar a repository."""
        try:
            if not self.user:
                self.connect()
            
            repo = self.github.get_repo(repo_name)
            self.user.remove_from_starred(repo)
            
            logger.info(f"Unstarred repository: {repo_name}")
            return True
            
        except GithubException as e:
            logger.error(f"Failed to unstar repository: {e}")
            return False
