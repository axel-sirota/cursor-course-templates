# Database Management Vibe Coding Guide

## Purpose & Scope

This guide provides rules, patterns, and instructions for AI coding assistants (Claude Code, Cursor, etc.) working on database-related tasks in projects using Supabase with the Repository Pattern. Reference this document when implementing database models, repositories, services, or migration tasks.

**Related Documents:**
- [FastAPI Boilerplate Guide](vibe_fastapi_boilerplate.md) - For API model patterns and camelCase conventions
- [Agent Module Guide](vibe_agent_module.md) - For module structure and service patterns

**When to use this guide:**
- Creating database models and repositories from migrations
- Implementing CRUD operations for database tables
- Working with Supabase database schemas
- Managing database migrations across environments
- Creating domain services that use multiple repositories

## Project Architecture Quick Reference

### Core Principles
1. **Repository Pattern**: Each table has its own repository class with CRUD operations
2. **Layered Model Architecture**: Use Base → Full → Create/Update model hierarchy for type safety
3. **Service Layer**: Complex operations and JOINs are handled in services, not repositories
4. **Module Isolation**: Repositories are never exported or accessed from outside their module
5. **Migration-Driven**: Database schema changes are managed through Supabase CLI migrations
6. **Centralized Database Access**: Use shared database client instead of individual Supabase clients

### Environment Structure
```
database/
├── develop/
│   └── supabase/
│       ├── config.toml
│       └── migrations/
│           └── {timestamp}_{description}.sql
└── prod/
    └── supabase/
        ├── config.toml
        └── migrations/
            └── {timestamp}_{description}.sql
```

### Module Directory Structure
```
module_name/
├── models/
│   ├── __init__.py          # Export models only
│   └── domain_models.py     # Layered Pydantic models (Base → Full → Create/Update)
└── repository/
    ├── __init__.py          # Empty - repositories not exported
    └── repository.py        # Repository classes with CRUD + type-safe mappers
```

### Enhanced Model Architecture
```
domain_models.py structure:
├── {Entity}Base           # Business fields only (no id, timestamps)
├── {Entity}               # Full model (Base + id + timestamps)
├── {Entity}Create         # For creation (inherits from Base)
└── {Entity}Update         # For updates (only updatable fields)
```

### Benefits of Layered Architecture
1. **Type Safety**: Operation-specific models prevent invalid field combinations
2. **Clear Separation**: Business logic vs database metadata clearly separated
3. **Flexibility**: Different models for different operations (create vs update)
4. **Maintainability**: Schema changes don't break business logic
5. **Validation**: Pydantic handles validation at model boundaries
6. **Centralized Database Access**: Single database client reduces complexity

### Data Flow Pattern
```
API Request → Service Layer → Repository → Database
     ↓              ↓            ↓
Domain Models → Operation Models → Raw Data
     ↑              ↑            ↑
API Response ← Service Layer ← Repository ← Database
```

**Key Flow:**
1. **API Request** uses camelCase API models
2. **Service Layer** converts to database models (Create/Update)
3. **Repository** uses type-safe mappers for database operations
4. **Database** returns raw data
5. **Repository** converts to full domain models
6. **Service Layer** handles business logic
7. **API Response** converts to camelCase API models

## Mandatory Rules

### 1. Repository Access Control
- **NEVER** export repositories from modules
- **NEVER** access repositories directly from outside their module
- **ALWAYS** use services to access database operations
- **ALWAYS** return model objects, never raw dictionaries

### 2. Layered Model Definition
- **ALWAYS** use layered model architecture (Base → Full → Create/Update)
- **ALWAYS** separate business fields from database metadata (id, timestamps)
- **ALWAYS** include proper field types and validation
- **ALWAYS** use snake_case for field names (matches database)
- **ALWAYS** include proper docstrings for models
- **ALWAYS** use operation-specific models (Create/Update) for type safety
- **NEVER** use database models for API responses - create separate API models
- **ALWAYS** use camelCase for API request/response models (see FastAPI boilerplate patterns)

### 3. Repository Implementation
- **ALWAYS** implement full CRUD operations (Create, Read, Update, Delete)
- **ALWAYS** include type-safe mapper functions for each model type (Base, Create, Update)
- **ALWAYS** use centralized database client (`db.client`) instead of individual Supabase clients
- **ALWAYS** handle database exceptions gracefully
- **NEVER** perform JOINs across different tables in repositories
- **ALWAYS** use operation-specific models in method signatures (Create for create, Update for update)

