"""
Repository Scanner - Clone and analyze GitHub repositories
"""

import os
import shutil
import tempfile
import subprocess
from pathlib import Path
from code_wiki_generator import RepoAnalyzer


class GitHubRepoScanner:
    """Scan GitHub repositories and generate wiki pages"""
    
    def __init__(self, repo_url: str):
        self.repo_url = repo_url
        self.temp_dir = tempfile.mkdtemp()
        self.repo_name = repo_url.split('/')[-1].replace('.git', '')
    
    def clone_repo(self) -> str:
        """Clone repository to temp directory"""
        try:
            cmd = f"git clone --depth 1 {self.repo_url} {self.temp_dir}"
            subprocess.run(cmd, shell=True, check=True, capture_output=True, timeout=30)
            return self.temp_dir
        except Exception as e:
            raise Exception(f"Failed to clone repo: {str(e)}")
    
    def analyze(self) -> dict:
        """Clone and analyze the repository"""
        try:
            # Clone the repository
            self.clone_repo()
            
            # Analyze it
            analyzer = RepoAnalyzer(self.temp_dir)
            analysis = analyzer.analyze()
            analysis['repo_url'] = self.repo_url
            analysis['repo_name'] = self.repo_name
            
            # Generate wiki pages with repo name prefix
            pages_data = analyzer.generate_wiki_pages()
            
            # Update page titles and slugs to include repo name
            for page in pages_data:
                page['title'] = f"{self.repo_name}: {page['title']}"
                page['slug'] = f"{self.repo_name}-{page['slug']}"
                page['tags'].append(self.repo_name)
            
            return {
                "repo_url": self.repo_url,
                "repo_name": self.repo_name,
                "analysis": analysis,
                "pages": pages_data
            }
        finally:
            # Cleanup temp directory
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
    
    def get_repo_info(self) -> dict:
        """Extract basic repo info from URL"""
        parts = self.repo_url.rstrip('/').split('/')
        return {
            "owner": parts[-2],
            "name": parts[-1].replace('.git', ''),
            "url": self.repo_url
        }
