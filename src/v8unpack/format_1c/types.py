import os

from .. import helper
from .common import unquote


def build_type_maps(src_dir: str):
    def scan_ref_types(parent_dir: str, file_name: str, type_index: int):
        mapping = {}
        if not os.path.isdir(parent_dir):
            return mapping
        for obj_name in os.listdir(parent_dir):
            obj_dir = os.path.join(parent_dir, obj_name)
            if not os.path.isdir(obj_dir):
                continue
            try:
                header = helper.json_read(obj_dir, file_name)
                arr = header['header'][0][1]
                type_id = arr[type_index]
                name = header.get('name', obj_name)
                mapping[type_id] = name
            except Exception:
                continue
        return mapping

    def scan_defined_types(parent_dir: str):
        mapping = {}
        if not os.path.isdir(parent_dir):
            return mapping
        for obj_name in os.listdir(parent_dir):
            obj_dir = os.path.join(parent_dir, obj_name)
            if not os.path.isdir(obj_dir):
                continue
            try:
                header = helper.json_read(obj_dir, 'DefinedType.json')
                arr = header['header'][0][1]
                type_id = arr[1]
                name = header.get('name', obj_name)
                mapping[type_id] = name
            except Exception:
                continue
        return mapping

    return {
        'catalog_ref': scan_ref_types(os.path.join(src_dir, 'Catalog'), 'Catalog.json', 3),
        'document_ref': scan_ref_types(os.path.join(src_dir, 'Document'), 'Document.json', 3),
        'defined_type': scan_defined_types(os.path.join(src_dir, 'DefinedType')),
    }


def resolve_full_attribute_type(pattern: list, type_maps: dict):
    try:
        marker = unquote(pattern[1][0])
    except Exception:
        return {'kind': 'boolean'}

    if marker == 'B':
        return {'kind': 'boolean'}
    if marker == 'S':
        length = pattern[1][1] if len(pattern[1]) > 1 else ''
        allowed = 'Variable' if len(pattern[1]) > 2 and str(pattern[1][2]) == '1' else 'Fixed'
        return {'kind': 'string', 'length': length, 'allowed': allowed}
    if marker == '#':
        return {'kind': 'value_storage'}
    return {'kind': 'boolean'}


def resolve_extended_attribute_type(pattern: list, type_maps: dict):
    try:
        type_uuid = pattern[1][1]
    except Exception:
        return {'kind': 'typeset', 'value': 'cfg:AnyIBRef'}

    if type_uuid in type_maps.get('defined_type', {}):
        name = type_maps['defined_type'][type_uuid]
        return {'kind': 'typeset', 'value': f'cfg:DefinedType.{name}'}
    if type_uuid in type_maps.get('catalog_ref', {}):
        name = type_maps['catalog_ref'][type_uuid]
        return {'kind': 'type', 'value': f'cfg:CatalogRef.{name}'}
    if type_uuid in type_maps.get('document_ref', {}):
        name = type_maps['document_ref'][type_uuid]
        return {'kind': 'type', 'value': f'cfg:DocumentRef.{name}'}
    return {'kind': 'typeset', 'value': 'cfg:AnyIBRef'}
