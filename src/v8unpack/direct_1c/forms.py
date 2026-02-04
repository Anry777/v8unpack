import re
from xml.sax.saxutils import escape

from .. import helper
from ..MetaDataObject.CatalogForm import CatalogForm
from ..format_1c.common import _XML_NS

UUID_RE = re.compile(r'[0-9a-f\-]{36}', re.IGNORECASE)


def export_catalog_form(src_dir: str, form_file: str, dest_forms_dir: str, *, options=None):
    if options is None:
        options = {}

    header_data = helper.brace_file_read(src_dir, form_file)
    obj = CatalogForm(options=options)
    obj.decode_header(header_data, id_in_separate_file=False)
    # decode form to extract module (stored inside form data for many cases)
    try:
        obj.decode_includes(src_dir, '', '', header_data)
    except Exception:
        pass
    obj.decode_code(src_dir, uncomment_directive=True)

    name = obj.header.get('name', '')
    comment = obj.header.get('comment', '')
    uuid = obj.header.get('uuid', '')
    ext_uuid = find_last_uuid(header_data)

    form_type = _detect_form_type(header_data)
    xml_text = build_catalog_form_xml(
        name=name,
        uuid=uuid,
        comment=comment,
        ext_uuid=ext_uuid,
        form_type=form_type,
    )

    helper.txt_write(xml_text, dest_forms_dir, f'{name}.xml', encoding='utf-8-sig')

    # Ext/Form.xml
    form_xml = _try_extract_form_xml(src_dir, obj, header_data)
    if form_xml:
        ext_dir = _ensure_form_ext_dir(dest_forms_dir, name)
        helper.txt_write(form_xml, ext_dir, 'Form.xml', encoding='utf-8-sig')

    # Form module
    code = obj.code.get('obj')
    if isinstance(code, str) and code:
        module_dir = _ensure_form_module_dir(dest_forms_dir, name)
        helper.txt_write(code, module_dir, 'Module.bsl', encoding='utf-8-sig')

    return name


def build_catalog_form_xml(*, name, uuid, comment, ext_uuid, form_type):
    name_xml = escape(name)
    comment_xml = f'<Comment>{escape(comment)}</Comment>' if comment else '<Comment/>'
    ext_uuid_xml = escape(ext_uuid or '')

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<MetaDataObject {_XML_NS}>',
        f'\t<Form uuid="{escape(uuid)}">',
        '\t\t<InternalInfo>',
        '\t\t\t<xr:PropertyState>',
        '\t\t\t\t<xr:Property>Form</xr:Property>',
        '\t\t\t\t<xr:State>Extended</xr:State>',
        '\t\t\t</xr:PropertyState>',
        '\t\t</InternalInfo>',
        '\t\t<Properties>',
        '\t\t\t<ObjectBelonging>Adopted</ObjectBelonging>',
        f'\t\t\t<Name>{name_xml}</Name>',
        f'\t\t\t{comment_xml}',
        f'\t\t\t<ExtendedConfigurationObject>{ext_uuid_xml}</ExtendedConfigurationObject>',
        f'\t\t\t<FormType>{form_type}</FormType>',
        '\t\t</Properties>',
        '\t</Form>',
        '</MetaDataObject>',
    ]
    return '\n'.join(lines)


def _detect_form_type(header_data):
    try:
        form_root = CatalogForm.get_form_root(header_data)
        form_type = form_root[1][3]
    except Exception:
        form_type = '1'

    return 'Managed' if str(form_type) == '1' else 'Ordinary'


def _ensure_form_ext_dir(dest_forms_dir: str, name: str):
    ext_dir = helper.makedirs(os.path.join(dest_forms_dir, name, 'Ext'), exist_ok=True)
    return os.path.join(dest_forms_dir, name, 'Ext')


def _ensure_form_module_dir(dest_forms_dir: str, name: str):
    module_dir = os.path.join(dest_forms_dir, name, 'Ext', 'Form')
    helper.makedirs(module_dir, exist_ok=True)
    return module_dir


def _try_extract_form_xml(src_dir: str, obj: CatalogForm, header_data):
    # Attempt to read raw file as XML if present
    try:
        file_name = obj.header['uuid']
    except Exception:
        return None

    for suffix in ['0', '1']:
        path = os.path.join(src_dir, f'{file_name}.{suffix}')
        if not os.path.isfile(path):
            continue
        try:
            with open(path, 'rb') as f:
                chunk = f.read(2048)
            if b'<Form ' in chunk or b'<Form xmlns' in chunk:
                with open(path, 'rb') as f:
                    data = f.read()
                try:
                    return data.decode('utf-8-sig')
                except UnicodeDecodeError:
                    try:
                        return data.decode('windows-1251')
                    except UnicodeDecodeError:
                        return None
        except Exception:
            continue
    return None


def find_last_uuid(value):
    last = ''
    if isinstance(value, str):
        if UUID_RE.fullmatch(value):
            return value
        return ''
    if isinstance(value, list):
        for item in value:
            found = find_last_uuid(item)
            if found:
                last = found
    return last

