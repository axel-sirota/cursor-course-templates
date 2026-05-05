# Phase N Checklist: [HTTP Method] [Endpoint Path]

## Phase Information
- Phase Number: N
- Endpoint: [Method] [Path]
- Goal: [One sentence description]
- Dependencies: [List previous phases]
- Estimated Time: [X] minutes
- Start Time: [YYYY-MM-DD HH:MM]

## Pre-Phase Setup
- [ ] Previous phase summary reviewed
- [ ] Shared libraries identified
- [ ] Dependencies understood
- [ ] Phase requirements clear

## Step 1: E2E Test (5-10 min)
- [ ] Test file created: tests/api/test_[feature].py
- [ ] Test written using skeleton mock data structure
- [ ] Test includes success case
- [ ] Test includes error cases
- [ ] Test includes authentication check
- [ ] Test run and confirmed FAILING
- [ ] Test failure makes sense (no implementation yet)

## Step 2: Database Migration/Setup (Alembic) (5-10 min)
- [ ] Migration file created with timestamp
- [ ] Schema matches domain model requirements
- [ ] Primary key defined (UUID with default)
- [ ] Foreign keys added (if applicable)
- [ ] Timestamps added (created_at, updated_at)
- [ ] Indexes added for common queries
- [ ] NOT NULL constraints where appropriate
- [ ] Migration applied locally
- [ ] Schema verified in database

## Step 3: Domain Models (5-10 min)
- [ ] Base model created (business fields only)
- [ ] Full model created (includes ID and timestamps)
- [ ] Create model created (for creation operations)
- [ ] Update model created (for update operations)
- [ ] Type hints on all fields
- [ ] Field descriptions added
- [ ] Config settings proper (from_attributes = True)
- [ ] Models exported from __init__.py

## Step 4: Repository (10-15 min)
- [ ] Repository class created
- [ ] SQLAlchemy model(s) identified
- [ ] Session injected (dependency or constructor)
- [ ] row_to_model() mapper implemented (if needed)
- [ ] create_input_to_orm() mapper implemented (if needed)
- [ ] update_input_to_orm() mapper implemented (if needed)
- [ ] create() method implemented (if needed)
- [ ] get_by_id() method implemented (if needed)
- [ ] get_all() method implemented (if needed)
- [ ] update() method implemented (if needed)
- [ ] delete() method implemented (if needed)
- [ ] Error handling added
- [ ] Transactions and rollbacks handled
- [ ] Logging added
- [ ] Type hints on all methods
- [ ] Docstrings on all methods

## Step 5: Service Layer (5-10 min)
- [ ] Service class created
- [ ] Repository initialized
- [ ] Business logic method implemented
- [ ] Error handling added
- [ ] Logging added
- [ ] Type hints on all methods
- [ ] Docstrings on all methods
- [ ] Input validation implemented

## Step 6: API Endpoint (5-10 min)
- [ ] Mock implementation removed
- [ ] Service imported
- [ ] API request model converted to domain model
- [ ] Service method called with error handling
- [ ] Domain model converted to API response
- [ ] HTTP status codes correct
- [ ] Error responses properly formatted
- [ ] Authentication dependency added
- [ ] Type hints on all parameters
- [ ] Docstring added to endpoint

## Step 7: Test Validation (5 min)
- [ ] E2E test run
- [ ] E2E test now PASSING
- [ ] Test validates actual database interaction
- [ ] Test validates proper timestamps
- [ ] Test validates proper ID generation
- [ ] All test scenarios passing

## Step 8: Code Quality (5 min)
- [ ] Linting passed: ruff check app/ tests/
- [ ] Code formatted with Black: black app/ tests/
- [ ] Type checking passed: mypy app/
- [ ] All tests passing: pytest tests/
- [ ] No linting errors
- [ ] No type checking errors
- [ ] Code reviewed for best practices

## Step 9: Phase Transition (5-10 min)
- [ ] Phase summary generated: phases/phase-N-summary.md
- [ ] Implementation details documented
- [ ] Shared libraries documented
- [ ] Known limitations noted
- [ ] Next phase recommendations provided
- [ ] Files changed list complete
- [ ] Time actual vs estimate noted

## Final Checklist
- [ ] All E2E tests passing
- [ ] All unit tests passing (if applicable)
- [ ] Code formatted and type-checked
- [ ] No hardcoded values
- [ ] Secrets properly managed
- [ ] Error handling comprehensive
- [ ] Logging appropriate
- [ ] Documentation complete
- [ ] Ready for next phase

## Time Tracking
- Estimated Time: [X] minutes
- Actual Time: [Y] minutes
- Variance: [+/-Z] minutes
- Notes on variance: [Why it took longer/shorter]

## Notes and Learnings
[Document any issues encountered, solutions found, or learnings for future phases]