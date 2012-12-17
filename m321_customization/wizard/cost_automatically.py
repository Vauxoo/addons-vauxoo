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


load_cost()
