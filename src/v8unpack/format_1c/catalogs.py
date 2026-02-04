import os
from xml.sax.saxutils import escape

from .. import helper
from .common import _XML_NS, last_uuid_in_meta_header, is_zero_uuid
from .types import build_type_maps
from .catalog_attributes import parse_catalog_attributes, render_catalog_attribute
from .catalog_commands import parse_catalog_commands, render_catalog_command


def export_catalogs(src_dir: str, dest_dir: str):
    src_root = os.path.join(src_dir, 'Catalog')
    if not os.path.isdir(src_root):
        return

    dest_root = os.path.join(dest_dir, 'Catalogs')
    helper.makedirs(dest_root, exist_ok=True)
    type_maps = build_type_maps(src_dir)

    for obj_name in os.listdir(src_root):
        obj_dir = os.path.join(src_root, obj_name)
        if not os.path.isdir(obj_dir):
            continue

        header = helper.json_read(obj_dir, 'Catalog.json')
        data_id = helper.json_read(obj_dir, 'Catalog.id.json')

        name = header.get('name', obj_name)
        synonym = header.get('name2') or {}
        comment = header.get('comment', '')
        uuid = data_id.get('uuid', '')

        arr = header['header'][0][1]
        meta_header = arr[9][1]
        meta_len = len(meta_header)

        gen = catalog_generated_types(arr, name)
        ext_uuid = last_uuid_in_meta_header(meta_header)
        is_extended = bool(ext_uuid) and not is_zero_uuid(ext_uuid)

        has_predefined = os.path.isfile(os.path.join(obj_dir, PREDEFINED_DATA_FILENAME))
        forms = list_catalog_forms(obj_dir)
        attributes = parse_catalog_attributes(header, type_maps)
        commands = parse_catalog_commands(obj_dir)

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

        helper.txt_write(xml_text, dest_root, f'{obj_name}.xml', encoding='utf-8-sig')

        # modules
        export_catalog_module(obj_dir, dest_root, obj_name, 'Catalog.obj.bsl', 'ObjectModule.bsl')
        export_catalog_module(obj_dir, dest_root, obj_name, 'Catalog.mgr.bsl', 'ManagerModule.bsl')


def export_catalog_module(obj_dir: str, dest_root: str, obj_name: str, src_name: str, dest_name: str):
    src_path = os.path.join(obj_dir, src_name)
    if not os.path.isfile(src_path):
        return
    dest_module_dir = os.path.join(dest_root, obj_name, 'Ext')
    helper.makedirs(dest_module_dir, exist_ok=True)
    helper.txt_write(
        helper.txt_read(obj_dir, src_name, encoding='utf-8-sig'),
        dest_module_dir,
        dest_name,
        encoding='utf-8-sig'
    )


PREDEFINED_DATA_FILENAME = (
    '\u041f\u0440\u0435\u0434\u0443\u0441\u0442\u0430\u043d\u043e\u0432\u043b\u0435\u043d\u043d\u044b\u0435 '
    '\u0434\u0430\u043d\u043d\u044b\u0435.bin'
)


def catalog_generated_types(arr, name: str):
    return {
        'Object': (arr[1], arr[2]),
        'Ref': (arr[3], arr[4]),
        'Selection': (arr[5], arr[6]),
        'List': (arr[7], arr[8]),
        'Manager': (arr[34], arr[35]),
        'Name': name
    }


def list_catalog_forms(obj_dir: str):
    forms_dir = os.path.join(obj_dir, 'CatalogForm')
    if not os.path.isdir(forms_dir):
        return []
    result = []
    for form_name in os.listdir(forms_dir):
        if os.path.isdir(os.path.join(forms_dir, form_name)):
            result.append(form_name)
    def sort_key(name: str):
        if name == '\u0424\u043e\u0440\u043c\u0430\u042d\u043b\u0435\u043c\u0435\u043d\u0442\u0430':
            return (0, name)
        if name == '\u0424\u043e\u0440\u043c\u0430\u0421\u043f\u0438\u0441\u043a\u0430':
            return (1, name)
        return (2, name)
    return sorted(result, key=sort_key)


