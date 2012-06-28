import time

from osv import osv, fields
from tools.translate import _
import base64



class wizard_import(osv.osv_memory):
    _name='wizard.import'
    _columns={
        'name' : fields.binary('File')
    }
    
    def send_lines(self,cr,uid,ids,context={}):
        form = self.read(cr,uid,ids,[])
        fdata = base64.decodestring( form[0]['name'] )
        print fdata
        return True
    
    
wizard_import()