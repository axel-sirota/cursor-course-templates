# Research Export Command

Generate a comprehensive research export document when encountering issues requiring external research.

## Prerequisites

Before generating research export, read:
- @templates/research-export.md - Research export template
- @vibe/vibe_phase_workflow.md - Development context
- @plan/sessions/session-N-phase-M.md - Current session context
- Relevant implementation files for context

## Research Export Process

### 1. Document the Problem
- Clear description of the issue
- Context from current session
- What has been attempted
- Why external research is needed

### 2. Use Research Export Template

Follow @templates/research-export.md structure:

```markdown
# Research Export: [Issue Title]

## Problem Statement
- Detailed description of the problem
- Current session context
- Impact on development progress

## Attempted Solutions
- List all solutions tried
- Code snippets and configurations
- Error messages and logs
- Results of each attempt

## Context Files
- Reference relevant files with @ syntax
- Explain relevance of each file
- Include current implementation state

## Specific Questions
- Formulate clear, specific questions
- Include technical requirements
- Specify desired outcomes

## Research Areas
- Technical feasibility
- Best practices
- Integration considerations
- Performance implications
- Security considerations

## Expected Deliverables
- Research findings
- Recommendations
- Implementation guidance
- Alternative approaches
```

### 3. Include Relevant Context

Always include @ references to:
- @plan/sessions/session-N-phase-M.md - Current session plan
- @vibe/vibe_phase_workflow.md - Development patterns
- @.cursor/rules/ - Relevant development rules
- Current implementation files
- Error logs and configurations

### 4. Export Location

Save research export to:
- `research-exports/research-{issue}-{date}.md`
- Use descriptive filename
- Include timestamp for tracking

## Research Focus Areas

Structure research around:
- **Technical Feasibility**: Can it be implemented?
- **Best Practices**: How should it be done?
- **Integration**: How does it fit with existing code?
- **Performance**: What are the implications?
- **Security**: Are there security considerations?
- **Alternatives**: What other approaches exist?

## Integration with Development

- Use research findings to update session plan
- Document decisions in session summary
- Update templates if patterns emerge
- Share learnings in transition prompts
