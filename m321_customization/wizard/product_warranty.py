# -*- encoding: utf-8 -*-
############################################################################
#    Module Writen to OpenERP, Open Source Management Solution             #
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).            #
#    All Rights Reserved                                                   #
###############Credits######################################################
#    Coded by: author Miguel Delgado <miguel@openerp.com.ve>               #
#    Planified by: Nhomar Hernandez                                        #
#    Audited by: Humberto Arocha humberto@openerp.com.ve                   #
############################################################################
#    This program is free software: you can redistribute it and/or modify  #
#    it under the terms of the GNU General Public License as published by  #
#    the Free Software Foundation, either version 3 of the License, or     #
#    (at your option) any later version.                                   #
#                                                                          #
#    This program is distributed in the hope that it will be useful,       #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of        #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         #
#    GNU General Public License for more details.                          #
#                                                                          #
#    You should have received a copy of the GNU General Public License     #
#    along with this program.  If not, see <http://www.gnu.org/licenses/>. #
############################################################################

from osv import osv,fields
import pooler
import time

class product_warranty(osv.osv_memory):
    _name = "product.warranty"
    
    
    
    _columns = {
        'name':fields.char('Month Number', 5, help='Month number to warranty'), 
        'clean':fields.boolean('Clean name', help='Select if you wish to remove warranty in the product name'), 
        
        
    }

    def warranty_execute(self, cr, uid, ids, context=None):

        if context is None:
            context = {}
        
        product_obj = self.pool.get('product.product')
        wzr_brw = self.browse(cr, uid,ids, context=context)[0]
        
        if context.get('active_ids',False):
 
            if wzr_brw.clean:
                for product in product_obj.browse(cr, uid, context.get('active_ids',False), context=context):
                    name = product.name
                    name = name.find('Garantia') > 0 and name[:name.find('Garantia')].strip() or name
                    product_obj.write(cr, uid, [product.id], {'name':'%s' % (name)}, context=context)

            else:

                for product in product_obj.browse(cr, uid, context.get('active_ids',False), context=context):
                    name = product.name
                    name = name.find('Garantia') > 0 and name[:name.find('Garantia')].strip() or name
                    product_obj.write(cr, uid, [product.id], {'warranty':float(wzr_brw.name),
                                                              'name':'%s Garantia %s Meses' % (name,wzr_brw.name)}, context=context)
            
            
        return {'type': 'ir.actions.act_window_close'}
    

product_warranty()