### 4. Migration Management
- **ALWAYS** create migrations using Supabase CLI only
- **ALWAYS** test migrations on develop environment first
- **ALWAYS** manually copy migrations to prod when ready for release
- **NEVER** automate production migration deployment

### 5. Testing Strategy
- **NEVER** write unit tests for repositories (they're straightforward CRUD)
- **ALWAYS** write unit tests for services with mocked repositories
- **ALWAYS** test business logic, error handling, and data transformations in services
- **ALWAYS** include mypy type checking for models and services

## Task Implementation Guide

### Create Model and Repository from Migration

**Command**: "Based on <link to migration file> create model and repository for {table_name}"

**Implementation Steps:**

1. **Analyze migration file** to understand table structure:
```sql
-- Example migration file analysis
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

2. **Create layered Pydantic models** in `app/modules/{module_name}/models/domain_models.py`:
```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid

# =============================================================================
# USER MODELS - Layered Architecture
# =============================================================================

class UserBase(BaseModel):
    """Base User model with only business fields (no id, timestamps)"""
    email: str = Field(..., description="User email address")
    full_name: str = Field(..., description="User's full name")
    
    class Config:
        from_attributes = True

class User(UserBase):
    """Full User model with all database fields"""
    id: str = Field(..., description="Unique user identifier")
    created_at: datetime = Field(..., description="Record creation timestamp")
    updated_at: datetime = Field(..., description="Record update timestamp")
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }

class UserCreate(UserBase):
    """User creation model (inherits from UserBase)"""
    pass

class UserUpdate(BaseModel):
    """User update model (only fields that can be updated)"""
    email: Optional[str] = Field(default=None, description="User email address")
    full_name: Optional[str] = Field(default=None, description="User's full name")
    
    class Config:
        from_attributes = True
```

3. **Export models** in `app/modules/{module_name}/models/__init__.py`:
```python
from .domain_models import User, UserCreate, UserUpdate

__all__ = ["User", "UserCreate", "UserUpdate"]
```

4. **Create repository class** in `app/modules/{module_name}/repository/repository.py`:
```python
from typing import List, Optional, Dict, Any
from app.core.database import db
from app.modules.{module_name}.models import User, UserCreate, UserUpdate
import logging

logger = logging.getLogger(__name__)

class UserRepository:
    """Repository for User table operations"""
    
    def __init__(self):
        self.table_name = "users"
    
    def _supabase_to_model(self, row: Dict[str, Any]) -> User:
        """Convert Supabase row to User model"""
        return User(
            id=str(row["id"]),  # Convert UUID to string
            email=row["email"],
            full_name=row["full_name"],
            created_at=row["created_at"],
            updated_at=row["updated_at"]
        )
    
    def _modelcreate_to_supabase(self, user_data: UserCreate) -> Dict[str, Any]:
        """Convert UserCreate model to Supabase row format"""
        return {
            "email": user_data.email,
            "full_name": user_data.full_name,
        }
    
    def _update_to_supabase(self, user_data: UserUpdate) -> Dict[str, Any]:
        """Convert UserUpdate model to Supabase row format"""
        return user_data.model_dump(exclude_none=True)
    
    async def create(self, user_data: UserCreate) -> User:
        """Create a new user"""
        try:
            data = self._modelcreate_to_supabase(user_data)
            result = db.client.table(self.table_name).insert(data).execute()
            
            if result.data:
                return self._supabase_to_model(result.data[0])
            else:
                raise Exception("Failed to create user")
                
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise
    
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        try:
            result = (
                db.client.table(self.table_name)
                .select("*")
                .eq("id", user_id)
                .execute()
            )
            
            if result.data:
                return self._supabase_to_model(result.data[0])
            return None
            
        except Exception as e:
            logger.error(f"Error getting user by ID {user_id}: {e}")
            raise
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        try:
            result = (
                db.client.table(self.table_name)
                .select("*")
                .eq("email", email)
                .execute()
            )
            
            if result.data:
                return self._supabase_to_model(result.data[0])
            return None
            
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {e}")
            raise
    
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[User]:
        """Get all users with pagination"""
        try:
            result = (
                db.client.table(self.table_name)
                .select("*")
                .range(offset, offset + limit - 1)
                .execute()
            )
            
            return [self._supabase_to_model(row) for row in result.data]
            
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            raise
    
    async def update(self, user_id: str, user_data: UserUpdate) -> User:
        """Update an existing user"""
        try:
            data = self._update_to_supabase(user_data)
            result = (
                db.client.table(self.table_name)
                .update(data)
                .eq("id", user_id)
                .execute()
            )
            
            if result.data:
                return self._supabase_to_model(result.data[0])
            else:
                raise Exception("Failed to update user")
                
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {e}")
            raise
    
    async def delete(self, user_id: str) -> bool:
        """Delete a user by ID"""
        try:
            result = (
                db.client.table(self.table_name)
                .delete()
                .eq("id", user_id)
                .execute()
            )
            
            return len(result.data) > 0
            
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {e}")
            raise
