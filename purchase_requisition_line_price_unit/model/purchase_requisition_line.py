# -*- encoding: utf-8 -*-
########################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
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
#
########################################################################
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
from openerp import netsvc

from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp import tools

class purchase_requisition(osv.Model):
    _inherit = "purchase.requisition"

    def _get_requisition(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('purchase.requisition.line').browse(cr, uid, ids, context=context):
            result[line.requisition_id.id] = True
        return result.keys()

    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        cur_obj=self.pool.get('res.currency')
        for requisition in self.browse(cr, uid, ids, context=context):
            res[requisition.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0,
            }
            val = val1 = 0.0
            cur = requisition.currency_id
            for line in requisition.line_ids:
               val1 += line.price_subtotal
               for c in self.pool.get('account.tax').compute_all(cr, uid, [], line.price_unit, line.product_qty, line.product_id)['taxes']:
                    val += c.get('amount', 0.0)
            #res[requisition.id]['amount_tax']=cur_obj.round(cr, uid, cur, val)
            amount_untaxed =cur_obj.round(cr, uid, cur, val1)
            res[requisition.id]['amount_total']= amount_untaxed # + res[requisition.id]['amount_tax']
        return res
    
    _columns = {
        'amount_total': fields.function(_amount_all, digits_compute= dp.get_precision('Account'), string='Total',
            store={
                'purchase.requisition.line': (_get_requisition, None, 10),
            }, multi="sums",help="The total amount"),
    }

class purchase_requisition_line(osv.Model):
    _inherit = "purchase.requisition.line"

    def _amount_line(self, cr, uid, ids, prop, arg, context=None):
        res = {}
        cur_obj=self.pool.get('res.currency')
        tax_obj = self.pool.get('account.tax')
        for line in self.browse(cr, uid, ids, context=context):
            taxes = tax_obj.compute_all(cr, uid, [], line.price_unit, line.product_qty, line.product_id)
            #cur = line.requisition_id.pricelist_id.currency_id
            cur = line.requisition_id.currency_id
            res[line.id] = cur_obj.round(cr, uid, cur, taxes['total'])
        return res

    _columns = {
        'price_unit': fields.float('Unit Price', required=True, digits_compute= dp.get_precision('Product Price')),
        'price_subtotal': fields.function(_amount_line, string='Subtotal', digits_compute= dp.get_precision('Account')),
    }
    
