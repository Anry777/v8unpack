# OpenCode Context

This folder contains project intelligence for AI agents to understand your codebase patterns.

## Purpose

AI agents (like OpenAgent) load these files to generate code that matches **your** project's:
- Tech stack and architecture
- Code patterns and conventions
- Business context and requirements
- Current TODOs and known issues

## Structure

```
.opencode/
├── context/
│   ├── project-intelligence/
│   │   ├── technical-domain.md    # Tech stack, architecture, patterns
│   │   ├── business-domain.md     # Business context, users, value
│   │   ├── business-tech-bridge.md # How business maps to technical
│   │   ├── decisions-log.md      # Major decisions with rationale
│   │   ├── living-notes.md       # Current TODOs, issues, insights
│   │   └── navigation.md        # Quick overview
```

## Usage

AI agents automatically load these files when working on this project.

## Updating

Run `/add-context` wizard to update files when:
- Tech stack changes
- New patterns emerge
- Architecture decisions made
- TODOs completed

## Version Control

These files are committed to git and shared across your team.

## Global vs Project Context

- **Global**: `~/.opencode/context/project-intelligence/` (shared across all projects)
- **Project-local**: `.opencode/context/project-intelligence/` (this project, git-tracked)

AI agents check project-local first, then fall back to global.