```

5. **Create empty repository __init__.py**:
```python
# Repositories are not exported - access through services only
__all__ = []
```

### Find and Use Existing Model

**Command**: "Use {ModelName} model to get {ModelName} objects"

**Implementation Steps:**

1. **Search for existing model** in codebase:
```bash
# Search for model definition
grep -r "class {ModelName}" app/modules/
```

2. **Locate module** that contains the model:
```python
# Check app/modules/{module_name}/models/__init__.py
from .domain_models import {ModelName}
```

3. **Check if service exists** in the module:
```bash
# Search for service that uses the model
grep -r "{ModelName}" app/modules/{module_name}/services/
```

4. **If service exists**, use it directly:
```python
from app.modules.{module_name}.services.{module_name}_service import {ModuleName}Service

# In your code
service = {ModuleName}Service()
result = await service.get_{model_name.lower()}s()
```

5. **If service doesn't exist**, propose creating one:
```python
# Suggest creating service in app/modules/{module_name}/services/{module_name}_service.py
class {ModuleName}Service:
    def __init__(self, supabase_client: Client):
        self.{model_name.lower()}_repo = {ModelName}Repository(supabase_client)
    
    async def get_{model_name.lower()}_by_id(self, {model_name.lower()}_id: str) -> Optional[{ModelName}]:
        """Get {model_name.lower()} by ID"""
        return await self.{model_name.lower()}_repo.get_by_id({model_name.lower()}_id)
    
    async def create_{model_name.lower()}(self, {model_name.lower()}: {ModelName}) -> {ModelName}:
        """Create new {model_name.lower()}"""
        return await self.{model_name.lower()}_repo.create({model_name.lower()})
```

## Code Templates

### Layered Pydantic Model Template
```python
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

# =============================================================================
# {MODEL_NAME} MODELS - Layered Architecture
# =============================================================================

class {ModelName}Base(BaseModel):
    """Base {ModelName} model with only business fields (no id, timestamps)"""
    # Add business fields based on migration
    name: str = Field(..., description="Entity name")
    description: Optional[str] = Field(default=None, description="Entity description")
    # Add other business fields...
    
    class Config:
        from_attributes = True

class {ModelName}({ModelName}Base):
    """Full {ModelName} model with all database fields"""
    id: str = Field(..., description="Unique identifier")
    created_at: datetime = Field(..., description="Record creation timestamp")
    updated_at: datetime = Field(..., description="Record update timestamp")
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }

class {ModelName}Create({ModelName}Base):
    """{ModelName} creation model (inherits from {ModelName}Base)"""
    pass

class {ModelName}Update(BaseModel):
    """{ModelName} update model (only fields that can be updated)"""
    name: Optional[str] = Field(default=None, description="Entity name")
    description: Optional[str] = Field(default=None, description="Entity description")
    # Add other updatable fields...
    
    class Config:
        from_attributes = True
```

### Repository Template
```python
from typing import List, Optional, Dict, Any
from app.core.database import db
from app.modules.{module_name}.models import {ModelName}, {ModelName}Create, {ModelName}Update
import logging

logger = logging.getLogger(__name__)

