"""
API Tester - Test discovered APIs with requests and response validation
Captures request/response pairs for documentation and testing
"""

import requests
import json
import time
from datetime import datetime
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
import traceback


@dataclass
class APIRequest:
    """Represents an API request"""
    method: str
    url: str
    headers: Dict[str, str] = None
    body: Dict[str, Any] = None
    params: Dict[str, Any] = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
        if self.headers is None:
            self.headers = {}


@dataclass
class APIResponse:
    """Represents an API response"""
    status_code: int
    headers: Dict[str, str]
    body: Any
    time_ms: float
    error: str = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


@dataclass
class APITestResult:
    """Complete test result for an API endpoint"""
    api_path: str
    method: str
    request: APIRequest
    response: APIResponse
    success: bool
    test_timestamp: str = None
    notes: str = None
    
    def __post_init__(self):
        if self.test_timestamp is None:
            self.test_timestamp = datetime.now().isoformat()


class APITester:
    """Test APIs discovered by the repository scanner"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.test_results: List[APITestResult] = []
        self.request_templates = {
            "GET": {"headers": {"Accept": "application/json"}},
            "POST": {"headers": {"Content-Type": "application/json"}, "body": {}},
            "PUT": {"headers": {"Content-Type": "application/json"}, "body": {}},
            "PATCH": {"headers": {"Content-Type": "application/json"}, "body": {}},
            "DELETE": {"headers": {"Accept": "application/json"}},
        }
    
    def test_api(self, api_path: str, method: str = "GET", body: Dict = None, 
                 headers: Dict = None, params: Dict = None, timeout: int = 5, validate_only: bool = False) -> APITestResult:
        """Test a single API endpoint"""
        
        # Build full URL
        full_url = f"{self.base_url}{api_path}"
        
        # Handle path parameters
        url = self._replace_path_params(full_url, params or {})
        
        # Prepare headers
        test_headers = self.request_templates.get(method.upper(), {}).get("headers", {}).copy()
        if headers:
            test_headers.update(headers)
        
        # Prepare body
        test_body = body or self.request_templates.get(method.upper(), {}).get("body", {})
        
        # Create request
        request = APIRequest(
            method=method.upper(),
            url=url,
            headers=test_headers,
            body=test_body if test_body else None,
            params=params
        )
        
        # Execute request
        try:
            start_time = time.time()
            
            if method.upper() == "GET":
                resp = requests.get(url, headers=test_headers, params=params, timeout=timeout)
            elif method.upper() == "POST":
                resp = requests.post(url, headers=test_headers, json=test_body, timeout=timeout)
            elif method.upper() == "PUT":
                resp = requests.put(url, headers=test_headers, json=test_body, timeout=timeout)
            elif method.upper() == "PATCH":
                resp = requests.patch(url, headers=test_headers, json=test_body, timeout=timeout)
            elif method.upper() == "DELETE":
                resp = requests.delete(url, headers=test_headers, timeout=timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            end_time = time.time()
            time_ms = (end_time - start_time) * 1000
            
            # Parse response body
            try:
                response_body = resp.json()
            except:
                response_body = resp.text
            
            # Create response
            response = APIResponse(
                status_code=resp.status_code,
                headers=dict(resp.headers),
                body=response_body,
                time_ms=time_ms,
                error=None
            )
            
            # Create test result
            success = 200 <= resp.status_code < 300
            result = APITestResult(
                api_path=api_path,
                method=method.upper(),
                request=request,
                response=response,
                success=success,
                notes=f"Response time: {time_ms:.2f}ms"
            )
            
        except requests.exceptions.Timeout:
            response = APIResponse(
                status_code=0,
                headers={},
                body=None,
                time_ms=timeout * 1000,
                error=f"Request timeout after {timeout}s"
            )
            result = APITestResult(
                api_path=api_path,
                method=method.upper(),
                request=request,
                response=response,
                success=False,
                notes="Request timed out"
            )
        
        except Exception as e:
            response = APIResponse(
                status_code=0,
                headers={},
                body=None,
                time_ms=0,
                error=str(e)
            )
            result = APITestResult(
                api_path=api_path,
                method=method.upper(),
                request=request,
                response=response,
                success=False,
                notes=f"Error: {str(e)}"
            )
        
        self.test_results.append(result)
        return result
    
    def test_apis_batch(self, apis: List[Dict], timeout: int = 5) -> List[APITestResult]:
        """Test multiple APIs"""
        results = []
        for api in apis:
            try:
                result = self.test_api(
                    api_path=api.get('path', ''),
                    method=api.get('methods', ['GET'])[0],
                    timeout=timeout
                )
                results.append(result)
            except Exception as e:
                print(f"Error testing {api.get('path')}: {str(e)}")
        
        return results
    
    def _replace_path_params(self, url: str, params: Dict) -> str:
        """Replace path parameters in URL (e.g., :id with actual value)"""
        import re
        def replace_param(match):
            param_name = match.group(1)
            return str(params.get(param_name, match.group(0)))
        
        return re.sub(r':(\w+)', replace_param, url)
    
    def get_test_summary(self) -> Dict:
        """Get summary of all tests"""
        total = len(self.test_results)
        passed = len([r for r in self.test_results if r.success])
        failed = total - passed
        avg_time = sum([r.response.time_ms for r in self.test_results]) / total if total > 0 else 0
        
        return {
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "success_rate": f"{(passed/total*100):.1f}%" if total > 0 else "0%",
            "avg_response_time_ms": f"{avg_time:.2f}",
            "test_timestamp": datetime.now().isoformat()
        }
    
    def export_results(self, format: str = "json") -> str:
        """Export test results in various formats"""
        
        if format.lower() == "json":
            return self._export_json()
        elif format.lower() == "csv":
            return self._export_csv()
        elif format.lower() == "markdown":
            return self._export_markdown()
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _export_json(self) -> str:
        """Export as JSON"""
        data = {
            "summary": self.get_test_summary(),
            "results": [
                {
                    "api_path": r.api_path,
                    "method": r.method,
                    "request": {
                        "url": r.request.url,
                        "headers": r.request.headers,
                        "body": r.request.body
                    },
                    "response": {
                        "status_code": r.response.status_code,
                        "time_ms": r.response.time_ms,
                        "body": r.response.body,
                        "error": r.response.error
                    },
                    "success": r.success,
                    "notes": r.notes
                }
                for r in self.test_results
            ]
        }
        return json.dumps(data, indent=2, default=str)
    
    def _export_csv(self) -> str:
        """Export as CSV"""
        import csv
        from io import StringIO
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            "API Path", "Method", "Status Code", "Response Time (ms)", 
            "Success", "Error", "Notes"
        ])
        
        # Data
        for r in self.test_results:
            writer.writerow([
                r.api_path,
                r.method,
                r.response.status_code,
                f"{r.response.time_ms:.2f}",
                "Yes" if r.success else "No",
                r.response.error or "",
                r.notes or ""
            ])
        
        return output.getvalue()
    
    def _export_markdown(self) -> str:
        """Export as Markdown table"""
        summary = self.get_test_summary()
        
        md = f"""# API Test Results

