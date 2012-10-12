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

from tools.translate import _
from osv import osv, fields
import decimal_precision as dp

class mrp_production_product_line(osv.osv):
    _inherit = "mrp.production.product.line"
    
    _columns = {
        
    }
    
    def onchange_product_scheduled_line(self, cr, uid, ids, product_id):
        if product_id:
            new_product_id = [product_id]
            product_product_obj = self.pool.get('product.product')
            product_product_data = product_product_obj.browse(cr, uid, new_product_id, context=None)
            for line in product_product_data:
                val = {'name' : line.name, 'product_uom' : line.uom_id.id, 'product_qty' : 1}
                domain_uom = {'product_uom':[('category_id', '=', line.uom_id.category_id.id)]}
                return {'value': val, 'domain': domain_uom}
        return {}

mrp_production_product_line()