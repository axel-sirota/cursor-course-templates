# Agentic Module Vibe Coding Guide

## Purpose & Scope

This guide provides rules, patterns, and instructions for AI coding assistants (Claude Code, Cursor, etc.) working on projects using the Agentic Module Pattern. Reference this document when implementing modules, agents, or related components.

**When to use this guide:**
- Creating new agentic modules
- Adding or modifying agents
- Implementing processors, services, or API endpoints
- Writing tests for agentic components

## Project Architecture Quick Reference

### Core Principles
1. **Single Entry Point**: External access only through services
2. **Clean State Management**: All agent states inherit from BaseAgentState
3. **Processor Isolation**: Business logic separated from external integrations
4. **Graph-Level Injection**: Dependency injection at orchestrator level for testing

### Directory Structure
```
module_name/
├── models/domain_models.py
├── repository/
│   ├── repository.py
│   └── mappers.py
├── services/module_service.py
├── cache/
│   ├── cache_manager.py
│   ├── cache_keys.py
│   ├── invalidation.py
│   └── typed_accessors.py
├── processors/
│   ├── llm_processor.py
│   └── api_processor.py
├── prompts/processor_prompts.py
├── agents/
│   └── agent_name/
│       ├── state.py
│       ├── nodes/
│       │   ├── __init__.py
│       │   └── example_node.py
│       └── orchestrator.py
├── jobs/agent_jobs.py
└── tests/
    ├── test_services.py
    ├── test_agents.py
    └── test_processors.py
```

### API Architecture Pattern

**Dual API Structure**: APIs are split into two types based on their consumers:

1. **Experience APIs** (`/api/*`): UI-facing APIs for human users
   - Handle user authentication and authorization
   - Optimized for presentation layer concerns
   - Use user tokens and session management
   - Located in `app/api/`

2. **Agent Tools APIs** (`/api/tools/*`): Internal APIs for AI agents and automation
   - Handle service-to-service authentication
   - Optimized for programmatic access
   - Use service tokens and API keys
   - Located in `app/api/tools/`

**Example Structure:**
```
app/api/
├── module_api.py          # Experience API for UI
└── tools/
    └── module_tool_api.py # Agent Tools API for automation
```

**Benefits:**
- Different authentication models (user vs service tokens)
- Different response formats (UI-optimized vs agent-optimized)
- Different rate limiting and usage patterns
- Cleaner separation of concerns
- Future flexibility for agent-specific features

## Mandatory Rules

### 1. Access Control
- **NEVER** allow direct access to repositories, processors, or agents from external modules
- **ALWAYS** route external access through services
- **NEVER** use SQL JOINs with tables from other modules

### 2. State Management
- **ALWAYS** inherit from BaseAgentState for all agent states
- **NEVER** store processor instances in state objects
- **ALWAYS** treat nodes as pure functions (state in → state out)

### 3. Testing Requirements
- **ALWAYS** use graph-level processor injection for testing
- **ALWAYS** write both node unit tests and agent flow tests
- **NEVER** test with real external APIs/LLMs in agent flow tests

### 4. Dependency Injection
- **ALWAYS** inject processors at graph creation time
- **NEVER** hardcode processor dependencies in nodes
- **ALWAYS** provide default processors for production use

## Task Implementation Guide

### Create Dual API Module

**Command**: "Create dual API module called {module_name}"

**Implementation Steps:**

1. **Create Experience API** in `app/api/{module_name}_api.py`:
```python
from fastapi import APIRouter, Depends
from app.core.dependencies import require_auth

router = APIRouter(prefix="/{module_name}", tags=["{module_name}"])

@router.get("/data")
async def get_data(current_user: dict = Depends(require_auth)):
    """UI-facing endpoint for human users"""
    return {"data": "UI-optimized response"}
```

