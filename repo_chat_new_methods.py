# These methods should be added to the RepositoryContextBuilder class

def _extract_tech_stack(self):
    """Extract technology stack information"""
    print("  - Analyzing tech stack...")
    tech_stack = {
        "languages": [],
        "frameworks": [],
        "databases": [],
        "tools": [],
        "ui_frameworks": []
    }
    
    # Count files by extension
    file_types = {}
    for file_path in self.repo_path.glob('**/*.*'):
        ext = file_path.suffix.lower()
        if ext and ext.startswith('.'):
            file_types[ext] = file_types.get(ext, 0) + 1
    
    # Detect languages
    if file_types.get('.py', 0) > 0: 
        tech_stack["languages"].append({"name": "Python", "files": file_types.get('.py', 0)})
    if file_types.get('.ts', 0) > 0 or file_types.get('.tsx', 0) > 0: 
        tech_stack["languages"].append({"name": "TypeScript", "files": file_types.get('.ts', 0) + file_types.get('.tsx', 0)})
    if file_types.get('.js', 0) > 0 or file_types.get('.jsx', 0) > 0: 
        tech_stack["languages"].append({"name": "JavaScript", "files": file_types.get('.js', 0) + file_types.get('.jsx', 0)})
    if file_types.get('.go', 0) > 0: 
        tech_stack["languages"].append({"name": "Go", "files": file_types.get('.go', 0)})
    if file_types.get('.java', 0) > 0: 
        tech_stack["languages"].append({"name": "Java", "files": file_types.get('.java', 0)})
    
    # Detect frameworks from dependencies
    for dep in self.context.get("dependencies", []):
        pkg = dep["package"].lower()
        if "flask" in pkg and "Flask" not in tech_stack["frameworks"]: 
            tech_stack["frameworks"].append("Flask")
        if "django" in pkg and "Django" not in tech_stack["frameworks"]: 
            tech_stack["frameworks"].append("Django")
        if "fastapi" in pkg and "FastAPI" not in tech_stack["frameworks"]: 
            tech_stack["frameworks"].append("FastAPI")
        if "express" in pkg and "Express.js" not in tech_stack["frameworks"]: 
            tech_stack["frameworks"].append("Express.js")
        if "react" in pkg and "React" not in tech_stack["ui_frameworks"]: 
            tech_stack["ui_frameworks"].append("React")
        if "vue" in pkg and "Vue.js" not in tech_stack["ui_frameworks"]: 
            tech_stack["ui_frameworks"].append("Vue.js")
        if "angular" in pkg and "Angular" not in tech_stack["ui_frameworks"]: 
            tech_stack["ui_frameworks"].append("Angular")
        if "postgresql" in pkg and "PostgreSQL" not in tech_stack["databases"]: 
            tech_stack["databases"].append("PostgreSQL")
        if "psycopg" in pkg and "PostgreSQL" not in tech_stack["databases"]: 
            tech_stack["databases"].append("PostgreSQL")
        if "mongodb" in pkg and "MongoDB" not in tech_stack["databases"]: 
            tech_stack["databases"].append("MongoDB")
        if "mongoose" in pkg and "MongoDB" not in tech_stack["databases"]: 
            tech_stack["databases"].append("MongoDB")
        if "redis" in pkg and "Redis" not in tech_stack["databases"]: 
            tech_stack["databases"].append("Redis")
        if "mysql" in pkg and "MySQL" not in tech_stack["databases"]: 
            tech_stack["databases"].append("MySQL")
    
    self.context["tech_stack"] = tech_stack

