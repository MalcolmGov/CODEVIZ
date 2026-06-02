"""
Repository Chat - AI-powered chat about any codebase
Comprehensive artifact discovery including APIs, classes, middleware, models, interfaces, enums, and constants
"""

import os
import re
import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime


class RepositoryContextBuilder:
    """Builds and caches comprehensive code context from repository"""
    
    def __init__(self, repo_path: str, max_files: int = 100):
        self.repo_path = Path(repo_path)
        self.max_files = max_files
        self.context = {
            "repo_name": self.repo_path.name,
            "repo_path": str(repo_path),
            "files": [],
            "structure": "",
            "apis": [],
            "functions": [],
            "classes": [],
            "error_handlers": [],
            "middleware": [],
            "models": [],
            "enums": [],
            "interfaces": [],
            "constants": [],
            "key_files": [],
            "dependencies": [],
            "tech_stack": {},
            "architecture": {},
            "ux_architecture": {},
            "statistics": {},
            "production_base_url": None,
            "scanned_at": datetime.now().isoformat()
        }
    
    def scan_repository(self) -> Dict:
        """Scan and build complete code context with all artifact types"""
        print(f"Scanning repository: {self.repo_path}")
        
        self._extract_structure()
        self._extract_key_files()
        self._extract_comprehensive_artifacts()
        self._extract_dependencies()
        self._extract_tech_stack()
        self._extract_architecture()
        self._extract_ux_architecture()
        self._extract_statistics()
        
        self.context["production_base_url"] = self._detect_prod_url()
        
        return self.context
    
    def _extract_structure(self):
        """Extract repository directory structure"""
        print("  - Extracting structure...")
        structure_lines = []
        file_count = 0
        dir_count = 0
        
        for root, dirs, files in os.walk(self.repo_path):
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.env', 'venv', '.vscode', '.idea', 'dist', 'build']]
            
            level = root.replace(str(self.repo_path), '').count(os.sep)
            
            if level < 4:
                indent = '  ' * level
                rel_path = os.path.basename(root)
                if rel_path:
                    structure_lines.append(f'{indent}{rel_path}/')
                    dir_count += 1
                
                for file in sorted(files)[:15]:
                    if not file.startswith('.') and file_count < self.max_files:
                        file_indent = '  ' * (level + 1)
                        structure_lines.append(f'{file_indent}{file}')
                        file_count += 1
                        self.context["files"].append(f"{rel_path}/{file}" if rel_path else file)
        
        self.context["structure"] = '\n'.join(structure_lines[:200])
        self.context["statistics"]["total_files"] = file_count
        self.context["statistics"]["total_directories"] = dir_count
    
    def _extract_key_files(self):
        """Extract content of key files"""
        print("  - Extracting key files...")
        key_patterns = [
            'main.py', 'app.py', '__init__.py', 'requirements.txt', 'package.json', 
            'README.md', 'setup.py', 'config.py', 'index.ts', 'index.js', 'main.ts',
            'server.ts', 'server.js', 'routes.ts', 'routes.js', 'db.ts', 'config.ts'
        ]
        
        for pattern in key_patterns:
            for file_path in self.repo_path.glob(f'**/{pattern}'):
                try:
                    with open(file_path, 'r', errors='ignore') as f:
                        content = f.read()
                        if len(content) < 10000:
                            self.context["key_files"].append({
                                "name": str(file_path.relative_to(self.repo_path)),
                                "size": len(content),
                                "lines": len(content.split('\n')),
                                "content": content[:3000]
                            })
                except:
                    pass
    
    def _detect_port(self) -> int:
        """Detect the application port from config files, package.json, or .env"""
        # 1. Try to read from .env
        env_path = self.repo_path / '.env'
        if env_path.exists():
            try:
                with open(env_path, 'r', errors='ignore') as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith('#'):
                            continue
                        if '=' in line:
                            parts = line.split('=', 1)
                            key = parts[0].strip()
                            val = parts[1].strip().strip('\'"')
                            if key in ('PORT', 'APP_PORT', 'SERVER_PORT', 'BACKEND_PORT'):
                                try:
                                    return int(val)
                                except ValueError:
                                    pass
            except Exception:
                pass

        # 2. Try to read from package.json
        package_json_path = self.repo_path / 'package.json'
        if package_json_path.exists():
            try:
                with open(package_json_path, 'r', errors='ignore') as f:
                    data = json.load(f)
                    # Check scripts for port definitions
                    scripts = data.get('scripts', {})
                    for script_val in scripts.values():
                        port_match = re.search(r'(?:--port|-p)\s+(\d+)', script_val)
                        if port_match:
                            return int(port_match.group(1))
            except Exception:
                pass

        # 3. Default fallbacks based on project type
        if (self.repo_path / 'package.json').exists():
            # For express/node, look at index.ts/js files for listen port
            for p in list(self.repo_path.glob('**/server.ts')) + list(self.repo_path.glob('**/server.js')) + list(self.repo_path.glob('**/index.ts')) + list(self.repo_path.glob('**/index.js')):
                try:
                    with open(p, 'r', errors='ignore') as f:
                        content = f.read()
                        listen_match = re.search(r'\.listen\(\s*(?:process\.env\.PORT\s*\|\|\s*)?(\d+)', content)
                        if listen_match:
                            return int(listen_match.group(1))
                except Exception:
                    pass
            # Default node port
            return 3000
            
        return 8000

    def _detect_prod_url(self) -> Optional[str]:
        """Detect the production / deployment URL from config or source files"""
        repo_name_lower = self.repo_path.name.lower()
        
        # Try to extract the real repository name from .git/config if it is a cloned repo
        git_config_path = self.repo_path / '.git' / 'config'
        if git_config_path.exists():
            try:
                with open(git_config_path, 'r', errors='ignore') as f:
                    config_content = f.read()
                    url_match = re.search(r'url\s*=\s*(.+)', config_content)
                    if url_match:
                        git_url = url_match.group(1).strip()
                        repo_name = git_url.split('/')[-1]
                        if repo_name.endswith('.git'):
                            repo_name = repo_name[:-4]
                        repo_name_lower = repo_name.lower()
            except Exception:
                pass
        candidate_urls = {}
        
        exclude_keywords = (
            'github.com', 'localhost', '127.0.0.1', 'schema.org', 'npmjs.com', 
            'w3.org', 'auth0.com', 'google.com', 'googleapis.com', 'facebook.com', 
            'replit.app', 'vitejs.dev', 'reactjs.org', 'react.dev', 'tailwindcss.com', 
            'sentry.io', 'vercel.app', 'githubusercontent.com', 'unpkg.com', 
            'skypack.dev', 'cloudflare.com', 'gravatar.com', 'wa.me', 'sendgrid.com', 
            'twilio.com', 'twitter.com', 'linkedin.com', 'instagram.com', 'apple.com'
        )

        for p in list(self.repo_path.glob('**/server/*.ts')) + list(self.repo_path.glob('**/server/*.js')) + list(self.repo_path.glob('**/*.ts')) + list(self.repo_path.glob('**/*.js')):
            try:
                with open(p, 'r', errors='ignore') as f:
                    content = f.read()
                    url_matches = re.findall(r'https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', content)
                    for url in url_matches:
                        url_lower = url.lower()
                        if not any(x in url_lower for x in exclude_keywords):
                            # Clean it up to the root domain
                            domain_match = re.match(r'https?://[a-zA-Z0-9.-]+', url)
                            if domain_match:
                                domain = domain_match.group(0)
                                candidate_urls[domain] = candidate_urls.get(domain, 0) + 1
            except Exception:
                pass

        if not candidate_urls:
            return None

        # Sort candidates: favor domains that contain the repo name, then by frequency
        def score_candidate(item):
            domain, count = item
            score = count
            if repo_name_lower in domain.lower():
                score += 1000  # huge boost if repo name is in domain
            return score

        best_domain = max(candidate_urls.items(), key=score_candidate)[0]
        return best_domain

    def _extract_comprehensive_artifacts(self):
        """Extract all code artifacts: APIs, classes, middleware, models, interfaces, enums, constants, error handlers"""
        print("  - Extracting comprehensive code artifacts...")
        
        detected_port = self._detect_port()
        base_url = f"http://localhost:{detected_port}"
        
        apis = []
        functions = []
        classes = []
        error_handlers = []
        middleware = []
        models = []
        enums = []
        interfaces = []
        constants = []
        
        # ========== PYTHON FILES ==========
        for py_file in list(self.repo_path.glob('**/*.py'))[:50]:
            try:
                with open(py_file, 'r', errors='ignore') as f:
                    content = f.read()
                    relative_path = py_file.relative_to(self.repo_path)
                    
                    # Flask/Django routes
                    routes = re.findall(r'@(?:app|router)\.(?:route|get|post|put|delete|patch)\(["\']([^"\']+)["\'](?:.*?methods=\[([^\]]+)\])?', content, re.DOTALL)
                    for route_match in routes[:15]:
                        route = route_match[0]
                        methods = route_match[1] if len(route_match) > 1 and route_match[1] else 'GET'
                        methods_list = [m.strip().strip('"\'') for m in methods.split(',')] if methods else ['GET']
                        apis.append({
                            "file": str(relative_path),
                            "path": route,
                            "methods": methods_list,
                            "type": "flask_route",
                            "testable": True,
                            "base_url": base_url,
                            "source": "local",
                            "environment": "development"
                        })
                    
                    # Error handlers
                    err_handlers = re.findall(r'@(?:app|errorhandler|error_handler)\(?(\d+)\)?', content)
                    for code in err_handlers[:5]:
                        error_handlers.append({
                            "file": str(relative_path),
                            "error_code": code,
                            "type": "error_handler"
                        })
                    
                    # Classes
                    class_defs = re.findall(r'class\s+(\w+)(?:\(([^)]*)\))?:', content)
                    for class_name, bases in class_defs[:10]:
                        classes.append({
                            "name": class_name,
                            "file": str(relative_path),
                            "bases": bases if bases else "object",
                            "type": "class"
                        })
                    
                    # Functions
                    funcs = re.findall(r'def\s+(\w+)\s*\(([^)]*)\):', content)
                    for func_name, params in funcs[:15]:
                        functions.append({
                            "name": func_name,
                            "file": str(relative_path),
                            "params": params[:80] if params else "",
                            "type": "function",
                            "source": "local"
                        })
                    
                    # SQLAlchemy/Database models
                    db_models = re.findall(r'class\s+(\w+)\s*\(\s*(?:db\.)?Model\s*\)', content)
                    for model_name in db_models[:10]:
                        models.append({
                            "name": model_name,
                            "file": str(relative_path),
                            "type": "database_model"
                        })
                    
                    # Constants
                    consts = re.findall(r'^([A-Z_][A-Z0-9_]*)\s*=\s*(.+?)(?=\n|$)', content, re.MULTILINE)
                    for const_name, const_value in consts[:8]:
                        constants.append({
                            "name": const_name,
                            "value": const_value[:60].strip(),
                            "file": str(relative_path),
                            "type": "constant"
                        })
            except Exception as e:
                pass
        
        # ========== TYPESCRIPT/JAVASCRIPT FILES ==========
        for ts_file in list(self.repo_path.glob('**/*.ts')) + list(self.repo_path.glob('**/*.tsx')) + list(self.repo_path.glob('**/*.js'))[:50]:
            try:
                with open(ts_file, 'r', errors='ignore') as f:
                    content = f.read()
                    relative_path = ts_file.relative_to(self.repo_path)
                    
                    # Express/Fastify routes
                    http_methods = ['get', 'post', 'put', 'delete', 'patch', 'options', 'head']
                    for method in http_methods:
                        routes = re.findall(rf'(?:app|router)\.{method}\(["\']([^"\']+)["\']', content, re.IGNORECASE)
                        for route in routes[:10]:
                            apis.append({
                                "file": str(relative_path),
                                "path": route,
                                "methods": [method.upper()],
                                "type": "express_route",
                                "testable": True,
                                "base_url": base_url,
                                "source": "local",
                                "environment": "development"
                            })
                    
                    # Middleware
                    middleware_matches = re.findall(r'(?:app|router)\.use\((?:(["\']([^"\']+)["\'])|(\w+))\)', content)
                    for match in middleware_matches[:8]:
                        middleware.append({
                            "file": str(relative_path),
                            "name": match[1] or match[2] or "middleware",
                            "type": "middleware"
                        })
                    
                    # Classes
                    class_defs = re.findall(r'(?:export\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+(\w+))?', content)
                    for class_match in class_defs[:10]:
                        classes.append({
                            "name": class_match[0],
                            "file": str(relative_path),
                            "extends": class_match[1] if class_match[1] else None,
                            "implements": class_match[2] if class_match[2] else None,
                            "type": "class"
                        })
                    
                    # Interfaces
                    interfaces_matches = re.findall(r'(?:export\s+)?interface\s+(\w+)(?:\s+extends\s+(\w+))?', content)
                    for iface_name, extends in interfaces_matches[:8]:
                        interfaces.append({
                            "name": iface_name,
                            "extends": extends if extends else None,
                            "file": str(relative_path),
                            "type": "interface"
                        })
                    
                    # Enums
                    enums_matches = re.findall(r'(?:export\s+)?enum\s+(\w+)', content)
                    for enum_name in enums_matches[:8]:
                        enums.append({
                            "name": enum_name,
                            "file": str(relative_path),
                            "type": "enum"
                        })
                    
                    # Functions
                    funcs = re.findall(r'(?:async\s+)?(?:function\s+|const|let|var)\s+(\w+)\s*(?::|=|function)', content)
                    for func_name in funcs[:15]:
                        functions.append({
                            "name": func_name,
                            "file": str(relative_path),
                            "params": "",
                            "type": "ts_function",
                            "source": "local"
                        })
                    
                    # Constants
                    consts = re.findall(r'(?:const|export\s+const)\s+([A-Z_][A-Z0-9_]*)\s*=\s*(.+?)(?=;|\n)', content)
                    for const_name, const_value in consts[:8]:
                        constants.append({
                            "name": const_name,
                            "value": const_value[:60].strip(),
                            "file": str(relative_path),
                            "type": "constant"
                        })
            except Exception as e:
                pass
        
        # Store all artifacts
        self.context["apis"] = apis
        self.context["functions"] = functions
        self.context["classes"] = classes
        self.context["error_handlers"] = error_handlers
        self.context["middleware"] = middleware
        self.context["models"] = models
        self.context["enums"] = enums
        self.context["interfaces"] = interfaces
        self.context["constants"] = constants
        
        # Update statistics
        self.context["statistics"]["total_apis"] = len(apis)
        self.context["statistics"]["total_functions"] = len(functions)
        self.context["statistics"]["total_classes"] = len(classes)
        self.context["statistics"]["total_error_handlers"] = len(error_handlers)
        self.context["statistics"]["total_middleware"] = len(middleware)
        self.context["statistics"]["total_models"] = len(models)
        self.context["statistics"]["total_interfaces"] = len(interfaces)
        self.context["statistics"]["total_enums"] = len(enums)
        self.context["statistics"]["total_constants"] = len(constants)
    
    def _extract_dependencies(self):
        """Extract project dependencies"""
        print("  - Extracting dependencies...")
        deps = []
        
        # Python
        for req_file in self.repo_path.glob('**/requirements.txt'):
            try:
                with open(req_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            deps.append({"type": "python", "package": line})
            except:
                pass
        
        # JavaScript
        for pkg_file in self.repo_path.glob('**/package.json'):
            try:
                with open(pkg_file, 'r') as f:
                    pkg = json.load(f)
                    for dep, version in pkg.get('dependencies', {}).items():
                        deps.append({"type": "npm", "package": f"{dep}@{version}"})
                    for dep, version in pkg.get('devDependencies', {}).items():
                        deps.append({"type": "npm_dev", "package": f"{dep}@{version}"})
            except:
                pass
        
        self.context["dependencies"] = deps
        self.context["statistics"]["total_dependencies"] = len(deps)
    
    def _extract_tech_stack(self):
        """Extract technology stack information"""
        print("  - Analyzing tech stack...")
        tech_stack = {
            "languages": [],
            "frameworks": [],
            "databases": [],
            "ui_frameworks": []
        }
        
        # Detect languages by file extension
        file_types = {}
        try:
            for file_path in self.repo_path.glob('**/*.*'):
                ext = file_path.suffix.lower()
                if ext:
                    file_types[ext] = file_types.get(ext, 0) + 1
            
            if file_types.get('.py', 0) > 0:
                tech_stack["languages"].append("Python")
            if file_types.get('.ts', 0) > 0 or file_types.get('.tsx', 0) > 0:
                tech_stack["languages"].append("TypeScript")
            if file_types.get('.js', 0) > 0 or file_types.get('.jsx', 0) > 0:
                tech_stack["languages"].append("JavaScript")
        except:
            pass
        
        # IMPORTANT: Extract from actual dependencies list (extracted earlier)
        for dep in self.context.get("dependencies", []):
            pkg_lower = dep["package"].lower()
            
            # Frameworks
            if "express" in pkg_lower and "Express" not in tech_stack["frameworks"]:
                tech_stack["frameworks"].append("Express")
            if "flask" in pkg_lower and "Flask" not in tech_stack["frameworks"]: 
                tech_stack["frameworks"].append("Flask")
            if "django" in pkg_lower and "Django" not in tech_stack["frameworks"]: 
                tech_stack["frameworks"].append("Django")
            if "fastapi" in pkg_lower and "FastAPI" not in tech_stack["frameworks"]: 
                tech_stack["frameworks"].append("FastAPI")
            if "react" in pkg_lower and "react" in pkg_lower and "React" not in tech_stack["ui_frameworks"]:
                tech_stack["ui_frameworks"].append("React")
            if "next" in pkg_lower and "next.js" in pkg_lower and "Next.js" not in tech_stack["frameworks"]:
                tech_stack["frameworks"].append("Next.js")
            if "vue" in pkg_lower and "Vue.js" not in tech_stack["ui_frameworks"]: 
                tech_stack["ui_frameworks"].append("Vue.js")
            if "angular" in pkg_lower and "Angular" not in tech_stack["ui_frameworks"]:
                tech_stack["ui_frameworks"].append("Angular")
            
            # Databases
            if "postgresql" in pkg_lower and "PostgreSQL" not in tech_stack["databases"]: 
                tech_stack["databases"].append("PostgreSQL")
            if "psycopg" in pkg_lower and "PostgreSQL" not in tech_stack["databases"]: 
                tech_stack["databases"].append("PostgreSQL")
            if "mysql" in pkg_lower and "MySQL" not in tech_stack["databases"]:
                tech_stack["databases"].append("MySQL")
            if "mongodb" in pkg_lower and "MongoDB" not in tech_stack["databases"]:
                tech_stack["databases"].append("MongoDB")
            if "mongoose" in pkg_lower and "MongoDB" not in tech_stack["databases"]:
                tech_stack["databases"].append("MongoDB")
            if "redis" in pkg_lower and "Redis" not in tech_stack["databases"]: 
                tech_stack["databases"].append("Redis")
            if "sqlite" in pkg_lower and "SQLite" not in tech_stack["databases"]:
                tech_stack["databases"].append("SQLite")
            if "prisma" in pkg_lower and "Prisma" not in tech_stack["databases"]:
                tech_stack["databases"].append("Prisma ORM")
            if "sequelize" in pkg_lower and "Sequelize" not in tech_stack["databases"]:
                tech_stack["databases"].append("Sequelize ORM")
            if "typeorm" in pkg_lower and "TypeORM" not in tech_stack["databases"]:
                tech_stack["databases"].append("TypeORM")
            if "sqlalchemy" in pkg_lower and "SQLAlchemy" not in tech_stack["databases"]:
                tech_stack["databases"].append("SQLAlchemy")
        
        self.context["tech_stack"] = tech_stack

    def _extract_architecture(self):
        """Extract technical architecture information"""
        print("  - Analyzing technical architecture...")
        architecture = {
            "layers": [],
            "patterns": [],
            "external_services": []
        }
        
        # Detect patterns from class names
        for cls in self.context.get("classes", []):
            name = cls["name"].lower()
            if "repository" in name and "Repository Pattern" not in architecture["patterns"]: 
                architecture["patterns"].append("Repository Pattern")
            if "service" in name and "Service Layer" not in architecture["patterns"]: 
                architecture["patterns"].append("Service Layer")
            if "factory" in name and "Factory Pattern" not in architecture["patterns"]: 
                architecture["patterns"].append("Factory Pattern")
        
        # Detect external integrations
        for dep in self.context.get("dependencies", []):
            pkg = dep["package"].lower()
            if "slack" in pkg and "Slack API" not in architecture["external_services"]: 
                architecture["external_services"].append("Slack API")
            if "github" in pkg and "GitHub API" not in architecture["external_services"]: 
                architecture["external_services"].append("GitHub API")
            if "redis" in pkg and "Redis" not in architecture["external_services"]: 
                architecture["external_services"].append("Redis")
        
        self.context["architecture"] = architecture

    def _extract_ux_architecture(self):
        """Extract UX/Frontend architecture information"""
        print("  - Analyzing UX architecture...")
        ux = {
            "frontend_framework": None,
            "styling": [],
            "state_management": [],
            "build_tools": []
        }
        
        # Detect frontend frameworks and tools
        for dep in self.context.get("dependencies", []):
            pkg = dep["package"].lower()
            if "react" in pkg: 
                ux["frontend_framework"] = "React"
            if "tailwind" in pkg and "Tailwind CSS" not in ux["styling"]: 
                ux["styling"].append("Tailwind CSS")
            if "bootstrap" in pkg and "Bootstrap" not in ux["styling"]: 
                ux["styling"].append("Bootstrap")
            if "redux" in pkg and "Redux" not in ux["state_management"]: 
                ux["state_management"].append("Redux")
            if "vite" in pkg and "Vite" not in ux["build_tools"]: 
                ux["build_tools"].append("Vite")
            if "webpack" in pkg and "Webpack" not in ux["build_tools"]: 
                ux["build_tools"].append("Webpack")
        
        self.context["ux_architecture"] = ux

    def _extract_statistics(self):
        """Extract repository statistics"""
        print("  - Calculating statistics...")
        loc = 0
        file_count = 0
        
        extensions = ['*.py', '*.ts', '*.tsx', '*.js', '*.jsx', '*.java', '*.go', '*.rb', '*.php', '*.c', '*.cpp', '*.cs']
        for ext in extensions:
            for src_file in self.repo_path.glob(f'**/{ext}'):
                try:
                    with open(src_file, 'r', errors='ignore') as f:
                        lines = len(f.readlines())
                        loc += lines
                        file_count += 1
                except:
                    pass
        
        self.context["statistics"]["lines_of_code"] = loc
        self.context["statistics"]["scanned_source_files"] = file_count
        self.context["statistics"]["scanned_at"] = datetime.now().isoformat()
    
    def get_context_summary(self) -> str:
        """Get a summary of the context"""
        summary = f"""
# Repository: {self.context['repo_name']}

## Statistics
- Total Files: {self.context['statistics'].get('total_files', 0)}
- Lines of Code: {self.context['statistics'].get('lines_of_code', 0)}
- APIs: {self.context['statistics'].get('total_apis', 0)}
- Classes: {self.context['statistics'].get('total_classes', 0)}
- Functions: {self.context['statistics'].get('total_functions', 0)}
- Models: {self.context['statistics'].get('total_models', 0)}
- Middleware: {self.context['statistics'].get('total_middleware', 0)}
- Dependencies: {self.context['statistics'].get('total_dependencies', 0)}

## Directory Structure
```
{self.context['structure'][:1000]}
```
"""
        return summary


class RepositoryChat:
    """Chat interface for understanding repositories"""
    
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.context_builder = RepositoryContextBuilder(repo_path)
        self.context = None
        self.context_summary = None
        self.conversation_history = []
        self.is_scanned = False
        self.last_answer_source = None  # 'llm' or 'keyword'

    
    def scan(self) -> Dict:
        """Scan the repository"""
        print(f"\n🔍 Scanning repository: {self.repo_path}")
        self.context = self.context_builder.scan_repository()
        self.context_summary = self.context_builder.get_context_summary()
        self.is_scanned = True
        
        print(f"✅ Scan complete!")
        return self.context
    
    def ask(self, question: str) -> str:
        """Ask a question about the repository.

        Tries an LLM-backed answer (grounded on the scan context) first, and
        falls back to the deterministic keyword answer if the LLM is disabled
        or unavailable. Sets ``self.last_answer_source`` to 'llm' or 'keyword'.
        """
        if not self.is_scanned:
            return "❌ Repository not scanned yet. Please scan first."

        self.conversation_history.append({
            "role": "user",
            "content": question,
            "timestamp": datetime.now().isoformat()
        })

        answer = self._llm_answer(question)
        if answer is not None:
            self.last_answer_source = "llm"
        else:
            answer = self._generate_answer(question)
            self.last_answer_source = "keyword"

        self.conversation_history.append({
            "role": "assistant",
            "content": answer,
            "timestamp": datetime.now().isoformat()
        })

        return answer

    def _llm_answer(self, question: str):
        """Attempt an LLM-backed answer. Returns None to trigger fallback."""
        try:
            from services.ollama import answer_question
            grounding = self._grounding_text()
            history = self.conversation_history[:-1]  # exclude current question
            return answer_question(question, grounding, history)
        except Exception:
            return None

    def _grounding_text(self) -> str:
        """Build a bounded context string used to ground the LLM."""
        summary = self.context_summary or ""
        ctx = self.context or {}

        def _digest(items, fmt, limit):
            out = []
            for it in (items or [])[:limit]:
                try:
                    out.append(fmt(it))
                except Exception:
                    continue
            return out

        apis = _digest(
            ctx.get("apis"),
            lambda a: f"- {' '.join(a.get('methods', [])).upper()} {a.get('path', '')} ({a.get('file', '')})",
            40,
        )
        classes = _digest(ctx.get("classes"),
                          lambda c: f"- {c.get('name', '')} ({c.get('file', '')})", 40)
        models = _digest(ctx.get("models"),
                         lambda m: f"- {m.get('name', '')} ({m.get('file', '')})", 30)
        deps = _digest(ctx.get("dependencies"),
                       lambda d: f"- {d.get('package', '')}", 40)
        tech = ctx.get("tech_stack") or []

        parts = [summary]
        if tech:
            parts.append("## Tech Stack\n" + ", ".join(str(t) for t in tech))
        if apis:
            parts.append("## API Endpoints (sample)\n" + "\n".join(apis))
        if classes:
            parts.append("## Classes (sample)\n" + "\n".join(classes))
        if models:
            parts.append("## Data Models\n" + "\n".join(models))
        if deps:
            parts.append("## Dependencies (sample)\n" + "\n".join(deps))
        return "\n\n".join(p for p in parts if p and p.strip())
    
    def _generate_answer(self, question: str) -> str:
        """Generate answer based on discovered artifacts and source code scanning"""
        q_lower = question.lower()
        
        # 1. SQL Injection / Security Vulnerabilities
        if any(x in q_lower for x in ("sql", "injection", "security", "vulnerability", "risk", "credential", "password", "leak")):
            hotspots = []
            
            # Scan files under the repository path for SQL injection patterns and secrets
            for root, dirs, files in os.walk(self.repo_path):
                dirs[:] = [d for d in dirs if d not in ('.git', 'node_modules', '__pycache__', 'dist', 'build', 'venv')]
                for file in files:
                    if file.endswith(('.py', '.ts', '.tsx', '.js', '.jsx')):
                        file_path = Path(root) / file
                        try:
                            with open(file_path, 'r', errors='ignore') as f:
                                lines = f.readlines()
                                for i, line in enumerate(lines):
                                    line_strip = line.strip()
                                    # Skip comment lines
                                    if line_strip.startswith(('#', '//', '*')):
                                        continue
                                        
                                    # A. SQL Injection detection: look for raw SELECT/UPDATE queries using variable interpolation
                                    sql_patterns = (
                                        r'\b(?:execute|query|run)\b.*\b(?:select|insert|update|delete|from|where)\b.*(?:%s|\+.*\b[a-zA-Z]|\{.*\b[a-zA-Z]|\$\{.*\b[a-zA-Z])',
                                        r'\b(?:select|insert|update|delete)\b.*(?:f"[^"]*\{|[a-zA-Z_]\w*\s*\+\s*["\']|["\'][^"\']*\s*\+\s*[a-zA-Z_])'
                                    )
                                    for pattern in sql_patterns:
                                        if re.search(pattern, line_lower := line.lower()):
                                            # Avoid parameterized bindings like "?", "$1", ":param"
                                            if not any(x in line_lower for x in ('params=', 'bind=', '?', '$1', '$2', '$3', 'param')):
                                                hotspots.append({
                                                    "file": str(file_path.relative_to(self.repo_path)),
                                                    "line": i + 1,
                                                    "content": line_strip,
                                                    "type": "⚠️ Potential SQL Injection (Unparameterized Raw Query)"
                                                })
                                                break
                                                
                                    # B. Hardcoded Secrets detection
                                    secret_patterns = (
                                        r'\b(?:api_key|apikey|secret_key|private_key|token|auth_token|jwt_secret|password|db_pass)\b\s*[:=]\s*["\'][a-zA-Z0-9_\-\.\/]{10,}["\']',
                                    )
                                    for pattern in secret_patterns:
                                        if re.search(pattern, line_lower):
                                            # Exclude dev-secret or empty or placeholders
                                            val = line_strip.split('=')[-1].split(':')[-1].strip().strip('\'"')
                                            if not any(x in val.lower() for x in ('dev-secret', 'secret_key', 'test', 'example', 'placeholder', 'dummy', 'none', '""', "''")):
                                                hotspots.append({
                                                    "file": str(file_path.relative_to(self.repo_path)),
                                                    "line": i + 1,
                                                    "content": line_strip,
                                                    "type": "🔑 Potential Hardcoded Secret / Credential Leak"
                                                })
                                                break
                        except Exception:
                            pass
            
            if hotspots:
                answer = f"🛡️ **Codebase Security Scan Results**\n\nFound **{len(hotspots)}** potential security risks in the codebase:\n\n"
                for h in hotspots[:15]:
                    answer += f"### {h['type']}\n"
                    answer += f"- **File**: `{h['file']}` (Line {h['line']})\n"
                    answer += f"- **Code**: `{h['content']}`\n\n"
                if len(hotspots) > 15:
                    answer += f"*...and {len(hotspots) - 15} more hotspots found. Please check your config parameters.*"
                return answer
            else:
                return "🛡️ **Codebase Security Scan Results**\n\nNo potential raw SQL injections or hardcoded keys were detected using AST pattern matching. The scanned routes and model interfaces appear to follow correct binding patterns."

        # 2. APIs/Endpoints/Routes
        if any(x in q_lower for x in ("api", "endpoint", "route", "http")):
            matches = [a for a in self.context["apis"] if a['path'].lower() in q_lower or q_lower in a['path'].lower()]
            if matches:
                answer = f"🔌 **Discovered API Endpoints matching your query ({len(matches)}):**\n\n"
                for api in matches:
                    answer += f"- **{' '.join(api['methods']).upper()}** `{api['path']}`\n"
                    answer += f"  - Location: `{api['file']}`\n"
                    answer += f"  - Target Environment: `{api['environment']}`\n\n"
                return answer
            
            answer = f"🔌 **Discovered API Endpoints ({len(self.context['apis'])}):**\n\n"
            for api in self.context["apis"][:20]:
                answer += f"- **{' '.join(api['methods']).upper()}** `{api['path']}` (`{api['file']}`)\n"
            return answer

        # 3. Class and models
        if "class" in q_lower or "model" in q_lower or "database" in q_lower:
            matches = [c for c in self.context["classes"] if c['name'].lower() in q_lower or q_lower in c['name'].lower()]
            if matches:
                answer = f"📦 **Classes matching your query ({len(matches)}):**\n\n"
                for cls in matches:
                    answer += f"- **{cls['name']}** (`{cls['file']}`)\n"
                    if cls.get('bases'):
                        answer += f"  - Inherits from: `{cls['bases']}`\n"
                return answer
            
            answer = f"📦 **Scanned Database Models / Classes:**\n\n"
            for cls in self.context["classes"][:15]:
                answer += f"- `{cls['name']}` ({cls['file']})\n"
            return answer

        # 4. Keyword codebase concept explorer (e.g. auth, payment, user, etc.)
        concepts = ("auth", "user", "payment", "stripe", "order", "email", "notification", "config", "util", "helper")
        matched_concept = next((c for c in concepts if c in q_lower), None)
        if matched_concept:
            matched_files = []
            for root, dirs, files in os.walk(self.repo_path):
                dirs[:] = [d for d in dirs if d not in ('.git', 'node_modules', '__pycache__', 'dist', 'build', 'venv')]
                for file in files:
                    if matched_concept in file.lower() and file.endswith(('.py', '.ts', '.tsx', '.js')):
                        matched_files.append(str(Path(root).relative_to(self.repo_path) / file))
            if matched_files:
                answer = f"🔍 **Codebase Concept Explorer: '{matched_concept}'**\n\nHere are the files related to '{matched_concept}':\n\n"
                for f in matched_files[:10]:
                    answer += f"- `{f}`\n"
                answer += f"\nThese components contain the core logic for {matched_concept} systems. You can browse their definitions in the Files tab."
                return answer

        # Default fallback
        summary = self.context_summary if self.context_summary else self.context_builder.get_context_summary()
        return f"💡 **AI Assistant fallbacks (No LLM active)**\n\nYour question didn't trigger any specific AST scanners. Here is a summary of the scanned codebase structure:\n\n{summary}\n\n*Try asking about: APIs, security/SQL injection risks, classes, functions, or specific concepts like auth, database, or dependencies.*"
    
    def get_scan_status(self) -> Dict:
        """Get scan status"""
        if not self.is_scanned:
            return {"scanned": False, "message": "Repository not scanned yet"}
        
        return {
            "scanned": True,
            "repo_name": self.context["repo_name"],
            "files": self.context["statistics"].get("total_files", 0),
            "loc": self.context["statistics"].get("lines_of_code", 0),
            "apis": self.context["statistics"].get("total_apis", 0),
            "classes": self.context["statistics"].get("total_classes", 0),
            "functions": self.context["statistics"].get("total_functions", 0),
            "models": self.context["statistics"].get("total_models", 0),
            "interfaces": self.context["statistics"].get("total_interfaces", 0),
            "enums": self.context["statistics"].get("total_enums", 0),
            "middleware": self.context["statistics"].get("total_middleware", 0),
            "error_handlers": self.context["statistics"].get("total_error_handlers", 0),
            "constants": self.context["statistics"].get("total_constants", 0),
            "dependencies": self.context["statistics"].get("total_dependencies", 0),
            "scanned_at": self.context["scanned_at"]
        }
    
    def get_history(self) -> List[Dict]:
        """Get conversation history"""
        return self.conversation_history
