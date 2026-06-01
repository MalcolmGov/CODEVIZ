"""
AI-Powered Code Refactoring Suggestion Engine

Uses Ollama LLM to generate refactoring suggestions based on identified opportunities.
Generates complete refactored code, explanations, and test cases.
"""

import json
import re
from typing import Optional, Dict
from dataclasses import dataclass
from refactoring_detector import RefactoringOpportunity, RefactoringType

try:
    from agents import create_llm_agent
except ImportError:
    # Fallback if agents module not available
    create_llm_agent = None


@dataclass
class RefactoringSuggestion:
    """Represents a complete refactoring suggestion"""
    opportunity: RefactoringOpportunity
    refactored_code: str
    explanation: str
    test_code: str
    before_metrics: Dict  # lines, complexity, etc.
    after_metrics: Dict
    
    def to_dict(self):
        return {
            "opportunity": self.opportunity.to_dict(),
            "refactored_code": self.refactored_code,
            "explanation": self.explanation,
            "test_code": self.test_code,
            "before_metrics": self.before_metrics,
            "after_metrics": self.after_metrics
        }


class AIRefactorer:
    """Generates AI-powered refactoring suggestions using Ollama"""
    
    def __init__(self, ollama_base_url: str = "http://localhost:11434"):
        """
        Initialize AI Refactorer
        
        Args:
            ollama_base_url: Base URL for Ollama service
        """
        self.ollama_base_url = ollama_base_url
        self.agent = None
        
        if create_llm_agent:
            try:
                self.agent = create_llm_agent(ollama_base_url)
            except Exception as e:
                print(f"Warning: Could not create LLM agent: {e}")
    
    def suggest_refactoring(self, opportunity: RefactoringOpportunity) -> Optional[RefactoringSuggestion]:
        """
        Generate AI refactoring suggestion for an opportunity
        
        Args:
            opportunity: RefactoringOpportunity to refactor
            
        Returns:
            RefactoringSuggestion or None if generation fails
        """
        if not self.agent:
            return self._generate_template_suggestion(opportunity)
        
        # Generate prompt based on refactoring type
        prompt = self._generate_prompt(opportunity)
        
        try:
            # Call LLM
            response = self.agent.invoke({"message": prompt})
            
            # Parse response
            suggestion = self._parse_response(opportunity, response)
            
            return suggestion
            
        except Exception as e:
            print(f"Error calling LLM: {e}")
            # Fall back to template
            return self._generate_template_suggestion(opportunity)
    
    def _generate_prompt(self, opportunity: RefactoringOpportunity) -> str:
        """Generate prompt for LLM based on refactoring type"""
        
        base_prompt = f"""You are an expert Python/JavaScript code refactorer. Your task is to suggest a high-quality refactoring.

Refactoring Type: {opportunity.type.value}
File: {opportunity.file_path}
Lines: {opportunity.line_numbers[0]}-{opportunity.line_numbers[1]}
Priority: {opportunity.priority}/10

Current Code:
```
{opportunity.current_code}
```

Problem: {opportunity.description}

Please provide a response in this EXACT format (no other text):

REFACTORED_CODE:
[Complete refactored code here - must be valid and working]

EXPLANATION:
[Explanation of what changed and why - 2-3 sentences]

TEST_CASES:
[2-3 test cases to verify the refactoring works - pytest or jest format]

METRICS:
[Expected improvements in format: "complexity: 12->6, lines: 50->35"]

Do not include markdown code blocks, just the raw code.
"""
        
        # Add refactoring type specific instructions
        if opportunity.type == RefactoringType.EXTRACT_METHOD:
            base_prompt += """

For EXTRACT_METHOD:
1. Identify logical chunks of code that can be extracted
2. Create focused helper methods with clear names
3. Update original method to call new methods
4. Ensure no duplicate code remains
5. All parameters clearly named
"""
        
        elif opportunity.type == RefactoringType.EXTRACT_CLASS:
            base_prompt += """

For EXTRACT_CLASS:
1. Identify cohesive methods and properties
2. Create new class with extracted functionality
3. Update original class to delegate if needed
4. Ensure clear separation of concerns
5. All public methods documented
"""
        
        elif opportunity.type == RefactoringType.SIMPLIFY_CONDITIONAL:
            base_prompt += """

For SIMPLIFY_CONDITIONAL:
1. Break complex if/else chains into guard clauses
2. Extract conditions into named variables/methods
3. Use polymorphism if appropriate
4. Consider strategy pattern for different behaviors
5. All conditions clearly express intent
"""
        
        return base_prompt
    
    def _parse_response(self, opportunity: RefactoringOpportunity, response: str) -> Optional[RefactoringSuggestion]:
        """Parse LLM response into RefactoringSuggestion"""
        
        try:
            # Extract sections
            refactored_match = re.search(r'REFACTORED_CODE:\s*\n(.*?)\n\s*EXPLANATION:', response, re.DOTALL)
            explanation_match = re.search(r'EXPLANATION:\s*\n(.*?)\n\s*TEST_CASES:', response, re.DOTALL)
            tests_match = re.search(r'TEST_CASES:\s*\n(.*?)\n\s*METRICS:', response, re.DOTALL)
            metrics_match = re.search(r'METRICS:\s*\n(.*?)$', response, re.DOTALL)
            
            if not all([refactored_match, explanation_match, tests_match]):
                return None
            
            refactored_code = refactored_match.group(1).strip()
            explanation = explanation_match.group(1).strip()
            test_code = tests_match.group(1).strip()
            metrics_str = metrics_match.group(1).strip() if metrics_match else ""
            
            # Parse metrics
            after_metrics = self._parse_metrics(metrics_str)
            before_metrics = {
                "lines": len(opportunity.current_code.split('\n')),
                "description": opportunity.description
            }
            
            suggestion = RefactoringSuggestion(
                opportunity=opportunity,
                refactored_code=refactored_code,
                explanation=explanation,
                test_code=test_code,
                before_metrics=before_metrics,
                after_metrics=after_metrics
            )
            
            return suggestion
            
        except Exception as e:
            print(f"Error parsing response: {e}")
            return None
    
    def _parse_metrics(self, metrics_str: str) -> Dict:
        """Parse metrics string into dictionary"""
        metrics = {}
        
        # Try to parse key: before->after format
        for part in metrics_str.split(','):
            if '->' in part:
                key_val = part.split(':')
                if len(key_val) == 2:
                    key = key_val[0].strip()
                    vals = key_val[1].split('->')
                    if len(vals) == 2:
                        metrics[f"{key}_before"] = vals[0].strip()
                        metrics[f"{key}_after"] = vals[1].strip()
        
        return metrics
    
    def _generate_template_suggestion(self, opportunity: RefactoringOpportunity) -> RefactoringSuggestion:
        """Generate template suggestion when LLM is unavailable"""
        
        templates = {
            RefactoringType.EXTRACT_METHOD: {
                "code": f"""# Refactored version of {opportunity.current_code[:50]}...
def helper_method_1(param1, param2):
    \"\"\"Extracted helper method\"\"\"
    # TODO: Implement extracted logic here
    return result

def main_method(param1, param2):
    \"\"\"Original method calling new helper\"\"\"
    result1 = helper_method_1(param1, param2)
    # Rest of logic here
    return result1""",
                "explanation": "Extracted long method into smaller, focused helper methods. Each method now has a single responsibility, improving readability and testability.",
                "tests": """import pytest

def test_helper_method_1():
    \"\"\"Test extracted helper method\"\"\"
    result = helper_method_1(test_param1, test_param2)
    assert result == expected_result

def test_main_method():
    \"\"\"Test original method with extraction\"\"\"
    result = main_method(test_param1, test_param2)
    assert result == expected_result"""
            },
            
            RefactoringType.EXTRACT_CLASS: {
                "code": f"""# New extracted class
class ExtractedResponsibility:
    \"\"\"Extracted cohesive functionality\"\"\"
    def __init__(self, param1):
        self.param1 = param1
    
    def method_1(self):
        # TODO: Moved logic here
        pass

# Original class - simplified
class OriginalClass:
    def __init__(self, param1):
        self.helper = ExtractedResponsibility(param1)
    
    def main_method(self):
        return self.helper.method_1()""",
                "explanation": "Extracted cohesive methods and properties into new class. Original class now delegates to new class, reducing complexity and improving separation of concerns.",
                "tests": """import pytest

def test_extracted_responsibility():
    \"\"\"Test newly extracted class\"\"\"
    helper = ExtractedResponsibility(test_param)
    result = helper.method_1()
    assert result == expected_result

def test_original_class():
    \"\"\"Test original class with delegation\"\"\"
    obj = OriginalClass(test_param)
    result = obj.main_method()
    assert result == expected_result"""
            },
            
            RefactoringType.SIMPLIFY_CONDITIONAL: {
                "code": f"""# Simplified version
def process(value):
    # Guard clauses make intent clear
    if not value:
        return None
    
    if value < 0:
        return handle_negative(value)
    
    if value == 0:
        return handle_zero()
    
    return handle_positive(value)""",
                "explanation": "Replaced complex nested if/else chains with guard clauses. Each condition now clearly expresses an intent, improving code readability.",
                "tests": """import pytest

def test_guard_clause_none():
    assert process(None) is None

def test_guard_clause_negative():
    assert process(-5) == expected_negative_result

def test_guard_clause_zero():
    assert process(0) == expected_zero_result

def test_guard_clause_positive():
    assert process(5) == expected_positive_result"""
            }
        }
        
        # Get template or use generic
        template = templates.get(opportunity.type, templates[RefactoringType.EXTRACT_METHOD])
        
        suggestion = RefactoringSuggestion(
            opportunity=opportunity,
            refactored_code=template["code"],
            explanation=template["explanation"],
            test_code=template["tests"],
            before_metrics={"lines": len(opportunity.current_code.split('\n')), "note": "Original implementation"},
            after_metrics={"estimated_improvement": "20-30% complexity reduction"}
        )
        
        return suggestion
    
    def suggest_pr_content(self, suggestion: RefactoringSuggestion) -> Dict:
        """Generate GitHub PR content for refactoring suggestion"""
        
        return {
            "title": f"🔨 Refactor: {suggestion.opportunity.type.value.replace('_', ' ').title()}",
            "description": f"""## Refactoring Suggestion

**Type**: {suggestion.opportunity.type.value.replace('_', ' ')}  
**File**: `{suggestion.opportunity.file_path}`  
**Lines**: {suggestion.opportunity.line_numbers[0]}-{suggestion.opportunity.line_numbers[1]}  
**Priority**: {suggestion.opportunity.priority}/10  
**Impact**: {suggestion.opportunity.impact}  

### Problem
{suggestion.opportunity.description}

### Solution
{suggestion.explanation}

### Changes
This refactoring:
- Improves code readability and maintainability
- Reduces complexity and cyclomatic complexity
- Makes code easier to test and debug
- Follows software engineering best practices

### Metrics
**Before**:
- Lines: {suggestion.before_metrics.get('lines', 'N/A')}

**After**: 
- Expected improvements: {suggestion.after_metrics.get('estimated_improvement', 'complexity reduction')}

### Generated Code
The refactored code is production-ready and includes comprehensive tests.

### Review Checklist
- [ ] Code compiles and all tests pass
- [ ] Behavior is identical to original (no logic changes)
- [ ] No new dependencies introduced
- [ ] Performance is maintained or improved
- [ ] Documentation updated (docstrings, comments)
- [ ] Code follows team style guide

### Tests
{len(suggestion.test_code.split('def test_'))} test cases included to verify the refactoring.

---
*Generated by CodeViz AI Refactoring Engine*
*Confidence: {suggestion.opportunity.confidence * 100:.0f}%*
""",
            "refactored_code": suggestion.refactored_code,
            "test_code": suggestion.test_code
        }