class {ModelName}Repository:
    """Repository for {ModelName} table operations"""
    
    def __init__(self):
        self.table_name = "{table_name}"
    
    def _supabase_to_model(self, row: Dict[str, Any]) -> {ModelName}:
        """Convert Supabase row to {ModelName} model"""
        return {ModelName}(
            id=str(row["id"]),  # Convert UUID to string
            # Add other field mappings based on your model
            created_at=row["created_at"],
            updated_at=row["updated_at"]
        )
    
    def _modelcreate_to_supabase(self, {model_name.lower()}_data: {ModelName}Create) -> Dict[str, Any]:
        """Convert {ModelName}Create model to Supabase row format"""
        return {
            # Add field mappings based on your model
            "name": {model_name.lower()}_data.name,
            "description": {model_name.lower()}_data.description,
        }
    
    def _update_to_supabase(self, {model_name.lower()}_data: {ModelName}Update) -> Dict[str, Any]:
        """Convert {ModelName}Update model to Supabase row format"""
        return {model_name.lower()}_data.model_dump(exclude_none=True)
    
    async def create(self, {model_name.lower()}_data: {ModelName}Create) -> {ModelName}:
        """Create a new {model_name.lower()}"""
        try:
            data = self._modelcreate_to_supabase({model_name.lower()}_data)
            result = db.client.table(self.table_name).insert(data).execute()
            
            if result.data:
                return self._supabase_to_model(result.data[0])
            else:
                raise Exception(f"Failed to create {model_name.lower()}")
                
        except Exception as e:
            logger.error(f"Error creating {model_name.lower()}: {e}")
            raise
    
    async def get_by_id(self, {model_name.lower()}_id: str) -> Optional[{ModelName}]:
        """Get {model_name.lower()} by ID"""
        try:
            result = (
                db.client.table(self.table_name)
                .select("*")
                .eq("id", {model_name.lower()}_id)
                .execute()
            )
            
            if result.data:
                return self._supabase_to_model(result.data[0])
            return None
            
        except Exception as e:
            logger.error(f"Error getting {model_name.lower()} by ID {{{model_name.lower()}_id}}: {e}")
            raise
    
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[{ModelName}]:
        """Get all {model_name.lower()}s with pagination"""
        try:
            result = (
                db.client.table(self.table_name)
                .select("*")
                .range(offset, offset + limit - 1)
                .execute()
            )
            
            return [self._supabase_to_model(row) for row in result.data]
            
        except Exception as e:
            logger.error(f"Error getting all {model_name.lower()}s: {e}")
            raise
    
    async def update(self, {model_name.lower()}_id: str, {model_name.lower()}_data: {ModelName}Update) -> {ModelName}:
        """Update an existing {model_name.lower()}"""
        try:
            data = self._update_to_supabase({model_name.lower()}_data)
            result = (
                db.client.table(self.table_name)
                .update(data)
                .eq("id", {model_name.lower()}_id)
                .execute()
            )
            
            if result.data:
                return self._supabase_to_model(result.data[0])
            else:
                raise Exception(f"Failed to update {model_name.lower()}")
                
        except Exception as e:
            logger.error(f"Error updating {model_name.lower()} {{{model_name.lower()}_id}}: {e}")
            raise
    
    async def delete(self, {model_name.lower()}_id: str) -> bool:
        """Delete {model_name.lower()} by ID"""
        try:
            result = (
                db.client.table(self.table_name)
                .delete()
                .eq("id", {model_name.lower()}_id)
                .execute()
            )
            
            return len(result.data) > 0
            
        except Exception as e:
            logger.error(f"Error deleting {model_name.lower()} {{{model_name.lower()}_id}}: {e}")
            raise
```

### Service Template
```python
from typing import List, Optional
from app.modules.{module_name}.models import {ModelName}, {ModelName}Create, {ModelName}Update
from app.modules.{module_name}.repository.repository import {ModelName}Repository

