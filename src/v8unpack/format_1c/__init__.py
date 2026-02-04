import os

from .. import helper
from ..ext_exception import ExtException
from .common_modules import export_common_modules
from .catalogs import export_catalogs


def export_1c_format(src_dir: str, dest_dir: str):
    try:
        helper.clear_dir(dest_dir)
        export_common_modules(src_dir, dest_dir)
        export_catalogs(src_dir, dest_dir)
    except Exception as err:
        raise ExtException(parent=err, message='?????? ???????? ? ?????? 1?')
