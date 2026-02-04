import os

from .. import helper
from ..metadata_types import MetaDataTypes, MetaDataGroup
from ..ext_exception import ExtException
from .common_modules import export_common_module
from .catalogs import export_catalog
from .types import build_type_maps_from_root


SUPPORTED_TYPES = {
    'CommonModule': export_common_module,
    'Catalog': export_catalog,
}


def extract_1c_direct(src_dir: str, dest_dir: str, *, options=None, pool=None):
    """Extract directly into 1C XML layout without JSON intermediates."""
    if options is None:
        options = {}

    helper.clear_dir(dest_dir)

    _src_dir = _detect_container_root(src_dir)
    header_data = _read_root_header(_src_dir)
    type_maps = build_type_maps_from_root(_src_dir, header_data)
    for obj_type, obj_file in _iter_root_includes(header_data):
        handler = SUPPORTED_TYPES.get(obj_type)
        if not handler:
            continue
        if obj_type == 'Catalog':
            handler(_src_dir, obj_file, dest_dir, options=options, root_header=header_data, type_maps=type_maps)
        else:
            handler(_src_dir, obj_file, dest_dir, options=options)


def _read_root_header(src_dir: str):
    if os.path.isfile(os.path.join(src_dir, 'configinfo')):
        configinfo = helper.brace_file_read(src_dir, 'configinfo')
        file_uuid = configinfo[1][1]
        return helper.brace_file_read(src_dir, f'{file_uuid}')

    root = helper.brace_file_read(src_dir, 'root')
    file_uuid = root[0][1]
    return helper.brace_file_read(src_dir, f'{file_uuid}')


def _detect_container_root(src_dir: str) -> str:
    if os.path.isfile(os.path.join(src_dir, 'root')) or os.path.isfile(os.path.join(src_dir, 'configinfo')):
        return src_dir

    try:
        containers = sorted(os.listdir(src_dir))
    except FileNotFoundError as err:
        raise ExtException(parent=err, message='Container directory not found') from None

    # Expected 1 or 2 container folders, use the last (main) one
    if containers:
        candidate = os.path.join(src_dir, containers[-1])
        if os.path.isdir(candidate):
            return candidate

    return src_dir


def _iter_root_includes(header_data):
    index_includes_group = 2
    try:
        count_groups = int(header_data[0][index_includes_group])
    except Exception as err:
        raise ExtException(parent=err, message='Include groups not found') from None

    for index_group in range(count_groups):
        group = header_data[0][index_includes_group + index_group + 1]
        try:
            group_uuid = group[0]
            group_version = group[1][0]
        except Exception as err:
            raise ExtException(parent=err, message='Malformed include group') from None

        try:
            MetaDataGroup(group_uuid)
        except ValueError:
            # ignore unknown group
            continue

        include = group[1][1] if group_version == '6' else group[1]
        yield from _iter_include_objects(include)


def _iter_include_objects(include):
    try:
        count_include_types = int(include[2])
    except Exception as err:
        raise ExtException(parent=err, message='Include types not found') from None

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
            # internal objects ignored in minimal direct mode