class {ModuleName}Service:
    """Service for {ModelName} operations"""
    
    def __init__(self):
        self.{model_name.lower()}_repo = {ModelName}Repository()
    
    async def get_{model_name.lower()}_by_id(self, {model_name.lower()}_id: str) -> Optional[{ModelName}]:
        """Get {model_name.lower()} by ID"""
        return await self.{model_name.lower()}_repo.get_by_id({model_name.lower()}_id)
    
    async def create_{model_name.lower()}(self, {model_name.lower()}_data: {ModelName}Create) -> {ModelName}:
        """Create new {model_name.lower()}"""
        return await self.{model_name.lower()}_repo.create({model_name.lower()}_data)
    
    async def get_all_{model_name.lower()}s(self, limit: int = 100, offset: int = 0) -> List[{ModelName}]:
        """Get all {model_name.lower()}s"""
        return await self.{model_name.lower()}_repo.get_all(limit, offset)
    
    async def update_{model_name.lower()}(self, {model_name.lower()}_id: str, {model_name.lower()}_data: {ModelName}Update) -> {ModelName}:
        """Update {model_name.lower()}"""
        return await self.{model_name.lower()}_repo.update({model_name.lower()}_id, {model_name.lower()}_data)
    
    async def delete_{model_name.lower()}(self, {model_name.lower()}_id: str) -> bool:
        """Delete {model_name.lower()}"""
        return await self.{model_name.lower()}_repo.delete({model_name.lower()}_id)
```

### API Models vs Database Models

**CRITICAL**: Database models and API models serve different purposes and should be kept separate:

**Database Models** (in `app/modules/{module_name}/models/`):
- Represent database table structure
- Use snake_case field names (matches database)
- Include database-specific fields (timestamps, IDs)
- NOT exposed via API

**API Models** (in `app/api/` or module-specific API files):
- Represent API request/response structure
- Use camelCase field names (see FastAPI boilerplate patterns)
- May include computed fields, nested objects, or aggregated data
- Include validation and serialization logic

**Example API Models** (following FastAPI boilerplate patterns):
```python
# app/api/{module_name}.py or app/modules/{module_name}/api_models.py
from pydantic import BaseModel, Field
from typing import List, Optional

class {ModelName}Request(BaseModel):
    """API request model for {ModelName}"""
    email: str = Field(..., description="User email")
    full_name: str = Field(alias="fullName", description="User's full name")
    
    model_config = {"validate_by_name": True}

class {ModelName}Response(BaseModel):
    """API response model for {ModelName}"""
    user_id: str = Field(alias="userId", description="User identifier")
    email: str = Field(..., description="User email")
    full_name: str = Field(alias="fullName", description="User's full name")
    created_at: str = Field(alias="createdAt", description="Creation timestamp")
    
    model_config = {"validate_by_name": True}

class {ModelName}ListResponse(BaseModel):
    """API response model for {ModelName} list"""
    {model_name.lower()}s: List[{ModelName}Response] = Field(alias="{model_name.lower()}s")
    total_count: int = Field(alias="totalCount")
    has_more: bool = Field(alias="hasMore")
    
    model_config = {"validate_by_name": True}
```

**API Endpoint Example**:
```python
# app/api/{module_name}.py
from fastapi import APIRouter, Depends
from app.core.dependencies import require_auth
from app.modules.{module_name}.services.{module_name}_service import {ModuleName}Service
from .api_models import {ModelName}Request, {ModelName}Response, {ModelName}ListResponse

router = APIRouter(prefix="/api/{module_name}", tags=["{module_name}"])

@router.post("/{model_name.lower()}", response_model={ModelName}Response)
async def create_{model_name.lower()}(
    request: {ModelName}Request,
    current_user: dict = Depends(require_auth)
):
    """Create new {model_name.lower()}"""
    # Convert API model to database model
    from app.modules.{module_name}.models import {ModelName}
    
    db_model = {ModelName}(
        email=request.email,
        full_name=request.full_name
    )
    
    service = {ModuleName}Service()
    created_model = await service.create_{model_name.lower()}(db_model)
    
    # Convert database model to API response
    return {ModelName}Response(
        userId=str(created_model.id),
        email=created_model.email,
        fullName=created_model.full_name,
        createdAt=created_model.created_at.isoformat() if created_model.created_at else None
    )
```

## Testing Strategy

### Repository Testing Philosophy

**Why NOT test repositories directly:**
- Repositories are straightforward CRUD operations
- Testing them would essentially test Supabase's client library
- Mapper functions are simple field mappings
- Database integration tests are slow and complex to maintain

**Focus testing on services instead:**
- Services contain the real business logic
- Services handle data transformations between database and API models
- Services orchestrate multiple repository calls
- Services implement error handling and validation

### Service Testing with Mocked Repositories

**Test Structure:**
```python
# tests/modules/{module_name}/test_{module_name}_service.py
import pytest
from unittest.mock import Mock, AsyncMock
from app.modules.{module_name}.models import {ModelName}
from app.modules.{module_name}.services.{module_name}_service import {ModuleName}Service

