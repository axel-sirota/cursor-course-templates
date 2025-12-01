---
description: Integration guide for Claude Desktop and MCP
---

# Claude Desktop Integration

This command configures or guides the integration between Cursor and Claude Desktop using MCP (Model Context Protocol).

## Setup Checks

**1. MCP Config**
- Check for `claude_desktop_config.json` (typical location depends on OS).
- Verify if Cursor is acting as an MCP Client or Server (usually Client).

## Workflow Integration
- **Handoff**: How to pass a complex reasoning task from Cursor to Claude Desktop.
- **Context Sharing**: Ensure both tools see the same `context.md`.

## Best Practices
- Use Claude Desktop for **High-Level Reasoning** and **Architecture Review**.
- Use Cursor for **Implementation** and **File Editing**.

## Usage
`@claude-desktop` -> *Displays setup status and integration tips.*