2. **Create Agent Tools API** in `app/api/tools/{module_name}_tool_api.py`:
```python
from fastapi import APIRouter, Depends, Header
from typing import Optional

router = APIRouter(prefix="/tools/{module_name}", tags=["{module_name}_tools"])

@router.get("/data")
async def get_data_for_agent(x_service_token: Optional[str] = Header(None)):
    """Agent-facing endpoint for automation"""
    # Service token validation would go here
    return {"data": "Agent-optimized response"}
```

3. **Create corresponding test files**:
   - `tests/api/test_{module_name}_api.py` - Experience API tests
   - `tests/api/tools/test_{module_name}_tool_api.py` - Agent Tools API tests

4. **Register both routers** in `app/main.py`:
```python
from app.api import {module_name}_api
from app.api.tools import {module_name}_tool_api

# In create_app() function
app.include_router({module_name}_api.router, prefix="/api")
app.include_router({module_name}_tool_api.router, prefix="/api")
```

### Create New Agent Module

**Command**: "Create new agent module called {module_name}"

**Implementation Steps:**

1. **Add required dependencies** to requirements.txt:
```bash
pip install langgraph
```
Add to requirements.txt:
```
langgraph>=0.2.0
```

2. **Create directory structure** following the pattern above
3. **Implement BaseAgentState** in app/models/base_agent_state.py and import in app/models/__init__.py:
```python
from typing import TypedDict, List, Set, Optional, Any, Dict
from datetime import datetime

class BaseAgentState(TypedDict, total=False):
    node_history: List[str]
    completed_nodes: Set[str]
    current_step: str
    errors: List[str]
    retry_count: int
    started_at: Optional[datetime]
    updated_at: Optional[datetime]
    config: Dict[str, Any]

# Utility functions for state operations
def add_error(state: BaseAgentState, error: str) -> None:
    """Add an error to the state"""
    if "errors" not in state:
        state["errors"] = []
    state["errors"].append(error)
    state["updated_at"] = datetime.now()

def mark_node_complete(state: BaseAgentState, node_name: str) -> None:
    """Mark a node as complete in the state"""
    if "completed_nodes" not in state:
        state["completed_nodes"] = set()
    if "node_history" not in state:
        state["node_history"] = []
    
    state["completed_nodes"].add(node_name)
    state["node_history"].append(node_name)
    state["current_step"] = node_name
    state["updated_at"] = datetime.now()

def create_initial_state() -> BaseAgentState:
    """Create an initial state with default values"""
    return BaseAgentState(
        node_history=[],
        completed_nodes=set(),
        current_step="",
        errors=[],
        retry_count=0,
        started_at=datetime.now(),
        updated_at=datetime.now(),
        config={}
    )
```

**app/models/__init__.py**:
```python
from .base_agent_state import BaseAgentState, add_error, mark_node_complete, create_initial_state

__all__ = ["BaseAgentState", "add_error", "mark_node_complete", "create_initial_state"]
```

4. **Create module structure** in app/modules/{module_name}/
5. **Create agent-specific state** in app/modules/{module_name}/agents/{agent_name}/state.py:
```python
from typing import TypedDict
from app.models import BaseAgentState

class {AgentName}State(BaseAgentState, total=False):
    user_request: str
    final_result: str
```

6. **Create minimal orchestrator** in app/modules/{module_name}/agents/{agent_name}/orchestrator.py:
```python
from typing import Any
from langgraph.graph import StateGraph, START, END
from .state import {AgentName}State
from app.models import mark_node_complete

def create_{agent_name}_graph(processors=None) -> Any:
    """Build the LangGraph workflow for {agent_name} agent"""
    def passthrough_node(state: {AgentName}State) -> {AgentName}State:
        state["final_result"] = "{agent_name}"
        mark_node_complete(state, "passthrough")
        return state
    
    graph = StateGraph({AgentName}State)
    graph.add_node("passthrough", passthrough_node)
    graph.add_edge(START, "passthrough")
    graph.add_edge("passthrough", END)
    
    return graph.compile()
```

