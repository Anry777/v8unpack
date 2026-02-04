from .. import helper
from ..metadata_types import MetaDataTypes
from ..MetaDataObject.Catalog import Catalog
from ..MetaDataObject.Document import Document
from ..MetaDataObject.DefinedType import DefinedType


def _decode_header(header_data, *, options=None):
    class _Dummy:
        def __init__(self, options):
            self.header = {}
            self.options = options or {}
            self.parent_id = ''
            self.container_uuid = None
            self.parent_container_uuid = None
    dummy = _Dummy(options)
    helper.decode_header(dummy, header_data, id_in_separate_file=False)
    return dummy.header


def build_type_maps_from_root(src_dir: str, root_header):
    catalog_ref = {}
    document_ref = {}
    defined_type = {}

    class_map = {
        'Catalog': Catalog,
        'Document': Document,
        'DefinedType': DefinedType,
    }

    for obj_type, obj_file in _iter_root_objects(root_header):
        if obj_type not in ('Catalog', 'Document', 'DefinedType'):
            continue
        try:
            header_data = helper.brace_file_read(src_dir, obj_file)
        except Exception:
            continue

        try:
            meta_cls = class_map[obj_type]
            obj_header = _decode_header(meta_cls.get_decode_header(header_data))
        except Exception:
            continue

        name = obj_header.get('name', '')
        try:
            arr = header_data[0][1]
        except Exception:
            continue

        if obj_type == 'Catalog':
            type_id = _safe_get(arr, 3)
            if type_id:
                catalog_ref[type_id] = name
        elif obj_type == 'Document':
            type_id = _safe_get(arr, 3)
            if type_id:
                document_ref[type_id] = name
        elif obj_type == 'DefinedType':
            type_id = _safe_get(arr, 1)
            if type_id:
                defined_type[type_id] = name

    return {
        'catalog_ref': catalog_ref,
        'document_ref': document_ref,
        'defined_type': defined_type,
    }


def _safe_get(arr, index):
    try:
        return arr[index]
    except Exception:
        return None


def _iter_root_objects(header_data):
    index_includes_group = 2
    try:
        count_groups = int(header_data[0][index_includes_group])
    except Exception:
        return

    for index_group in range(count_groups):
        group = header_data[0][index_includes_group + index_group + 1]
        try:
            group_version = group[1][0]
        except Exception:
            continue
        include = group[1][1] if group_version == '6' else group[1]
        for obj_type, obj_file in _iter_include_objects(include):
            yield obj_type, obj_file


def _iter_include_objects(include):
    try:
        count_include_types = int(include[2])
    except Exception:
        return

    for i in range(count_include_types):
        _metadata = include[i + 3]
        try:
            _count_obj = int(_metadata[1])
            _metadata_type_uuid = _metadata[0]
        except Exception:
            continue

        try:
            metadata_type = MetaDataTypes(_metadata_type_uuid)
        except ValueError:
            continue

        if not _count_obj:
            continue

        for j in range(_count_obj):
            obj_data = _metadata[j + 2]
            if isinstance(obj_data, str):
                yield metadata_type.name, obj_data

