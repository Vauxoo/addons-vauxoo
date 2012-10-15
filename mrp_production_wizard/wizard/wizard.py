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
        'move_lines': fields.many2many('stock.move', 'mrp_production_move_ids', 'production_id', 'move_id', 'Consumed Products', domain=[('state','in', ('done', 'cancel'))]),
    }
    
    def sum_qty_products(self,cr,uid,ids,context={}):
        print "testing"
        return True
mrp_production_wizard()