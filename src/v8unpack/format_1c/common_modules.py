import os
from xml.sax.saxutils import escape

from .. import helper
from .common import _XML_NS, last_uuid_in_header_list, is_zero_uuid


def export_common_modules(src_dir: str, dest_dir: str):
    src_root = os.path.join(src_dir, 'CommonModule')
    if not os.path.isdir(src_root):
        return

    dest_root = os.path.join(dest_dir, 'CommonModules')
    helper.makedirs(dest_root, exist_ok=True)

    for obj_name in os.listdir(src_root):
        obj_dir = os.path.join(src_root, obj_name)
        if not os.path.isdir(obj_dir):
            continue

        header = helper.json_read(obj_dir, 'CommonModule.json')
        data_id = helper.json_read(obj_dir, 'CommonModule.id.json')

        name = header.get('name', obj_name)
        synonym = header.get('name2') or {}
        comment = header.get('comment', '')
        uuid = data_id.get('uuid', '')

        flags = []
        try:
            flags = header['header'][0][1][2:]
        except Exception:
            flags = []

        props = parse_common_module_flags(flags)
        ext_uuid = last_uuid_in_header_list(header)
        is_extended = bool(ext_uuid) and not is_zero_uuid(ext_uuid)

        xml_text = build_common_module_xml(
            name=name,
            uuid=uuid,
            synonym=synonym,
            comment=comment,
            props=props,
            is_extended=is_extended,
            ext_uuid=ext_uuid
        )
        helper.txt_write(xml_text, dest_root, f'{obj_name}.xml', encoding='utf-8-sig')

        # module code
        src_module = os.path.join(obj_dir, 'CommonModule.obj.bsl')
        if os.path.isfile(src_module):
            dest_module_dir = os.path.join(dest_root, obj_name, 'Ext')
            helper.makedirs(dest_module_dir, exist_ok=True)
            helper.txt_write(
                helper.txt_read(obj_dir, 'CommonModule.obj.bsl', encoding='utf-8-sig'),
                dest_module_dir,
                'Module.bsl',
                encoding='utf-8-sig'
            )


def parse_common_module_flags(flags):
    def _flag(i):
        try:
            return str(flags[i]) == '1'
        except Exception:
            return False

    return {
        'Global': _flag(3),
        'ClientManagedApplication': _flag(5),
        'Server': _flag(1),
        'ExternalConnection': _flag(2),
        'ClientOrdinaryApplication': _flag(0),
        'ServerCall': _flag(7),
        'Privileged': _flag(4),
        'ReturnValuesReuse': 'DontUse'
    }


def build_common_module_xml(*, name, uuid, synonym, comment, props, is_extended, ext_uuid):
    name = escape(name)
    comment_xml = f'<Comment>{escape(comment)}</Comment>' if comment else '<Comment/>'

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<MetaDataObject {_XML_NS}>',
        f'	<CommonModule uuid="{escape(uuid)}">'
    ]

    if is_extended:
        lines.extend([
            '		<InternalInfo>',
            '			<xr:PropertyState>',
            '				<xr:Property>Module</xr:Property>',
            '				<xr:State>Extended</xr:State>',
            '			</xr:PropertyState>',
            '		</InternalInfo>'
        ])

    lines.append('		<Properties>')

    if is_extended:
        lines.append('			<ObjectBelonging>Adopted</ObjectBelonging>')

    lines.append(f'			<Name>{name}</Name>')

    if synonym:
        lines.append('			<Synonym>')
        for lang, content in synonym.items():
            lines.append('				<v8:item>')
            lines.append(f'					<v8:lang>{escape(lang)}</v8:lang>')
            lines.append(f'					<v8:content>{escape(content)}</v8:content>')
            lines.append('				</v8:item>')
        lines.append('			</Synonym>')

    lines.append(f'			{comment_xml}')

    if is_extended:
        lines.append(f'			<ExtendedConfigurationObject>{escape(ext_uuid)}</ExtendedConfigurationObject>')

    lines.extend([
        f'			<Global>{str(props["Global"]).lower()}</Global>',
        f'			<ClientManagedApplication>{str(props["ClientManagedApplication"]).lower()}</ClientManagedApplication>',
        f'			<Server>{str(props["Server"]).lower()}</Server>',
        f'			<ExternalConnection>{str(props["ExternalConnection"]).lower()}</ExternalConnection>',
        f'			<ClientOrdinaryApplication>{str(props["ClientOrdinaryApplication"]).lower()}</ClientOrdinaryApplication>',
        f'			<ServerCall>{str(props["ServerCall"]).lower()}</ServerCall>'
    ])

    if not is_extended:
        lines.append(f'			<Privileged>{str(props["Privileged"]).lower()}</Privileged>')
        lines.append(f'			<ReturnValuesReuse>{props["ReturnValuesReuse"]}</ReturnValuesReuse>')

    lines.extend([
        '		</Properties>',
        '	</CommonModule>',
        '</MetaDataObject>'
    ])

    return '\n'.join(lines)
