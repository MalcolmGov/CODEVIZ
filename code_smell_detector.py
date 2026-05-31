"""
Code Smell Detection Engine
Detects: Dead Code, Duplicates, Complexity, Magic Numbers, Unused Variables
"""

import re
from typing import List, Dict, Tuple, Set
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

class SmellType(Enum):
    DEAD_CODE = "Dead Code"
    DUPLICATE_CODE = "Duplicate Code"
    HIGH_COMPLEXITY = "High Complexity"
    MAGIC_NUMBER = "Magic Number"
    UNUSED_VARIABLE = "Unused Variable"
    LONG_METHOD = "Long Method"
    GOD_CLASS = "God Class (Too Many Methods)"
    DEEP_NESTING = "Deep Nesting"

class SmellSeverity(Enum):
    MINOR = "🟢 MINOR"
    MEDIUM = "🟡 MEDIUM"
    MAJOR = "🟠 MAJOR"

@dataclass
class CodeSmell:
    smell_id: str
    smell_type: SmellType
    severity: SmellSeverity
    file_path: str
    line_number: int
    code_snippet: str
    description: str
    impact: str
    refactor_suggestion: str
    effort: str  # Low, Medium, High
    
    def to_dict(self):
        return {
            'smell_id': self.smell_id,
            'type': self.smell_type.value,
            'severity': self.severity.value,
            'file': self.file_path,
            'line': self.line_number,
            'code': self.code_snippet,
            'description': self.description,
            'impact': self.impact,
            'refactor': self.refactor_suggestion,
            'effort': self.effort
        }

