<!-- Context: project-intelligence/notes | Priority: high | Version: 1.1 | Updated: 2026-02-04 -->

# Living Notes

> Active issues, technical debt, and TODOs for v8unpack.

## Quick Reference

- **Purpose**: Current state, problems, open questions
- **Update**: When TODOs change or issues found
- **Archive**: Move resolved to bottom

## Technical Debt

| Item | Impact | Priority | Mitigation |
|------|--------|----------|------------|
| Form.xml (logform) generation | High - export incomplete | High | Implement converter from form structure |
| Module.bsl extraction unreliable | High - forms missing code | High | Deepen parsing, check Form type 0/1 |
| Predefined.xml parsing | Medium - data lost | Medium | Implement `<uuid>.1c` parser |
| JSON path maintenance | Medium - dual paths | Low | Share code between JSON/direct_1c |

### Debt Details

**Form.xml Generation** - Implement converter from MetaDataObject/Form/* to logform XML (`http://v8.1c.ru/8.3/xcf/logform`). Effort: Medium. Status: Scheduled.

**Module.bsl Extraction** - Improve `decode_includes()` to reliably extract form modules, investigate Form type 0/1 differences. Effort: Medium. Status: In Progress.

**Predefined.xml** - Parse `<uuid>.1c` binary, generate `Ext/Predefined.xml` (xcf/predef). Effort: Medium. Status: Scheduled.

## Known Issues

| Issue | Severity | Workaround | Status |
|-------|----------|------------|--------|
| Ext/Form/Module.bsl not generated | High | Use JSON export | In Progress |
| Ext/Form.xml missing | High | Use 1C Designer | In Progress |
| Predefined data missing | Medium | Manual 1C export | Known |

### Issue Details

**Module.bsl Missing** - `decode_includes()` doesn't extract form modules. Check Form type 0 vs 1 storage. Fix: Deepen form parsing.

**Form.xml Missing** - Form.xml is separate logform XML, not in CFE. Fix: Implement logform generator.

## Open Questions

| Question | Stakeholders | Status |
|----------|--------------|--------|
| Form type 0 vs 1 code storage | SABY | Open |
| Logform XML namespace completeness | SABY | Open |
| Predefined data binary format | Community | Open |

## Insights

### What Works Well
- 4-stage pipeline - clear separation, easy debugging
- Include regions - simple, enables reuse
- Version-specific builds - single source for 8.1/8.2/8.3
- Enum-based types - type-safe, self-documenting

### What Could Be Better
- Dual extraction paths (JSON/direct_1c) - maintenance overhead
- Form module extraction - needs redesign
- Documentation - 1C binary reverse-engineering needs more docs

### Gotchas
- 1C directives auto-commenting - `\n#` pattern, ensure newline before directive
- Include conflicts - use includr (read-only) for secondary
- Index.json paths - use forward slashes for Linux
- Form type differences - type 0 vs 1 store modules differently

## Active Projects

| Project | Goal | Timeline |
|---------|------|----------|
| Direct 1C Export | Complete Form.xml, Module.bsl, Predefined.xml | Q1 2026 |
| Code Sharing | Improve index.json, submodule support | Ongoing |

## Current TODOs

1. **Form.xml (logform)** - Implement converter from form structure to XML format
2. **Module.bsl** - Clarify module location, improve extraction
3. **Predefined.xml** - Implement `<uuid>.1c` parser
4. **1:1 Verification** - Re-verify after Form.xml/Module.bsl complete

## Archive

### Resolved: Direct 1C Export Skeleton
- **Resolved**: 2026-02-04
- **Resolution**: Implemented `direct_1c/` package (decoder, catalogs, forms, types)
- **Learnings**: Bypassing JSON feasible, requires logform generation

## Onboarding Checklist

- [ ] Know current TODOs (Form.xml, Module.bsl, Predefined.xml)
- [ ] Understand tech debt impact on direct 1C export
- [ ] Know known issues and workarounds
- [ ] Understand gotchas: include conflicts, form types, 1C directives

## Related Files

- `decisions-log.md` - Direct 1C export decision
- `STATUS.md` - Current TODOs and progress
- `business-tech-bridge.md` - Direct 1C export business value