7. **Create service** in app/modules/{module_name}/services/{module_name}_service.py:
```python
import asyncio
from app.modules.{module_name}.agents.{agent_name}.orchestrator import create_{agent_name}_graph
from app.modules.{module_name}.agents.{agent_name}.state import {AgentName}State
from app.models import create_initial_state

class {ModuleName}Service:
    def __init__(self):
        self.{agent_name}_graph = create_{agent_name}_graph()
    
    async def execute_{agent_name}(self, user_request: str) -> str:
        initial_state = create_initial_state()
        initial_state.update({
            "user_request": user_request,
            "final_result": ""
        })
        final_state = await self.{agent_name}_graph.ainvoke(initial_state)
        return final_state["final_result"]
```

8. **Create E2E test** in tests/modules/{module_name}/test_{module_name}.py:
```python
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.modules.{module_name}.agents.{agent_name}.orchestrator import create_{agent_name}_graph
from app.modules.{module_name}.agents.{agent_name}.state import {AgentName}State
from app.models import create_initial_state

client = TestClient(app)

@pytest.mark.asyncio
async def test_{agent_name}_agent_flow():
    """Test agent flow execution"""
    # Create graph (no mocks needed for passthrough)
    graph = create_{agent_name}_graph()
    
    # Execute agent
    initial_state = create_initial_state()
    initial_state.update({
        "user_request": "test",
        "final_result": ""
    })
    final_state = await graph.ainvoke(initial_state)
    
    # Verify results
    assert final_state["final_result"] == "{agent_name}"
    assert "passthrough" in final_state["completed_nodes"]

def test_{module_name}_api_endpoint():
    """Test API endpoint"""
    # Register and get token
    register_response = client.post("/api/auth/register", json={{
        "email": "test_{module_name}@example.com", 
        "password": "testpass",
        "fullName": "API Test User"
    }})
    assert register_response.status_code == 200
    token = register_response.json()["accessToken"]
    
    # Test the module endpoint
    response = client.post(
        "/api/{module_name}/execute",
        json={{"userRequest": "test request"}},
        headers={{"Authorization": f"Bearer {{token}}"}}
    )
    assert response.status_code == 200
    
    data = response.json()
    assert data["result"] == "{agent_name}"

def test_{module_name}_api_unauthorized():
    """Test API endpoint without authentication"""
    response = client.post(
        "/api/{module_name}/execute",
        json={{"userRequest": "test request"}}
    )
    assert response.status_code == 401
```

9. **Register module API** in app/main.py by adding the import and router:
```python
# Add to imports section
from app.api import health, auth, {module_name}

# Add to create_app() function after existing routers
app.include_router({module_name}.router)
```

10. **Create API endpoints** in app/api/{module_name}.py:
```python
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from app.core.dependencies import require_auth
from app.modules.{module_name}.services.{module_name}_service import {ModuleName}Service
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/{module_name}", tags=["{module_name}"])

class {ModuleName}Request(BaseModel):
    user_request: str = Field(alias="userRequest")
    
    model_config = {"validate_by_name": True}

class {ModuleName}Response(BaseModel):
    result: str

service = {ModuleName}Service()

@router.post("/execute", response_model={ModuleName}Response)
async def execute_{module_name}(
    request: {ModuleName}Request,
    current_user: dict = Depends(require_auth)
):
    """Execute {module_name} agent"""
    result = await service.execute_{agent_name}(request.user_request)
    return {ModuleName}Response(result=result)
```

### Add LLM Node

**Command**: "Add agent LLM step as position {position} for {purpose}"

**Implementation Steps:**

1. **Create prompt file** in app/modules/{module_name}/prompts/{node_name}_prompts.py:

