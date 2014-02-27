# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
# Credits######################################################
#    Coded by: javieredm@gmail.com,
#    Planified by: Nhomar Hernandez
#    Finance by: Helados Gilda, C.A. http://heladosgilda.com.ve
#    Audited by: Humberto Arocha humberto@openerp.com.ve
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##############################################################################

import time
import openerp.netsvc as netsvc
from openerp.osv import osv, fields
from mx import DateTime
from openerp.tools.translate import _


class sale_uom_group(osv.Model):
    _name = "sale.uom.group"
    _description = "Sum by Product Uom"
    _columns = {
        'sale_id': fields.many2one('sale.order', 'Sale order',
                                   ondelete='cascade', select=True),
        'name': fields.char('Uom Description', size=64),
        'product_uom': fields.many2one('product.uom', 'Product UoM',
                                       required=True, readonly=True,
                                       states={'draft': [('readonly', False)]
                                               }),
        'amount': fields.float('Amount', digits=(16, 2)),
    }

    def compute(self, cr, uid, sale_id, context={}):
        uom_grouped = {}
        sale_brw = self.pool.get('sale.order').browse(
            cr, uid, sale_id, context)
        res = {}
        for line in sale_brw.order_line:
            res.setdefault(line.product_uom.id, 0.0)
            res[line.product_uom.id] += line.product_uom_qty

        for uom in res.keys():
            uom_grouped[uom] = {
                'sale_id': sale_brw.id,
                'product_uom': uom,
                'amount': res[uom]
            }

        return uom_grouped


class sale_order(osv.Model):
    _inherit = 'sale.order'
    _columns = {
        'puom_line': fields.one2many('sale.uom.group', 'sale_id',
                                     'UOM Lines', readonly=True),
    }

    def button_reset_uom(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        sug_obj = self.pool.get('sale.uom.group')
        for id in ids:
            cr.execute("DELETE FROM sale_uom_group WHERE sale_id=%s", (id,))
            for uom in sug_obj.compute(cr, uid, id, context=context).values():
                sug_obj.create(cr, uid, uom)

        return True

    def button_compute(self, cr, uid, ids, context=None):
        self.button_reset_uom(cr, uid, ids, context)
        return True

    def create(self, cr, uid, vals, context={}):
        sale_id = super(sale_order, self).create(cr, uid, vals, context)
        if 'order_line' in vals and vals['order_line']:
            self.button_compute(cr, uid, [sale_id])

        return sale_id

    def write(self, cr, uid, ids, vals, context=None):
        res = super(sale_order, self).write(cr, uid, ids, vals, context)
        if 'order_line' in vals and vals['order_line']:
            self.button_compute(cr, uid, ids)

        return res
