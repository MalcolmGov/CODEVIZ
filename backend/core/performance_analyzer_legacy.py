"""
Performance Analysis Engine
Detects: N+1 Queries, Memory Leaks, Inefficient Algorithms, Async Issues
"""

import re
from typing import List, Dict, Tuple, Set
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

class PerformanceIssueType(Enum):
    N_PLUS_ONE = "N+1 Query Problem"
    MEMORY_LEAK = "Memory Leak"
    INEFFICIENT_ALGORITHM = "Inefficient Algorithm"
    SYNC_BLOCKING = "Synchronous Blocking"
    ASYNC_FIRE_AND_FORGET = "Async Fire-and-Forget"
    BULK_OPERATIONS = "Missing Bulk Operations"
    LAZY_LOADING_ISSUE = "Lazy Loading Issue"
    INEFFICIENT_LOOP = "Inefficient Loop"

class PerformanceSeverity(Enum):
    CRITICAL = "🔴 CRITICAL"
    HIGH = "🟠 HIGH"
    MEDIUM = "🟡 MEDIUM"
    LOW = "🟢 LOW"

@dataclass
class PerformanceIssue:
    issue_id: str
    issue_type: PerformanceIssueType
    severity: PerformanceSeverity
    file_path: str
    line_number: int
    code_snippet: str
    description: str
    impact: str
    estimated_slowdown: str  # "2x slower", "10x slower", etc.
    fix_suggestion: str
    expected_improvement: str
    
    def to_dict(self):
        return {
            'issue_id': self.issue_id,
            'type': self.issue_type.value,
            'severity': self.severity.value,
            'file': self.file_path,
            'line': self.line_number,
            'code': self.code_snippet,
            'description': self.description,
            'impact': self.impact,
            'slowdown': self.estimated_slowdown,
            'fix': self.fix_suggestion,
            'improvement': self.expected_improvement
        }

@dataclass
class PerformanceMetrics:
    total_issues: int
    critical_count: int
    estimated_total_slowdown_percent: float
    estimated_improvement_percent: float
    by_type: Dict[str, int]
    by_severity: Dict[str, int]
    files_affected: int
    
    def to_dict(self):
        return {
            'total_issues': self.total_issues,
            'critical': self.critical_count,
            'estimated_slowdown_percent': self.estimated_total_slowdown_percent,
            'estimated_improvement_percent': self.estimated_improvement_percent,
            'by_type': self.by_type,
            'by_severity': self.by_severity,
            'files_affected': self.files_affected
        }

