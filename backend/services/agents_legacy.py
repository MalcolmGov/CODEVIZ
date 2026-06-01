import os
import json
import requests
from datetime import datetime
from typing import Any, Dict, List, Optional
from langchain.llms import Ollama
from langchain.agents import Tool, initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
import redis

# Initialize connections
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama2")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

redis_client = redis.from_url(REDIS_URL, decode_responses=True)

# Initialize LLM
llm = Ollama(base_url=OLLAMA_BASE_URL, model=OLLAMA_MODEL, temperature=0.7)


class Agent:
    """Base agent for task automation"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.memory = ConversationBufferMemory(memory_key="chat_history")
        self.tools = self._create_tools()
        self.agent = None

    def _create_tools(self) -> List[Tool]:
        """Create tools available to the agent"""
        return [
            Tool(
                name="file_read",
                func=self._file_read,
                description="Read contents of a file. Input: file_path",
            ),
            Tool(
                name="file_write",
                func=self._file_write,
                description="Write content to a file. Input: json with file_path and content",
            ),
            Tool(
                name="web_search",
                func=self._web_search,
                description="Search the web for information. Input: search query",
            ),
            Tool(
                name="cache_set",
                func=self._cache_set,
                description="Store data in cache. Input: json with key and value",
            ),
            Tool(
                name="cache_get",
                func=self._cache_get,
                description="Retrieve data from cache. Input: cache key",
            ),
            Tool(
                name="task_log",
                func=self._task_log,
                description="Log a task result. Input: json with task_name and result",
            ),
        ]

    def _file_read(self, file_path: str) -> str:
        """Read file contents"""
        try:
            with open(file_path, "r") as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"

    def _file_write(self, params: str) -> str:
        """Write to file"""
        try:
            data = json.loads(params)
            file_path = data.get("file_path")
            content = data.get("content")
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w") as f:
                f.write(content)
            return f"Successfully wrote to {file_path}"
        except Exception as e:
            return f"Error writing file: {str(e)}"

    def _web_search(self, query: str) -> str:
        """Simulate web search (returns mock data for demo)"""
        return f"Search results for '{query}': [mock data - integrate with real search API]"

    def _cache_set(self, params: str) -> str:
        """Set cache value"""
        try:
            data = json.loads(params)
            key = data.get("key")
            value = data.get("value")
            redis_client.setex(key, 3600, json.dumps(value))
            return f"Cached {key}"
        except Exception as e:
            return f"Cache error: {str(e)}"

    def _cache_get(self, key: str) -> str:
        """Get cache value"""
        try:
            value = redis_client.get(key)
            if value:
                return json.loads(value)
            return f"No cache found for {key}"
        except Exception as e:
            return f"Cache error: {str(e)}"

    def _task_log(self, params: str) -> str:
        """Log task execution"""
        try:
            data = json.loads(params)
            task_name = data.get("task_name")
            result = data.get("result")
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "task": task_name,
                "result": result,
            }
            redis_client.lpush(f"tasks:{self.name}", json.dumps(log_entry))
            return f"Logged: {task_name}"
        except Exception as e:
            return f"Logging error: {str(e)}"

    def initialize(self):
        """Initialize the agent with tools"""
        self.agent = initialize_agent(
            tools=self.tools,
            llm=llm,
            agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
            memory=self.memory,
            verbose=True,
            max_iterations=5,
        )

    def run(self, task: str) -> Dict[str, Any]:
        """Execute a task"""
        if not self.agent:
            self.initialize()

        try:
            result = self.agent.run(task)
            return {"status": "success", "result": result, "timestamp": datetime.now().isoformat()}
        except Exception as e:
            return {"status": "error", "error": str(e), "timestamp": datetime.now().isoformat()}


class DataProcessingAgent(Agent):
    """Agent for data processing and analysis tasks"""

    def __init__(self):
        super().__init__("DataProcessor", "Processes and analyzes data files")

    def _create_tools(self) -> List[Tool]:
        """Add data-specific tools"""
        base_tools = super()._create_tools()
        base_tools.extend([
            Tool(
                name="parse_csv",
                func=self._parse_csv,
                description="Parse CSV file and return summary. Input: file_path",
            ),
            Tool(
                name="process_json",
                func=self._process_json,
                description="Process JSON file. Input: file_path",
            ),
        ])
        return base_tools

    def _parse_csv(self, file_path: str) -> str:
        """Parse CSV file"""
        try:
            import csv
            with open(file_path, "r") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            return f"CSV parsed: {len(rows)} rows, columns: {list(rows[0].keys()) if rows else 'none'}"
        except Exception as e:
            return f"Error parsing CSV: {str(e)}"

    def _process_json(self, file_path: str) -> str:
        """Process JSON file"""
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
            return f"JSON processed: {json.dumps(data, indent=2)[:500]}..."
        except Exception as e:
            return f"Error processing JSON: {str(e)}"


class CodeReviewAgent(Agent):
    """Agent for code review and analysis"""

    def __init__(self):
        super().__init__("CodeReviewer", "Reviews and analyzes code")

    def _create_tools(self) -> List[Tool]:
        """Add code-specific tools"""
        base_tools = super()._create_tools()
        base_tools.extend([
            Tool(
                name="analyze_python",
                func=self._analyze_python,
                description="Analyze Python file for issues. Input: file_path",
            ),
        ])
        return base_tools

    def _analyze_python(self, file_path: str) -> str:
        """Analyze Python code"""
        try:
            with open(file_path, "r") as f:
                code = f.read()
            # Basic analysis
            issues = []
            if "pass" in code and code.count("pass") > 3:
                issues.append("Multiple empty functions detected")
            if len(code.split("\n")) > 500:
                issues.append("File is large, consider splitting")
            return f"Code analysis for {file_path}: {issues if issues else 'No major issues'}"
        except Exception as e:
            return f"Error analyzing code: {str(e)}"


def create_agent(agent_type: str) -> Agent:
    """Factory function to create agents"""
    agents = {
        "general": Agent("GeneralAssistant", "General purpose task assistant"),
        "data": DataProcessingAgent(),
        "code": CodeReviewAgent(),
    }
    return agents.get(agent_type, agents["general"])
