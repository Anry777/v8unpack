import re
from xml.sax.saxutils import escape

_XML_HEADER = '<?xml version="1.0" encoding="UTF-8"?>\n'
_XML_NS = (
    'xmlns="http://v8.1c.ru/8.3/MDClasses" '
    'xmlns:app="http://v8.1c.ru/8.2/managed-application/core" '
    'xmlns:cfg="http://v8.1c.ru/8.1/data/enterprise/current-config" '
    'xmlns:cmi="http://v8.1c.ru/8.2/managed-application/cmi" '
    'xmlns:ent="http://v8.1c.ru/8.1/data/enterprise" '
    'xmlns:lf="http://v8.1c.ru/8.2/managed-application/logform" '
    'xmlns:style="http://v8.1c.ru/8.1/data/ui/style" '
    'xmlns:sys="http://v8.1c.ru/8.1/data/ui/fonts/system" '
    'xmlns:v8="http://v8.1c.ru/8.1/data/core" '
    'xmlns:v8ui="http://v8.1c.ru/8.1/data/ui" '
    'xmlns:web="http://v8.1c.ru/8.1/data/ui/colors/web" '
    'xmlns:win="http://v8.1c.ru/8.1/data/ui/colors/windows" '
    'xmlns:xen="http://v8.1c.ru/8.3/xcf/enums" '
    'xmlns:xpr="http://v8.1c.ru/8.3/xcf/predef" '
    'xmlns:xr="http://v8.1c.ru/8.3/xcf/readable" '
    'xmlns:xs="http://www.w3.org/2001/XMLSchema" '
    'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
    'version="2.20"'
)


def unquote(value: str) -> str:
    if isinstance(value, str) and len(value) >= 2 and value[0] == '"' and value[-1] == '"':
        return value[1:-1]
    return value if isinstance(value, str) else ''


def parse_lang_item(value):
    if not isinstance(value, list) or not value:
        return None
    if value[0] != '1' or len(value) < 3:
        return None
    return {
        'lang': unquote(value[1]),
        'content': unquote(value[2]),
    }


def render_lang_block(tag: str, label: str, item: dict):
    if not item:
        return [f'{tag}<{label}/>' ]
    return [
        f'{tag}<{label}>',
        f'{tag}	<v8:item>',
        f'{tag}		<v8:lang>{escape(item["lang"])}</v8:lang>',
        f'{tag}		<v8:content>{escape(item["content"])}</v8:content>',
        f'{tag}	</v8:item>',
        f'{tag}</{label}>',
    ]


def last_uuid_in_header_list(header):
    try:
        header_list = header['header'][0][1][1]
    except Exception:
        return None
    uuids = [x for x in header_list if isinstance(x, str) and re.fullmatch(r'[0-9a-f\-]{36}', x)]
    return uuids[-1] if uuids else None


def last_uuid_in_meta_header(meta_header):
    uuids = [x for x in meta_header if isinstance(x, str) and re.fullmatch(r'[0-9a-f\-]{36}', x)]
    return uuids[-1] if uuids else None


def is_zero_uuid(value: str) -> bool:
    return value == '00000000-0000-0000-0000-000000000000'