class CodeSmellDetector:
    """Detects code smells and quality issues"""
    
    def __init__(self):
        self.smell_counter = 0
        self.file_cache = {}
        self.duplicate_blocks = {}
    
    def scan_files(self, directory: str, file_pattern: str = "*.py") -> List[CodeSmell]:
        """Scan directory for code smells"""
        smells = []
        path = Path(directory)
        
        python_files = list(path.glob(f"**/{file_pattern}"))
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', errors='ignore') as f:
                    code = f.read()
                    self.file_cache[str(file_path)] = code
                    
                    # Run all detectors
                    smells.extend(self._detect_dead_code(code, str(file_path)))
                    smells.extend(self._detect_duplicate_code(code, str(file_path)))
                    smells.extend(self._detect_high_complexity(code, str(file_path)))
                    smells.extend(self._detect_magic_numbers(code, str(file_path)))
                    smells.extend(self._detect_unused_variables(code, str(file_path)))
                    smells.extend(self._detect_long_methods(code, str(file_path)))
                    smells.extend(self._detect_deep_nesting(code, str(file_path)))
            except Exception as e:
                print(f"Error scanning {file_path}: {e}")
        
        # Find duplicate blocks across files
        smells.extend(self._find_duplicate_blocks())
        
        return smells
    
    def _detect_dead_code(self, code: str, file_path: str) -> List[CodeSmell]:
        """Detect unreachable and unused code"""
        smells = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Unreachable code after return
            if i > 1 and i < len(lines):
                prev_line = lines[i-2].strip()
                if prev_line in ('return', 'raise', 'break', 'continue') and stripped and not stripped.startswith('#'):
                    if not any(stripped.startswith(x) for x in ['def ', 'class ', '@', 'except', 'finally']):
                        smells.append(self._create_smell(
                            SmellType.DEAD_CODE,
                            SmellSeverity.MAJOR,
                            file_path,
                            i,
                            stripped,
                            "Code after return/raise statement is unreachable",
                            "This code never executes, wasting space and confusing readers",
                            f"Remove the unreachable code on line {i}",
                            "Low"
                        ))
            
            # Commented code blocks (potential dead code)
            if stripped.startswith('#') and len(stripped) > 10:
                if re.search(r'#\s*(def |class |=|import|from)', stripped):
                    smells.append(self._create_smell(
                        SmellType.DEAD_CODE,
                        SmellSeverity.MINOR,
                        file_path,
                        i,
                        stripped,
                        "Commented-out code detected",
                        "Dead code takes up space; use version control instead",
                        f"Delete the commented code or use git history",
                        "Low"
                    ))
        
        return smells
    
    def _detect_duplicate_code(self, code: str, file_path: str) -> List[CodeSmell]:
        """Detect duplicate code blocks"""
        smells = []
        lines = code.split('\n')
        
        # Look for duplicate code blocks (3+ lines)
        for i in range(len(lines) - 3):
            block = '\n'.join(lines[i:i+3])
            
            # Check if this block appears again later
            for j in range(i + 3, len(lines) - 2):
                other_block = '\n'.join(lines[j:j+3])
                
                if block == other_block and block.strip() and not block.strip().startswith('#'):
                    key = block[:50]  # Use first 50 chars as key
                    if key not in self.duplicate_blocks:
                        self.duplicate_blocks[key] = [(file_path, i+1)]
                    self.duplicate_blocks[key].append((file_path, j+1))
                    
                    smells.append(self._create_smell(
                        SmellType.DUPLICATE_CODE,
                        SmellSeverity.MEDIUM,
                        file_path,
                        j+1,
                        other_block.split('\n')[0],
                        f"Duplicate code found (also at line {i+1})",
                        "Code duplication increases maintenance burden and bug surface",
                        "Extract to a shared function or base class",
                        "Medium"
                    ))
        
        return smells
    
    def _detect_high_complexity(self, code: str, file_path: str) -> List[CodeSmell]:
        """Detect high cyclomatic complexity"""
        smells = []
        lines = code.split('\n')
        
        in_function = False
        function_lines = []
        function_name = ""
        function_start = 0
        complexity = 0
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Detect function start
            if re.match(r'^\s*def\s+\w+', line):
                if function_lines:
                    # Check previous function complexity
                    if complexity > 10:
                        smells.append(self._create_smell(
                            SmellType.HIGH_COMPLEXITY,
                            SmellSeverity.MAJOR,
                            file_path,
                            function_start,
                            function_name,
                            f"High cyclomatic complexity: {complexity}",
                            "Complex functions are hard to test, maintain, and debug",
                            "Break into smaller functions; reduce conditionals",
                            "High"
                        ))
                
                in_function = True
                function_lines = [stripped]
                function_name = re.search(r'def\s+(\w+)', line).group(1)
                function_start = i
                complexity = 1
            
            elif in_function and (line and not line[0].isspace()):
                in_function = False
            
            elif in_function:
                function_lines.append(stripped)
                # Count decision points
                if any(keyword in stripped for keyword in ['if ', 'elif ', 'else:', 'for ', 'while ', 'except ', 'and ', 'or ']):
                    complexity += 1
        
        return smells
    
    def _detect_magic_numbers(self, code: str, file_path: str) -> List[CodeSmell]:
        """Detect magic numbers in code"""
        smells = []
        lines = code.split('\n')
        
        magic_patterns = [
            (r'[^\w]\s*([2-9]|[1-9]\d+)\s*[=!<>]', "Unnamed constant"),  # Numbers >= 2
            (r'if\s+.*[=!<>]\s*([2-9]|[1-9]\d+)', "Magic number in condition"),
            (r'return\s+([2-9]|[1-9]\d+)', "Magic number in return"),
        ]
        
        for i, line in enumerate(lines, 1):
            # Skip strings and comments
            if '"""' in line or "'''" in line or line.strip().startswith('#'):
                continue
            
            for pattern, desc in magic_patterns:
                matches = re.finditer(pattern, line)
                for match in matches:
                    number = match.group(1)
                    if number not in ('0', '1', '10', '100', '1000'):  # Allow common numbers
                        smells.append(self._create_smell(
                            SmellType.MAGIC_NUMBER,
                            SmellSeverity.MINOR,
                            file_path,
                            i,
                            line.strip(),
                            f"{desc}: {number}",
                            "Magic numbers reduce code readability and maintainability",
                            f"Define a named constant: MAX_ATTEMPTS = {number}",
                            "Low"
                        ))
        
        return smells
    
    def _detect_unused_variables(self, code: str, file_path: str) -> List[CodeSmell]:
        """Detect unused variables"""
        smells = []
        lines = code.split('\n')
        
        # Simple pattern: find assignments and check if used
        for i, line in enumerate(lines, 1):
            # Find variable assignments
            match = re.match(r'\s*(\w+)\s*=', line)
            if match:
                var_name = match.group(1)
                
                # Skip common variables
                if var_name in ('_', 'self', 'cls', 'args', 'kwargs', 'result', 'data', 'temp'):
                    continue
                
                # Check if variable is used in subsequent lines
                remaining_code = '\n'.join(lines[i:])
                
                # Look for the variable being used (not just in comments)
                if not re.search(rf'\b{var_name}\b(?!\s*=)', remaining_code[:500]):
                    smells.append(self._create_smell(
                        SmellType.UNUSED_VARIABLE,
                        SmellSeverity.MINOR,
                        file_path,
                        i,
                        line.strip(),
                        f"Variable '{var_name}' assigned but never used",
                        "Unused variables increase code clutter",
                        f"Remove the variable or use it",
                        "Low"
                    ))
        
        return smells
    
    def _detect_long_methods(self, code: str, file_path: str) -> List[CodeSmell]:
        """Detect methods/functions that are too long"""
        smells = []
        lines = code.split('\n')
        
        in_method = False
        method_start = 0
        method_name = ""
        method_lines = 0
        indent_level = 0
        
        for i, line in enumerate(lines, 1):
            if re.match(r'^\s*def\s+', line):
                if method_lines > 50:
                    smells.append(self._create_smell(
                        SmellType.LONG_METHOD,
                        SmellSeverity.MAJOR,
                        file_path,
                        method_start,
                        method_name,
                        f"Method is {method_lines} lines long",
                        "Long methods are hard to understand, test, and maintain",
                        "Extract into smaller helper methods",
                        "High"
                    ))
                
                in_method = True
                method_start = i
                method_name = re.search(r'def\s+(\w+)', line).group(1)
                method_lines = 1
                indent_level = len(line) - len(line.lstrip())
            
            elif in_method and line and not line[0].isspace():
                in_method = False
            
            elif in_method:
                method_lines += 1
        
        return smells
    
    def _detect_deep_nesting(self, code: str, file_path: str) -> List[CodeSmell]:
        """Detect deeply nested code blocks"""
        smells = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            if line.strip() and not line.strip().startswith('#'):
                indent = len(line) - len(line.lstrip())
                depth = indent // 4  # Assuming 4-space indentation
                
                if depth > 4:
                    smells.append(self._create_smell(
                        SmellType.DEEP_NESTING,
                        SmellSeverity.MEDIUM,
                        file_path,
                        i,
                        line.strip()[:50],
                        f"Deep nesting level: {depth}",
                        "Deeply nested code is hard to follow and understand",
                        "Extract nested blocks to separate methods",
                        "Medium"
                    ))
        
        return smells
    
    def _find_duplicate_blocks(self) -> List[CodeSmell]:
        """Find duplicate code blocks across files"""
        smells = []
        
        for block_key, locations in self.duplicate_blocks.items():
            if len(locations) > 1:
                for file_path, line_num in locations[1:]:
                    smells.append(self._create_smell(
                        SmellType.DUPLICATE_CODE,
                        SmellSeverity.MAJOR,
                        file_path,
                        line_num,
                        block_key,
                        f"Code duplicated across {len(locations)} locations",
                        "Duplication spreads bugs and requires multiple fixes",
                        "Extract to shared module or utility function",
                        "High"
                    ))
        
        return smells
    
    def _create_smell(self, smell_type: SmellType, severity: SmellSeverity, 
                      file_path: str, line_num: int, code: str, description: str,
                      impact: str, refactor: str, effort: str) -> CodeSmell:
        """Create a code smell record"""
        self.smell_counter += 1
        smell_id = f"SMELL-{self.smell_counter:04d}"
        
        return CodeSmell(
            smell_id=smell_id,
            smell_type=smell_type,
            severity=severity,
            file_path=file_path,
            line_number=line_num,
            code_snippet=code,
            description=description,
            impact=impact,
            refactor_suggestion=refactor,
            effort=effort
        )
    
    def generate_refactor_code(self, smell: CodeSmell) -> Dict[str, str]:
        """Generate before/after code for refactoring"""
        
        refactors = {
            SmellType.DUPLICATE_CODE: {
                'before': 'def process_user():\n    user = db.get_user()\n    name = user["name"]\n    email = user["email"]\n\ndef process_admin():\n    admin = db.get_admin()\n    name = admin["name"]\n    email = admin["email"]',
                'after': 'def get_user_info(user_obj):\n    return {"name": user_obj["name"], "email": user_obj["email"]}\n\nuser_info = get_user_info(db.get_user())\nadmin_info = get_user_info(db.get_admin())',
                'explanation': 'Extract common logic into a shared function'
            },
            SmellType.LONG_METHOD: {
                'before': 'def process_order(order):\n    # 100 lines of validation, calculation, DB access\n    validate(order)\n    calculate_total(order)\n    apply_discount(order)\n    save_to_db(order)\n    send_email(order)',
                'after': 'def process_order(order):\n    validate_order(order)\n    total = calculate_total(order)\n    apply_discount(order, total)\n    save_to_db(order)\n    send_email(order)',
                'explanation': 'Break into smaller, single-responsibility methods'
            },
            SmellType.MAGIC_NUMBER: {
                'before': 'if age > 18 and salary > 50000:\n    approved = True',
                'after': 'MINIMUM_AGE = 18\nMINIMUM_SALARY = 50000\n\nif age > MINIMUM_AGE and salary > MINIMUM_SALARY:\n    approved = True',
                'explanation': 'Use named constants instead of magic numbers'
            },
            SmellType.DEEP_NESTING: {
                'before': 'for user in users:\n    if user.active:\n        for order in user.orders:\n            if order.status == "pending":\n                for item in order.items:\n                    if item.price > 100:\n                        send_alert(item)',
                'after': 'def get_high_value_items(users):\n    for user in users:\n        if not user.active:\n            continue\n        for order in user.orders:\n            if order.status != "pending":\n                continue\n            for item in order.items:\n                if item.price > 100:\n                    yield item\n\nfor item in get_high_value_items(users):\n    send_alert(item)',
                'explanation': 'Use early returns to reduce nesting depth'
            },
        }
        
        return refactors.get(smell.smell_type, {
            'before': smell.code_snippet,
            'after': '# Apply the refactoring suggestion above',
            'explanation': smell.refactor_suggestion
        })
    
    def get_complexity_summary(self, smells: List[CodeSmell]) -> Dict:
        """Generate summary statistics"""
        by_type = {}
        by_severity = {}
        
        for smell in smells:
            # Count by type
            type_name = smell.smell_type.value
            by_type[type_name] = by_type.get(type_name, 0) + 1
            
            # Count by severity
            sev_name = smell.severity.value
            by_severity[sev_name] = by_severity.get(sev_name, 0) + 1
        
        # Calculate effort
        total_effort_score = sum(
            {'Low': 1, 'Medium': 3, 'High': 5}.get(s.effort, 2) 
            for s in smells
        )
        
        return {
            'total_smells': len(smells),
            'by_type': by_type,
            'by_severity': by_severity,
            'total_effort_score': total_effort_score,
            'estimated_refactor_hours': total_effort_score / 2
        }