def build_catalog_xml(*, name, uuid, synonym, comment, is_extended, ext_uuid, gen, has_predefined, meta_len, arr, forms,
                      attributes, commands):
    name = escape(name)
    comment_xml = f'<Comment>{escape(comment)}</Comment>' if comment else '<Comment/>'

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<MetaDataObject {_XML_NS}>',
        f'\t<Catalog uuid=\"{escape(uuid)}\">',
        '\t\t<InternalInfo>',
        f'\t\t\t<xr:GeneratedType name=\"CatalogObject.{name}\" category=\"Object\">',
        f'\t\t\t\t<xr:TypeId>{gen["Object"][0]}</xr:TypeId>',
        f'\t\t\t\t<xr:ValueId>{gen["Object"][1]}</xr:ValueId>',
        '\t\t\t</xr:GeneratedType>',
        f'\t\t\t<xr:GeneratedType name=\"CatalogRef.{name}\" category=\"Ref\">',
        f'\t\t\t\t<xr:TypeId>{gen["Ref"][0]}</xr:TypeId>',
        f'\t\t\t\t<xr:ValueId>{gen["Ref"][1]}</xr:ValueId>',
        '\t\t\t</xr:GeneratedType>',
        f'\t\t\t<xr:GeneratedType name=\"CatalogSelection.{name}\" category=\"Selection\">',
        f'\t\t\t\t<xr:TypeId>{gen["Selection"][0]}</xr:TypeId>',
        f'\t\t\t\t<xr:ValueId>{gen["Selection"][1]}</xr:ValueId>',
        '\t\t\t</xr:GeneratedType>',
        f'\t\t\t<xr:GeneratedType name=\"CatalogList.{name}\" category=\"List\">',
        f'\t\t\t\t<xr:TypeId>{gen["List"][0]}</xr:TypeId>',
        f'\t\t\t\t<xr:ValueId>{gen["List"][1]}</xr:ValueId>',
        '\t\t\t</xr:GeneratedType>',
        f'\t\t\t<xr:GeneratedType name=\"CatalogManager.{name}\" category=\"Manager\">',
        f'\t\t\t\t<xr:TypeId>{gen["Manager"][0]}</xr:TypeId>',
        f'\t\t\t\t<xr:ValueId>{gen["Manager"][1]}</xr:ValueId>',
        '\t\t\t</xr:GeneratedType>',
        '\t\t</InternalInfo>',
        '\t\t<Properties>',
    ]

    if is_extended:
        lines.append('\t\t\t<ObjectBelonging>Adopted</ObjectBelonging>')

    lines.append(f'\t\t\t<Name>{name}</Name>')

    if synonym:
        lines.append('\t\t\t<Synonym>')
        for lang, content in synonym.items():
            lines.append('\t\t\t\t<v8:item>')
            lines.append(f'\t\t\t\t\t<v8:lang>{escape(lang)}</v8:lang>')
            lines.append(f'\t\t\t\t\t<v8:content>{escape(content)}</v8:content>')
            lines.append('\t\t\t\t</v8:item>')
        lines.append('\t\t\t</Synonym>')

    lines.append(f'\t\t\t{comment_xml}')

    if is_extended:
        lines.append(f'\t\t\t<ExtendedConfigurationObject>{escape(ext_uuid)}</ExtendedConfigurationObject>')

    if meta_len == 19:
        code_length = arr[11]
        lines.extend([
            '\t\t\t<CodeLength>9</CodeLength>',
            f'\t\t\t<DescriptionLength>{arr[19]}</DescriptionLength>',
            '\t\t\t<CodeType>String</CodeType>',
            f'\t\t\t<CodeAllowedLength>{"Variable" if code_length != "0" else "Fixed"}</CodeAllowedLength>',
            '\t\t\t<CodeSeries>WholeCatalog</CodeSeries>',
            '\t\t\t<CheckUnique>true</CheckUnique>',
            '\t\t\t<Autonumbering>true</Autonumbering>',
            '\t\t\t<DefaultPresentation>AsDescription</DefaultPresentation>',
            '\t\t\t<Hierarchical>false</Hierarchical>',
            '\t\t\t<HierarchyType>HierarchyFoldersAndItems</HierarchyType>',
            '\t\t\t<LimitLevelCount>false</LimitLevelCount>',
            '\t\t\t<LevelCount>2</LevelCount>',
            '\t\t\t<FoldersOnTop>true</FoldersOnTop>',
            '\t\t\t<UseStandardCommands>true</UseStandardCommands>',
            '\t\t\t<Owners/>',
            '\t\t\t<SubordinationUse>ToItems</SubordinationUse>',
        ])
    elif meta_len == 9:
        lines.extend([
            '\t\t\t<Hierarchical>false</Hierarchical>',
            '\t\t\t<HierarchyType>HierarchyFoldersAndItems</HierarchyType>',
            '\t\t\t<LimitLevelCount>false</LimitLevelCount>',
            f'\t\t\t<LevelCount>{arr[10]}</LevelCount>',
            '\t\t\t<FoldersOnTop>true</FoldersOnTop>',
            '\t\t\t<UseStandardCommands>true</UseStandardCommands>',
            '\t\t\t<Owners/>',
            '\t\t\t<SubordinationUse>ToItems</SubordinationUse>',
            f'\t\t\t<CodeLength>{arr[11]}</CodeLength>',
            f'\t\t\t<DescriptionLength>{arr[19]}</DescriptionLength>',
            '\t\t\t<CodeType>String</CodeType>',
            f'\t\t\t<CodeAllowedLength>{"Variable" if arr[11] != "0" else "Fixed"}</CodeAllowedLength>',
            '\t\t\t<CodeSeries>WholeCatalog</CodeSeries>',
            '\t\t\t<CheckUnique>true</CheckUnique>',
            '\t\t\t<Autonumbering>true</Autonumbering>',
            '\t\t\t<DefaultPresentation>AsDescription</DefaultPresentation>',
            STANDARD_ATTRIBUTES_BLOCK,
            '\t\t\t<Characteristics/>',
            '\t\t\t<PredefinedDataUpdate>Auto</PredefinedDataUpdate>',
            '\t\t\t<EditType>InDialog</EditType>',
            '\t\t\t<QuickChoice>false</QuickChoice>',
            '\t\t\t<ChoiceMode>BothWays</ChoiceMode>',
            input_by_string_block(name),
            '\t\t\t<SearchStringModeOnInputByString>Begin</SearchStringModeOnInputByString>',
            '\t\t\t<FullTextSearchOnInputByString>DontUse</FullTextSearchOnInputByString>',
            '\t\t\t<ChoiceDataGetModeOnInputByString>Directly</ChoiceDataGetModeOnInputByString>',
        ])

        default_object_form = ''
        if forms:
            default_object_form = f'Catalog.{name}.Form.{forms[0]}'
        lines.append(f'\t\t\t<DefaultObjectForm>{escape(default_object_form)}</DefaultObjectForm>' if default_object_form else '\t\t\t<DefaultObjectForm/>')
        lines.extend([
            '\t\t\t<DefaultFolderForm/>',
            '\t\t\t<DefaultListForm/>',
            '\t\t\t<DefaultChoiceForm/>',
            '\t\t\t<DefaultFolderChoiceForm/>',
            '\t\t\t<AuxiliaryObjectForm/>',
            '\t\t\t<AuxiliaryFolderForm/>',
            '\t\t\t<AuxiliaryListForm/>',
            '\t\t\t<AuxiliaryChoiceForm/>',
            '\t\t\t<AuxiliaryFolderChoiceForm/>',
            '\t\t\t<IncludeHelpInContents>false</IncludeHelpInContents>',
            '\t\t\t<BasedOn/>',
            '\t\t\t<DataLockFields/>',
            '\t\t\t<DataLockControlMode>Managed</DataLockControlMode>',
            '\t\t\t<FullTextSearch>Use</FullTextSearch>',
            '\t\t\t<ObjectPresentation/>',
            '\t\t\t<ExtendedObjectPresentation/>',
            '\t\t\t<ListPresentation/>',
            '\t\t\t<ExtendedListPresentation/>',
            '\t\t\t<Explanation/>',
            '\t\t\t<CreateOnInput>Use</CreateOnInput>',
            '\t\t\t<ChoiceHistoryOnInput>Auto</ChoiceHistoryOnInput>',
            '\t\t\t<DataHistory>DontUse</DataHistory>',
            '\t\t\t<UpdateDataHistoryImmediatelyAfterWrite>false</UpdateDataHistoryImmediatelyAfterWrite>',
            '\t\t\t<ExecuteAfterWriteDataHistoryVersionProcessing>false</ExecuteAfterWriteDataHistoryVersionProcessing>',
        ])

    lines.append('\t\t</Properties>')

    child_lines = []
    for attr in attributes:
        child_lines.extend(render_catalog_attribute(attr))
    for cmd in commands:
        child_lines.extend(render_catalog_command(cmd))
    for form in forms:
        child_lines.append(f'\t\t\t<Form>{escape(form)}</Form>')

    if child_lines:
        lines.append('\t\t<ChildObjects>')
        lines.extend(child_lines)
        lines.append('\t\t</ChildObjects>')
    else:
        lines.append('\t\t<ChildObjects/>')

    lines.extend([
        '\t</Catalog>',
        '</MetaDataObject>'
    ])

    return '\n'.join(lines)