class Test{ModuleName}Service:
    def setup_method(self):
        """Setup test fixtures"""
        self.mock_repo = Mock()
        self.mock_repo.create = AsyncMock()
        self.mock_repo.get_by_id = AsyncMock()
        self.mock_repo.update = AsyncMock()
        self.mock_repo.delete = AsyncMock()
        
        # Inject mocked repository into service
        self.service = {ModuleName}Service(supabase_client=None)
        self.service.{model_name.lower()}_repo = self.mock_repo
    
    @pytest.mark.asyncio
    async def test_create_{model_name.lower()}_success(self):
        """Test successful {model_name.lower()} creation"""
        # Arrange
        user_data = {ModelName}(
            email="test@example.com",
            full_name="Test User"
        )
        expected_result = {ModelName}(
            id="123",
            email="test@example.com",
            full_name="Test User"
        )
        self.mock_repo.create.return_value = expected_result
        
        # Act
        result = await self.service.create_{model_name.lower()}(user_data)
        
        # Assert
        assert result.id == "123"
        assert result.email == "test@example.com"
        self.mock_repo.create.assert_called_once_with(user_data)
    
    @pytest.mark.asyncio
    async def test_create_{model_name.lower()}_repository_error(self):
        """Test {model_name.lower()} creation with repository error"""
        # Arrange
        user_data = {ModelName}(
            email="test@example.com",
            full_name="Test User"
        )
        self.mock_repo.create.side_effect = Exception("Database error")
        
        # Act & Assert
        with pytest.raises(Exception, match="Database error"):
            await self.service.create_{model_name.lower()}(user_data)
    
    @pytest.mark.asyncio
    async def test_get_{model_name.lower()}_not_found(self):
        """Test getting non-existent {model_name.lower()}"""
        # Arrange
        self.mock_repo.get_by_id.return_value = None
        
        # Act
        result = await self.service.get_{model_name.lower()}_by_id("nonexistent")
        
        # Assert
        assert result is None
        self.mock_repo.get_by_id.assert_called_once_with("nonexistent")
    
    @pytest.mark.asyncio
    async def test_update_{model_name.lower()}_validation(self):
        """Test {model_name.lower()} update with validation logic"""
        # Arrange
        user_data = {ModelName}(
            id="123",
            email="updated@example.com",
            full_name="Updated User"
        )
        self.mock_repo.update.return_value = user_data
        
        # Act
        result = await self.service.update_{model_name.lower()}(user_data)
        
        # Assert
        assert result.email == "updated@example.com"
        self.mock_repo.update.assert_called_once_with(user_data)
    
    @pytest.mark.asyncio
    async def test_delete_{model_name.lower()}_success(self):
        """Test successful {model_name.lower()} deletion"""
        # Arrange
        self.mock_repo.delete.return_value = True
        
        # Act
        result = await self.service.delete_{model_name.lower()}("123")
        
        # Assert
        assert result is True
        self.mock_repo.delete.assert_called_once_with("123")
```

### Integration Testing

**When you DO need database testing:**
```python
# tests/integration/test_database_integration.py
import pytest
from app.core.database import db
from app.modules.{module_name}.models import {ModelName}
from app.modules.{module_name}.services.{module_name}_service import {ModuleName}Service

@pytest.mark.integration
@pytest.mark.asyncio
async def test_user_crud_integration():
    """Integration test for user CRUD operations"""
    if not db.client:
        pytest.skip("Database not available")
    
    service = {ModuleName}Service(db.client)
    
    # Test create
    user = {ModelName}(
        email="integration@example.com",
        full_name="Integration Test User"
    )
    created_user = await service.create_{model_name.lower()}(user)
    assert created_user.id is not None
    assert created_user.email == "integration@example.com"
    
    # Test read
    retrieved_user = await service.get_{model_name.lower()}_by_id(created_user.id)
    assert retrieved_user is not None
    assert retrieved_user.email == "integration@example.com"
    
    # Test update
    retrieved_user.full_name = "Updated Integration User"
    updated_user = await service.update_{model_name.lower()}(retrieved_user)
    assert updated_user.full_name == "Updated Integration User"
    
    # Test delete
    delete_result = await service.delete_{model_name.lower()}(created_user.id)
    assert delete_result is True
    
    # Verify deletion
    deleted_user = await service.get_{model_name.lower()}_by_id(created_user.id)
    assert deleted_user is None
