import time

from osv import osv, fields
from tools.translate import _
import base64

import csv
import cStringIO


class wizard_import(osv.osv_memory):
    _name='wizard.import'
    _columns={
        'name' : fields.binary('File')
    }
    
    def send_lines(self,cr,uid,ids,context={}):
        print context
        order_id=context.get('active_id',False)
        order=self.pool.get('sale.order').browse(cr,uid,order_id)
        form = self.read(cr,uid,ids,[])
        fdata = base64.decodestring( form[0]['name'] )
        input=cStringIO.StringIO(fdata)
        input.seek(0)
        data = list(csv.reader(input, quotechar='"' or '"', delimiter=','))
        data[0].append('order_id.id')
        list_prod=data[0].index('product_id')
        datas=[]
        for dat in data[1:]:
            prod_name=dat[list_prod]
            prod_id=self.pool.get('product.product').search(cr,uid,[('name','=',prod_name)],limit=1)
            
            lines=self.pool.get('sale.order.line').product_id_change(cr, uid, [], order.pricelist_id.id,prod_id[0],
                                        qty=0,uom=False, qty_uos=0, uos=False, name='', partner_id=order.partner_id.id,
                                        lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False,).get('value',False)
            print lines.keys()
            print lines.values()
            dat.append(order_id)
            datas.append(dat)
        print datas,'imprimo datas'
#        self.pool.get('sale.order.line').import_data(cr, uid, data[0], datas, 'init', '')
        return True
    
    
wizard_import()