**IMPORTANT**: Do NOT attempt to write actual prompt content. Use placeholder text "ADD YOUR PROMPT HERE" for both SYSTEM_PROMPT and USER_PROMPT. The actual prompts should be written by domain experts, not generated automatically.
```python
from pydantic import BaseModel, Field
from typing import Dict, Any

class {NodeName}Input(BaseModel):
    user_request: str = Field(alias="userRequest")
    context: Dict[str, Any] = {}
    
    model_config = {"validate_by_name": True}

class {NodeName}Output(BaseModel):
    result: str
    confidence: float = 0.0

SYSTEM_PROMPT = "ADD YOUR PROMPT HERE"

USER_PROMPT = "ADD YOUR PROMPT HERE"
```

2. **Create processor** in app/modules/{module_name}/processors/{node_name}_processor.py:
```python
from app.modules.{module_name}.prompts.{node_name}_prompts import {NodeName}Input, {NodeName}Output, SYSTEM_PROMPT, USER_PROMPT

class {NodeName}Processor:
    def __init__(self, llm_client):
        self.llm_client = llm_client
    
    def process(self, input_data: {NodeName}Input) -> {NodeName}Output:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_PROMPT.format(**input_data.model_dump())}
        ]
        
        response = self.llm_client.chat_completion(messages)
        
        return {NodeName}Output(
            result=response["content"],
            confidence=0.8  # Default confidence
        )
```

3. **Create node** in app/modules/{module_name}/agents/{agent_name}/nodes/{node_name}_node.py:
```python
from ..state import {AgentName}State
from app.modules.{module_name}.prompts.{node_name}_prompts import {NodeName}Input
from app.models import mark_node_complete

def create_{node_name}_node(processor):
    def {node_name}_node(state: {AgentName}State) -> {AgentName}State:
        # Extract input from state
        input_data = {NodeName}Input(
            userRequest=state["user_request"],
            context=state.get("context", {})
        )
        
        # Process through LLM
        result = processor.process(input_data)
        
        # Update state
        state["{node_name}_result"] = result.result
        state["{node_name}_confidence"] = result.confidence
        mark_node_complete(state, "{node_name}")
        
        return state
    
    return {node_name}_node
```

4. **Update state** to include new fields:
```python
from typing import TypedDict
from app.models import BaseAgentState

class {AgentName}State(BaseAgentState, total=False):
    user_request: str
    {node_name}_result: str
    {node_name}_confidence: float
    final_result: str
```

5. **Update orchestrator** to include new node and positioning
6. **Create node unit test** and **update E2E test** with mocked processor

### Add Simple Node

**Command**: "Add simple node for {purpose}"

**Implementation Steps:**

1. **Create processor** in app/modules/{module_name}/processors/{node_name}_processor.py:
```python
class {NodeName}Processor:
    def process(self, input_data: dict) -> dict:
        # Implement business logic
        return {"result": f"Processed: {input_data.get('data', 'no data')}"}
```

2. **Create node** in app/modules/{module_name}/agents/{agent_name}/nodes/{node_name}_node.py:
```python
from app.models import mark_node_complete

def create_{node_name}_node(processor):
    def {node_name}_node(state: {AgentName}State) -> {AgentName}State:
        # Extract input from state
        input_data = {
            "data": state.get("relevant_field", ""),
            "config": state.get("config", {})
        }
        
        # Process
        result = processor.process(input_data)
        
        # Update state
        state["{node_name}_result"] = result["result"]
        mark_node_complete(state, "{node_name}")
        
        return state
    
    return {node_name}_node
```

3. **Update state, orchestrator, and tests** following same pattern as LLM node

## Code Templates

### BaseAgentState Extension
```python
from typing import TypedDict
from app.models import BaseAgentState

class {AgentName}State(BaseAgentState, total=False):
    # Input
    user_request: str
    
    # Processing results
    {step}_result: str
    
    # Final output
    final_result: str
    
    # Configuration
    api_keys: Dict[str, str]
```