def _extract_architecture(self):
    """Extract technical architecture information"""
    print("  - Analyzing technical architecture...")
    architecture = {
        "layers": [],
        "patterns": [],
        "external_services": [],
        "description": ""
    }
    
    # Detect layers
    dir_names = set()
    try:
        for item in self.repo_path.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                dir_names.add(item.name.lower())
    except:
        pass
    
    if any(x in dir_names for x in ['models', 'model', 'data', 'db', 'database']): 
        architecture["layers"].append("Data Layer")
    if any(x in dir_names for x in ['services', 'business', 'logic', 'core']): 
        architecture["layers"].append("Business Logic Layer")
    if any(x in dir_names for x in ['routes', 'controllers', 'handlers', 'api', 'endpoints']): 
        architecture["layers"].append("API/Route Layer")
    if any(x in dir_names for x in ['middleware']): 
        architecture["layers"].append("Middleware Layer")
    if any(x in dir_names for x in ['utils', 'helpers', 'lib', 'common']): 
        architecture["layers"].append("Utility Layer")
    
    # Detect patterns
    for cls in self.context.get("classes", []):
        name = cls["name"].lower()
        if "factory" in name and "Factory Pattern" not in architecture["patterns"]: 
            architecture["patterns"].append("Factory Pattern")
        if "singleton" in name and "Singleton Pattern" not in architecture["patterns"]: 
            architecture["patterns"].append("Singleton Pattern")
        if "repository" in name or "repo" in name:
            if "Repository Pattern" not in architecture["patterns"]: 
                architecture["patterns"].append("Repository Pattern")
        if "service" in name and "Service Layer" not in architecture["patterns"]: 
            architecture["patterns"].append("Service Layer")
        if "dto" in name and "DTO Pattern" not in architecture["patterns"]: 
            architecture["patterns"].append("DTO Pattern")
    
    # Detect external integrations
    for dep in self.context.get("dependencies", []):
        pkg = dep["package"].lower()
        if "stripe" in pkg and "Stripe Payment" not in architecture["external_services"]: 
            architecture["external_services"].append("Stripe Payment")
        if "slack" in pkg and "Slack API" not in architecture["external_services"]: 
            architecture["external_services"].append("Slack API")
        if "github" in pkg and "GitHub API" not in architecture["external_services"]: 
            architecture["external_services"].append("GitHub API")
        if "aws" in pkg or "boto" in pkg:
            if "AWS" not in architecture["external_services"]: 
                architecture["external_services"].append("AWS")
        if "firebase" in pkg and "Firebase" not in architecture["external_services"]: 
            architecture["external_services"].append("Firebase")
    
    self.context["architecture"] = architecture

def _extract_ux_architecture(self):
    """Extract UX/Frontend architecture information"""
    print("  - Analyzing UX architecture...")
    ux = {
        "frontend_framework": None,
        "styling": [],
        "state_management": [],
        "build_tools": [],
        "component_count": 0,
        "template_count": 0
    }
    
    # Check for frontend files
    try:
        template_count = len(list(self.repo_path.glob('**/templates/**/*.html'))) + len(list(self.repo_path.glob('**/public/**/*.html')))
        component_count = len(list(self.repo_path.glob('**/components/**/*.tsx'))) + len(list(self.repo_path.glob('**/components/**/*.jsx')))
    except:
        template_count = 0
        component_count = 0
    
    # Detect frontend frameworks and tools
    for dep in self.context.get("dependencies", []):
        pkg = dep["package"].lower()
        if "react" in pkg: 
            ux["frontend_framework"] = "React"
        if "vue" in pkg: 
            ux["frontend_framework"] = "Vue.js"
        if "angular" in pkg: 
            ux["frontend_framework"] = "Angular"
        if "svelte" in pkg: 
            ux["frontend_framework"] = "Svelte"
        if "tailwind" in pkg and "Tailwind CSS" not in ux["styling"]: 
            ux["styling"].append("Tailwind CSS")
        if "bootstrap" in pkg and "Bootstrap" not in ux["styling"]: 
            ux["styling"].append("Bootstrap")
        if "styled" in pkg and "Styled Components" not in ux["styling"]: 
            ux["styling"].append("Styled Components")
        if ("sass" in pkg or "scss" in pkg) and "Sass/SCSS" not in ux["styling"]: 
            ux["styling"].append("Sass/SCSS")
        if "redux" in pkg and "Redux" not in ux["state_management"]: 
            ux["state_management"].append("Redux")
        if "vuex" in pkg and "Vuex" not in ux["state_management"]: 
            ux["state_management"].append("Vuex")
        if "zustand" in pkg and "Zustand" not in ux["state_management"]: 
            ux["state_management"].append("Zustand")
        if "webpack" in pkg and "Webpack" not in ux["build_tools"]: 
            ux["build_tools"].append("Webpack")
        if "vite" in pkg and "Vite" not in ux["build_tools"]: 
            ux["build_tools"].append("Vite")
        if "next" in pkg and "Next.js" not in ux["build_tools"]: 
            ux["build_tools"].append("Next.js")
    
    ux["component_count"] = component_count
    ux["template_count"] = template_count
    
    self.context["ux_architecture"] = ux
