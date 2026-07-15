---
description: Generate a comprehensive research export document for external review
---

# Research Export Command

Generate a structured Markdown document to explain a complex problem to an external expert or colleague.

## Execution Flow

**1. Gather Context**
- Read `CLAUDE.md`
- Read the current problem evidence provided by the user — this may be error logs, a failing test, a Terraform plan/apply diff, a design/spec mismatch, a CLI output, or a written description, depending on the active stack shape.

**2. Generate Document**
Create a file `research-exports/research-[topic]-[date].md` (use YYYY-MM-DD) with this structure:

```markdown
# Research Export: [Topic]

## 1. Problem Statement
- **Goal**: What are we trying to do?
- **Blocker**: What is stopping us?
- **Stack**: [Insert active stack from context]

## 2. Attempted Solutions
- Approach A: [Result]
- Approach B: [Result]

## 3. Relevant Code
[Insert snippet, file reference, config diff, or infra plan output — whichever artifact is relevant to the active stack]

## 4. Specific Questions
- [Question 1]
- [Question 2]
```

## Usage
`/research-export "Database connection timeout"`
-> *Creates research-exports/research-db-timeout-YYYYMMDD.md*
