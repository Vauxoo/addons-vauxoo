#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Vauxoo C.A.           
#    Planified by: Nhomar Hernandez
#    Audited by: Vauxoo C.A.
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
################################################################################

from osv import fields, osv
from tools.translate import _
import base64
import xlrd
from xlrd import open_workbook
import xlwt
import os
class load_cost(osv.osv_memory):

    
    _name = 'load.cost'
    _columns = {
       'cost_file' : fields.binary('File XLS',requered=True, help="XLS with costt to create"),
       'update_cost':fields.boolean('Update Cost', help='Select if wish update cost structure'), 
       'update_price_list':fields.boolean('Update Price List', help='Select if wish update price list'), 
       
       
    }

    def xls_file(self,cr,uid,ids,context={}):
        wz_brw = self.browse(cr,uid,ids,context=context)[0]
        archivo = open("/tmp/load_cost.xls","w")
        product_obj = self.pool.get('product.product')
        cost_obj = self.pool.get('cost.structure')
        archivo.write(base64.b64decode(wz_brw \
                                       and wz_brw.cost_file \
                                       or 'Archivo Invalido'))
        archivo.close()
        if archivo:
            file = open_workbook('/tmp/load_cost.xls')
            sheet = file.sheet_by_index(0)
            for ind in range(sheet.nrows):
                value = sheet.row_values(ind)
                product_ids = product_obj.search(cr, uid,
                              [('default_code','=',value[0].strip())], context=context)
                if product_ids:
                    product_brw = product_obj.browse(cr, uid,
                                                     product_ids[0],
                                                     context=context)
                    if not product_brw.property_cost_structure:
                        cost_id = cost_obj.create(cr, uid,
                                                   {'type':'v',
                                                    'description':product_brw.name,
                                                    'cost_ult':value[1]},
                                                    context=context)
                        
                        product_obj.write(cr, uid,[product_brw.id],
                                               {'property_cost_structure':cost_id},
                                                  context=context)

                    else:
                        cost_obj.write(cr, uid,
                                [product_brw.property_cost_structure.id],
                                       {'cost_ult':value[1]}, context=context)

        try:        
            os.popen('rm /tmp/load_cost.xls') 
        except:
            pass
        
        return True





    
    
    def update_price_list(self,cr,uid,ids,context={}):
        wz_brw = self.browse(cr,uid,ids,context=context)[0]
        archivo = open("/tmp/load_cost.xls","w")
        product_obj = self.pool.get('product.product')
        cost_obj = self.pool.get('cost.structure')
        item_obj = self.pool.get('product.pricelist.item')
        version_obj = self.pool.get('product.pricelist.version')
        price_obj = self.pool.get('product.pricelist.version')
        archivo.write(base64.b64decode(wz_brw \
                                       and wz_brw.cost_file \
                                       or 'Archivo Invalido'))
        archivo.close()
        if archivo:
            file = open_workbook('/tmp/load_cost.xls')
            sheet = file.sheet_by_index(0)
            for ind in range(sheet.nrows):
                value = sheet.row_values(ind)
                product_ids = product_obj.search(cr, uid,
                              [('default_code','=',value[0].strip())],
                              context=context)
                if product_ids:
                    product_brw = product_obj.browse(cr, uid,
                                                     product_ids[0],
                                                     context=context)
                    if not product_brw.property_cost_structure:
                        cost_id = cost_obj.create(cr, uid,
                                                   {'type':'v',
                                                'description':product_brw.name,
                                                    'cost_ult':value[1]},
                                                    context=context)
                        
                        product_obj.write(cr, uid,[product_brw.id],
                                           {'property_cost_structure':cost_id},
                                                  context=context)

                    else:
                        cost_obj.write(cr, uid,
                                [product_brw.property_cost_structure.id],
                                       {'cost_ult':value[1]}, context=context)
                    name = 6 
                    
                    for price in range(1,6):
                        version_ids = version_obj.search(cr,
                                                        uid,
                                [('pricelist_id.name','=','Precio %s' % price)],
                                context=context)

                        if version_ids:
                            items_ids = item_obj.search(cr,
                                    uid,
                                    [('product_id','=',product_ids[0]),
                                     ('price_version_id','=',version_ids[0])],
                                    context=context)
                           
                            items_ids \
                            and item_obj.write(cr, uid,
                                              items_ids,
                                              {'price_discount':value[name],
                                               'sequence':1,
                                               'base':2,
                                                  },
                                              context=context) \
                            or item_obj.create(cr, uid,
                                    {'product_id':product_ids[0],
                                     'price_version_id':version_ids[0],
                                     'price_discount':value[name],
                                     'base':2,
                                     'sequence':1,
                                     'name':product_brw.name},
                                    context=context)
                            

                        name-=1
                
        try:        
            os.popen('rm /tmp/load_cost.xls') 
        except:
            pass
        
        return True


load_cost()
