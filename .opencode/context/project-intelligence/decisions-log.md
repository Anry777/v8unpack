<!-- Context: project-intelligence/decisions | Priority: high | Version: 1.1 | Updated: 2026-02-04 -->

# Decisions Log

> Record major technical and business decisions with context and rationale.

## Quick Reference

- **Purpose**: Understand why we made specific choices
- **Format**: Condensed decision entries
- **Status**: Accepted | Rejected | Deprecated

---

## 2026-02-04: Direct 1C Export (--format 1c)

**Status**: Accepted (in development) | **Impact**: High
**Context**: JSON intermediate slows extraction, prevents direct 1C Designer comparison
**Decision**: Separate `direct_1c/` package bypassing JSON, export to 1C XML
**Rationale**: Faster extraction, direct comparison, cleaner workflow
**Alternatives**: JSON→XSLT (complex), post-processing (extra step)
**Trade-offs**: Gain speed/directness, lose feature parity (Form.xml, Module.bsl)
**Related**: `src/v8unpack/direct_1c/`, `STATUS.md`

---

## 2021: 4-Stage Pipeline

**Status**: Accepted | **Impact**: Critical
**Context**: Binary 1C files need transformation to human-readable sources
**Decision**: Extract → Convert → Organize → Build pipeline
**Rationale**: Each stage addresses specific challenge, enables version transforms
**Alternatives**: 2-stage (too complex), 3-stage (insufficient), 5+ (over-engineering)
**Trade-offs**: Gain modularity/testability, lose complexity
**Related**: `src/v8unpack/decoder.py`, `README.md`

---

## 2021: JSON Intermediate Format

**Status**: Accepted | **Impact**: High
**Context**: Need human-readable, version-controllable storage
**Decision**: JSON format with human-readable keys
**Rationale**: Universal, git-friendly, easy to transform
**Alternatives**: Direct XML (verbose), binary (not versionable), custom (no ecosystem)
**Trade-offs**: Gain universality/readability, lose verbosity (mitigated by splitting)
**Related**: `src/v8unpack/json_container_decoder.py`

---

## 2021: Include Regions for Code Splitting

**Status**: Accepted | **Impact**: High
**Context**: Code duplication across forms/objects
**Decision**: `#Область include_path` regions, `includr` for read-only
**Rationale**: Familiar to 1C devs, enables submodules, edit once
**Alternatives**: Copy-paste (high maintenance), macros (non-standard)
**Trade-offs**: Gain reuse/single source, lose file management complexity
**Related**: `src/v8unpack/organizer_code.py`, `docs/usage.md`

---

## 2021: Version-Specific Builds (--version, --descent)

**Status**: Accepted | **Impact**: High
**Context**: Maintain 8.1/8.2/8.3 from single source
**Decision**: CLI params for version handling
**Rationale**: Single source, auto 8.3 commenting, ~90% duplication reduction
**Alternatives**: Branches (merge hell), scripts (manual), no support (duplicate)
**Trade-offs**: Gain one-source/multi-target, lose complex source structure
**Related**: `src/v8unpack/decoder.py`, `docs/usage.md`

---

## 2021: index.json for Git Submodules

**Status**: Accepted | **Impact**: Medium
**Context**: Share code via git submodules, declarative mapping
**Decision**: JSON file mapping source → submodule paths
**Rationale**: Git-native, flexible (* wildcards, exceptions), overrides include regions
**Alternatives**: Hardcoded paths (inflexible), symlinks (Windows issues), scripts (extra step)
**Trade-offs**: Gain git-native/flexible, lose manual management
**Related**: `src/v8unpack/index.py`, `docs/usage.md`

---

## 2021: Enum-Based Metadata Types

**Status**: Accepted | **Impact**: Medium
**Context**: Type-safe, self-documenting type definitions
**Decision**: Python Enum for MetaDataTypes/MetaDataGroup
**Rationale**: Type-safe, self-documenting, IDE autocomplete
**Alternatives**: Strings (typos), dictionary (no autocomplete), class (verbose)
**Trade-offs**: Gain safety/readability/IDE support, lose minimal verbosity
**Related**: `src/v8unpack/metadata_types.py`

---

## 2021: Class-Based Handler Registry

**Status**: Accepted | **Impact**: Low
**Context**: Different 1C file types need different handlers
**Decision**: Dictionary mapping names → classes, dynamic instantiation
**Rationale**: Easy to add, centralized, testable, extensible
**Alternatives**: If/elif (verbose), factory (boilerplate), single (bloated)
**Trade-offs**: Gain extensibility/clarity, lose minimal overhead
**Related**: `src/v8unpack/decoder.py`, `src/v8unpack/MetaObject/`

---

## Deprecated Decisions

| Decision | Date | Replaced By | Why |
|----------|------|-------------|-----|
| None yet | - | - | - |

## Summary

| Category | Decisions | Impact |
|----------|-----------|--------|
| Architecture | 4-stage, direct_1c | Critical |
| Data Format | JSON, enum types | High |
| Code Management | Include regions, version builds | High |
| Extensibility | index.json, handler registry | Medium |

## Onboarding Checklist

- [ ] Understand 4-stage pipeline rationale
- [ ] Know JSON vs direct 1C trade-offs
- [ ] See include regions solve duplication
- [ ] Understand version-specific builds
- [ ] Explain index.json vs alternatives

## Related Files

- `technical-domain.md` - Technical implementation
- `business-tech-bridge.md` - Business value of choices
- `living-notes.md` - Current TODOs
