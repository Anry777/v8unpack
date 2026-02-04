from xml.sax.saxutils import escape

from .common import unquote, parse_lang_item, render_lang_block
from .types import resolve_full_attribute_type, resolve_extended_attribute_type


def parse_catalog_attributes(header: dict, type_maps: dict):
    try:
        block = header['header'][0][6]
    except Exception:
        return []

    if not isinstance(block, list) or len(block) <= 2:
        return []

    attrs = []
    for item in block[2:]:
        if not isinstance(item, list) or not item:
            continue
        attr_def = item[0]
        attr = parse_catalog_attribute(attr_def, type_maps)
        if attr:
            attrs.append(attr)
    return attrs


def parse_catalog_attribute(attr_def: list, type_maps: dict):
    try:
        sub = attr_def[1]
        sub1 = sub[1]
        props = sub1[1]
        pattern = sub1[2]
    except Exception:
        return None

    name = unquote(props[2]) if len(props) > 2 else ''
    uuid = props[1][2] if isinstance(props[1], list) and len(props[1]) > 2 else ''
    comment = unquote(props[4]) if len(props) > 4 else ''
    synonym = parse_lang_item(props[3]) if len(props) > 3 else None
    tooltip = parse_lang_item(sub[4]) if len(sub) > 4 else None
    password_mode = str(sub[2]) == '1'

    if len(props) <= 9:
        type_info = resolve_full_attribute_type(pattern, type_maps)
        return {
            'full': True,
            'uuid': uuid,
            'name': name,
            'comment': comment,
            'synonym': synonym,
            'tooltip': tooltip,
            'password_mode': password_mode,
            'type': type_info,
        }

    ext_uuid = props[11] if len(props) > 11 else ''
    type_info = resolve_extended_attribute_type(pattern, type_maps)
    return {
        'full': False,
        'uuid': uuid,
        'name': name,
        'comment': comment,
        'ext_uuid': ext_uuid,
        'type': type_info,
    }


def render_catalog_attribute(attr: dict):
    if not attr:
        return []

    uuid = escape(attr.get('uuid', ''))
    name = escape(attr.get('name', ''))
    comment = attr.get('comment', '')
    comment_xml = f'<Comment>{escape(comment)}</Comment>' if comment else '<Comment/>'

    if not attr.get('full'):
        type_info = attr.get('type', {})
        type_tag = 'TypeSet' if type_info.get('kind') == 'typeset' else 'Type'
        type_value = type_info.get('value', '')
        ext_uuid = escape(attr.get('ext_uuid', ''))
        lines = [
            f'			<Attribute uuid="{uuid}">',
            '				<InternalInfo/>',
            '				<Properties>',
            '					<ObjectBelonging>Adopted</ObjectBelonging>',
            f'					<Name>{name}</Name>',
            f'					{comment_xml}',
            f'					<ExtendedConfigurationObject>{ext_uuid}</ExtendedConfigurationObject>',
            '					<Type>',
            f'						<v8:{type_tag}>{escape(type_value)}</v8:{type_tag}>',
            '					</Type>',
            '				</Properties>',
            '			</Attribute>',
        ]
        return lines

    type_info = attr.get('type', {})
    password_mode = 'true' if attr.get('password_mode') else 'false'
    synonym = attr.get('synonym')
    tooltip = attr.get('tooltip')

    lines = [
        f'			<Attribute uuid="{uuid}">',
        '				<Properties>',
        f'					<Name>{name}</Name>',
    ]
    lines.extend(render_lang_block('					', 'Synonym', synonym))
    lines.append(f'					{comment_xml}')

    if type_info.get('kind') == 'string':
        lines.extend([
            '					<Type>',
            '						<v8:Type>xs:string</v8:Type>',
            '						<v8:StringQualifiers>',
            f'							<v8:Length>{type_info.get("length", "")}</v8:Length>',
            f'							<v8:AllowedLength>{type_info.get("allowed", "Variable")}</v8:AllowedLength>',
            '						</v8:StringQualifiers>',
            '					</Type>',
        ])
        fill_value = '<FillValue xsi:type="xs:string"/>'
        full_text_search = 'Use'
    elif type_info.get('kind') == 'value_storage':
        lines.extend([
            '					<Type>',
            '						<v8:Type>v8:ValueStorage</v8:Type>',
            '					</Type>',
        ])
        fill_value = '<FillValue xsi:nil="true"/>'
        full_text_search = 'DontUse'
    else:
        lines.extend([
            '					<Type>',
            '						<v8:Type>xs:boolean</v8:Type>',
            '					</Type>',
        ])
        fill_value = '<FillValue xsi:nil="true"/>'
        full_text_search = 'Use'

    lines.extend([
        f'					<PasswordMode>{password_mode}</PasswordMode>',
        '					<Format/>',
        '					<EditFormat/>',
    ])
    lines.extend(render_lang_block('					', 'ToolTip', tooltip))
    lines.extend([
        '					<MarkNegatives>false</MarkNegatives>',
        '					<Mask/>',
        '					<MultiLine>false</MultiLine>',
        '					<ExtendedEdit>false</ExtendedEdit>',
        '					<MinValue xsi:nil="true"/>',
        '					<MaxValue xsi:nil="true"/>',
        '					<FillFromFillingValue>false</FillFromFillingValue>',
        f'					{fill_value}',
        '					<FillChecking>DontCheck</FillChecking>',
        '					<ChoiceFoldersAndItems>Items</ChoiceFoldersAndItems>',
        '					<ChoiceParameterLinks/>',
        '					<ChoiceParameters/>',
        '					<QuickChoice>Auto</QuickChoice>',
        '					<CreateOnInput>Auto</CreateOnInput>',
        '					<ChoiceForm/>',
        '					<LinkByType/>',
        '					<ChoiceHistoryOnInput>Auto</ChoiceHistoryOnInput>',
        '					<Use>ForItem</Use>',
        '					<Indexing>DontIndex</Indexing>',
        f'					<FullTextSearch>{full_text_search}</FullTextSearch>',
        '					<DataHistory>Use</DataHistory>',
        '				</Properties>',
        '			</Attribute>',
    ])
    return lines
