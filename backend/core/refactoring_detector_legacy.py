"""
AI-Powered Code Refactoring Engine - Opportunity Detector

Identifies refactoring opportunities in analyzed code artifacts.
Focuses on: large classes, long methods, duplication, unclear names, magic numbers.
"""

from enum import Enum
from dataclasses import dataclass
from typing import List, Optional
import re


class RefactoringType(Enum):
    """Types of refactoring opportunities"""
    EXTRACT_CLASS = "extract_class"
    EXTRACT_METHOD = "extract_method"
    REMOVE_DUPLICATION = "remove_duplication"
    SIMPLIFY_CONDITIONAL = "simplify_conditional"
    REPLACE_MAGIC_NUMBERS = "replace_magic_numbers"
    RENAME_UNCLEAR_VARS = "rename_unclear_vars"
    EXTRACT_INTERFACE = "extract_interface"
    REDUCE_COMPLEXITY = "reduce_complexity"


@dataclass
class RefactoringOpportunity:
    """Represents a single refactoring opportunity"""
    type: RefactoringType
    file_path: str
    line_numbers: tuple  # (start, end)
    current_code: str
    description: str
    priority: int  # 1-10, 10 is most important
    confidence: float  # 0-1, how confident we are about this opportunity
    impact: str  # "high", "medium", "low" - impact on codebase
    
    def to_dict(self):
        return {
            "type": self.type.value,
            "file": self.file_path,
            "line_numbers": self.line_numbers,
            "description": self.description,
            "priority": self.priority,
            "confidence": round(self.confidence, 2),
            "impact": self.impact
        }