### Node Factory Template
```python
from app.models import mark_node_complete

def create_{node_name}_node(processors: Dict[str, Any] = None) -> callable:
    """Factory function to create a {node_name} node"""
    # Get processor from dependency injection or create default
    # CRITICAL: Use .get() with default value to handle missing keys
    processor = processors.get("{processor_key}", DefaultProcessor()) if processors else DefaultProcessor()
    
    def {node_name}_node(state: {AgentName}State) -> {AgentName}State:
        # Read from state
        input_data = extract_input(state)
        
        # Process
        result = processor.process(input_data)
        
        # Write to state
        update_state(state, result)
        mark_node_complete(state, "{node_name}")
        
        return state
    
    return {node_name}_node
```

**CRITICAL**: When using processor injection, always use `.get(key, default)` pattern, not just `.get(key)`. This prevents `None` values when the processors dict exists but doesn't contain the specific processor key.

### Test Template
```python
from unittest.mock import Mock
import pytest
from app.models import create_initial_state

def test_{node_name}_node():
    # Mock processor
    mock_processor = Mock()
    mock_processor.process.return_value = {"result": "expected_result"}
    
    # Create node
    node = create_{node_name}_node(mock_processor)
    
    # Test state
    state = create_initial_state()
    state.update({"input_field": "test_input"})
    result_state = node(state)
    
    # Assertions
    assert result_state["{node_name}_result"] == "expected_result"
    assert "{node_name}" in result_state["completed_nodes"]
```

## Validation Checklist

Before completing any task, verify:

### Architecture Compliance
- [ ] External access only through services
- [ ] State inherits from BaseAgentState
- [ ] Processors injected at graph level
- [ ] No direct database/API calls in nodes

### Code Quality
- [ ] All nodes have unit tests
- [ ] Agent flow has E2E test
- [ ] Mocks used for external dependencies
- [ ] Error handling implemented

### File Structure
- [ ] Files in correct directories
- [ ] Proper imports and dependencies
- [ ] __init__.py files where needed

## Common Anti-Patterns to Avoid

### ❌ Don't Do This
```python
# Hardcoded processor in node
def bad_node(state):
    result = llm_processor.process()  # ❌ Hardcoded dependency

# Direct external access
def bad_controller():
    return module.repository.get_data()  # ❌ Bypassing service

# Processor in state
@dataclass
class BadState(BaseAgentState):
    processor: LLMProcessor  # ❌ Infrastructure in domain model

# WRONG: Processor injection without default fallback
def create_bad_node(processors=None):
    processor = processors.get("processor_key") if processors else DefaultProcessor()  # ❌ Returns None when key missing
    def bad_node(state):
        result = processor.process()  # ❌ Will fail with NoneType error
```

### ✅ Do This Instead
```python
# Injected processor
def create_good_node(processor):
    def good_node(state):
        result = processor.process()  # ✅ Injected dependency

# Service access
def good_controller():
    return module_service.get_data()  # ✅ Through service

# Clean state
@dataclass
class GoodState(BaseAgentState):
    business_data: str  # ✅ Domain-focused

# CORRECT: Processor injection with proper fallback
def create_good_node(processors=None):
    processor = processors.get("processor_key", DefaultProcessor()) if processors else DefaultProcessor()  # ✅ Always returns valid processor
    def good_node(state):
        result = processor.process()  # ✅ Always works
```

## Troubleshooting

### Common Issues

**"Cannot find processor"**
- Ensure processor is injected at graph creation
- Check orchestrator default processor mapping

**"State modification not working"**
- Verify node returns modified state
- Check state field types and defaults

**"Tests failing with real APIs"**
- Confirm mocks are injected properly
- Verify test uses create_graph(mock_processors)

**"Import errors"**
- Check __init__.py files exist
- Verify relative imports in agent modules

### Quick Fixes

**Add missing __init__.py**: Touch file in each package directory
**Fix circular imports**: Move shared types to models/
**Mock not working**: Ensure mock passed to create_graph()
**State not updating**: Return state from node function