```

### MyPy Configuration for Database Models

**Update pyproject.toml to include models in type checking:**
```toml
[tool.mypy]
python_version = "3.11"
warn_return_any = false
warn_unused_configs = true
disallow_untyped_defs = false
disallow_incomplete_defs = false
check_untyped_defs = true
disallow_untyped_decorators = false
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true

# Type check database models and services
[[tool.mypy.overrides]]
module = [
    "app.modules.*.models.*",      # ✅ Check database models
    "app.modules.*.services.*",    # ✅ Check service layer
    "app.api.*"                    # ✅ Check API endpoints
]
ignore_errors = false

# Skip internal implementation details
[[tool.mypy.overrides]]
module = [
    "app.modules.*.agents.*",      # Skip agent internals
    "app.modules.*.processors.*",  # Skip processor internals
    "app.modules.*.prompts.*"      # Skip prompt internals
]
ignore_errors = true

# External dependencies
[[tool.mypy.overrides]]
module = ["supabase.*", "jose.*"]
ignore_missing_imports = true
```

**Run type checking:**
```bash
# Check database models and services
mypy app/modules/*/models/ app/modules/*/services/ app/api/

# Or use Makefile target
make type-check
```

### Test Organization

**File structure for database testing:**
```
tests/
├── modules/
│   └── {module_name}/
│       ├── test_{module_name}_service.py    # Service unit tests (mocked repos)
│       └── test_{module_name}_models.py     # Model validation tests (optional)
└── integration/
    └── test_database_integration.py         # Full database integration tests
```

**Model validation tests (optional, for complex models):**
```python
# tests/modules/{module_name}/test_{module_name}_models.py
import pytest
from pydantic import ValidationError
from app.modules.{module_name}.models import {ModelName}

class Test{ModelName}Model:
    def test_valid_{model_name.lower()}_creation(self):
        """Test creating valid {model_name.lower()} model"""
        user = {ModelName}(
            email="test@example.com",
            full_name="Test User"
        )
        assert user.email == "test@example.com"
        assert user.full_name == "Test User"
        assert user.id is None  # Default value
    
    def test_invalid_email_format(self):
        """Test model validation with invalid email"""
        with pytest.raises(ValidationError):
            {ModelName}(
                email="invalid-email",
                full_name="Test User"
            )
    
    def test_required_fields(self):
        """Test that required fields are enforced"""
        with pytest.raises(ValidationError):
            {ModelName}()  # Missing required fields
```

## Migration Workflow

### Development Workflow
1. **Create migration** using Supabase CLI:
```bash
cd database/develop
supabase migration new add_users_table
```

2. **Edit migration file** in `database/develop/supabase/migrations/`:
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

3. **Apply migration locally**:
```bash
supabase db reset
```

4. **Test migration** with local development

5. **Push to remote develop**:
```bash
supabase db push
```

### Production Deployment
1. **Copy migration file** to production:
```bash
cp database/develop/supabase/migrations/{timestamp}_add_users_table.sql \
   database/prod/supabase/migrations/
```

2. **Apply to production** (manual process):
```bash
cd database/prod
supabase db push
```

## Validation Checklist

Before completing any database task, verify:

### Architecture Compliance
- [ ] Repository not exported from module
- [ ] Layered model architecture implemented (Base → Full → Create/Update)
- [ ] Business fields separated from database metadata
- [ ] Type-safe mapper functions for each model type
- [ ] Centralized database client used (`db.client`)
- [ ] Service layer exists for external access
- [ ] No direct repository access from outside module
- [ ] API models separate from database models
- [ ] API models use camelCase with proper aliases
- [ ] Operation-specific models used in method signatures

### Code Quality
- [ ] Proper error handling in repository methods
- [ ] Logging for database operations
- [ ] Type hints for all methods
- [ ] Docstrings for all classes and methods
- [ ] Proper validation in Pydantic models

### Testing
- [ ] Service unit tests with mocked repositories
- [ ] Test business logic and error handling scenarios
- [ ] Integration tests for critical database operations
- [ ] MyPy type checking enabled for models and services
- [ ] No unit tests for repositories (they're straightforward CRUD)

### Database Design
- [ ] Migration file follows naming convention
- [ ] Table structure matches migration
- [ ] Proper indexes and constraints
- [ ] Timestamp fields for audit trail

## Common Anti-Patterns to Avoid

### ❌ Don't Do This
```python
# Exporting repository from module
from app.modules.user.repository import UserRepository  # ❌ Direct repository access

