---
description: Generate a comprehensive research export document for external review
---

# Research Export Command

Generate a structured Markdown document to explain a complex problem to an external expert or colleague.

## Execution Flow

**1. Gather Context**
- Read `CLAUDE.md`
- Read the current error logs or problem description provided by the user.

**2. Generate Document**
Create a file `research-exports/research-[topic]-[date].md` with this structure:

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
[Insert snippet or file reference]

## 4. Specific Questions
- [Question 1]
- [Question 2]
```

## Usage
`/research-export "Database connection timeout"`
-> *Creates research-exports/research-db-timeout-20240101.md*
