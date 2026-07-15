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
- [ ] Test file created: tests/routes/[feature].test.ts
- [ ] Test written using skeleton mock data structure
- [ ] Test includes success case
- [ ] Test includes error cases
- [ ] Test includes authentication check
- [ ] Test run and confirmed FAILING
- [ ] Test failure makes sense (no implementation yet)

## Step 2: Database Migration/Setup (Prisma) (5-10 min)
- [ ] Model added/updated in prisma/schema.prisma
- [ ] Migration created: `npx prisma migrate dev --name [description]`
- [ ] Schema matches domain schema requirements
- [ ] Primary key defined (`@id @default(uuid())`)
- [ ] Foreign keys added (if applicable)
- [ ] Timestamps added (createdAt, updatedAt)
- [ ] Indexes added for common queries (`@@index`)
- [ ] Required fields have no `?` where they shouldn't
- [ ] Migration applied locally
- [ ] Schema verified (`npx prisma studio` or `npx prisma migrate status`)

## Step 3: Domain Schemas (Zod) (5-10 min)
- [ ] Base schema created (business fields only)
- [ ] Full schema created (includes ID and timestamps)
- [ ] Create schema created (for creation operations)
- [ ] Update schema created (`.partial()` for update operations)
- [ ] TS types exported via `z.infer<>`
- [ ] Field constraints added (`.min()`, `.max()`, `.email()`, etc.)
- [ ] Schemas exported from a barrel file if applicable

## Step 4: Repository (10-15 min)
- [ ] Repository class created
- [ ] PrismaClient injected via constructor
- [ ] toModel() mapper implemented (Prisma row → domain schema)
- [ ] create() method implemented (if needed)
- [ ] getById() method implemented (if needed)
- [ ] getAll() method implemented (if needed)
- [ ] update() method implemented (if needed)
- [ ] delete() method implemented (if needed)
- [ ] Error handling added
- [ ] Transactions handled where multiple writes are involved
- [ ] Logging added
- [ ] Explicit return types on all methods
- [ ] TSDoc comments on all methods

## Step 5: Service Layer (5-10 min)
- [ ] Service class created
- [ ] Repository injected via constructor
- [ ] Business logic method implemented
- [ ] Error handling added (custom error classes)
- [ ] Logging added
- [ ] Explicit return types on all methods
- [ ] TSDoc comments on all methods
- [ ] Input validation implemented (beyond Zod, if business-rule-specific)

## Step 6: API Endpoint (5-10 min)
- [ ] Mock implementation removed
- [ ] Service imported and instantiated (or injected)
- [ ] Request body parsed with Zod `.parse()`
- [ ] Service method called with error handling
- [ ] Domain schema converted to API response
- [ ] HTTP status codes correct
- [ ] Error responses properly formatted
- [ ] Auth middleware added to route
- [ ] Explicit return types on controller functions
- [ ] TSDoc comment added to controller

## Step 7: Test Validation (5 min)
- [ ] E2E test run
- [ ] E2E test now PASSING
- [ ] Test validates actual database interaction
- [ ] Test validates proper timestamps
- [ ] Test validates proper ID generation
- [ ] All test scenarios passing

## Step 8: Code Quality (5 min)
- [ ] Linting passed: `npx eslint src/ tests/ --fix`
- [ ] Code formatted with Prettier: `npx prettier --write src/ tests/`
- [ ] Type checking passed: `npx tsc --noEmit`
- [ ] All tests passing: `npx jest`
- [ ] No linting errors
- [ ] No type checking errors
- [ ] Code reviewed for best practices

## Step 9: Phase Transition (5-10 min)
- [ ] Phase summary generated: plan/sessions/session-N-summary.md
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