class PerformanceAnalyzer:
    """Analyzes code for performance issues"""
    
    def __init__(self):
        self.issue_counter = 0
        self.file_cache = {}
        self.db_operations = {}
    
    def scan_files(self, directory: str, file_pattern: str = "*.py") -> Tuple[List[PerformanceIssue], PerformanceMetrics]:
        """Scan directory for performance issues"""
        issues = []
        path = Path(directory)
        
        python_files = list(path.glob(f"**/{file_pattern}"))
        files_affected = set()
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', errors='ignore') as f:
                    code = f.read()
                    self.file_cache[str(file_path)] = code
                    
                    # Run all detectors
                    file_issues = []
                    file_issues.extend(self._detect_n_plus_one(code, str(file_path)))
                    file_issues.extend(self._detect_memory_leaks(code, str(file_path)))
                    file_issues.extend(self._detect_inefficient_algorithms(code, str(file_path)))
                    file_issues.extend(self._detect_sync_blocking(code, str(file_path)))
                    file_issues.extend(self._detect_async_issues(code, str(file_path)))
                    file_issues.extend(self._detect_bulk_operations(code, str(file_path)))
                    file_issues.extend(self._detect_lazy_loading_issues(code, str(file_path)))
                    
                    if file_issues:
                        files_affected.add(str(file_path))
                        issues.extend(file_issues)
            except Exception as e:
                print(f"Error scanning {file_path}: {e}")
        
        # Calculate metrics
        metrics = self._calculate_metrics(issues, len(files_affected))
        
        return issues, metrics
    
    def _detect_n_plus_one(self, code: str, file_path: str) -> List[PerformanceIssue]:
        """Detect N+1 query problems"""
        issues = []
        lines = code.split('\n')
        
        # Pattern: for loop with database query inside
        for i, line in enumerate(lines):
            # Detect for loops
            if re.match(r'\s*for\s+\w+\s+in\s+', line):
                # Check next lines for DB operations
                for j in range(i+1, min(i+10, len(lines))):
                    if any(db_op in lines[j] for db_op in ['db.query', 'db.session.query', '.query(', 'get_object', 'fetch', 'execute']):
                        if not any(x in lines[j] for x in ['bulk', 'batch', 'prefetch', 'select_related', 'prefetch_related']):
                            issues.append(self._create_issue(
                                PerformanceIssueType.N_PLUS_ONE,
                                PerformanceSeverity.CRITICAL,
                                file_path,
                                i+1,
                                line.strip(),
                                "N+1 Query: Database query inside a loop",
                                f"For each item in loop, one query executes. With 100 items, 101 queries total (1 initial + 100 in loop)",
                                "100x slower",
                                f"Use batch query: items = {lines[i].strip()}, then query once",
                                "100x faster"
                            ))
        
        # Pattern: ORM lazy loading
        for i, line in enumerate(lines):
            if re.search(r'for\s+\w+\s+in\s+\w+\.\w+:', line):
                # Check if accessing related fields
                for j in range(i+1, min(i+5, len(lines))):
                    if re.search(r'\w+\.\w+\.\w+', lines[j]):  # Accessing nested property
                        issues.append(self._create_issue(
                            PerformanceIssueType.N_PLUS_ONE,
                            PerformanceSeverity.HIGH,
                            file_path,
                            j+1,
                            lines[j].strip(),
                            "Lazy loading N+1: Accessing relationships inside loop",
                            "Each relationship access triggers a database query",
                            "50-100x slower",
                            "Use prefetch_related() or select_related()",
                            "50-100x faster"
                        ))
        
        return issues
    
    def _detect_memory_leaks(self, code: str, file_path: str) -> List[PerformanceIssue]:
        """Detect potential memory leaks"""
        issues = []
        lines = code.split('\n')
        
        # Pattern: Event listeners without cleanup
        for i, line in enumerate(lines):
            if 'addEventListener' in line or 'on(' in line:
                # Check if there's cleanup
                remaining_code = '\n'.join(lines[i:min(i+20, len(lines))])
                if 'removeEventListener' not in remaining_code and 'off(' not in remaining_code:
                    issues.append(self._create_issue(
                        PerformanceIssueType.MEMORY_LEAK,
                        PerformanceSeverity.HIGH,
                        file_path,
                        i+1,
                        line.strip(),
                        "Event listener without cleanup",
                        "Event listeners accumulate in memory, never removed. Causes memory to grow over time",
                        "Memory grows ~1MB per 1000 listeners",
                        "Add cleanup: element.removeEventListener() or use one-time listeners",
                        "Zero memory leaks"
                    ))
        
        # Pattern: Circular references
        for i, line in enumerate(lines):
            if re.search(r'\w+\.\w+\s*=\s*\w+', line):
                next_lines = '\n'.join(lines[i:min(i+3, len(lines))])
                if re.search(r'\w+\.\w+\s*=\s*\w+', next_lines) and 'self' in next_lines:
                    issues.append(self._create_issue(
                        PerformanceIssueType.MEMORY_LEAK,
                        PerformanceSeverity.MEDIUM,
                        file_path,
                        i+1,
                        line.strip(),
                        "Potential circular reference",
                        "Objects referencing each other prevent garbage collection",
                        "Memory not freed until objects are dereferenced",
                        "Use weak references or break circular references on cleanup",
                        "Immediate garbage collection"
                    ))
        
        # Pattern: Large objects without cleanup
        for i, line in enumerate(lines):
            if re.search(r'(cache|buffer|accumulate|append|extend)\s*=\s*\[\]', line):
                # Check if items are added in a loop
                for j in range(i+1, min(i+10, len(lines))):
                    if 'append' in lines[j] or 'extend' in lines[j]:
                        if 'clear' not in '\n'.join(lines[j:j+5]):
                            issues.append(self._create_issue(
                                PerformanceIssueType.MEMORY_LEAK,
                                PerformanceSeverity.MEDIUM,
                                file_path,
                                j+1,
                                lines[j].strip(),
                                "Unbounded data structure growth",
                                "List grows indefinitely without clearing, consumes all available memory",
                                "Memory exhaustion after ~100k items",
                                "Clear periodically: collection.clear() or use deque with maxlen",
                                "Constant memory usage"
                            ))
        
        return issues
    
    def _detect_inefficient_algorithms(self, code: str, file_path: str) -> List[PerformanceIssue]:
        """Detect inefficient algorithms"""
        issues = []
        lines = code.split('\n')
        
        # Pattern: Nested loops (O(n²))
        for i, line in enumerate(lines):
            if re.match(r'\s*for\s+\w+\s+in\s+', line):
                for j in range(i+1, min(i+5, len(lines))):
                    if re.match(r'\s+for\s+\w+\s+in\s+', lines[j]):
                        inner_loop = lines[j].strip()
                        if 'if' not in lines[j+1] or 'break' not in '\n'.join(lines[j+1:j+3]):
                            issues.append(self._create_issue(
                                PerformanceIssueType.INEFFICIENT_ALGORITHM,
                                PerformanceSeverity.HIGH,
                                file_path,
                                j+1,
                                inner_loop,
                                "Nested loop - O(n²) complexity",
                                "Two nested loops multiply execution time. 100 items = 10,000 iterations",
                                "10,000x slower than linear",
                                "Use hash map/set for O(n log n) or O(n) lookup instead",
                                "100-10,000x faster"
                            ))
        
        # Pattern: Searching in list inside loop
        for i, line in enumerate(lines):
            if any(search in line for search in ['.find(', '.index(', ' in ', '.count(']):
                if i > 0 and re.match(r'\s*for\s+', lines[i-1]):
                    issues.append(self._create_issue(
                        PerformanceIssueType.INEFFICIENT_ALGORITHM,
                        PerformanceSeverity.HIGH,
                        file_path,
                        i+1,
                        line.strip(),
                        "Linear search in loop - O(n²)",
                        "Searching through list for each item is slow",
                        "100x slower for 100 items",
                        "Convert list to set: if item in item_set:",
                        "100x faster"
                    ))
        
        # Pattern: String concatenation in loop
        for i, line in enumerate(lines):
            if '+=' in line and '"' in line and i > 0:
                if re.match(r'\s*for\s+', lines[i-1]):
                    issues.append(self._create_issue(
                        PerformanceIssueType.INEFFICIENT_ALGORITHM,
                        PerformanceSeverity.MEDIUM,
                        file_path,
                        i+1,
                        line.strip(),
                        "String concatenation in loop",
                        "String concatenation creates new objects each time",
                        "10-100x slower for large strings",
                        "Use list.append() and ''.join() at the end",
                        "10-100x faster"
                    ))
        
        return issues
    
    def _detect_sync_blocking(self, code: str, file_path: str) -> List[PerformanceIssue]:
        """Detect synchronous blocking operations"""
        issues = []
        lines = code.split('\n')
        
        # Pattern: Blocking I/O without async
        blocking_patterns = [
            ('requests.get', 'HTTP request'),
            ('open(', 'File I/O'),
            ('time.sleep', 'Sleep delay'),
            ('db.execute', 'Database query'),
            ('subprocess.run', 'Subprocess'),
        ]
        
        for i, line in enumerate(lines):
            if 'async' not in lines[max(0, i-5):i]:  # Not in async context
                for pattern, desc in blocking_patterns:
                    if pattern in line:
                        issues.append(self._create_issue(
                            PerformanceIssueType.SYNC_BLOCKING,
                            PerformanceSeverity.HIGH,
                            file_path,
                            i+1,
                            line.strip(),
                            f"Blocking {desc}",
                            f"{desc} blocks entire application. With 100 concurrent requests, all must wait",
                            "100x slower under load",
                            f"Use async/await: response = await fetch() or use thread pool",
                            "100x faster under load"
                        ))
        
        return issues
    
    def _detect_async_issues(self, code: str, file_path: str) -> List[PerformanceIssue]:
        """Detect async/await issues"""
        issues = []
        lines = code.split('\n')
        
        # Pattern: Fire-and-forget async
        for i, line in enumerate(lines):
            if re.search(r'asyncio\.create_task\(|\.spawn\(|task\.fire\(', line):
                # Check if there's error handling
                remaining = '\n'.join(lines[i:min(i+5, len(lines))])
                if 'await' not in remaining and 'catch' not in remaining and 'except' not in remaining:
                    issues.append(self._create_issue(
                        PerformanceIssueType.ASYNC_FIRE_AND_FORGET,
                        PerformanceSeverity.HIGH,
                        file_path,
                        i+1,
                        line.strip(),
                        "Fire-and-forget async task",
                        "Async task started but not awaited. Errors silently fail, hard to debug",
                        "Silent failures, no error reporting",
                        "Add exception handling or await the result",
                        "Proper error handling"
                    ))
        
        # Pattern: Sequential await instead of parallel
        for i, line in enumerate(lines):
            if 'await' in line:
                next_line = lines[i+1] if i+1 < len(lines) else ""
                if 'await' in next_line:
                    issues.append(self._create_issue(
                        PerformanceIssueType.ASYNC_FIRE_AND_FORGET,
                        PerformanceSeverity.MEDIUM,
                        file_path,
                        i+1,
                        line.strip(),
                        "Sequential awaits - should be parallel",
                        "Two async operations await sequentially instead of in parallel",
                        "2x slower than parallel",
                        "Use asyncio.gather() or Promise.all() for parallel execution",
                        "2x faster"
                    ))
        
        return issues
    
    def _detect_bulk_operations(self, code: str, file_path: str) -> List[PerformanceIssue]:
        """Detect missing bulk operations"""
        issues = []
        lines = code.split('\n')
        
        # Pattern: Individual inserts in loop
        for i, line in enumerate(lines):
            if 'create(' in line or '.save()' in line or '.insert()' in line:
                if i > 0 and re.match(r'\s*for\s+', lines[i-1]):
                    issues.append(self._create_issue(
                        PerformanceIssueType.BULK_OPERATIONS,
                        PerformanceSeverity.CRITICAL,
                        file_path,
                        i+1,
                        line.strip(),
                        "Individual database inserts in loop",
                        "Each insert is a separate database transaction. 1000 items = 1000 DB hits",
                        "1000x slower",
                        "Use bulk_create(): Model.objects.bulk_create(objects)",
                        "100-1000x faster"
                    ))
        
        return issues
    
    def _detect_lazy_loading_issues(self, code: str, file_path: str) -> List[PerformanceIssue]:
        """Detect lazy loading issues"""
        issues = []
        lines = code.split('\n')
        
        # Pattern: Missing select_related/prefetch_related
        for i, line in enumerate(lines):
            if '.get(' in line or '.filter(' in line or '.all()' in line:
                if 'select_related' not in line and 'prefetch_related' not in line:
                    # Check if related fields are accessed later
                    remaining = '\n'.join(lines[i:min(i+10, len(lines))])
                    if re.search(r'\.\w+\.\w+', remaining):  # Accessing relationships
                        issues.append(self._create_issue(
                            PerformanceIssueType.LAZY_LOADING_ISSUE,
                            PerformanceSeverity.HIGH,
                            file_path,
                            i+1,
                            line.strip(),
                            "Missing select_related/prefetch_related",
                            "Relationships loaded lazily, causing N+1 queries",
                            "N times slower (N = number of items)",
                            "Add .select_related() or .prefetch_related() to query",
                            "N times faster"
                        ))
        
        return issues
    
    def _create_issue(self, issue_type: PerformanceIssueType, severity: PerformanceSeverity,
                      file_path: str, line_num: int, code: str, description: str,
                      impact: str, slowdown: str, fix: str, improvement: str) -> PerformanceIssue:
        """Create a performance issue record"""
        self.issue_counter += 1
        issue_id = f"PERF-{self.issue_counter:04d}"
        
        return PerformanceIssue(
            issue_id=issue_id,
            issue_type=issue_type,
            severity=severity,
            file_path=file_path,
            line_number=line_num,
            code_snippet=code,
            description=description,
            impact=impact,
            estimated_slowdown=slowdown,
            fix_suggestion=fix,
            expected_improvement=improvement
        )
    
    def _calculate_metrics(self, issues: List[PerformanceIssue], files_affected: int) -> PerformanceMetrics:
        """Calculate performance metrics"""
        by_type = {}
        by_severity = {}
        
        # Extract slowdown percentages
        slowdown_multipliers = []
        
        for issue in issues:
            # Count by type
            type_name = issue.issue_type.value
            by_type[type_name] = by_type.get(type_name, 0) + 1
            
            # Count by severity
            sev_name = issue.severity.value
            by_severity[sev_name] = by_severity.get(sev_name, 0) + 1
            
            # Parse slowdown multiplier
            if 'x slower' in issue.estimated_slowdown:
                mult = int(issue.estimated_slowdown.split('x')[0])
                slowdown_multipliers.append(mult)
        
        # Calculate aggregate slowdown (geometric mean)
        if slowdown_multipliers:
            # Use geometric mean to avoid extreme outliers
            import math
            geometric_mean = math.exp(sum(math.log(m) for m in slowdown_multipliers) / len(slowdown_multipliers))
            slowdown_percent = min(int((geometric_mean - 1) * 100), 99)
            improvement_percent = min(int((geometric_mean - 1) / geometric_mean * 100), 99)
        else:
            slowdown_percent = 0
            improvement_percent = 0
        
        critical_count = len([i for i in issues if i.severity == PerformanceSeverity.CRITICAL])
        
        return PerformanceMetrics(
            total_issues=len(issues),
            critical_count=critical_count,
            estimated_total_slowdown_percent=slowdown_percent,
            estimated_improvement_percent=improvement_percent,
            by_type=by_type,
            by_severity=by_severity,
            files_affected=files_affected
        )
    
    def generate_optimization_code(self, issue: PerformanceIssue) -> Dict[str, str]:
        """Generate before/after code for optimization"""
        
        optimizations = {
            PerformanceIssueType.N_PLUS_ONE: {
                'before': 'for user in users:\n    posts = db.session.query(Post).filter(Post.user_id == user.id).all()\n    print(user.name, posts)',
                'after': 'users = db.session.query(User).options(joinedload(User.posts)).all()\nfor user in users:\n    print(user.name, user.posts)',
                'explanation': 'Use joinedload or select_related to fetch relationships in one query'
            },
            PerformanceIssueType.MEMORY_LEAK: {
                'before': 'element.addEventListener("click", handler)\n# No cleanup - memory leaks',
                'after': 'element.addEventListener("click", handler)\nelement.addEventListener("destroy", () => {\n    element.removeEventListener("click", handler)\n})',
                'explanation': 'Always cleanup event listeners when elements are removed'
            },
            PerformanceIssueType.INEFFICIENT_ALGORITHM: {
                'before': 'for user in users:\n    if user.id in large_list:\n        process(user)',
                'after': 'id_set = set(large_list)\nfor user in users:\n    if user.id in id_set:\n        process(user)',
                'explanation': 'Use set for O(1) lookup instead of list O(n) lookup'
            },
            PerformanceIssueType.SYNC_BLOCKING: {
                'before': 'response = requests.get(url)\nprocess(response)',
                'after': 'response = await aiohttp.get(url)\nprocess(response)',
                'explanation': 'Use async/await for non-blocking I/O operations'
            },
            PerformanceIssueType.BULK_OPERATIONS: {
                'before': 'for item in items:\n    db.session.add(item)\n    db.session.commit()',
                'after': 'db.session.bulk_insert_mappings(Model, items)\ndb.session.commit()',
                'explanation': 'Use bulk operations for multiple inserts instead of individual ones'
            },
        }
        
        return optimizations.get(issue.issue_type, {
            'before': issue.code_snippet,
            'after': '# Apply optimization based on fix suggestion',
            'explanation': issue.fix_suggestion
        })
