import os

from .. import helper
from ..MetaDataObject.CommonModule import CommonModule
from ..format_1c.common_modules import build_common_module_xml, parse_common_module_flags
from ..format_1c.common import last_uuid_in_header_list, is_zero_uuid


def export_common_module(src_dir: str, obj_file: str, dest_dir: str, *, options=None):
    if options is None:
        options = {}

    header_data = helper.brace_file_read(src_dir, obj_file)
    obj = CommonModule(options=options)
    obj.decode_header(header_data, id_in_separate_file=False)
    obj.decode_code(src_dir)

    name = obj.header.get('name', '')
    synonym = obj.header.get('name2') or {}
    comment = obj.header.get('comment', '')
    uuid = obj.header.get('uuid', '')

    try:
        flags = header_data[0][1][2:]
    except Exception:
        flags = []

    props = parse_common_module_flags(flags)
    ext_uuid = last_uuid_in_header_list({'header': header_data})
    is_extended = bool(ext_uuid) and not is_zero_uuid(ext_uuid)

    xml_text = build_common_module_xml(
        name=name,
        uuid=uuid,
        synonym=synonym,
        comment=comment,
        props=props,
        is_extended=is_extended,
        ext_uuid=ext_uuid,
    )

    dest_root = os.path.join(dest_dir, 'CommonModules')
    helper.makedirs(dest_root, exist_ok=True)
    helper.txt_write(xml_text, dest_root, f'{name}.xml', encoding='utf-8-sig')

    code = obj.code.get('obj')
    if isinstance(code, str) and code:
        dest_module_dir = os.path.join(dest_root, name, 'Ext')
        helper.makedirs(dest_module_dir, exist_ok=True)
        helper.txt_write(code, dest_module_dir, 'Module.bsl', encoding='utf-8-sig')

