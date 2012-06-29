# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
############################################################################
#    Coded by: julio (julio@vauxoo.com)
############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

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
        
#        self.write(cr,uid,ids,{'msg':'No se encontro Referencia %s'%(context.get('ref',False))})
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
        list_prod_qty=data[0].index('price_unit')
        msg=''
        for dat in data[1:]:
            print dat,'dat'
            datas=[]
            data2=list(data[0])
            dat.append(order_id)
            prod_name=dat[list_prod]
            prod_id=self.pool.get('product.product').search(cr,uid,[('name','=',prod_name)],limit=1)

            lines=prod_id and self.pool.get('sale.order.line').product_id_change(cr, uid, [], order.pricelist_id.id,prod_id[0],
                                        qty=0,uom=False, qty_uos=0, uos=False, name='', partner_id=order.partner_id.id,
                                        lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False,).get('value',False) or {}
            print lines,'imrpimo lines'
                                        
            if not lines: msg+='No se encontro Referencia %s \n'% (prod_name)
                                        
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
                else:
#                    print dat[data[0].index(lines.keys()[lin])] 
 #                   print lines[lines.keys()[lin]]
                    if str(dat[data[0].index(lines.keys()[lin])]) <> str(lines[lines.keys()[lin]]):
                        msg+='%s :Configuracion OpenERP %s, CSV %s, En Producto %s \n' % (lines.keys()[lin],lines[lines.keys()[lin]],dat[data[0].index(lines.keys()[lin])],prod_name)
                        dat[data[0].index(lines.keys()[lin])] = lines[lines.keys()[lin]]
            datas.append(dat)
            print data2
            print datas
            lines and self.pool.get('sale.order.line').import_data(cr, uid, data2, datas, 'init', '') or False
            data2=[]
        self.write(cr,uid,ids,{'msg':msg})
        return True
wizard_import()