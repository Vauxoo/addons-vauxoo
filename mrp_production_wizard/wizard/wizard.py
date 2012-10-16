# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
############################################################################
#    Coded by: fernandoL (fernando_ld@vauxoo.com)
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
import decimal_precision as dp
from tools.translate import _

class mrp_production_wizard(osv.osv_memory):
    _name='mrp.production.wizard'
    _columns={
        'product_id': fields.many2one('product.product', 'Product', required=True, ),
        'wiz_data': fields.one2many('wizard.data', 'mrp_production_wiz', 'Prod lines'),
    }
    
    def pass_products_to_parent(self,cr,uid,ids,context={}):
        if not context:
            context={}
        form=self.read(cr,uid,ids,[])
        product = form and form[0]['product_id'] or []
        print product, " = product"
        wizard_data_data = self.browse(cr, uid, ids, context=context)
        for line in wizard_data_data:
            for move in line.wiz_data:
                print move.product_id_consume.id, " = product id"
        return True
    
mrp_production_wizard()

class wizard_data(osv.osv_memory):
    _name='wizard.data'
    
    _columns={
        'mrp_production_wiz': fields.many2one('mrp.production.wizard', 'Padre'),
        'product_id_consume': fields.many2one('product.product', 'Product', required=True),
        'product_qty': fields.float('Product Qty', required=True),
        'product_uom': fields.many2one('product.uom', 'Product UOM', required=True),
    }

wizard_data()