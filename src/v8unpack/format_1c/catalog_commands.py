import os
from xml.sax.saxutils import escape

from .. import helper


def parse_catalog_commands(obj_dir: str):
    commands_dir = os.path.join(obj_dir, 'CatalogCommand')
    if not os.path.isdir(commands_dir):
        return []

    commands = []
    for cmd_name in os.listdir(commands_dir):
        cmd_dir = os.path.join(commands_dir, cmd_name)
        if not os.path.isdir(cmd_dir):
            continue
        try:
            header = helper.json_read(cmd_dir, 'CatalogCommand.json')
            data_id = helper.json_read(cmd_dir, 'CatalogCommand.id.json')
        except Exception:
            continue

        name = header.get('name', cmd_name)
        comment = header.get('comment', '')
        uuid = data_id.get('uuid', '')
        ext_uuid = find_command_ext_uuid(header)

        commands.append({
            'uuid': uuid,
            'name': name,
            'comment': comment,
            'ext_uuid': ext_uuid,
            'group': 'FormNavigationPanelGoTo',
        })

    return commands


def find_command_ext_uuid(header: dict) -> str:
    def walk(value):
        if isinstance(value, list):
            if value and value[0] == '3' and len(value) >= 12:
                return value[11]
            for item in value:
                found = walk(item)
                if found:
                    return found
        return ''

    try:
        return walk(header.get('header'))
    except Exception:
        return ''


def render_catalog_command(cmd: dict):
    if not cmd:
        return []
    uuid = escape(cmd.get('uuid', ''))
    name = escape(cmd.get('name', ''))
    comment = cmd.get('comment', '')
    comment_xml = f'<Comment>{escape(comment)}</Comment>' if comment else '<Comment/>'
    ext_uuid = escape(cmd.get('ext_uuid', ''))
    group = escape(cmd.get('group', 'FormNavigationPanelGoTo'))

    return [
        f'			<Command uuid="{uuid}">',
        '				<InternalInfo/>',
        '				<Properties>',
        '					<ObjectBelonging>Adopted</ObjectBelonging>',
        f'					<Name>{name}</Name>',
        f'					{comment_xml}',
        f'					<ExtendedConfigurationObject>{ext_uuid}</ExtendedConfigurationObject>',
        f'					<Group>{group}</Group>',
        '				</Properties>',
        '			</Command>',
    ]
