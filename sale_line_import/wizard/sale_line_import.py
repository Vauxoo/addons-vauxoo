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
        'msg' : fields.text('Mensajes',readonly=True)
    }
    def send_lines(self,cr,uid,ids,context={}):
        order_id=context.get('active_id',False)
        order=self.pool.get('sale.order').browse(cr,uid,order_id)
        form = self.read(cr,uid,ids,[])
        fdata = form and base64.decodestring( form[0]['name'] ) or False
        input=cStringIO.StringIO(fdata)
        input.seek(0)
        data = list(csv.reader(input, quotechar='"' or '"', delimiter=','))
        data[0].append('order_id.id')
        list_prod=data[0].index('product_id')
        msg=''
        for dat in data[1:]:
            datas=[]
            data2=list(data[0])
            dat.append(order_id)
            prod_name=dat[list_prod]
            prod_name_search=self.pool.get('product.product').name_search(cr,uid,prod_name)
            prod_id = prod_name_search and prod_name_search[0][0] or False
            lines=prod_id and self.pool.get('sale.order.line').product_id_change(cr, uid, [], order.pricelist_id.id,prod_id,
                                        qty=0,uom=False, qty_uos=0, uos=False, name='', partner_id=order.partner_id.id,
                                        lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False,).get('value',False) or {}
            if not lines: msg+='No Se Encontro Referencia: %s \n'% (prod_name)
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
                    val_str=dat[data[0].index(lines.keys()[lin])]
                    val_str_2=lines[lines.keys()[lin]]
                    if lines.keys()[lin]=='product_uom':
                        val_str_2=self.pool.get('product.uom').browse(cr,uid,val_str_2).name
                    if lines.keys()[lin]=='price_unit':
                        val_str=float(dat[data[0].index(lines.keys()[lin])])
                        val_str_2=float(lines[lines.keys()[lin]])
                    if val_str <> val_str_2:
                        msg+='%s :Configuracion OpenERP %s, CSV %s, En Producto %s \n' % (lines.keys()[lin],lines[lines.keys()[lin]],dat[data[0].index(lines.keys()[lin])],prod_name)
                        dat[data[0].index(lines.keys()[lin])] = val_str_2
            datas.append(dat)
            try:
                lines and self.pool.get('sale.order.line').import_data(cr, uid, data2, datas, 'init', '') or False
            except Exception, e:
                return False
            data2=[]
        if msg:
            self.write(cr,uid,ids,{'msg':msg})
            return True
        else:
            return {}
wizard_import()