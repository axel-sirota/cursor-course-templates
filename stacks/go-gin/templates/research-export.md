# Research Export: [Problem Title]

## Export Information
- Date: [YYYY-MM-DD]
- Phase: Phase N - [Endpoint]
- Severity: [Low/Medium/High/Blocking]
- Exported By: [Your Name]

## Problem Statement

### Brief Description
[One paragraph describing the problem in plain language]

### Impact
- What is blocked: [Feature/Endpoint/Functionality]
- Workaround available: [Yes/No - describe if yes]
- Production impact: [Yes/No - describe if yes]

## Context

### Current Phase
- Phase Number: N
- Endpoint Being Implemented: [Method] [Path]
- Step Where Problem Occurred: [E2E Test/Migration/Implementation/etc.]

### Related Phases
- Dependencies on previous phases: [List]
- Impact on future phases: [List]

### System State
- Environment: [Local/Development/Production]
- Database: [PostgreSQL version, status]
- Go version: [1.23.x] (`go version`)
- Gin version: [x.x.x] (`go list -m github.com/gin-gonic/gin`)
- GORM version: [x.x.x]
- Other relevant module versions: [`go list -m all` excerpt]

## What We Tried

### Attempt 1
**Approach:**
[Describe what was tried]

**Result:**
[What happened]

**Why it didn't work:**
[Analysis of why this approach failed]

**Code snippets:**
```go
// Include relevant code that was tried
```

### Attempt 2
**Approach:**
[Describe what was tried]

**Result:**
[What happened]

**Why it didn't work:**
[Analysis of why this approach failed]

**Code snippets:**
```go
// Include relevant code that was tried
```

### Attempt 3
**Approach:**
[Describe what was tried]

**Result:**
[What happened]

**Why it didn't work:**
[Analysis of why this approach failed]

**Code snippets:**
```go
// Include relevant code that was tried
```

## Error Messages

### Primary Error
```
[Full error message including stack trace / panic trace]
```

### Secondary Errors
```
[Any related errors, go vet warnings, or golangci-lint findings]
```

### Log Output
```
[Relevant log entries showing the problem]
```

## Current Code

### Problematic Code
**File:** [path/to/file.go]
**Lines:** [XX-YY]

```go
// Include the problematic code section
```

### Related Code
**File:** [path/to/related/file.go]
**Lines:** [XX-YY]

```go
// Include related code that might be relevant
```

### Configuration
**.env settings:**
```
[Relevant environment variables]
```

**docker-compose.yml:**
```yaml
# Relevant Docker configuration
```

## Research Questions

### Primary Questions
1. [Main question about the problem]
2. [Secondary question]
3. [Follow-up question]

### Technical Questions
1. [Specific technical detail to research — e.g. GORM behavior, Gin binding edge case]
2. [Library/API behavior question]
3. [Best practice question]

### Architecture Questions
1. [Design pattern question]
2. [Structure question]
3. [Alternative approach question]

## Hypotheses

### Hypothesis 1
**Theory:**
[What might be causing the problem]

**Evidence:**
- [Supporting evidence]
- [Related observations]

**Test:**
[How to test this hypothesis]

### Hypothesis 2
**Theory:**
[Alternative explanation]

**Evidence:**
- [Supporting evidence]
- [Related observations]

**Test:**
[How to test this hypothesis]

## Documentation References

### Official Documentation Consulted
- [Go docs link] - [What was checked]
- [Gin docs link] - [What was checked]
- [GORM docs link] - [What was checked]
- [golangci-lint docs link] - [What was checked]

### Stack Overflow / Forum Posts
- [Link] - [Summary of what was found]
- [Link] - [Summary of what was found]

### Blog Posts / Tutorials
- [Link] - [Summary of content]
- [Link] - [Summary of content]

## Environment Details

### Database Schema
```sql
-- Relevant table definitions
CREATE TABLE example (
    ...
);
```

### Database State
```sql
-- Relevant data samples
SELECT * FROM example WHERE ...;
```

### Go Module State
```bash
go list -m all
# Or relevant portions
```

## Constraints and Requirements

### Must Have
- [Requirement that cannot be compromised]
- [Requirement that cannot be compromised]

### Nice to Have
- [Preference but can be adjusted]
- [Preference but can be adjusted]

### Cannot Do
- [Approaches that are not options]
- [Approaches that are not options]

## Success Criteria

### How We'll Know It's Fixed
- [ ] [Specific test passes]
- [ ] [Specific behavior works]
- [ ] [Specific metric achieved]

### Acceptance Tests
```go
func TestSolution(t *testing.T) {
    // This test should pass when the problem is solved
}
```

## Additional Context

### Similar Issues Encountered
- Phase X: [Similar problem and how it was solved]
- Phase Y: [Related issue]

### Working Code References
**File:** [path/to/working/example.go]
```go
// Working code that might provide hints
```

### Related Phase Summaries
- Phase N-1 Summary: [Key points that might be relevant]
- Phase N-2 Summary: [Key points that might be relevant]

## Next Steps After Research

### Information Needed
- [ ] [Specific information to gather]
- [ ] [Documentation to review]
- [ ] [Expertise to consult]

### Potential Solutions to Test
1. [Solution idea from research]
2. [Alternative solution]
3. [Fallback solution]

### Timeline
- Time spent so far: [X] hours
- Maximum time to allocate: [Y] hours
- Decision point: [When to escalate or pivot]

## Notes for Future Reference

### Lessons Learned
[Document insights even if the problem is not yet solved]

### Documentation Gaps
[Note where official docs were unclear or missing]

### Process Improvements
[Note how this could have been prevented or caught earlier]

---

## Research Results (To Be Filled After External Research)

### Solution Found
[Describe the solution]

### Why It Works
[Explain the underlying issue and why this solution addresses it]

### Implementation Plan
1. [Step to implement solution]
2. [Step to verify solution]
3. [Step to prevent recurrence]

### Code Changes Required
```go
// New code to implement
```

### Testing Strategy
```go
// Tests to verify solution
```

### Documentation Updates Needed
- [What needs to be documented]
- [Where to document it]
