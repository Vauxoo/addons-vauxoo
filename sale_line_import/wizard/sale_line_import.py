import time

from osv import osv, fields
from tools.translate import _



class wizard_import(osv.osv_memory):
    _name='wizard.import'
    _columns={
        'name' : fields.binary('File')
    }

wizard_import()