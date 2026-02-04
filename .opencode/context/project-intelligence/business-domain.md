<!-- Context: project-intelligence/business | Priority: critical | Version: 1.1 | Updated: 2026-02-04 -->

# Business Domain

**Purpose**: Enable 1C developers to use modern version control and development practices.
**Last Updated**: 2026-02-04

## Quick Reference
**Update When**: New 1C features | Platform changes | User feedback
**Audience**: 1C developers, DevOps teams, technical managers

## Project Identity
```
Project Name: saby v8unpack
Tagline: Unpack 1C binary files to version-friendly source code
Problem Statement: 1C binary files (cf, cfe, epf) cannot be version controlled at source level
Solution: CLI utility converting binaries to human-readable JSON/XML with metadata structure
```

## Target Users

| User Segment | Who They Are | What They Need | Pain Points |
|--------------|--------------|----------------|-------------|
| Primary | 1C developers | Version control, code reuse, team collaboration | Flat unreadable files, hidden form code, manual merging |
| Secondary | DevOps/CI/CD | Automated builds, version-specific binaries | Manual compilation, no pipeline integration |
| Tertiary | Integration teams | Single source for multiple 1C platforms | Duplicate code across 8.1/8.2/8.3 |

## Value Proposition

**For Users**:
- Human-readable source code with metadata structure (not flat files)
- Program code in separate files, splittable via regions
- Git submodules for shared code across projects
- Version-specific builds from single source (8.1, 8.2, 8.3)
- Automatic 8.3 directive commenting for older platforms

**For Business**:
- Reduce code duplication across platforms
- Enable modern development practices (CI/CD, code review)
- Single source for multiple 1C products
- Faster iteration with automated builds

## Success Metrics

| Metric | Definition | Target | Current |
|--------|------------|--------|---------|
| Projects using v8unpack | Active repos | 100+ | Growing |
| Time saved per merge | Manual vs automated | 90% | High |
| Platform coverage | 1C versions supported | 8.1/8.2/8.3 | Complete |

## Business Model
```
Revenue Model: Open source (MIT license)
Pricing Strategy: Free (community maintained)
Unit Economics: SBI (SABY) internal tool, external contributions welcome
Market Position: Unique 1C source code management tool
```

## Key Stakeholders

| Role | Name | Responsibility | Contact |
|------|------|----------------|---------|
| Maintainer | SABY Integration | Core development, releases | GitHub issues |
| Contributors | Community | PRs, bug reports, features | GitHub repo |

## Roadmap Context
**Current Focus**: Direct 1C export (--format 1c) without JSON intermediate
**Next Milestone**: Complete Form.xml generation and Module.bsl extraction
**Long-term Vision**: Universal 1C source management with full diff capabilities

## Business Constraints
- Binary format changes require updates (1C platform evolution)
- Must maintain backward compatibility with existing unpacked sources
- Limited by 1C documentation (reverse engineering required)

## Onboarding Checklist
- [ ] Understand the 1C binary format problem
- [ ] Know the 4-stage pipeline architecture
- [ ] Understand version-specific builds (8.1/8.2/8.3)
- [ ] Know about include regions for code splitting
- [ ] Understand git submodule usage for shared code
- [ ] Be able to extract and build 1C files

## Related Files
- `technical-domain.md` - 4-stage pipeline implementation
- `business-tech-bridge.md` - How 1C needs map to Python solutions
- `decisions-log.md` - Architecture and format decisions