# Using single model for all operations
class User(BaseModel):
    id: Optional[str] = None  # ❌ Mixed business and DB fields
    email: str
    created_at: Optional[datetime] = None

# Using database models for API responses
@router.get("/users/{user_id}")
async def bad_get_user(user_id: str):
    user = await user_repo.get_by_id(user_id)
    return user  # ❌ Returning database model directly to API

# Individual Supabase clients in repositories
class UserRepository:
    def __init__(self, supabase_client: Client):  # ❌ Individual client
        self.supabase = supabase_client

# Raw dictionary returns
def bad_get_user():
    return {"id": "123", "name": "John"}  # ❌ Should return model

# JOIN operations in repository
def bad_get_user_with_posts():
    return supabase.table("users").select("*, posts(*)").execute()  # ❌ Complex query in repo

# Missing error handling
def bad_create_user(user_data):
    return supabase.table("users").insert(user_data).execute()  # ❌ No error handling

# Separate mappers file
# app/modules/user/repository/mappers.py  # ❌ Unnecessary complexity
```

### ✅ Do This Instead
```python
# Layered model architecture
class UserBase(BaseModel):
    email: str
    full_name: str

class User(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    email: Optional[str] = None
    full_name: Optional[str] = None

# Access through service
from app.modules.user.services.user_service import UserService  # ✅ Service access

# Centralized database client
from app.core.database import db

class UserRepository:
    def __init__(self):
        self.table_name = "users"  # ✅ Configuration, not client

# Type-safe mappers
def _modelcreate_to_supabase(self, user_data: UserCreate) -> Dict[str, Any]:
    return {
        "email": user_data.email,
        "full_name": user_data.full_name,
    }

def _update_to_supabase(self, user_data: UserUpdate) -> Dict[str, Any]:
    return user_data.model_dump(exclude_none=True)  # ✅ Only non-null fields

# Separate API models for responses
@router.get("/users/{user_id}", response_model=UserResponse)
async def good_get_user(user_id: str):
    user = await user_service.get_user_by_id(user_id)
    return UserResponse(
        userId=str(user.id),
        email=user.email,
        fullName=user.full_name,
        createdAt=user.created_at.isoformat()
    )  # ✅ Convert database model to API response

# Operation-specific method signatures
async def create(self, user_data: UserCreate) -> User:  # ✅ Create model
async def update(self, user_id: str, user_data: UserUpdate) -> User:  # ✅ Update model

# Proper error handling
async def good_create_user(user_data: UserCreate) -> User:
    try:
        return await self.user_repo.create(user_data)
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise
```

## Troubleshooting

### Common Issues

**"Cannot import repository"**
- Repositories should not be imported directly
- Use services instead for external access

**"Model validation errors"**
- Check field types match database schema
- Verify required fields are marked properly
- Ensure UUID fields are handled correctly

**"Migration conflicts"**
- Check migration file naming and timestamps
- Ensure migrations are applied in correct order
- Reset local database if needed

**"Supabase connection errors"**
- Verify environment variables are set
- Check Supabase client initialization
- Ensure proper authentication tokens

### Quick Fixes

**Fix model field types**: Match database column types exactly
**Add missing imports**: Include uuid, datetime, Optional as needed
**Fix mapper functions**: Handle None values and type conversions
**Add error handling**: Wrap database operations in try-catch blocks
**Update service**: Create service if repository exists but no service found

## Environment-Specific Notes

### Development Environment
- Uses local Supabase instance
- Automatic migrations on `supabase db reset`
- Full logging enabled for debugging

### Production Environment
- Uses remote Supabase instance
- Manual migration deployment process
- Minimal logging for performance
- Backup procedures before schema changes
