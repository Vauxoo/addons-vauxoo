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
import decimal_precision as dp

class mrp_consume(osv.osv_memory):
    _name='mrp.consume'
    _columns={
        'consume_line_ids' : fields.one2many('mrp.consume.line','wizard_id','Consume')
    }
mrp_consume()

class mrp_consume_line(osv.osv_memory):
    _name='mrp.consume.line'
    _rec_name = 'product_id'
    _columns = {
        'product_id' : fields.many2one('product.product', string="Product", required=True),
        'quantity' : fields.float("Quantity", digits_compute=dp.get_precision('Product UoM'), required=True),
        'product_uom': fields.many2one('product.uom', 'Unit of Measure', required=True,),
        'location_id': fields.many2one('stock.location', 'Location', required=True),
        'location_dest_id': fields.many2one('stock.location', 'Dest. Location', required=True),
        'wizard_id' : fields.many2one('mrp.consume', string="Wizard"),
    }

mrp_consume_line()
