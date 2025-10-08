# Claude Desktop Research Prompt Generator

Create a comprehensive research prompt for Claude Desktop to perform deep research on the specified topic.

## Process

1. **Create Research Prompt File**
   - Create file in `prompts/` directory with descriptive name
   - Use format: `prompts/research-{topic}-{date}.md`

2. **Include Essential Context Files**
   - @vibe/vibe_phase_workflow.md - Development workflow patterns
   - @vibe/vibe_fastapi_boilerplate.md - Project structure and patterns
   - @vibe/vibe_database.md - Database patterns and models
   - @vibe/vibe_development_lifecycle.md - Git workflow and deployment
   - @templates/openapi-template.yaml - API design patterns
   - @templates/docker-compose-template.yaml - Infrastructure setup
   - @.cursor/rules/ - All development rules and patterns

3. **Research Prompt Structure**
   ```markdown
   # Deep Research: {Topic}
   
   ## Problem Statement
   - Clear description of the problem
   - Why deep research is needed
   - Context and constraints
   
   ## Research Objectives
   - Specific questions to answer
   - Technical requirements
   - Success criteria
   
   ## Context Files
   - List all relevant files with @ references
   - Explain relevance of each file
   
   ## Tools and Versions
   - All tools used in the project
   - Version specifications
   - Environment requirements
   
   ## Architecture Context
   - Core system architecture
   - Deployment strategy
   - Integration points
   
   ## Expected Deliverables
   - Research findings
   - Recommendations
   - Implementation guidance
   ```

4. **Research Focus Areas**
   - Technical feasibility
   - Best practices and patterns
   - Integration considerations
   - Performance implications
   - Security considerations
   - Deployment requirements

## Template Usage

Use @templates/research-export.md as the foundation for structuring research findings and export format.
