import time

from osv import osv, fields
from tools.translate import _
import base64

import csv
import cStringIO


class wizard_import(osv.osv_memory):
    _name='wizard.import'
    _columns={
        'name' : fields.binary('File'),
        'msg' : fields.text('Mensajes')
    }
    def send_error(self,cr,uid,ids,context={}):
        print 'error'
        return {}
    
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

        for dat in data[1:]:
            datas=[]
            data2=list(data[0])
            dat.append(order_id)
            prod_name=dat[list_prod]
            prod_id=self.pool.get('product.product').search(cr,uid,[('name','=',prod_name)],limit=1)

            lines=prod_id and self.pool.get('sale.order.line').product_id_change(cr, uid, [], order.pricelist_id.id,prod_id[0],
                                        qty=0,uom=False, qty_uos=0, uos=False, name='', partner_id=order.partner_id.id,
                                        lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False,).get('value',False) or self.send_error(cr,uid,ids,context={})
                                        
            for lin in range(len(lines.keys())):
                if lines.keys()[lin] not in data[0]:
                    if lines.keys()[lin] in ('tax_id','product_uom','product_packaging'):
                        field_val=str(lines.keys()[lin])
                        field_val=field_val+'.id'
                        data2.append(field_val)
                        vals_many =str( lines[lines.keys()[lin]] ).replace('[','').replace(']','').replace('False','')
                        dat.append( vals_many )
                    else:
                        data2.append(lines.keys()[lin])
                        dat.append(lines[lines.keys()[lin]])
            datas.append(dat)
            print data2
            print datas
            lines and self.pool.get('sale.order.line').import_data(cr, uid, data2, datas, 'init', '') or False
            data2=[]
        return True
wizard_import()