**Generated:** {summary['test_timestamp']}

## Summary
- **Total Tests:** {summary['total_tests']}
- **Passed:** {summary['passed']}
- **Failed:** {summary['failed']}
- **Success Rate:** {summary['success_rate']}
- **Avg Response Time:** {summary['avg_response_time_ms']}ms

## Detailed Results

| API Path | Method | Status | Time (ms) | Success | Notes |
|----------|--------|--------|-----------|---------|-------|
"""
        
        for r in self.test_results:
            status_icon = "✅" if r.success else "❌"
            md += f"| `{r.api_path}` | {r.method} | {r.response.status_code} | {r.response.time_ms:.2f} | {status_icon} | {r.notes or ''} |\n"
        
        return md


class APIDocumenter:
    """Generate documentation from API tests"""
    
    def __init__(self, test_results: List[APITestResult]):
        self.test_results = test_results
    
    def generate_documentation(self) -> str:
        """Generate comprehensive API documentation"""
        
        doc = "# API Documentation\n\n"
        doc += f"*Generated: {datetime.now().isoformat()}*\n\n"
        
        # Group by path
        grouped = {}
        for result in self.test_results:
            path = result.api_path
            if path not in grouped:
                grouped[path] = []
            grouped[path].append(result)
        
        # Document each API
        for path in sorted(grouped.keys()):
            results = grouped[path]
            first_result = results[0]
            
            doc += f"## `{first_result.method} {path}`\n\n"
            
            # Show test results
            if results:
                latest = results[-1]
                doc += f"**Status:** {latest.response.status_code}\n"
                doc += f"**Response Time:** {latest.response.time_ms:.2f}ms\n"
                doc += f"**Last Tested:** {latest.test_timestamp}\n\n"
            
            # Show response example
            if first_result.response.body:
                doc += "### Response\n\n"
                if isinstance(first_result.response.body, dict):
                    doc += "```json\n"
                    doc += json.dumps(first_result.response.body, indent=2)
                    doc += "\n```\n\n"
                else:
                    doc += f"```\n{first_result.response.body}\n```\n\n"
        
        return doc
