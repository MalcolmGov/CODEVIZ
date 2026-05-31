"""
Code Wiki Generator - Auto-generates knowledge base from repository scan
Analyzes code structure, patterns, security, architecture, and APIs
"""

import os
import json
import re
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
import ast


class RepoAnalyzer:
    """Analyzes a repository to generate wiki pages"""
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.analysis = {
            "repo_name": self.repo_path.name,
            "scanned_at": datetime.now().isoformat(),
            "structure": {},
            "dependencies": [],
            "apis": [],
            "security_findings": [],
            "patterns": [],
            "files_analyzed": 0,
            "lines_of_code": 0
        }
    
    def analyze(self) -> Dict:
        """Run full repository analysis"""
        self.analyze_structure()
        self.analyze_dependencies()
        self.analyze_apis()
        self.analyze_code_patterns()
        self.analyze_security()
        return self.analysis
    
    def analyze_structure(self) -> Dict:
        """Analyze repository directory structure"""
        structure = {}
        loc = 0
        
        for root, dirs, files in os.walk(self.repo_path):
            # Skip common ignore patterns
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.env']]
            
            rel_path = os.path.relpath(root, self.repo_path)
            current = structure
            
            for part in rel_path.split(os.sep):
                if part != '.' and part not in current:
                    current[part] = {}
                if part != '.':
                    current = current[part]
            
            for file in files:
                if not file.startswith('.'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', errors='ignore') as f:
                            lines = len(f.readlines())
                            loc += lines
                            current[file] = {
                                "type": "file",
                                "size": os.path.getsize(file_path),
                                "lines": lines,
                                "extension": Path(file).suffix
                            }
                    except:
                        pass
        
        self.analysis["structure"] = structure
        self.analysis["lines_of_code"] = loc
        return structure
    
    def analyze_dependencies(self) -> List:
        """Extract dependencies from requirement files"""
        deps = []
        
        # Python requirements
        req_files = ['requirements.txt', 'setup.py', 'Pipfile', 'pyproject.toml']
        for req_file in req_files:
            req_path = self.repo_path / req_file
            if req_path.exists():
                try:
                    with open(req_path, 'r') as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#'):
                                deps.append({"type": "python", "package": line})
                except:
                    pass
        
        # JavaScript dependencies
        pkg_files = ['package.json']
        for pkg_file in pkg_files:
            pkg_path = self.repo_path / pkg_file
            if pkg_path.exists():
                try:
                    with open(pkg_path, 'r') as f:
                        pkg = json.load(f)
                        for dep, version in pkg.get('dependencies', {}).items():
                            deps.append({"type": "npm", "package": f"{dep}@{version}"})
                except:
                    pass
        
        self.analysis["dependencies"] = deps
        return deps
    
    def analyze_apis(self) -> List:
        """Extract API endpoints from Flask/Express routes"""
        apis = []
        
        # Python Flask
        py_files = list(self.repo_path.glob('**/*.py'))
        for py_file in py_files[:20]:  # Limit to first 20 files
            try:
                with open(py_file, 'r', errors='ignore') as f:
                    content = f.read()
                    
                    # Find Flask routes
                    routes = re.findall(r'@app\.route\(["\']([^"\']+)["\'],\s*methods=\[([^\]]+)\]', content)
                    for route, methods in routes:
                        methods_list = [m.strip().strip('"\'') for m in methods.split(',')]
                        apis.append({
                            "method": methods_list[0] if methods_list else "GET",
                            "path": route,
                            "file": py_file.name
                        })
            except:
                pass
        
        self.analysis["apis"] = apis[:20]  # Top 20 APIs
        return apis
    
    def analyze_code_patterns(self) -> List:
        """Detect common code patterns"""
        patterns = []
        pattern_counts = {}
        
        py_files = list(self.repo_path.glob('**/*.py'))
        for py_file in py_files[:15]:
            try:
                with open(py_file, 'r', errors='ignore') as f:
                    content = f.read()
                    
                    # Detect patterns
                    if 'class ' in content:
                        pattern_counts['OOP/Classes'] = pattern_counts.get('OOP/Classes', 0) + 1
                    if 'def ' in content:
                        pattern_counts['Functional'] = pattern_counts.get('Functional', 0) + 1
                    if '@dataclass' in content or '@property' in content:
                        pattern_counts['Decorators'] = pattern_counts.get('Decorators', 0) + 1
                    if 'async def' in content:
                        pattern_counts['Async/Await'] = pattern_counts.get('Async/Await', 0) + 1
                    if 'try:' in content:
                        pattern_counts['Error Handling'] = pattern_counts.get('Error Handling', 0) + 1
            except:
                pass
        
        for pattern, count in pattern_counts.items():
            patterns.append({"pattern": pattern, "occurrences": count})
        
        self.analysis["patterns"] = patterns
        return patterns
    
    def analyze_security(self) -> List:
        """Check for security issues in code"""
        findings = []
        
        py_files = list(self.repo_path.glob('**/*.py'))
        for py_file in py_files[:20]:
            try:
                with open(py_file, 'r', errors='ignore') as f:
                    content = f.read()
                    
                    # Check for security issues
                    if 'exec(' in content or 'eval(' in content:
                        findings.append({
                            "severity": "CRITICAL",
                            "issue": "Dynamic code execution detected",
                            "file": py_file.name,
                            "fix": "Use safer alternatives or strict validation"
                        })
                    if 'os.system(' in content or 'subprocess' in content:
                        findings.append({
                            "severity": "HIGH",
                            "issue": "Shell command execution",
                            "file": py_file.name,
                            "fix": "Use subprocess with shell=False"
                        })
                    if 'pickle.loads' in content:
                        findings.append({
                            "severity": "CRITICAL",
                            "issue": "Unsafe pickle deserialization",
                            "file": py_file.name,
                            "fix": "Use JSON or safer serialization"
                        })
                    if 'input(' in content and 'eval' in content:
                        findings.append({
                            "severity": "HIGH",
                            "issue": "User input passed to eval",
                            "file": py_file.name,
                            "fix": "Validate and sanitize input"
                        })
            except:
                pass
        
        self.analysis["security_findings"] = findings
        return findings
    
    def generate_wiki_pages(self) -> List[Dict]:
        """Generate wiki page data from analysis"""
        pages = []
        
        # Page 1: Repository Overview
        pages.append({
            "title": f"Repository Overview - {self.analysis['repo_name']}",
            "slug": "repo-overview",
            "type": "architecture",
            "content": f"""# {self.analysis['repo_name']} Repository

## Summary
- **Total Lines of Code:** {self.analysis['lines_of_code']:,}
- **Files Analyzed:** {len(list(self.repo_path.glob('**/*')))}
- **Scanned:** {self.analysis['scanned_at']}

## Key Metrics
- Codebase Size: {self.analysis['lines_of_code']:,} LOC
- Dependencies: {len(self.analysis['dependencies'])}
- API Endpoints: {len(self.analysis['apis'])}
- Security Issues: {len(self.analysis['security_findings'])}

## Code Patterns
{self._format_patterns()}

## Project Structure Overview
This is a {self.analysis['repo_name']} project with {len(self.analysis['dependencies'])} dependencies.
""",
            "description": f"Overview of {self.analysis['repo_name']} - metrics and structure",
            "tags": ["overview", "repository", self.analysis['repo_name']]
        })
        
        # Page 2: Architecture & Structure
        pages.append({
            "title": f"Architecture - {self.analysis['repo_name']}",
            "slug": "repo-architecture",
            "type": "architecture",
            "content": f"""# Architecture Overview

## Directory Structure
```
{self._format_structure()}
```

## Component Breakdown
- **Lines of Code:** {self.analysis['lines_of_code']:,}
- **Dependencies:** {len(self.analysis['dependencies'])}
- **API Routes:** {len(self.analysis['apis'])}

## Code Patterns Used
{self._format_patterns()}
""",
            "description": "Complete architecture and codebase structure",
            "tags": ["architecture", "structure", "codebase"]
        })
        
        # Page 3: Dependencies
        if self.analysis['dependencies']:
            pages.append({
                "title": f"Dependencies - {self.analysis['repo_name']}",
                "slug": "repo-dependencies",
                "type": "api_reference",
                "content": f"""# Project Dependencies

## All Dependencies ({len(self.analysis['dependencies'])})

{self._format_dependencies()}
""",
                "description": f"{len(self.analysis['dependencies'])} dependencies documented",
                "tags": ["dependencies", "packages", "libraries"]
            })
        
        # Page 4: API Endpoints
        if self.analysis['apis']:
            pages.append({
                "title": f"API Endpoints - {self.analysis['repo_name']}",
                "slug": "repo-apis",
                "type": "api_reference",
                "content": f"""# API Endpoints

## All Routes ({len(self.analysis['apis'])})

{self._format_apis()}
""",
                "description": f"{len(self.analysis['apis'])} API endpoints discovered",
                "tags": ["apis", "endpoints", "routes"]
            })
        
        # Page 5: Security Findings
        if self.analysis['security_findings']:
            pages.append({
                "title": f"Security Analysis - {self.analysis['repo_name']}",
                "slug": "repo-security",
                "type": "security_guidelines",
                "content": f"""# Security Findings

## Issues Found: {len(self.analysis['security_findings'])}

{self._format_security_findings()}
""",
                "description": f"{len(self.analysis['security_findings'])} security issues identified",
                "tags": ["security", "vulnerabilities", "analysis"]
            })
        
        return pages
    
    def _format_structure(self, d: Dict = None, prefix: str = "", max_depth: int = 3, current_depth: int = 0) -> str:
        """Format directory structure as tree"""
        if d is None:
            d = self.analysis["structure"]
        
        if current_depth >= max_depth:
            return ""
        
        lines = []
        items = list(d.items())[:10]  # Limit to 10 items per level
        
        for key, value in items:
            if isinstance(value, dict) and value.get('type') == 'file':
                # It's a file
                size = value.get('lines', 0)
                lines.append(f"{prefix}├── {key} ({size} lines)")
            elif isinstance(value, dict):
                # It's a directory
                lines.append(f"{prefix}├── {key}/")
                result = self._format_structure(value, prefix + "│   ", max_depth, current_depth + 1)
                if result:
                    lines.append(result)
        
        return "\n".join(filter(None, lines))
    
    def _format_dependencies(self) -> str:
        """Format dependencies list"""
        if not self.analysis['dependencies']:
            return "No dependencies found"
        
        by_type = {}
        for dep in self.analysis['dependencies']:
            dep_type = dep.get('type', 'other')
            if dep_type not in by_type:
                by_type[dep_type] = []
            by_type[dep_type].append(dep['package'])
        
        output = []
        for dep_type, packages in by_type.items():
            output.append(f"\n### {dep_type.upper()}")
            for pkg in packages[:10]:
                output.append(f"- {pkg}")
            if len(packages) > 10:
                output.append(f"- ... and {len(packages) - 10} more")
        
        return "\n".join(output)
    
    def _format_apis(self) -> str:
        """Format API endpoints"""
        if not self.analysis['apis']:
            return "No API endpoints found"
        
        output = []
        for api in self.analysis['apis']:
            method = api.get('method', 'GET')
            path = api.get('path', '')
            output.append(f"- **{method}** `{path}`")
        
        return "\n".join(output)
    
    def _format_patterns(self) -> str:
        """Format code patterns"""
        if not self.analysis['patterns']:
            return "No patterns detected"
        
        output = []
        for pattern in self.analysis['patterns']:
            output.append(f"- {pattern['pattern']}: {pattern['occurrences']} files")
        
        return "\n".join(output)
    
    def _format_security_findings(self) -> str:
        """Format security findings"""
        if not self.analysis['security_findings']:
            return "✅ No security issues found!"
        
        critical = [f for f in self.analysis['security_findings'] if f['severity'] == 'CRITICAL']
        high = [f for f in self.analysis['security_findings'] if f['severity'] == 'HIGH']
        
        output = []
        
        if critical:
            output.append("## 🔴 CRITICAL")
            for finding in critical:
                output.append(f"- **{finding['issue']}** in {finding['file']}")
                output.append(f"  - Fix: {finding['fix']}")
        
        if high:
            output.append("\n## 🟠 HIGH")
            for finding in high:
                output.append(f"- **{finding['issue']}** in {finding['file']}")
                output.append(f"  - Fix: {finding['fix']}")
        
        return "\n".join(output)


def generate_knowledge_base(repo_path: str, code_wiki_instance) -> List:
    """Generate and add wiki pages from repository analysis"""
    analyzer = RepoAnalyzer(repo_path)
    analysis = analyzer.analyze()
    pages = analyzer.generate_wiki_pages()
    
    # Add pages to wiki
    for page_data in pages:
        code_wiki_instance.create_page(
            title=page_data['title'],
            slug=page_data['slug'],
            page_type=page_data['type'],
            content=page_data['content'],
            description=page_data['description'],
            author="Code Wiki Generator",
            tags=page_data.get('tags', [])
        )
    
    return pages, analysis