STANDARD_ATTRIBUTES_BLOCK = (
    '\t\t\t<StandardAttributes>\n'
    '\t\t\t\t<xr:StandardAttribute name="PredefinedDataName">\n'
    '\t\t\t\t\t<xr:LinkByType/>\n'
    '\t\t\t\t\t<xr:FillChecking>DontCheck</xr:FillChecking>\n'
    '\t\t\t\t\t<xr:MultiLine>false</xr:MultiLine>\n'
    '\t\t\t\t\t<xr:FillFromFillingValue>false</xr:FillFromFillingValue>\n'
    '\t\t\t\t\t<xr:CreateOnInput>Auto</xr:CreateOnInput>\n'
    '\t\t\t\t\t<xr:TypeReductionMode>TransformValues</xr:TypeReductionMode>\n'
    '\t\t\t\t\t<xr:MaxValue xsi:nil="true"/>\n'
    '\t\t\t\t\t<xr:ToolTip/>\n'
    '\t\t\t\t\t<xr:ExtendedEdit>false</xr:ExtendedEdit>\n'
    '\t\t\t\t\t<xr:Format/>\n'
    '\t\t\t\t\t<xr:ChoiceForm/>\n'
    '\t\t\t\t\t<xr:QuickChoice>Auto</xr:QuickChoice>\n'
    '\t\t\t\t\t<xr:ChoiceHistoryOnInput>Auto</xr:ChoiceHistoryOnInput>\n'
    '\t\t\t\t\t<xr:EditFormat/>\n'
    '\t\t\t\t\t<xr:PasswordMode>false</xr:PasswordMode>\n'
    '\t\t\t\t\t<xr:DataHistory>Use</xr:DataHistory>\n'
    '\t\t\t\t\t<xr:MarkNegatives>false</xr:MarkNegatives>\n'
    '\t\t\t\t\t<xr:MinValue xsi:nil="true"/>\n'
    '\t\t\t\t\t<xr:Synonym/>\n'
    '\t\t\t\t\t<xr:Comment/>\n'
    '\t\t\t\t\t<xr:FullTextSearch>Use</xr:FullTextSearch>\n'
    '\t\t\t\t\t<xr:ChoiceParameterLinks/>\n'
    '\t\t\t\t\t<xr:FillValue xsi:nil="true"/>\n'
    '\t\t\t\t\t<xr:Mask/>\n'
    '\t\t\t\t\t<xr:ChoiceParameters/>\n'
    '\t\t\t\t</xr:StandardAttribute>\n'
    '\t\t\t\t<xr:StandardAttribute name="Predefined">\n'
    '\t\t\t\t\t<xr:LinkByType/>\n'
    '\t\t\t\t\t<xr:FillChecking>DontCheck</xr:FillChecking>\n'
    '\t\t\t\t\t<xr:MultiLine>false</xr:MultiLine>\n'
    '\t\t\t\t\t<xr:FillFromFillingValue>false</xr:FillFromFillingValue>\n'
    '\t\t\t\t\t<xr:CreateOnInput>Auto</xr:CreateOnInput>\n'
    '\t\t\t\t\t<xr:TypeReductionMode>TransformValues</xr:TypeReductionMode>\n'
    '\t\t\t\t\t<xr:MaxValue xsi:nil="true"/>\n'
    '\t\t\t\t\t<xr:ToolTip/>\n'
    '\t\t\t\t\t<xr:ExtendedEdit>false</xr:ExtendedEdit>\n'
    '\t\t\t\t\t<xr:Format/>\n'
    '\t\t\t\t\t<xr:ChoiceForm/>\n'
    '\t\t\t\t\t<xr:QuickChoice>Auto</xr:QuickChoice>\n'
    '\t\t\t\t\t<xr:ChoiceHistoryOnInput>Auto</xr:ChoiceHistoryOnInput>\n'
    '\t\t\t\t\t<xr:EditFormat/>\n'
    '\t\t\t\t\t<xr:PasswordMode>false</xr:PasswordMode>\n'
    '\t\t\t\t\t<xr:DataHistory>Use</xr:DataHistory>\n'
    '\t\t\t\t\t<xr:MarkNegatives>false</xr:MarkNegatives>\n'
    '\t\t\t\t\t<xr:MinValue xsi:nil="true"/>\n'
    '\t\t\t\t\t<xr:Synonym/>\n'
    '\t\t\t\t\t<xr:Comment/>\n'
    '\t\t\t\t\t<xr:FullTextSearch>Use</xr:FullTextSearch>\n'
    '\t\t\t\t\t<xr:ChoiceParameterLinks/>\n'
    '\t\t\t\t\t<xr:FillValue xsi:nil="true"/>\n'
    '\t\t\t\t\t<xr:Mask/>\n'
    '\t\t\t\t\t<xr:ChoiceParameters/>\n'
    '\t\t\t\t</xr:StandardAttribute>\n'
    '\t\t\t\t<xr:StandardAttribute name="Ref">\n'
    '\t\t\t\t\t<xr:LinkByType/>\n'
    '\t\t\t\t\t<xr:FillChecking>DontCheck</xr:FillChecking>\n'
    '\t\t\t\t\t<xr:MultiLine>false</xr:MultiLine>\n'
    '\t\t\t\t\t<xr:FillFromFillingValue>false</xr:FillFromFillingValue>\n'
    '\t\t\t\t\t<xr:CreateOnInput>Auto</xr:CreateOnInput>\n'
    '\t\t\t\t\t<xr:TypeReductionMode>TransformValues</xr:TypeReductionMode>\n'
    '\t\t\t\t\t<xr:MaxValue xsi:nil="true"/>\n'
    '\t\t\t\t\t<xr:ToolTip/>\n'
    '\t\t\t\t\t<xr:ExtendedEdit>false</xr:ExtendedEdit>\n'
    '\t\t\t\t\t<xr:Format/>\n'
    '\t\t\t\t\t<xr:ChoiceForm/>\n'
    '\t\t\t\t\t<xr:QuickChoice>Auto</xr:QuickChoice>\n'
    '\t\t\t\t\t<xr:ChoiceHistoryOnInput>Auto</xr:ChoiceHistoryOnInput>\n'
    '\t\t\t\t\t<xr:EditFormat/>\n'
    '\t\t\t\t\t<xr:PasswordMode>false</xr:PasswordMode>\n'
    '\t\t\t\t\t<xr:DataHistory>Use</xr:DataHistory>\n'
    '\t\t\t\t\t<xr:MarkNegatives>false</xr:MarkNegatives>\n'
    '\t\t\t\t\t<xr:MinValue xsi:nil="true"/>\n'
    '\t\t\t\t\t<xr:Synonym/>\n'
    '\t\t\t\t\t<xr:Comment/>\n'
    '\t\t\t\t\t<xr:FullTextSearch>Use</xr:FullTextSearch>\n'
    '\t\t\t\t\t<xr:ChoiceParameterLinks/>\n'
    '\t\t\t\t\t<xr:FillValue xsi:nil="true"/>\n'
    '\t\t\t\t\t<xr:Mask/>\n'
    '\t\t\t\t\t<xr:ChoiceParameters/>\n'
    '\t\t\t\t</xr:StandardAttribute>\n'
    '\t\t\t\t<xr:StandardAttribute name="DeletionMark">\n'
    '\t\t\t\t\t<xr:LinkByType/>\n'
    '\t\t\t\t\t<xr:FillChecking>DontCheck</xr:FillChecking>\n'
    '\t\t\t\t\t<xr:MultiLine>false</xr:MultiLine>\n'
    '\t\t\t\t\t<xr:FillFromFillingValue>false</xr:FillFromFillingValue>\n'
    '\t\t\t\t\t<xr:CreateOnInput>Auto</xr:CreateOnInput>\n'
    '\t\t\t\t\t<xr:TypeReductionMode>TransformValues</xr:TypeReductionMode>\n'
    '\t\t\t\t\t<xr:MaxValue xsi:nil="true"/>\n'
    '\t\t\t\t\t<xr:ToolTip/>\n'
    '\t\t\t\t\t<xr:ExtendedEdit>false</xr:ExtendedEdit>\n'
    '\t\t\t\t\t<xr:Format/>\n'
    '\t\t\t\t\t<xr:ChoiceForm/>\n'
    '\t\t\t\t\t<xr:QuickChoice>Auto</xr:QuickChoice>\n'
    '\t\t\t\t\t<xr:ChoiceHistoryOnInput>Auto</xr:ChoiceHistoryOnInput>\n'
    '\t\t\t\t\t<xr:EditFormat/>\n'
    '\t\t\t\t\t<xr:PasswordMode>false</xr:PasswordMode>\n'
    '\t\t\t\t\t<xr:DataHistory>Use</xr:DataHistory>\n'
    '\t\t\t\t\t<xr:MarkNegatives>false</xr:MarkNegatives>\n'
    '\t\t\t\t\t<xr:MinValue xsi:nil="true"/>\n'
    '\t\t\t\t\t<xr:Synonym/>\n'
    '\t\t\t\t\t<xr:Comment/>\n'
    '\t\t\t\t\t<xr:FullTextSearch>Use</xr:FullTextSearch>\n'
    '\t\t\t\t\t<xr:ChoiceParameterLinks/>\n'
    '\t\t\t\t\t<xr:FillValue xsi:nil="true"/>\n'
    '\t\t\t\t\t<xr:Mask/>\n'
    '\t\t\t\t\t<xr:ChoiceParameters/>\n'
    '\t\t\t\t</xr:StandardAttribute>\n'
    '\t\t\t\t<xr:StandardAttribute name="IsFolder">\n'
    '\t\t\t\t\t<xr:LinkByType/>\n'
    '\t\t\t\t\t<xr:FillChecking>DontCheck</xr:FillChecking>\n'
    '\t\t\t\t\t<xr:MultiLine>false</xr:MultiLine>\n'
    '\t\t\t\t\t<xr:FillFromFillingValue>false</xr:FillFromFillingValue>\n'
    '\t\t\t\t\t<xr:CreateOnInput>Auto</xr:CreateOnInput>\n'
    '\t\t\t\t\t<xr:TypeReductionMode>TransformValues</xr:TypeReductionMode>\n'
    '\t\t\t\t\t<xr:MaxValue xsi:nil="true"/>\n'
    '\t\t\t\t\t<xr:ToolTip/>\n'
    '\t\t\t\t\t<xr:ExtendedEdit>false</xr:ExtendedEdit>\n'
    '\t\t\t\t\t<xr:Format/>\n'
    '\t\t\t\t\t<xr:ChoiceForm/>\n'
    '\t\t\t\t\t<xr:QuickChoice>Auto</xr:QuickChoice>\n'
    '\t\t\t\t\t<xr:ChoiceHistoryOnInput>Auto</xr:ChoiceHistoryOnInput>\n'
    '\t\t\t\t\t<xr:EditFormat/>\n'
    '\t\t\t\t\t<xr:PasswordMode>false</xr:PasswordMode>\n'
    '\t\t\t\t\t<xr:DataHistory>Use</xr:DataHistory>\n'
    '\t\t\t\t\t<xr:MarkNegatives>false</xr:MarkNegatives>\n'
    '\t\t\t\t\t<xr:MinValue xsi:nil="true"/>\n'
    '\t\t\t\t\t<xr:Synonym/>\n'
    '\t\t\t\t\t<xr:Comment/>\n'
    '\t\t\t\t\t<xr:FullTextSearch>Use</xr:FullTextSearch>\n'
    '\t\t\t\t\t<xr:ChoiceParameterLinks/>\n'
    '\t\t\t\t\t<xr:FillValue xsi:nil="true"/>\n'
    '\t\t\t\t\t<xr:Mask/>\n'
    '\t\t\t\t\t<xr:ChoiceParameters/>\n'
    '\t\t\t\t</xr:StandardAttribute>\n'
    '\t\t\t\t<xr:StandardAttribute name="Owner">\n'
    '\t\t\t\t\t<xr:LinkByType/>\n'
    '\t\t\t\t\t<xr:FillChecking>ShowError</xr:FillChecking>\n'
    '\t\t\t\t\t<xr:MultiLine>false</xr:MultiLine>\n'
    '\t\t\t\t\t<xr:FillFromFillingValue>true</xr:FillFromFillingValue>\n'
    '\t\t\t\t\t<xr:CreateOnInput>Auto</xr:CreateOnInput>\n'
    '\t\t\t\t\t<xr:TypeReductionMode>Deny</xr:TypeReductionMode>\n'
    '\t\t\t\t\t<xr:MaxValue xsi:nil="true"/>\n'
    '\t\t\t\t\t<xr:ToolTip/>\n'
    '\t\t\t\t\t<xr:ExtendedEdit>false</xr:ExtendedEdit>\n'
    '\t\t\t\t\t<xr:Format/>\n'
    '\t\t\t\t\t<xr:ChoiceForm/>\n'
    '\t\t\t\t\t<xr:QuickChoice>Auto</xr:QuickChoice>\n'
    '\t\t\t\t\t<xr:ChoiceHistoryOnInput>Auto</xr:ChoiceHistoryOnInput>\n'
    '\t\t\t\t\t<xr:EditFormat/>\n'
    '\t\t\t\t\t<xr:PasswordMode>false</xr:PasswordMode>\n'
    '\t\t\t\t\t<xr:DataHistory>Use</xr:DataHistory>\n'
    '\t\t\t\t\t<xr:MarkNegatives>false</xr:MarkNegatives>\n'
    '\t\t\t\t\t<xr:MinValue xsi:nil="true"/>\n'
    '\t\t\t\t\t<xr:Synonym/>\n'
    '\t\t\t\t\t<xr:Comment/>\n'
    '\t\t\t\t\t<xr:FullTextSearch>Use</xr:FullTextSearch>\n'
    '\t\t\t\t\t<xr:ChoiceParameterLinks/>\n'
    '\t\t\t\t\t<xr:FillValue xsi:nil="true"/>\n'
    '\t\t\t\t\t<xr:Mask/>\n'
    '\t\t\t\t\t<xr:ChoiceParameters/>\n'
    '\t\t\t\t</xr:StandardAttribute>\n'
    '\t\t\t\t<xr:StandardAttribute name="Parent">\n'
    '\t\t\t\t\t<xr:LinkByType/>\n'
    '\t\t\t\t\t<xr:FillChecking>DontCheck</xr:FillChecking>\n'
    '\t\t\t\t\t<xr:MultiLine>false</xr:MultiLine>\n'
    '\t\t\t\t\t<xr:FillFromFillingValue>true</xr:FillFromFillingValue>\n'
    '\t\t\t\t\t<xr:CreateOnInput>Auto</xr:CreateOnInput>\n'
    '\t\t\t\t\t<xr:TypeReductionMode>TransformValues</xr:TypeReductionMode>\n'
    '\t\t\t\t\t<xr:MaxValue xsi:nil="true"/>\n'
    '\t\t\t\t\t<xr:ToolTip/>\n'
    '\t\t\t\t\t<xr:ExtendedEdit>false</xr:ExtendedEdit>\n'
    '\t\t\t\t\t<xr:Format/>\n'
    '\t\t\t\t\t<xr:ChoiceForm/>\n'
    '\t\t\t\t\t<xr:QuickChoice>Auto</xr:QuickChoice>\n'
    '\t\t\t\t\t<xr:ChoiceHistoryOnInput>Auto</xr:ChoiceHistoryOnInput>\n'
    '\t\t\t\t\t<xr:EditFormat/>\n'
    '\t\t\t\t\t<xr:PasswordMode>false</xr:PasswordMode>\n'
    '\t\t\t\t\t<xr:DataHistory>Use</xr:DataHistory>\n'
    '\t\t\t\t\t<xr:MarkNegatives>false</xr:MarkNegatives>\n'
    '\t\t\t\t\t<xr:MinValue xsi:nil="true"/>\n'
    '\t\t\t\t\t<xr:Synonym/>\n'
    '\t\t\t\t\t<xr:Comment/>\n'
    '\t\t\t\t\t<xr:FullTextSearch>Use</xr:FullTextSearch>\n'
    '\t\t\t\t\t<xr:ChoiceParameterLinks/>\n'
    '\t\t\t\t\t<xr:FillValue xsi:nil="true"/>\n'
    '\t\t\t\t\t<xr:Mask/>\n'
    '\t\t\t\t\t<xr:ChoiceParameters/>\n'
    '\t\t\t\t</xr:StandardAttribute>\n'
    '\t\t\t\t<xr:StandardAttribute name="Description">\n'
    '\t\t\t\t\t<xr:LinkByType/>\n'
    '\t\t\t\t\t<xr:FillChecking>ShowError</xr:FillChecking>\n'
    '\t\t\t\t\t<xr:MultiLine>false</xr:MultiLine>\n'
    '\t\t\t\t\t<xr:FillFromFillingValue>false</xr:FillFromFillingValue>\n'
    '\t\t\t\t\t<xr:CreateOnInput>Auto</xr:CreateOnInput>\n'
    '\t\t\t\t\t<xr:TypeReductionMode>TransformValues</xr:TypeReductionMode>\n'
    '\t\t\t\t\t<xr:MaxValue xsi:nil="true"/>\n'
    '\t\t\t\t\t<xr:ToolTip/>\n'
    '\t\t\t\t\t<xr:ExtendedEdit>false</xr:ExtendedEdit>\n'
    '\t\t\t\t\t<xr:Format/>\n'
    '\t\t\t\t\t<xr:ChoiceForm/>\n'
    '\t\t\t\t\t<xr:QuickChoice>Auto</xr:QuickChoice>\n'
    '\t\t\t\t\t<xr:ChoiceHistoryOnInput>Auto</xr:ChoiceHistoryOnInput>\n'
    '\t\t\t\t\t<xr:EditFormat/>\n'
    '\t\t\t\t\t<xr:PasswordMode>false</xr:PasswordMode>\n'
    '\t\t\t\t\t<xr:DataHistory>Use</xr:DataHistory>\n'
    '\t\t\t\t\t<xr:MarkNegatives>false</xr:MarkNegatives>\n'
    '\t\t\t\t\t<xr:MinValue xsi:nil="true"/>\n'
    '\t\t\t\t\t<xr:Synonym/>\n'
    '\t\t\t\t\t<xr:Comment/>\n'
    '\t\t\t\t\t<xr:FullTextSearch>Use</xr:FullTextSearch>\n'
    '\t\t\t\t\t<xr:ChoiceParameterLinks/>\n'
    '\t\t\t\t\t<xr:FillValue xsi:nil="true"/>\n'
    '\t\t\t\t\t<xr:Mask/>\n'
    '\t\t\t\t\t<xr:ChoiceParameters/>\n'
    '\t\t\t\t</xr:StandardAttribute>\n'
    '\t\t\t\t<xr:StandardAttribute name="Code">\n'
    '\t\t\t\t\t<xr:LinkByType/>\n'
    '\t\t\t\t\t<xr:FillChecking>DontCheck</xr:FillChecking>\n'
    '\t\t\t\t\t<xr:MultiLine>false</xr:MultiLine>\n'
    '\t\t\t\t\t<xr:FillFromFillingValue>false</xr:FillFromFillingValue>\n'
    '\t\t\t\t\t<xr:CreateOnInput>Auto</xr:CreateOnInput>\n'
    '\t\t\t\t\t<xr:TypeReductionMode>TransformValues</xr:TypeReductionMode>\n'
    '\t\t\t\t\t<xr:MaxValue xsi:nil="true"/>\n'
    '\t\t\t\t\t<xr:ToolTip/>\n'
    '\t\t\t\t\t<xr:ExtendedEdit>false</xr:ExtendedEdit>\n'
    '\t\t\t\t\t<xr:Format/>\n'
    '\t\t\t\t\t<xr:ChoiceForm/>\n'
    '\t\t\t\t\t<xr:QuickChoice>Auto</xr:QuickChoice>\n'
    '\t\t\t\t\t<xr:ChoiceHistoryOnInput>Auto</xr:ChoiceHistoryOnInput>\n'
    '\t\t\t\t\t<xr:EditFormat/>\n'
    '\t\t\t\t\t<xr:PasswordMode>false</xr:PasswordMode>\n'
    '\t\t\t\t\t<xr:DataHistory>Use</xr:DataHistory>\n'
    '\t\t\t\t\t<xr:MarkNegatives>false</xr:MarkNegatives>\n'
    '\t\t\t\t\t<xr:MinValue xsi:nil="true"/>\n'
    '\t\t\t\t\t<xr:Synonym/>\n'
    '\t\t\t\t\t<xr:Comment/>\n'
    '\t\t\t\t\t<xr:FullTextSearch>Use</xr:FullTextSearch>\n'
    '\t\t\t\t\t<xr:ChoiceParameterLinks/>\n'
    '\t\t\t\t\t<xr:FillValue xsi:nil="true"/>\n'
    '\t\t\t\t\t<xr:Mask/>\n'
    '\t\t\t\t\t<xr:ChoiceParameters/>\n'
    '\t\t\t\t</xr:StandardAttribute>\n'
    '\t\t\t</StandardAttributes>'
)


def input_by_string_block(name: str) -> str:
    return (
        '\t\t\t<InputByString>\n'
        f'\t\t\t\t<xr:Field>Catalog.{escape(name)}.StandardAttribute.Description</xr:Field>\n'
        f'\t\t\t\t<xr:Field>Catalog.{escape(name)}.StandardAttribute.Code</xr:Field>\n'
        '\t\t\t</InputByString>'
    )

