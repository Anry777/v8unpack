import os

from .. import helper
from ..MetaDataObject.Catalog import Catalog
from ..metadata_types import MetaDataTypes
from ..format_1c.catalogs import build_catalog_xml, catalog_generated_types
from ..format_1c.catalog_attributes import parse_catalog_attributes
from ..format_1c.catalog_commands import find_command_ext_uuid
from ..format_1c.common import last_uuid_in_meta_header, is_zero_uuid
from .types import build_type_maps_from_root
from .forms import export_catalog_form


def export_catalog(src_dir: str, obj_file: str, dest_dir: str, *, options=None, root_header=None, type_maps=None):
    if options is None:
        options = {}

    header_data = helper.brace_file_read(src_dir, obj_file)
    obj = Catalog(options=options)
    obj.decode_header(header_data, id_in_separate_file=False)

    name = obj.header.get('name', '')
    synonym = obj.header.get('name2') or {}
    comment = obj.header.get('comment', '')
    uuid = obj.header.get('uuid', '')

    arr = header_data[0][1]
    meta_header = arr[9][1]
    meta_len = len(meta_header)

    gen = catalog_generated_types(arr, name)
    ext_uuid = last_uuid_in_meta_header(meta_header)
    is_extended = bool(ext_uuid) and not is_zero_uuid(ext_uuid)

    has_predefined = os.path.isfile(os.path.join(src_dir, f'{uuid}.1c'))

    if type_maps is None:
        type_maps = build_type_maps_from_root(src_dir, root_header) if root_header else {
            'catalog_ref': {},
            'document_ref': {},
            'defined_type': {},
        }
    header_dict = {'header': header_data}
    attributes = parse_catalog_attributes(header_dict, type_maps)

    commands = _collect_catalog_commands(src_dir, header_data)
    forms = _collect_catalog_forms(src_dir, header_data, dest_dir, name, options)

    xml_text = build_catalog_xml(
        name=name,
        uuid=uuid,
        synonym=synonym,
        comment=comment,
        is_extended=is_extended,
        ext_uuid=ext_uuid,
        gen=gen,
        has_predefined=has_predefined,
        meta_len=meta_len,
        arr=arr,
        forms=forms,
        attributes=attributes,
        commands=commands,
    )

    dest_root = os.path.join(dest_dir, 'Catalogs')
    helper.makedirs(dest_root, exist_ok=True)
    helper.txt_write(xml_text, dest_root, f'{name}.xml', encoding='utf-8-sig')


def _collect_catalog_forms(src_dir: str, header_data, dest_dir: str, catalog_name: str, options):
    forms = []
    dest_forms_dir = os.path.join(dest_dir, 'Catalogs', catalog_name, 'Forms')
    for obj_type, obj_file in _iter_includes(header_data):
        if obj_type != 'CatalogForm':
            continue
        helper.makedirs(dest_forms_dir, exist_ok=True)
        try:
            form_name = export_catalog_form(src_dir, obj_file, dest_forms_dir, options=options)
        except Exception:
            continue
        if form_name:
            forms.append(form_name)
    return sorted(forms)


def _collect_catalog_commands(src_dir: str, header_data):
    commands = []
    for obj_type, obj_file in _iter_includes(header_data):
        if obj_type != 'CatalogCommand':
            continue
        try:
            cmd_header = helper.brace_file_read(src_dir, obj_file)
        except Exception:
            continue
        try:
            name, comment, uuid = _decode_name_comment_uuid(cmd_header)
        except Exception:
            continue
        ext_uuid = find_command_ext_uuid({'header': cmd_header})
        commands.append({
            'uuid': uuid,
            'name': name,
            'comment': comment,
            'ext_uuid': ext_uuid,
            'group': 'FormNavigationPanelGoTo',
        })
    return commands


def _iter_includes(header_data):
    try:
        include = header_data[0]
    except Exception:
        return []

    result = []
    try:
        count_include_types = int(include[2])
    except Exception:
        return []

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
                result.append((metadata_type.name, obj_data))
    return result


def _decode_name_comment_uuid(header_data):
    header = header_data[0][1][1]
    uuid = header[1][2]
    name = _unquote(header[2])
    comment = _unquote(header[4])
    return name, comment, uuid


def _unquote(value):
    if isinstance(value, str) and len(value) >= 2 and value[0] == '"' and value[-1] == '"':
        return value[1:-1]
    return value if isinstance(value, str) else ''

