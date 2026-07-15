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
- [ ] Test file created: internal/handler/[feature]_test.go
- [ ] Test written using skeleton mock data structure
- [ ] `gin.SetMode(gin.TestMode)` set in `TestMain`
- [ ] Test uses `httptest.NewRequest` / `httptest.NewRecorder`
- [ ] Test includes success case
- [ ] Test includes error cases
- [ ] Test includes validation check
- [ ] Test run and confirmed FAILING
- [ ] Test failure makes sense (no implementation yet)

## Step 2: Database Migration/Setup (5-10 min)
- [ ] Migration created — golang-migrate `.up.sql`/`.down.sql` pair OR GORM `AutoMigrate` call added
- [ ] Schema matches the GORM model's struct tags
- [ ] Primary key defined (`gorm:"type:uuid;primaryKey;default:gen_random_uuid()"`)
- [ ] Foreign keys added (if applicable)
- [ ] Timestamps added (`created_at`, `updated_at`)
- [ ] Indexes added for common query columns
- [ ] `NOT NULL` constraints where appropriate
- [ ] Migration applied locally
- [ ] Schema verified in database (`psql` or pgAdmin)

## Step 3: GORM Model + API DTOs (5-10 min)
- [ ] GORM model struct created (DB layer, `gorm:"..."` tags, `json:"-"` to keep it out of API responses)
- [ ] Request DTO struct created (`json:"..."` + `binding:"..."` tags)
- [ ] Response DTO struct created (`json:"..."` tags, camelCase JSON keys)
- [ ] `ToXResponse()` converter function implemented
- [ ] Doc comments on all exported structs and fields where non-obvious
- [ ] No inheritance-chain mimicry — flat, separate structs per operation (Go idiom, not Pydantic)

## Step 4: Repository (10-15 min)
- [ ] Repository struct created (e.g. `GormPostRepository`)
- [ ] Interface declared at point of use (in the `service` package, not the `repository` package)
- [ ] `*gorm.DB` injected via constructor (`NewGormPostRepository(db *gorm.DB)`)
- [ ] `Create()` method implemented (if needed)
- [ ] `GetByID()` method implemented (if needed)
- [ ] `List()` method implemented (if needed)
- [ ] `Update()` method implemented (if needed)
- [ ] `Delete()` method implemented (if needed)
- [ ] `context.Context` propagated via `db.WithContext(ctx)`
- [ ] Errors wrapped with `fmt.Errorf("...: %w", err)`
- [ ] Doc comments on all exported methods

## Step 5: Service Layer (5-10 min)
- [ ] Service struct created (e.g. `PostService`)
- [ ] Repository interface field, injected via constructor
- [ ] Business logic method implemented
- [ ] Input validation implemented (beyond Gin binding tags)
- [ ] Errors wrapped with context
- [ ] Doc comments on all exported methods and the type itself

## Step 6: Handler (5-10 min)
- [ ] Mock implementation removed
- [ ] Handler converted to dependency-injecting factory: `func Handler(svc *service.X) gin.HandlerFunc`
- [ ] Router registration updated to pass the service in
- [ ] Request DTO bound via `c.ShouldBindJSON(&req)`
- [ ] `c.Request.Context()` passed through to the service call
- [ ] Service errors mapped to HTTP status codes (`errors.Is` / `errors.As`)
- [ ] Response DTO returned via `c.JSON(status, model.ToXResponse(result))`
- [ ] HTTP status codes correct (`201` create, `200` read, `204` delete)
- [ ] Doc comment added to the handler factory function

## Step 7: Test Validation (5 min)
- [ ] E2E test run again
- [ ] E2E test now PASSING
- [ ] Test validates actual database interaction (not mock data)
- [ ] Test validates proper timestamps
- [ ] Test validates proper ID generation
- [ ] All test scenarios passing

## Step 8: Code Quality (5 min)
- [ ] Formatting checked: `gofmt -l .` (empty output)
- [ ] Imports fixed: `goimports -w .`
- [ ] Vet passed: `go vet ./...`
- [ ] Lint passed: `golangci-lint run`
- [ ] All tests passing: `go test ./... -v`
- [ ] No linting errors
- [ ] No vet errors
- [ ] Code reviewed for best practices (see rules/300-go-style.mdc)

## Step 9: Phase Transition (5-10 min)
- [ ] Phase summary generated: `plan/sessions/session-N-summary.md`
- [ ] Implementation details documented
- [ ] Shared libraries documented
- [ ] Known limitations noted
- [ ] Next phase recommendations provided
- [ ] Files changed list complete
- [ ] Time actual vs estimate noted

## Final Checklist
- [ ] All E2E tests passing
- [ ] All unit tests passing (if applicable)
- [ ] Code formatted and vetted
- [ ] No hardcoded values
- [ ] Secrets properly managed (via `.env` / viper, never committed)
- [ ] Error handling comprehensive
- [ ] Logging appropriate (structured, no secrets)
- [ ] Documentation complete
- [ ] Ready for next phase

## Time Tracking
- Estimated Time: [X] minutes
- Actual Time: [Y] minutes
- Variance: [+/-Z] minutes
- Notes on variance: [Why it took longer/shorter]

## Notes and Learnings
[Document any issues encountered, solutions found, or learnings for future phases]