class RefactoringDetector:
    """Detects refactoring opportunities in code artifacts"""
    
    def __init__(self, artifacts: dict):
        """
        Initialize detector with scanned artifacts
        
        Args:
            artifacts: Dictionary of artifacts from scanner
                       (classes, functions, etc.)
        """
        self.artifacts = artifacts
        self.opportunities = []
    
    def find_opportunities(self) -> List[RefactoringOpportunity]:
        """
        Find all refactoring opportunities
        
        Returns:
            List of RefactoringOpportunity sorted by priority (descending)
        """
        self.opportunities = []
        
        # Find opportunities by type
        self.opportunities.extend(self._find_large_classes())
        self.opportunities.extend(self._find_long_functions())
        self.opportunities.extend(self._find_magic_numbers())
        self.opportunities.extend(self._find_unclear_names())
        self.opportunities.extend(self._find_complex_conditionals())
        self.opportunities.extend(self._find_high_coupling())
        
        # Sort by priority (descending)
        self.opportunities.sort(key=lambda x: x.priority, reverse=True)
        
        return self.opportunities
    
    def _find_large_classes(self) -> List[RefactoringOpportunity]:
        """Find classes with >500 lines - candidates for extraction"""
        opportunities = []
        
        for cls in self.artifacts.get('classes', []):
            # Estimate lines by looking at methods
            method_count = len(cls.get('methods', []))
            lines = cls.get('lines', 0)
            
            # Classes over 500 lines should be split
            if lines > 500 or method_count > 15:
                opp = RefactoringOpportunity(
                    type=RefactoringType.EXTRACT_CLASS,
                    file_path=cls.get('file', 'unknown'),
                    line_numbers=(cls.get('line_start', 0), cls.get('line_end', 0)),
                    current_code=f"class {cls.get('name', 'Unknown')}",
                    description=f"Class '{cls.get('name')}' has {method_count} methods - consider extracting into smaller classes",
                    priority=9,
                    confidence=0.95,
                    impact="high"
                )
                opportunities.append(opp)
        
        return opportunities
    
    def _find_long_functions(self) -> List[RefactoringOpportunity]:
        """Find functions that could benefit from refactoring"""
        opportunities = []
        
        functions = self.artifacts.get('functions', [])
        
        # Add opportunities for functions with many parameters
        for i, func in enumerate(functions[:30]):  # Check first 30
            params = func.get('params', [])
            name = func.get('name', 'unknown')
            file_path = func.get('file', 'unknown')
            
            # Functions with many parameters should be simplified
            if len(params) > 5:
                opp = RefactoringOpportunity(
                    type=RefactoringType.EXTRACT_METHOD,
                    file_path=file_path,
                    line_numbers=(func.get('line', 0), func.get('line', 0) + 20),
                    current_code=f"def {name}({', '.join(params[:3])}...)",
                    description=f"Function '{name}' has {len(params)} parameters - consider extracting into smaller functions or using a parameter object",
                    priority=7,
                    confidence=0.8,
                    impact="medium"
                )
                opportunities.append(opp)
        
        return opportunities
    
    def _find_magic_numbers(self) -> List[RefactoringOpportunity]:
        """Find magic numbers that should be constants"""
        opportunities = []
        
        # Pattern for bare numbers in code (simplified)
        magic_patterns = [
            r'\s=\s[0-9]{3,}',  # Numbers >= 100
            r'if.*[0-9]{3,}',    # Conditionals with large numbers
            r'\[[0-9]{2,}\]',    # Array indices
        ]
        
        code_snippets = self.artifacts.get('code_snippets', [])
        
        for snippet in code_snippets[:10]:  # Check first 10 snippets
            for pattern in magic_patterns:
                if re.search(pattern, snippet.get('code', '')):
                    opp = RefactoringOpportunity(
                        type=RefactoringType.REPLACE_MAGIC_NUMBERS,
                        file_path=snippet.get('file', 'unknown'),
                        line_numbers=(snippet.get('line', 0), snippet.get('line', 0)),
                        current_code=snippet.get('code', '')[:80],
                        description="Found magic numbers - extract to named constants",
                        priority=5,
                        confidence=0.7,
                        impact="low"
                    )
                    opportunities.append(opp)
                    break
        
        return opportunities
    
    def _find_unclear_names(self) -> List[RefactoringOpportunity]:
        """Find variables with unclear names (a, x, temp, etc)"""
        opportunities = []
        
        # Common unclear variable names
        unclear_names = {'a', 'b', 'c', 'x', 'y', 'z', 'i', 'j', 'k', 'temp', 'tmp', 't', 'var', 'val', 'data'}
        
        for func in self.artifacts.get('functions', []):
            params = func.get('params', [])
            
            # Check if any parameters have unclear names
            unclear_params = [p for p in params if p.lower() in unclear_names]
            
            if unclear_params:
                opp = RefactoringOpportunity(
                    type=RefactoringType.RENAME_UNCLEAR_VARS,
                    file_path=func.get('file', 'unknown'),
                    line_numbers=(func.get('line_start', 0), func.get('line_start', 0) + 5),
                    current_code=f"def {func.get('name')}({', '.join(params)})",
                    description=f"Function parameters have unclear names: {', '.join(unclear_params)}",
                    priority=4,
                    confidence=0.85,
                    impact="medium"
                )
                opportunities.append(opp)
        
        return opportunities
    
    def _find_complex_conditionals(self) -> List[RefactoringOpportunity]:
        """Find complex conditional logic that could be simplified"""
        opportunities = []
        
        for func in self.artifacts.get('functions', []):
            complexity = func.get('cyclomatic_complexity', 0)
            
            # High complexity indicates complex conditionals
            if complexity > 10:
                opp = RefactoringOpportunity(
                    type=RefactoringType.SIMPLIFY_CONDITIONAL,
                    file_path=func.get('file', 'unknown'),
                    line_numbers=(func.get('line_start', 0), func.get('line_end', 0)),
                    current_code=f"def {func.get('name')}()",
                    description=f"Function has high cyclomatic complexity ({complexity}) - consider extracting conditions into helper functions",
                    priority=7,
                    confidence=0.85,
                    impact="high"
                )
                opportunities.append(opp)
        
        return opportunities
    
    def _find_high_coupling(self) -> List[RefactoringOpportunity]:
        """Find classes with high coupling to other classes"""
        opportunities = []
        
        for cls in self.artifacts.get('classes', []):
            dependencies = cls.get('dependencies', [])
            
            # Classes with >5 dependencies are tightly coupled
            if len(dependencies) > 5:
                opp = RefactoringOpportunity(
                    type=RefactoringType.EXTRACT_INTERFACE,
                    file_path=cls.get('file', 'unknown'),
                    line_numbers=(cls.get('line_start', 0), cls.get('line_end', 0)),
                    current_code=f"class {cls.get('name')}",
                    description=f"Class has high coupling ({len(dependencies)} dependencies) - consider extracting interfaces",
                    priority=6,
                    confidence=0.75,
                    impact="medium"
                )
                opportunities.append(opp)
        
        return opportunities
    
    def get_top_opportunities(self, limit: int = 5) -> List[RefactoringOpportunity]:
        """Get top N refactoring opportunities"""
        return self.opportunities[:limit]
    
    def get_summary(self) -> dict:
        """Get summary of refactoring opportunities"""
        by_type = {}
        total_priority = 0
        
        for opp in self.opportunities:
            opp_type = opp.type.value
            by_type[opp_type] = by_type.get(opp_type, 0) + 1
            total_priority += opp.priority
        
        return {
            "total_opportunities": len(self.opportunities),
            "by_type": by_type,
            "average_priority": total_priority / len(self.opportunities) if self.opportunities else 0,
            "top_opportunity": self.opportunities[0].to_dict() if self.opportunities else None
        }
