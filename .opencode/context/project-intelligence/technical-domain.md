<!-- Context: project-intelligence/technical | Priority: critical | Version: 1.1 | Updated: 2026-02-04 -->

# Technical Domain

**Purpose**: Python CLI utility for unpacking/packing 1C:Enterprise binary files to/from JSON/XML.
**Last Updated**: 2026-02-04

## Quick Reference
**Update Triggers**: New 1C version support | Architecture changes | New metadata types
**Audience**: Developers, CI/CD pipelines, 1C developers

## Primary Stack
| Layer | Technology | Version | Rationale |
|-------|-----------|---------|-----------|
| Language | Python | 3.7+ | Cross-platform, mature ecosystem |
| Framework | CLI (argparse) | stdlib | Lightweight, no dependencies |
| Key Libraries | tqdm | latest | Progress bars for large files |
| Packaging | setuptools | dynamic | Standard Python packaging |
| Testing | unittest | stdlib | Built-in, sufficient |

## Architecture Pattern
```
Type: Monolith CLI Utility
Pattern: 4-stage pipeline
1. Extract: v8unpack → raw files
2. Convert: raw → JSON/XML
3. Organize: split by metadata type, version code
4. Build: JSON/XML → v8unpack binary
```

**Why This Architecture?** Binary format is complex, requires staged parsing. 4 stages enable version-specific transformations (8.1/8.2/8.3 compatibility) and human-readable output.

## Code Patterns
### Class-based Handler Registry
```python
available_types = {
    'ExternalDataProcessor': ExternalDataProcessor,
    'Configuration': Configuration,
    'ConfigurationExtension': ConfigurationExtension
}

handler = available_types[obj_type.name](options=options, obj_version=version)
```

### Type-safe Enums
```python
class MetaDataTypes(Enum):
    Catalog = "cf4abea6-37b2-11d4-940f-008048da11f9"
    Document = "53690a5d-a543-4185-b449-03ff260f3edb"
```

### Exception Handling
```python
from ext_exception import ExtException
raise ExtException(message='Неподдерживаемый формат', detail=f'format={format_kind}')
```

## Naming Conventions
| Type | Convention | Example |
|------|-----------|---------|
| Files | snake_case.py | container_reader.py, metadata_types.py |
| Classes | PascalCase | ConfigurationExtension, Decoder |
| Functions | snake_case | extract(), build(), decode() |
| Variables | snake_case | src_dir, dest_dir, options |

## Code Standards
- Python 3.7+ type hints in function signatures
- Russian messages for 1C developers
- Multi-format output (json, 1c)
- Version-specific transformations (801, 802, 803)
- Test with unittest in tests/ directory
- Clear directory separation: MetaObject/, format_1c/, direct_1c/

## Security Requirements
- Validate file versions before processing
- Handle corrupted binaries gracefully
- Clear temp directories after processing
- Parameter validation in CLI arguments

## 📂 Codebase References
**Implementation**: `src/v8unpack/decoder.py` - Main decode/encode pipeline
**CLI**: `src/v8unpack/v8unpack.py` - Entry point, argument parsing
**Config**: `pyproject.toml` - Dependencies, version management
**Types**: `src/v8unpack/metadata_types.py` - 1C metadata type definitions
**Tests**: `tests/` - unittest test suite

## Related Files
- [Business Domain](business-domain.md)
- [Decisions Log](decisions-log.md)
