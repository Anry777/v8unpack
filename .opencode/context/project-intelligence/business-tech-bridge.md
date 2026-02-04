<!-- Context: project-intelligence/bridge | Priority: high | Version: 1.1 | Updated: 2026-02-04 -->

# Business ↔ Tech Bridge

> Document how 1C development needs translate to Python technical solutions.

## Quick Reference

- **Purpose**: Show how v8unpack technical features serve 1C development goals
- **Update When**: New features, refactoring, platform changes
- **Audience**: 1C developers, Python developers, DevOps teams

## Core Mapping

| Business Need | Technical Solution | Why This Mapping | Business Value |
|---------------|-------------------|------------------|----------------|
| Version control sources | 4-stage pipeline (Extract→Convert→Organize→Build) | Binary→text enables git diff, PR review | Track changes, collaborate effectively |
| Code reuse across projects | Include regions (#Область include_core_X) | Code extraction to shared files | Edit once, update everywhere |
| Git submodules support | index.json mapping to external folders | Separate shared code repositories | Single source of truth, easy updates |
| Build for 8.1/8.2/8.3 | --version/--descent parameters | Auto-comment 8.3 directives for older | One source, multiple platforms |
| Human-readable structure | Metadata type enums, snake_case naming | Clear file organization | Easy navigation, less mistakes |
| Separate code files | organizer_code.py splits modules | Code in dedicated files | Cleaner code, easier maintenance |
| Automated CI/CD | CLI API (extract/build functions) | Python programmatic interface | Pipeline integration, auto-deploys |

## Feature Mapping Examples

### Feature: 4-Stage Pipeline

**Business Context**:
- User need: 1C binary files (cf/cfe/epf) cannot be version controlled
- Business goal: Enable modern development practices (git, CI/CD)
- Priority: Critical (core problem v8unpack solves)

**Technical Implementation**:
- Solution: decoder.py implements 4-stage pipeline
  - Stage 1: v8unpack extraction → raw files
  - Stage 2: Raw → JSON/XML conversion
  - Stage 3: Metadata decoding + type separation
  - Stage 4: Code organization (split files, submodules)
- Architecture: Monolith CLI with modular handlers
- Trade-offs: 4 stages complex but necessary for version-specific transforms

**Connection**:
Without this pipeline, 1C binaries are black boxes. The pipeline enables git diff, code review, and automated builds. Each stage addresses a specific technical challenge (binary format, version differences, code organization). Business value: 1C teams can now use modern development practices.

### Feature: Include Regions for Code Splitting

**Business Context**:
- User need: Share code across multiple forms/objects without duplication
- Business goal: Reduce code duplication, maintain single source of truth
- Priority: High (major time saver for large projects)

**Technical Implementation**:
- Solution: #Область include_path_to_file regions in BSL code
- Architecture: organizer_code.py detects include regions during extraction
- Trade-offs: Code split increases file count but reduces duplication

**Connection**:
Include regions let 1C developers write reusable code. When extracting, v8unpack splits code into separate files. When building, it reassembles them. This enables sharing common functions across forms, submodules, and projects. Business value: Edit shared code once, automatically update all usages.

### Feature: Version-Specific Builds

**Business Context**:
- User need: Maintain 1C extensions for 8.1/8.2/8.3 from single source
- Business goal: Reduce maintenance overhead, ensure consistency
- Priority: High (SABY internal requirement)

**Technical Implementation**:
- Solution: --version/--descent CLI parameters
- Architecture: decoder.py adds version suffixes (--descent) and selects files (--version)
- Trade-offs: More complex source structure but eliminates version-specific branches

**Connection**:
Version-specific builds let teams maintain one source for multiple 1C platforms. During extraction, files get version suffixes (e.g., form.803.json). During build, v8unpack selects appropriate files for target version. Business value: 90% reduction in code duplication across platforms.

### Feature: Direct 1C Export (--format 1c)

**Business Context**:
- User need: Direct export to 1C XML format (skip JSON intermediate)
- Business goal: Faster extraction, direct comparison with 1C Designer
- Priority: Medium (in development)

**Technical Implementation**:
- Solution: direct_1c/ package with decoder.py, catalogs.py, forms.py
- Architecture: Separate extraction path bypassing JSON stage
- Trade-offs: New code path, requires logform generation

**Connection**:
Direct export eliminates JSON intermediate, matching 1C Designer output. Currently supports Catalogs with attributes, commands, forms. TODO: Form.xml (logform), Module.bsl extraction, Predefined.xml. Business value: Faster workflow, direct 1C compatibility.

## Trade-off Decisions

When business and technical needs conflict, document trade-off:

| Situation | Business Priority | Technical Priority | Decision Made | Rationale |
|-----------|-------------------|-------------------|---------------|-----------|
| Code split vs file count | Reuse > simplicity | Modularity > flat structure | Split code into files | Reuse saves more time than file management costs |
| JSON vs direct XML | Speed > compatibility | Standards > custom | Both formats supported | JSON for control, 1c for comparison |
| 8.3 directive auto-comment | Compatibility > manual | Automation > manual | Auto-comment on extract | Prevents syntax errors, saves time |
| Submodules vs monorepo | Flexibility > simplicity | Git native > custom | index.json mapping | Leverages git, enables true code sharing |

## Common Misalignments

| Misalignment | Warning Signs | Resolution Approach |
|--------------|---------------|---------------------|
| Include region conflicts | Duplicate code trying to write same file | Use includr (read-only) for secondary includes |
| Version suffix explosion | Too many {filename}.{version}.* files | Use index.json for shared code, minimal version-specific files |
| Form module extraction missing | Ext/Form/Module.bsl not generated | Check form type (0/1), decode_includes() depth |
| Index.json path errors | Files not copying to submodule | Use forward slashes (Linux compatibility), verify paths |

## Stakeholder Communication

This file helps translate between worlds:

**For 1C Developers**:
- Shows that technical 4-stage pipeline enables version control
- Explains how include regions solve code duplication
- Demonstrates ROI of version-specific builds

**For Python/DevOps Engineers**:
- Provides 1C context for why we need version-specific transforms
- Shows business value of direct 1C export (--format 1c)
- Helps prioritize technical debt (Form.xml generation) with business impact

## Onboarding Checklist

- [ ] Understand how 4-stage pipeline solves version control problem
- [ ] See how include regions map to code splitting
- [ ] Know why version-specific builds reduce duplication
- [ ] Be able to explain trade-offs to stakeholders
- [ ] Understand direct 1C export goals and current limitations

## Related Files

- `business-domain.md` - 1C version control problem
- `technical-domain.md` - Python implementation details
- `decisions-log.md` - Architecture decisions
- `living-notes.md` - Direct 1C export TODOs
